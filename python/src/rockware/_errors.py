"""Every way a call can fail, as one error type. SPEC.md section 4."""

from __future__ import annotations

from typing import Any, Literal

ErrorCode = Literal[
    "usage",
    "auth_required",
    "forbidden",
    "not_found",
    "validation",
    "rate_limit",
    "api_error",
    "network",
]

MAX_MESSAGE_LENGTH = 500

_SERVER_CODES: dict[str, ErrorCode] = {
    "UNAUTHENTICATED": "auth_required",
    "FORBIDDEN": "forbidden",
    "NOT_FOUND": "not_found",
    "BAD_USER_INPUT": "validation",
    "GRAPHQL_VALIDATION_FAILED": "validation",
    "GRAPHQL_PARSE_FAILED": "validation",
}


class RockwareError(Exception):
    """A call to Rockware failed. ``code`` says how."""

    def __init__(
        self,
        code: ErrorCode,
        message: str,
        *,
        hint: str | None = None,
        http_status: int | None = None,
        retryable: bool = False,
        retry_after: int | None = None,
        request_id: str | None = None,
        server_code: str | None = None,
        errors: list[dict[str, Any]] | None = None,
    ) -> None:
        if len(message) > MAX_MESSAGE_LENGTH:
            message = message[: MAX_MESSAGE_LENGTH - 1] + "…"
        super().__init__(message)
        self.code: ErrorCode = code
        self.message = message
        self.hint = hint
        """What to do about it, when the SDK knows."""
        self.http_status = http_status
        self.retryable = retryable
        """Whether trying again later might work."""
        self.retry_after = retry_after
        """Seconds the server asked to wait."""
        self.request_id = request_id
        """The server's id for the request. Give it to Rockware support."""
        self.server_code = server_code
        """The server's own code (extensions.code), as sent."""
        self.errors = errors or []
        """Every GraphQL error the server sent, as sent."""

    def __repr__(self) -> str:
        return f"RockwareError(code={self.code!r}, message={self.message!r}, http_status={self.http_status!r})"


def code_for_status(status: int) -> ErrorCode:
    """The code for an HTTP status that isn't 2xx."""
    codes: dict[int, ErrorCode] = {
        400: "validation",
        401: "auth_required",
        403: "forbidden",
        404: "not_found",
        429: "rate_limit",
    }
    return codes.get(status, "api_error")


def code_for_server_code(server_code: str | None) -> ErrorCode:
    """The code for a server code in a 2xx answer."""
    return _SERVER_CODES.get(server_code or "", "api_error")


def hint_for(code: ErrorCode, retry_after: int | None = None) -> str | None:
    if code == "auth_required":
        return "Check the token. It may be mistyped, revoked, or for a different plant."
    if code == "forbidden":
        return "The token may be missing a scope. A plant admin can make one with it under Settings → Developers."
    if code == "rate_limit":
        return (
            "Wait a minute, then try again." if retry_after is None else f"Wait {retry_after} seconds, then try again."
        )
    if code == "network":
        return "Check the host, and that this machine can reach it."
    return None
