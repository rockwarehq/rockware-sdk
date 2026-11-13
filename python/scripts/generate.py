"""Make src/rockware/_generated/ from the repo's schema, operations/ and behavior.json.

Run it after any of those change:  python scripts/generate.py

The TypeScript generator checks the operations against SPEC.md section 2 and
the server's limits. This one only checks that they're valid for the schema.
"""

from __future__ import annotations

import json
import keyword
import re
import subprocess
import sys
from pathlib import Path

from graphql import (
    FieldNode,
    FragmentDefinitionNode,
    FragmentSpreadNode,
    GraphQLEnumType,
    GraphQLInputObjectType,
    GraphQLList,
    GraphQLNonNull,
    GraphQLObjectType,
    GraphQLScalarType,
    ListTypeNode,
    NonNullTypeNode,
    OperationDefinitionNode,
    OperationType,
    SelectionSetNode,
    TypeNode,
    build_schema,
    parse,
    print_ast,
    validate,
)

HERE = Path(__file__).resolve().parent
PACKAGE = HERE.parent
ROOT = PACKAGE.parent
OUT = PACKAGE / "src" / "rockware" / "_generated"
HEADER = "# Made by scripts/generate.py from the repo's schema/, operations/ and behavior.json. Don't edit it.\n"

# What the server sends for each scalar. DateTime and Decimal stay strings, so
# no precision is lost. A DateTime you send may also be a datetime.
OUTPUT_SCALARS = {
    "ID": "str",
    "String": "str",
    "Int": "int",
    "Float": "float",
    "Boolean": "bool",
    "DateTime": "str",
    "Decimal": "str",
    "JSON": "Any",
}
INPUT_SCALARS = {**OUTPUT_SCALARS, "DateTime": "str | datetime"}

schema = build_schema((ROOT / "schema" / "developer-api.graphql").read_text())
document = parse("\n".join(p.read_text() for p in sorted((ROOT / "operations").glob("*.graphql"))))
behavior = json.loads((ROOT / "behavior.json").read_text())
version = (ROOT / "VERSION").read_text().strip()

problems = validate(schema, document)
if problems:
    sys.exit("operations/ has problems:\n- " + "\n- ".join(p.message for p in problems))

fragments: dict[str, FragmentDefinitionNode] = {}
operations: list[OperationDefinitionNode] = []
for definition in document.definitions:
    if isinstance(definition, FragmentDefinitionNode):
        fragments[definition.name.value] = definition
    elif isinstance(definition, OperationDefinitionNode):
        operations.append(definition)


def snake(name: str) -> str:
    """updatedSince → updated_since, ListProductionRuns → list_production_runs."""
    return re.sub(r"(?<=[a-z0-9])([A-Z])", r"_\1", name).lower()


def pascal(name: str) -> str:
    return name[0].upper() + name[1:]


def named(graphql_type):
    while isinstance(graphql_type, (GraphQLNonNull, GraphQLList)):
        graphql_type = graphql_type.of_type
    return graphql_type


def wrap(graphql_type, inner: str) -> str:
    """Add list and None around a named type's annotation."""
    if isinstance(graphql_type, GraphQLNonNull):
        return wrap_non_null(graphql_type.of_type, inner)
    return f"{wrap_non_null(graphql_type, inner)} | None"


def wrap_non_null(graphql_type, inner: str) -> str:
    if isinstance(graphql_type, GraphQLList):
        return f"list[{wrap(graphql_type.of_type, inner)}]"
    return inner


# ── Result types ─────────────────────────────────────────────────────────────

classes: list[str] = []
"""Every result TypedDict, each after the ones it uses."""


def typed_dict(name: str, fields: list[tuple[str, str]], bases: list[str]) -> None:
    for field_name, _ in fields:
        if keyword.iskeyword(field_name):
            sys.exit(f"{name}.{field_name} is a Python keyword; alias it in operations/")
    body = "\n".join(f"    {f}: {a}" for f, a in fields) or "    pass"
    classes.append(f"class {name}({', '.join(bases) or 'TypedDict'}):\n{body}\n")


def parts(selection_set: SelectionSetNode) -> tuple[list[str], list[FieldNode]]:
    spreads, fields = [], []
    for selection in selection_set.selections:
        if isinstance(selection, FragmentSpreadNode):
            spreads.append(selection.name.value)
        elif isinstance(selection, FieldNode):
            fields.append(selection)
        else:
            sys.exit("Inline fragments aren't supported; use a named fragment")
    return spreads, fields


def selection_class(name: str, parent: GraphQLObjectType, selection_set: SelectionSetNode) -> str:
    """The TypedDict for a selection. A lone fragment spread is the fragment's own class."""
    spreads, fields = parts(selection_set)
    if len(spreads) == 1 and not fields:
        return spreads[0]
    typed_dict(name, [(f.name.value, field_annotation(name, parent, f)) for f in fields], spreads)
    return name


def field_annotation(owner: str, parent: GraphQLObjectType, field: FieldNode) -> str:
    definition = parent.fields[field.name.value]
    inner_type = named(definition.type)
    if isinstance(inner_type, GraphQLObjectType):
        assert field.selection_set
        inner = selection_class(owner + pascal(field.name.value), inner_type, field.selection_set)
    elif isinstance(inner_type, GraphQLEnumType):
        inner = inner_type.name
    else:
        inner = OUTPUT_SCALARS[inner_type.name]
    return wrap(definition.type, inner)


def root_annotation(operation_name: str, root_type: GraphQLObjectType, field: FieldNode) -> str:
    """Like field_annotation, but the class for the root field is <Operation>Result."""
    definition = root_type.fields[field.name.value]
    inner_type = named(definition.type)
    if isinstance(inner_type, GraphQLObjectType):
        assert field.selection_set
        inner = selection_class(f"{operation_name}Result", inner_type, field.selection_set)
    else:
        inner = OUTPUT_SCALARS[inner_type.name]
    return wrap(definition.type, inner)


def spreads_in(selection_set: SelectionSetNode | None) -> list[str]:
    found: list[str] = []
    for selection in selection_set.selections if selection_set else []:
        if isinstance(selection, FragmentSpreadNode):
            found.append(selection.name.value)
        elif isinstance(selection, FieldNode):
            found.extend(spreads_in(selection.selection_set))
    return found


ordered: list[str] = []


def visit(name: str) -> None:
    if name in ordered:
        return
    for spread in spreads_in(fragments[name].selection_set):
        visit(spread)
    ordered.append(name)


for fragment_name in fragments:
    visit(fragment_name)

for fragment_name in ordered:
    fragment = fragments[fragment_name]
    parent = schema.get_type(fragment.type_condition.name.value)
    assert isinstance(parent, GraphQLObjectType)
    spreads, fields = parts(fragment.selection_set)
    typed_dict(fragment_name, [(f.name.value, field_annotation(fragment_name, parent, f)) for f in fields], spreads)


# ── Input types and enums ────────────────────────────────────────────────────


def input_annotation(graphql_type) -> str:
    inner_type = named(graphql_type)
    inner = INPUT_SCALARS[inner_type.name] if isinstance(inner_type, GraphQLScalarType) else inner_type.name
    return wrap(graphql_type, inner)


input_classes: list[str] = []
for input_type in sorted(
    (t for t in schema.type_map.values() if isinstance(t, GraphQLInputObjectType)), key=lambda t: t.name
):
    required = [
        (n, input_annotation(f.type)) for n, f in input_type.fields.items() if isinstance(f.type, GraphQLNonNull)
    ]
    optional = [
        (n, input_annotation(f.type)) for n, f in input_type.fields.items() if not isinstance(f.type, GraphQLNonNull)
    ]
    doc = f'    """{input_type.description}"""\n\n' if input_type.description else ""
    if required:
        lines = "\n".join(f"    {n}: {a}" for n, a in required)
        input_classes.append(f"class _{input_type.name}Required(TypedDict):\n{lines}\n")
        base = f"_{input_type.name}Required, total=False"
    else:
        base = "TypedDict, total=False"
    lines = "\n".join(f"    {n}: {a}" for n, a in optional) or "    pass"
    input_classes.append(f"class {input_type.name}({base}):\n{doc}{lines}\n")

enums = sorted(
    (t for t in schema.type_map.values() if isinstance(t, GraphQLEnumType) and not t.name.startswith("__")),
    key=lambda t: t.name,
)
enum_lines = [f"{e.name} = Literal[{', '.join(json.dumps(v) for v in e.values)}]" for e in enums]


# ── Operations ───────────────────────────────────────────────────────────────


def variable_annotation(type_node: TypeNode) -> str:
    if isinstance(type_node, NonNullTypeNode):
        return variable_annotation_inner(type_node.type)
    return f"{variable_annotation_inner(type_node)} | None"


def variable_annotation_inner(type_node: TypeNode) -> str:
    if isinstance(type_node, ListTypeNode):
        return f"list[{variable_annotation(type_node.type)}]"
    graphql_type = schema.get_type(type_node.name.value)  # type: ignore[attr-defined]
    return INPUT_SCALARS[graphql_type.name] if isinstance(graphql_type, GraphQLScalarType) else graphql_type.name


def used_fragments(selection_set: SelectionSetNode, found: list[str]) -> list[str]:
    for selection in selection_set.selections:
        if isinstance(selection, FragmentSpreadNode):
            if selection.name.value not in found:
                found.append(selection.name.value)
                used_fragments(fragments[selection.name.value].selection_set, found)
        elif isinstance(selection, FieldNode) and selection.selection_set:
            used_fragments(selection.selection_set, found)
    return found


table: list[str] = []
sync_methods: list[str] = []
async_methods: list[str] = []
pageable = 0

for operation in operations:
    name = operation.name.value  # type: ignore[union-attr]
    mutation = operation.operation == OperationType.MUTATION
    root_type = schema.mutation_type if mutation else schema.query_type
    assert root_type
    root_field = operation.selection_set.selections[0]
    assert isinstance(root_field, FieldNode)
    root = root_field.name.value
    definition = root_type.fields[root]
    result = root_annotation(name, root_type, root_field)

    text = "\n\n".join(
        print_ast(d) for d in [operation, *(fragments[f] for f in used_fragments(operation.selection_set, []))]
    )
    safe = (not mutation) or name in behavior["safeToRepeat"]
    table.append(
        f'    "{name}": Operation(\n        name="{name}",\n        root="{root}",\n        mutation={mutation},\n'
        f"        safe_to_repeat={safe},\n        document={json.dumps(text)},\n    ),"
    )

    params: list[tuple[str, str, str]] = []  # (graphql name, python parameter, mapping)
    for variable in operation.variable_definitions or []:
        var_name = variable.variable.name.value
        annotation = variable_annotation(variable.type)
        param = f"{snake(var_name)}: {annotation}" + ("" if isinstance(variable.type, NonNullTypeNode) else " = None")
        params.append((var_name, param, f'"{var_name}": {snake(var_name)}'))

    def signature(chosen: list[tuple[str, str, str]], extra: list[str] | None = None) -> str:
        names = [p for _, p, _ in chosen] + (extra or [])
        return ", ".join(["self", "*", *names]) if names else "self"

    def variables_dict(chosen: list[tuple[str, str, str]]) -> str:
        return "{" + ", ".join(m for _, _, m in chosen) + "}"

    method = snake(name)
    doc = f'        """{definition.description}"""\n' if definition.description else ""
    sync_methods.append(
        f"    def {method}({signature(params)}) -> {result}:\n{doc}"
        f'        return self._run(OPERATIONS["{name}"], {variables_dict(params)})\n'
    )
    async_methods.append(
        f"    async def {method}({signature(params)}) -> {result}:\n{doc}"
        f'        return await self._run(OPERATIONS["{name}"], {variables_dict(params)})\n'
    )

    connection = named(definition.type)
    if (
        not mutation
        and name.startswith("List")
        and isinstance(connection, GraphQLObjectType)
        and {"nodes", "pageInfo"} <= set(connection.fields)
        and any(var_name == "after" for var_name, _, _ in params)
    ):
        pageable += 1
        assert root_field.selection_set
        nodes = next(f for f in parts(root_field.selection_set)[1] if f.name.value == "nodes")
        assert nodes.selection_set
        spreads, fields = parts(nodes.selection_set)
        node_type = spreads[0] if len(spreads) == 1 and not fields else f"{name}ResultNodes"
        page_params = [p for p in params if p[0] != "after"]
        page_signature = signature(page_params, ["max_pages: int = DEFAULT_MAX_PAGES"])
        all_method = "list_all_" + snake(name.removeprefix("List"))
        page_doc = f'        """Every record from {method}, page by page. See SPEC.md, Paging."""\n'
        call = f'self._run_pages(OPERATIONS["{name}"], {variables_dict(page_params)}, max_pages)'
        sync_methods.append(
            f"    def {all_method}({page_signature}) -> Iterator[{node_type}]:\n{page_doc}        return {call}\n"
        )
        async_methods.append(
            f"    def {all_method}({page_signature}) -> AsyncIterator[{node_type}]:\n{page_doc}        return {call}\n"
        )


# ── Write ────────────────────────────────────────────────────────────────────

OUT.mkdir(parents=True, exist_ok=True)
(OUT / "__init__.py").write_text(HEADER)
(OUT / "types.py").write_text(
    HEADER
    + '"""Every type the operations send and get back. Field names are the API\'s own."""\n\n'
    + "from __future__ import annotations\n\n"
    + "from datetime import datetime\nfrom typing import Any, Literal, TypedDict\n\n"
    + "\n".join(enum_lines)
    + "\n\n\n"
    + "\n\n".join(input_classes)
    + "\n\n"
    + "\n\n".join(classes)
)
(OUT / "operations.py").write_text(
    f'''{HEADER}"""One method per operation in operations/. The clients fill in how they're sent."""

from __future__ import annotations

from abc import ABC, abstractmethod
from collections.abc import AsyncIterator, Iterator
from datetime import datetime
from typing import Any

from .._operation import DEFAULT_MAX_PAGES, Operation
from .types import *  # noqa: F403

OPERATIONS: dict[str, Operation] = {{
{chr(10).join(table)}
}}

PAGEABLE = {pageable}


class SyncOperations(ABC):
    @abstractmethod
    def _run(self, operation: Operation, variables: dict[str, Any]) -> Any: ...

    @abstractmethod
    def _run_pages(self, operation: Operation, variables: dict[str, Any], max_pages: int) -> Iterator[Any]: ...

{chr(10).join(sync_methods)}

class AsyncOperations(ABC):
    @abstractmethod
    async def _run(self, operation: Operation, variables: dict[str, Any]) -> Any: ...

    @abstractmethod
    def _run_pages(self, operation: Operation, variables: dict[str, Any], max_pages: int) -> AsyncIterator[Any]: ...

{chr(10).join(async_methods)}'''
)
(OUT / "version.py").write_text(f'{HEADER}\nVERSION = "{version}"\n')
(OUT / "behavior.py").write_text(
    f'{HEADER}\n"""How to retry. SPEC.md section 5."""\n\n'
    f"RETRY: dict[str, int] = {json.dumps(behavior['retry'], indent=4)}\n"
)

# Format what was written, so it reads like the rest of the code.
subprocess.run([sys.executable, "-m", "ruff", "format", "--quiet", str(OUT)], check=True)
subprocess.run([sys.executable, "-m", "ruff", "check", "--quiet", "--fix", "--select", "I,F401", str(OUT)], check=False)
print(f"Made {len(operations)} operations ({pageable} pageable) for SDK {version}.")
