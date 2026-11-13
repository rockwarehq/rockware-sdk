// Every way a call can fail, as one error type. SPEC.md section 4.

export type ErrorCode =
  | "usage"
  | "auth_required"
  | "forbidden"
  | "not_found"
  | "validation"
  | "rate_limit"
  | "api_error"
  | "network";

/** One error as the server sent it. */
export interface GraphqlError {
  message: string;
  path?: Array<string | number>;
  extensions?: { code?: string; [key: string]: unknown };
}

export interface RockwareErrorFields {
  hint?: string;
  httpStatus?: number;
  retryable?: boolean;
  retryAfter?: number;
  requestId?: string;
  serverCode?: string;
  errors?: GraphqlError[];
  cause?: unknown;
}

export const MAX_MESSAGE_LENGTH = 500;

export class RockwareError extends Error {
  override readonly name = "RockwareError";
  readonly code: ErrorCode;
  /** What to do about it, when the SDK knows. */
  readonly hint?: string;
  readonly httpStatus?: number;
  /** Whether trying again later might work. */
  readonly retryable: boolean;
  /** Seconds the server asked to wait. */
  readonly retryAfter?: number;
  /** The server's id for the request. Give it to Rockware support. */
  readonly requestId?: string;
  /** The server's own code (extensions.code), as sent. */
  readonly serverCode?: string;
  /** Every GraphQL error the server sent, as sent. */
  readonly errors: GraphqlError[];

  constructor(code: ErrorCode, message: string, fields: RockwareErrorFields = {}) {
    super(truncate(message), fields.cause === undefined ? undefined : { cause: fields.cause });
    this.code = code;
    this.hint = fields.hint;
    this.httpStatus = fields.httpStatus;
    this.retryable = fields.retryable ?? false;
    this.retryAfter = fields.retryAfter;
    this.requestId = fields.requestId;
    this.serverCode = fields.serverCode;
    this.errors = fields.errors ?? [];
  }
}

function truncate(message: string): string {
  return message.length > MAX_MESSAGE_LENGTH ? `${message.slice(0, MAX_MESSAGE_LENGTH - 1)}…` : message;
}

const SERVER_CODES: Record<string, ErrorCode> = {
  UNAUTHENTICATED: "auth_required",
  FORBIDDEN: "forbidden",
  NOT_FOUND: "not_found",
  BAD_USER_INPUT: "validation",
  GRAPHQL_VALIDATION_FAILED: "validation",
  GRAPHQL_PARSE_FAILED: "validation",
};

/** The code for an HTTP status that isn't 2xx. */
export function codeForStatus(status: number): ErrorCode {
  if (status === 401) return "auth_required";
  if (status === 403) return "forbidden";
  if (status === 404) return "not_found";
  if (status === 400) return "validation";
  if (status === 429) return "rate_limit";
  return "api_error";
}

/** The code for a server code in a 2xx answer. */
export function codeForServerCode(serverCode: string | undefined): ErrorCode {
  return (serverCode && SERVER_CODES[serverCode]) || "api_error";
}

export function hintFor(code: ErrorCode, retryAfter?: number): string | undefined {
  switch (code) {
    case "auth_required":
      return "Check the token. It may be mistyped, revoked, or for a different plant.";
    case "forbidden":
      return "The token may be missing a scope. A plant admin can make one with it under Settings → Developers.";
    case "rate_limit":
      return retryAfter === undefined
        ? "Wait a minute, then try again."
        : `Wait ${retryAfter} seconds, then try again.`;
    case "network":
      return "Check the host, and that this machine can reach it.";
    default:
      return undefined;
  }
}
