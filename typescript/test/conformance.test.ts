// Runs the repo's shared tests (conformance/) against this SDK. The fake
// fetch below plays the server. See conformance/README.md for the format.

import { readFileSync, readdirSync } from "node:fs";
import { dirname, join } from "node:path";
import { fileURLToPath } from "node:url";
import { describe, expect, it } from "vitest";
import { type OperationName, RockwareClient, RockwareError, verifyWebhook } from "../src/index.js";

const conformance = join(dirname(fileURLToPath(import.meta.url)), "..", "..", "conformance");

interface Answer {
  status?: number;
  headers?: Record<string, string>;
  body?: unknown;
  rawBody?: string;
  networkError?: boolean;
}

interface Case {
  name: string;
  client?: { host?: string; token?: string; userAgent?: string; retry?: boolean };
  operation: OperationName;
  variables?: Record<string, unknown>;
  paginate?: boolean;
  maxPages?: number;
  responses: Answer[];
  assertions: Array<Record<string, any>>;
}

interface Sent {
  at: number;
  method: string;
  url: string;
  headers: Headers;
  body: any;
}

function fakeServer(answers: Answer[]) {
  const sent: Sent[] = [];
  const fakeFetch: typeof fetch = async (input, init) => {
    sent.push({
      at: Date.now(),
      method: init?.method ?? "GET",
      url: String(input),
      headers: new Headers(init?.headers),
      body: JSON.parse(String(init?.body)),
    });
    const answer = answers[sent.length - 1];
    if (!answer) throw new Error(`The test has no answer for request ${sent.length}`);
    if (answer.networkError) throw new TypeError("fetch failed");
    const headers = new Headers();
    for (const [name, value] of Object.entries(answer.headers ?? {})) headers.set(name, resolveToken(value));
    const body = answer.rawBody ?? (answer.body === undefined ? null : JSON.stringify(answer.body));
    return new Response(body, { status: answer.status ?? 200, headers });
  };
  return { sent, fakeFetch };
}

/** {{httpdate+Ns}}: an HTTP date N + 1 seconds after now, on whole seconds. */
function resolveToken(value: string): string {
  return value.replace(/\{\{httpdate\+(\d{1,9})s\}\}/g, (_, seconds) =>
    new Date((Math.floor(Date.now() / 1000) + Number(seconds) + 1) * 1000).toUTCString(),
  );
}

function at(value: unknown, path: string): unknown {
  if (path === "") return value;
  let current: any = value;
  for (const key of path.split(".")) {
    if (current === undefined || current === null) return undefined;
    current = key === "length" && Array.isArray(current) ? current.length : current[key];
  }
  return current;
}

async function run(test: Case) {
  const { sent, fakeFetch } = fakeServer(test.responses);
  let result: unknown;
  let error: unknown;
  const collected: unknown[] = [];
  try {
    const client = new RockwareClient({
      host: test.client?.host ?? "https://acme-api.example.com",
      token: test.client?.token ?? "rw_app_test",
      userAgent: test.client?.userAgent,
      retry: test.client?.retry,
      fetch: fakeFetch,
    });
    const method = test.operation[0]!.toLowerCase() + test.operation.slice(1);
    if (test.paginate) {
      const all = `listAll${test.operation.slice("List".length)}`;
      for await (const record of (client as any)[all](test.variables ?? {}, { maxPages: test.maxPages })) {
        collected.push(record);
      }
    } else {
      result = await (client as any)[method](...(test.variables ? [test.variables] : []));
    }
  } catch (caught) {
    error = caught;
  }
  if (test.paginate) result = collected;
  return { sent, result, error };
}

const files = readdirSync(join(conformance, "tests")).filter((file) => file.endsWith(".json"));

for (const file of files) {
  const cases = JSON.parse(readFileSync(join(conformance, "tests", file), "utf8")) as Case[];
  describe(file, () => {
    for (const test of cases) {
      it(test.name, { timeout: 15_000 }, async () => {
        const { sent, result, error } = await run(test);
        for (const assertion of test.assertions) {
          const index = assertion.index ?? 0;
          switch (assertion.type) {
            case "requestCount":
              expect(sent.length, "requests").toBe(assertion.expected);
              break;
            case "requestMethod":
              expect(sent[0]?.method).toBe(assertion.expected);
              break;
            case "requestUrl":
              expect(sent[0]?.url).toBe(assertion.expected);
              break;
            case "requestHeader": {
              const value = sent[index]?.headers.get(assertion.name);
              if ("expected" in assertion) expect(value).toBe(assertion.expected);
              if (assertion.pattern) expect(value).toMatch(new RegExp(assertion.pattern));
              break;
            }
            case "requestBody": {
              const value = at(sent[index]?.body, assertion.path);
              if (assertion.absent) expect(value, assertion.path).toBeUndefined();
              if ("expected" in assertion) expect(value, assertion.path).toEqual(assertion.expected);
              if (assertion.pattern) expect(String(value)).toMatch(new RegExp(assertion.pattern));
              break;
            }
            case "delayBetweenRequests": {
              const gap = sent[index + 1]!.at - sent[index]!.at;
              expect(gap, `gap after request ${index}`).toBeGreaterThanOrEqual(assertion.minMs);
              if (assertion.maxMs !== undefined) expect(gap).toBeLessThanOrEqual(assertion.maxMs);
              break;
            }
            case "noError":
              expect(error).toBeUndefined();
              break;
            case "error": {
              expect(error).toBeInstanceOf(RockwareError);
              const fields = ["code", "httpStatus", "retryable", "retryAfter", "requestId", "serverCode"];
              for (const field of fields) {
                if (field in assertion) expect((error as any)[field], field).toEqual(assertion[field]);
              }
              break;
            }
            case "errorMessage": {
              const message = (error as Error).message;
              if (assertion.pattern) expect(message).toMatch(new RegExp(assertion.pattern));
              if (assertion.excludes) expect(message).not.toContain(assertion.excludes);
              break;
            }
            case "errorMessageLength":
              expect((error as Error).message.length).toBeLessThanOrEqual(assertion.max);
              break;
            case "errorCount":
              expect((error as RockwareError).errors).toHaveLength(assertion.expected);
              break;
            case "result":
              expect(at(result, assertion.path), assertion.path || "result").toEqual(assertion.expected);
              break;
            default:
              throw new Error(`Unknown assertion type ${assertion.type}`);
          }
        }
      });
    }
  });
}

describe("webhooks.json", () => {
  const { cases } = JSON.parse(readFileSync(join(conformance, "webhooks.json"), "utf8")) as {
    cases: Array<{
      name: string;
      secret: string;
      body: string;
      header: string;
      now: number;
      tolerance?: number;
      valid: boolean;
    }>;
  };
  for (const test of cases) {
    it(test.name, async () => {
      expect(
        await verifyWebhook(test.secret, test.body, test.header, { now: test.now, tolerance: test.tolerance }),
      ).toBe(test.valid);
    });
  }
});
