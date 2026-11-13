// The client: sends each operation to <host>/graphql, retries when it's safe,
// and turns every failure into a RockwareError. SPEC.md sections 3 to 6, 8, 9.

import { OPERATIONS, Operations } from "./generated/operations.js";
import { VERSION } from "./generated/version.js";
import { RETRY } from "./generated/behavior.js";
import { type GraphqlError, RockwareError, codeForServerCode, codeForStatus, hintFor } from "./errors.js";
import type { CallOptions, Operation, PageOptions } from "./operation.js";

export interface RequestInfo {
  operation: string;
  /** 1 for the first try. */
  attempt: number;
  url: string;
}

export interface ResponseInfo {
  httpStatus?: number;
  durationMs: number;
  error?: RockwareError;
}

/** Ways to watch the client work. All optional; an error thrown in one is ignored. */
export interface Hooks {
  onRequest?(info: RequestInfo): void;
  onResponse?(info: RequestInfo, result: ResponseInfo): void;
  onRetry?(info: RequestInfo, error: RockwareError, delayMs: number): void;
}

export interface RockwareOptions {
  /** The plant's API host, like https://acme-api.rockware.io. */
  host: string;
  /** An API token (rw_app_…) or a connected token (rw_mcp_…), or a function that gives one. */
  token: string | (() => string | Promise<string>);
  /** Milliseconds for each attempt. Default 30,000. */
  timeout?: number;
  /** Retry when it's safe. Default true. */
  retry?: boolean;
  /** Your app's name and version, like acme-erp-sync/2.1. */
  userAgent?: string;
  hooks?: Hooks;
  /** A fetch to use instead of the global one. */
  fetch?: typeof fetch;
}

const DEFAULT_TIMEOUT_MS = 30_000;
const DEFAULT_MAX_PAGES = 10_000;
const SDK_AGENT = `rockware-sdk-typescript/${VERSION}`;

/**
 * Rockware's developer API.
 *
 * ```ts
 * const rockware = new RockwareClient({ host: "https://acme-api.rockware.io", token: process.env.ROCKWARE_TOKEN! });
 * for await (const product of rockware.listAllProducts({ updatedSince })) console.log(product.sku);
 * ```
 */
export class RockwareClient extends Operations {
  readonly host: string;
  readonly #token: RockwareOptions["token"];
  readonly #timeout: number;
  readonly #retry: boolean;
  readonly #userAgent: string;
  readonly #hooks: Hooks;
  readonly #fetch: typeof fetch;

  constructor(options: RockwareOptions) {
    super();
    this.host = checkHost(options.host);
    if (typeof options.token === "string" && !options.token.trim()) {
      throw new RockwareError("usage", "A token is required");
    }
    if (typeof options.token !== "string" && typeof options.token !== "function") {
      throw new RockwareError("usage", "A token is required");
    }
    const timeout = options.timeout ?? DEFAULT_TIMEOUT_MS;
    if (!(timeout > 0)) throw new RockwareError("usage", "timeout must be more than 0");
    this.#token = options.token;
    this.#timeout = timeout;
    this.#retry = options.retry ?? true;
    this.#userAgent = options.userAgent?.trim() ? `${options.userAgent.trim()} ${SDK_AGENT}` : SDK_AGENT;
    this.#hooks = options.hooks ?? {};
    this.#fetch = options.fetch ?? globalThis.fetch.bind(globalThis);
  }

  /** Send any operation from operations/ by name. The methods are easier; this is for tools. */
  call<R = unknown>(name: keyof typeof OPERATIONS, variables?: object, options?: CallOptions): Promise<R> {
    return this.run(OPERATIONS[name], variables, options);
  }

  protected async run<R>(operation: Operation, variables: object | undefined, options: CallOptions = {}): Promise<R> {
    const token = await this.#resolveToken();
    const url = `${this.host}/graphql`;
    const body = JSON.stringify({
      query: operation.document,
      variables: variables ?? {},
      operationName: operation.name,
    });
    const attempts = this.#retry ? RETRY.attempts : 1;

    for (let attempt = 1; ; attempt++) {
      const info: RequestInfo = { operation: operation.name, attempt, url };
      safely(() => this.#hooks.onRequest?.(info));
      const started = Date.now();
      const outcome = await this.#send(url, token, body, options.signal);
      const result = outcome.ok ? outcome.data : undefined;
      const error = outcome.ok ? undefined : redact(outcome.error, token);
      safely(() =>
        this.#hooks.onResponse?.(info, { httpStatus: outcome.httpStatus, durationMs: Date.now() - started, error }),
      );
      if (!error) return (result as Record<string, unknown>)[operation.root] as R;

      const delay = attempt < attempts ? retryDelay(error, operation, attempt) : undefined;
      if (delay === undefined) throw error;
      safely(() => this.#hooks.onRetry?.(info, error, delay));
      await sleep(delay, options.signal);
    }
  }

  protected async *runPages<N>(operation: Operation, variables: object, options: PageOptions = {}): AsyncGenerator<N> {
    const maxPages = options.maxPages ?? DEFAULT_MAX_PAGES;
    if (!(maxPages > 0)) throw new RockwareError("usage", "maxPages must be more than 0");
    let after: string | undefined;
    for (let page = 1; ; page++) {
      const connection = await this.run<{ nodes: N[]; pageInfo: { hasNextPage: boolean; endCursor?: string | null } }>(
        operation,
        after === undefined ? variables : { ...variables, after },
        options,
      );
      yield* connection.nodes;
      const next = connection.pageInfo.endCursor;
      if (!connection.pageInfo.hasNextPage || !next || page >= maxPages) return;
      after = next;
    }
  }

  async #resolveToken(): Promise<string> {
    const token = typeof this.#token === "string" ? this.#token : await this.#token();
    if (!token?.trim()) throw new RockwareError("usage", "A token is required");
    return token;
  }

  async #send(
    url: string,
    token: string,
    body: string,
    signal: AbortSignal | undefined,
  ): Promise<
    { ok: true; data: unknown; httpStatus: number } | { ok: false; error: RockwareError; httpStatus?: number }
  > {
    const timeout = AbortSignal.timeout(this.#timeout);
    let response: Response;
    try {
      response = await this.#fetch(url, {
        method: "POST",
        headers: {
          authorization: `Bearer ${token}`,
          "content-type": "application/json",
          accept: "application/json",
          "user-agent": this.#userAgent,
        },
        body,
        redirect: "manual",
        signal: signal ? AbortSignal.any([signal, timeout]) : timeout,
      });
    } catch (cause) {
      if (signal?.aborted) throw signal.reason;
      const timedOut = timeout.aborted;
      return {
        ok: false,
        error: new RockwareError(
          "network",
          timedOut
            ? `${this.host} didn't answer within ${this.#timeout / 1000} seconds`
            : `Can't reach ${this.host}: ${(cause as Error)?.message ?? cause}`,
          { retryable: true, hint: hintFor("network"), cause },
        ),
      };
    }
    return { ...(await readAnswer(response)), httpStatus: response.status };
  }
}

function checkHost(host: string): string {
  let url: URL;
  try {
    url = new URL(host);
  } catch {
    throw new RockwareError("usage", `host isn't a URL: ${host}`);
  }
  const local = url.hostname === "localhost" || url.hostname === "127.0.0.1" || url.hostname === "[::1]";
  if (url.protocol !== "https:" && !(url.protocol === "http:" && local)) {
    throw new RockwareError("usage", "host must use https://, except localhost");
  }
  return host.replace(/\/+$/, "");
}

/** Turn an HTTP answer into the data, or the error it means. */
async function readAnswer(
  response: Response,
): Promise<{ ok: true; data: unknown } | { ok: false; error: RockwareError }> {
  const status = response.status;
  const requestId = response.headers.get("x-request-id") ?? undefined;
  const retryAfter = parseRetryAfter(response.headers.get("retry-after"));
  const text = await response.text().catch(() => "");
  let body: { data?: unknown; errors?: GraphqlError[] } | undefined;
  try {
    body = text ? JSON.parse(text) : undefined;
  } catch {
    body = undefined;
  }
  const errors = Array.isArray(body?.errors) ? body.errors : [];
  const serverCode = errors[0]?.extensions?.code;
  const fields = { httpStatus: status, requestId, retryAfter, serverCode, errors };
  const message = errors.map((error) => error.message).join("; ");

  if (status < 200 || status >= 300) {
    const code = codeForStatus(status);
    return {
      ok: false,
      error: new RockwareError(code, message || `The server answered HTTP ${status}`, {
        ...fields,
        retryable: code === "rate_limit" || status >= 500,
        hint: hintFor(code, retryAfter),
      }),
    };
  }
  if (!body || typeof body !== "object") {
    return {
      ok: false,
      error: new RockwareError("api_error", `The server's answer isn't JSON (HTTP ${status})`, fields),
    };
  }
  if (errors.length) {
    const code = codeForServerCode(serverCode);
    return { ok: false, error: new RockwareError(code, message, { ...fields, hint: hintFor(code) }) };
  }
  if (!body.data || typeof body.data !== "object") {
    return { ok: false, error: new RockwareError("api_error", "The server's answer has no data", fields) };
  }
  return { ok: true, data: body.data };
}

/** Seconds from a Retry-After header: whole seconds, or an HTTP date still ahead. */
function parseRetryAfter(value: string | null): number | undefined {
  if (!value) return undefined;
  if (/^\d+$/.test(value.trim())) return Number(value.trim());
  const date = Date.parse(value);
  if (Number.isNaN(date)) return undefined;
  const seconds = Math.ceil((date - Date.now()) / 1000);
  return seconds > 0 ? seconds : undefined;
}

/** How long to wait before trying again, or undefined to stop. SPEC.md section 5. */
function retryDelay(error: RockwareError, operation: Operation, attempt: number): number | undefined {
  const refusedBeforeRunning = error.code === "rate_limit";
  const mightHaveRun = error.code === "network" || (error.httpStatus !== undefined && error.httpStatus >= 500);
  if (!refusedBeforeRunning && !(mightHaveRun && operation.safeToRepeat)) return undefined;
  if (error.retryAfter !== undefined) {
    return error.retryAfter > RETRY.maxRetryAfterSeconds ? undefined : error.retryAfter * 1000;
  }
  return RETRY.baseDelayMs * 2 ** (attempt - 1) + Math.random() * RETRY.maxJitterMs;
}

function sleep(ms: number, signal: AbortSignal | undefined): Promise<void> {
  return new Promise((resolve, reject) => {
    if (signal?.aborted) return reject(signal.reason);
    const timer = setTimeout(() => {
      signal?.removeEventListener("abort", onAbort);
      resolve();
    }, ms);
    const onAbort = () => {
      clearTimeout(timer);
      reject(signal?.reason);
    };
    signal?.addEventListener("abort", onAbort, { once: true });
  });
}

/** The token never leaves in an error. */
function redact(error: RockwareError, token: string): RockwareError {
  if (!error.message.includes(token)) return error;
  return new RockwareError(error.code, error.message.split(token).join("[hidden]"), {
    hint: error.hint,
    httpStatus: error.httpStatus,
    retryable: error.retryable,
    retryAfter: error.retryAfter,
    requestId: error.requestId,
    serverCode: error.serverCode,
    errors: error.errors.map((e) => ({ ...e, message: e.message.split(token).join("[hidden]") })),
    cause: error.cause,
  });
}

function safely(hook: () => void): void {
  try {
    hook();
  } catch {
    // A hook's own failure never changes the call.
  }
}
