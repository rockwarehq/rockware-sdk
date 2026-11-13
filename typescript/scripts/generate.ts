// Makes src/generated/ from the schema, operations/ and behavior.json, all at
// the repo root. Run it after any of those change: pnpm generate.
//
// It also checks the operations against SPEC.md section 2, so a broken one
// fails here, before any SDK is built from it.
//
// pnpm check-operations only checks, and writes nothing. With RW_SCHEMA set
// to another schema file, it checks against that one: rw-server's CI does
// this with each PR's schema, so an API change that would break the SDKs
// fails there first.

import { readFileSync, readdirSync, writeFileSync, mkdirSync } from "node:fs";
import { dirname, join } from "node:path";
import { fileURLToPath } from "node:url";
import { codegen } from "@graphql-codegen/core";
import * as typescriptPlugin from "@graphql-codegen/typescript";
import * as operationsPlugin from "@graphql-codegen/typescript-operations";
import {
  type DocumentNode,
  type FragmentDefinitionNode,
  type GraphQLSchema,
  type OperationDefinitionNode,
  type SelectionSetNode,
  Kind,
  buildSchema,
  getNamedType,
  isObjectType,
  parse,
  print,
  validate,
} from "graphql";

const here = dirname(fileURLToPath(import.meta.url));
const root = join(here, "..", "..");
const out = join(here, "..", "src", "generated");

// The server's limits (rw-server apps/imm/src/transport/graphql/index.ts).
const MAX_DEPTH = 6;
const MAX_FIELDS = 300;
const VERBS = [
  "Get",
  "List",
  "Upsert",
  "Create",
  "Update",
  "Delete",
  "Rotate",
  "Send",
  "Redeliver",
  "Sequence",
  "Link",
];

const checkOnly = process.argv.includes("--check");
const schemaText = readFileSync(process.env.RW_SCHEMA ?? join(root, "schema", "developer-api.graphql"), "utf8");
const schema = buildSchema(schemaText);
const operationFiles = readdirSync(join(root, "operations"))
  .filter((file) => file.endsWith(".graphql"))
  .sort();
const document = parse(operationFiles.map((file) => readFileSync(join(root, "operations", file), "utf8")).join("\n"));
const behavior = JSON.parse(readFileSync(join(root, "behavior.json"), "utf8")) as {
  retry: { attempts: number; baseDelayMs: number; maxJitterMs: number; maxRetryAfterSeconds: number };
  safeToRepeat: string[];
};
const version = readFileSync(join(root, "VERSION"), "utf8").trim();

const problems: string[] = validate(schema, document).map((error) => error.message);
const fragments = new Map<string, FragmentDefinitionNode>();
const operations: OperationDefinitionNode[] = [];
for (const definition of document.definitions) {
  if (definition.kind === Kind.FRAGMENT_DEFINITION) fragments.set(definition.name.value, definition);
  if (definition.kind === Kind.OPERATION_DEFINITION) operations.push(definition);
}

/** Depth and field count the way the server measures them. */
function measure(selectionSet: SelectionSetNode): { depth: number; fields: number } {
  let depth = -1;
  let fields = 0;
  for (const selection of selectionSet.selections) {
    if (selection.kind === Kind.FIELD) {
      const below = selection.selectionSet ? measure(selection.selectionSet) : { depth: -1, fields: 0 };
      depth = Math.max(depth, below.depth + 1);
      fields += below.fields + 1;
    } else {
      const set =
        selection.kind === Kind.FRAGMENT_SPREAD
          ? fragments.get(selection.name.value)?.selectionSet
          : selection.selectionSet;
      if (!set) continue;
      const inner = measure(set);
      depth = Math.max(depth, inner.depth);
      fields += inner.fields;
    }
  }
  return { depth, fields };
}

/** The fragments an operation uses, and the ones they use, in the order first used. */
function usedFragments(selectionSet: SelectionSetNode, found = new Set<string>()): Set<string> {
  for (const selection of selectionSet.selections) {
    if (selection.kind === Kind.FRAGMENT_SPREAD) {
      const name = selection.name.value;
      if (found.has(name)) continue;
      found.add(name);
      const fragment = fragments.get(name);
      if (fragment) usedFragments(fragment.selectionSet, found);
    } else if (selection.selectionSet) {
      usedFragments(selection.selectionSet, found);
    }
  }
  return found;
}

interface Planned {
  name: string;
  method: string;
  root: string;
  mutation: boolean;
  safeToRepeat: boolean;
  document: string;
  typeName: string;
  hasVariables: boolean;
  variablesRequired: boolean;
  /** For a list that returns a connection: what else it needs besides `after`. */
  pageable: boolean;
  description?: string;
}

const planned: Planned[] = [];
const names = new Set<string>();
for (const operation of operations) {
  const name = operation.name?.value;
  if (!name) {
    problems.push("An operation has no name");
    continue;
  }
  if (names.has(name)) problems.push(`${name} is defined twice`);
  names.add(name);
  if (!VERBS.some((verb) => name.startsWith(verb)))
    problems.push(`${name} doesn't start with one of: ${VERBS.join(", ")}`);
  if (operation.operation === "subscription") problems.push(`${name} is a subscription; the API has none`);
  const [first, ...rest] = operation.selectionSet.selections;
  if (!first || rest.length > 0 || first.kind !== Kind.FIELD || first.alias) {
    problems.push(`${name} must ask for exactly one root field, with no alias`);
    continue;
  }
  const { depth, fields } = measure(operation.selectionSet);
  if (depth > MAX_DEPTH) problems.push(`${name} nests ${depth} deep; the server allows ${MAX_DEPTH}`);
  if (fields > MAX_FIELDS) problems.push(`${name} asks for ${fields} fields; the server allows ${MAX_FIELDS}`);

  const mutation = operation.operation === "mutation";
  const rootType = mutation ? schema.getMutationType() : schema.getQueryType();
  const field = rootType?.getFields()[first.name.value];
  const returns = field && getNamedType(field.type);
  const pageable =
    !mutation &&
    name.startsWith("List") &&
    !!returns &&
    isObjectType(returns) &&
    "pageInfo" in returns.getFields() &&
    "nodes" in returns.getFields() &&
    (operation.variableDefinitions ?? []).some((variable) => variable.variable.name.value === "after");
  const variables = operation.variableDefinitions ?? [];
  const used = [...usedFragments(operation.selectionSet)].flatMap((fragmentName) => fragments.get(fragmentName) ?? []);
  planned.push({
    name,
    method: name.charAt(0).toLowerCase() + name.slice(1),
    root: first.name.value,
    mutation,
    safeToRepeat: !mutation || behavior.safeToRepeat.includes(name),
    document: [operation, ...used].map((definition) => print(definition)).join("\n\n"),
    typeName: `${name}${mutation ? "Mutation" : "Query"}`,
    hasVariables: variables.length > 0,
    variablesRequired: variables.some(
      (variable) => variable.type.kind === Kind.NON_NULL_TYPE && !variable.defaultValue,
    ),
    pageable,
    description: field?.description ?? undefined,
  });
}
for (const name of behavior.safeToRepeat) {
  const operation = planned.find((op) => op.name === name);
  if (!operation) problems.push(`behavior.json lists ${name}, which isn't an operation`);
  else if (!operation.mutation) problems.push(`behavior.json lists ${name}, a query; queries are always safe`);
}

if (problems.length) {
  console.error(`operations/ has problems:\n- ${problems.join("\n- ")}`);
  process.exit(1);
}
if (checkOnly) {
  console.log(
    `All ${planned.length} operations are fine against ${process.env.RW_SCHEMA ?? "schema/developer-api.graphql"}.`,
  );
  process.exit(0);
}

const header =
  "// Made by scripts/generate.ts from the repo's schema/, operations/ and behavior.json. Don't edit it.\n";

// Scalars are what the server sends: DateTime and Decimal as strings. Every
// SDK keeps Decimal a string, so no precision is lost.
const sharedConfig = {
  scalars: { DateTime: "string", Decimal: "string", JSON: "unknown" },
  strictScalars: true,
  enumsAsTypes: true,
  onlyOperationTypes: true,
  skipTypename: true,
  avoidOptionals: false,
  maybeValue: "T | null",
  inputMaybeValue: "T | null | undefined",
  useTypeImports: true,
};
const typesText = await codegen({
  schema: parse(schemaText),
  schemaAst: schema as GraphQLSchema,
  documents: [{ document: document as DocumentNode, location: "operations" }],
  filename: "types.ts",
  config: sharedConfig,
  plugins: [{ typescript: {} }, { typescriptOperations: {} }],
  pluginMap: { typescript: typescriptPlugin, typescriptOperations: operationsPlugin },
});

function jsdoc(text: string | undefined, indent: string): string {
  if (!text) return "";
  const lines = text.split("\n").map((line) => `${indent} * ${line}`.trimEnd());
  return `${indent}/**\n${lines.join("\n")}\n${indent} */\n`;
}

const table = planned
  .map(
    (op) =>
      `  ${op.name}: {\n    name: "${op.name}",\n    root: "${op.root}",\n    mutation: ${op.mutation},\n    safeToRepeat: ${op.safeToRepeat},\n    document: ${JSON.stringify(op.document)},\n  },`,
  )
  .join("\n");

const methods = planned
  .map((op) => {
    const result = `T.${op.typeName}["${op.root}"]`;
    const variablesType = `T.${op.typeName}Variables`;
    const params = !op.hasVariables
      ? "options?: CallOptions"
      : op.variablesRequired
        ? `variables: ${variablesType}, options?: CallOptions`
        : `variables: ${variablesType} = {}, options?: CallOptions`;
    const args = op.hasVariables ? "variables" : "undefined";
    let text = `${jsdoc(op.description, "  ")}  ${op.method}(${params}): Promise<${result}> {\n    return this.run(OPERATIONS.${op.name}, ${args}, options);\n  }\n`;
    if (op.pageable) {
      const all = `listAll${op.name.slice("List".length)}`;
      const pageVariables = `Omit<${variablesType}, "after">`;
      const pageParams = op.variablesRequired
        ? `variables: ${pageVariables}, options?: PageOptions`
        : `variables: ${pageVariables} = {}, options?: PageOptions`;
      text += `\n  /** Every record from ${op.method}, page by page. See SPEC.md, Paging. */\n  ${all}(${pageParams}): AsyncGenerator<${result}["nodes"][number]> {\n    return this.runPages(OPERATIONS.${op.name}, variables, options);\n  }\n`;
    }
    return text;
  })
  .join("\n");

const pageable = planned.filter((op) => op.pageable).map((op) => `"${op.name}"`);

mkdirSync(out, { recursive: true });
writeFileSync(join(out, "types.ts"), `${header}/* eslint-disable */\n${typesText}`);
writeFileSync(
  join(out, "operations.ts"),
  `${header}
import type * as T from "./types.js";
import type { CallOptions, Operation, PageOptions } from "../operation.js";

export const OPERATIONS = {
${table}
} as const satisfies Record<string, Operation>;

export type OperationName = keyof typeof OPERATIONS;

/** Operations that return a connection, which listAll… pages through. */
export const PAGEABLE: readonly OperationName[] = [${pageable.join(", ")}];

/** One method per operation in operations/. RockwareClient fills in how they're sent. */
export abstract class Operations {
  protected abstract run<R>(operation: Operation, variables: object | undefined, options?: CallOptions): Promise<R>;
  protected abstract runPages<N>(operation: Operation, variables: object, options?: PageOptions): AsyncGenerator<N>;

${methods}}
`,
);
writeFileSync(join(out, "version.ts"), `${header}\nexport const VERSION = "${version}";\n`);
writeFileSync(
  join(out, "behavior.ts"),
  `${header}\n/** How to retry. SPEC.md section 5. */\nexport const RETRY = ${JSON.stringify(behavior.retry, null, 2)} as const;\n`,
);

console.log(`Made ${planned.length} operations (${pageable.length} pageable) for SDK ${version}.`);
