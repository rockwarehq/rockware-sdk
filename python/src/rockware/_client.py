"""The clients: send each operation to <host>/graphql, retry when it's safe, and
turn every failure into a RockwareError. SPEC.md sections 3 to 6, 8 and 9.

Rockware and AsyncRockware share everything here except how they wait and send.
"""

from __future__ import annotations

import asyncio
import inspect
import json
import random
import time
from collections.abc import AsyncIterator, Awaitable, Callable, Iterator
from dataclasses import dataclass
from datetime import datetime, timezone
from decimal import Decimal
from email.utils import parsedate_to_datetime
from typing import Any
from urllib.parse import urlsplit

import httpx

from ._errors import RockwareError, code_for_server_code, code_for_status, hint_for
from ._generated.behavior import RETRY
from ._generated.operations import OPERATIONS, AsyncOperations, SyncOperations
from ._generated.version import VERSION
from ._operation import Operation

DEFAULT_TIMEOUT = 30.0
SDK_AGENT = f"rockware-sdk-python/{VERSION}"
_LOCAL_HOSTS = {"localhost", "127.0.0.1", "::1"}


@dataclass(frozen=True)
class RequestInfo:
    operation: str
    attempt: int
    """1 for the first try."""
    url: str


@dataclass(frozen=True)
class ResponseInfo:
    http_status: int | None
    duration_ms: float
    error: RockwareError | None


class Hooks:
    """Ways to watch a client work. Override the ones you want. An error raised
    in a hook is ignored."""

    def on_request(self, info: RequestInfo) -> None: ...

    def on_response(self, info: RequestInfo, result: ResponseInfo) -> None: ...

    def on_retry(self, info: RequestInfo, error: RockwareError, delay_ms: float) -> None: ...


class _Base:
    def __init__(
        self,
        host: str,
        token: Any,
        timeout: float,
        retry: bool,
        user_agent: str | None,
        hooks: Hooks | None,
    ) -> None:
        self.host = _check_host(host)
        if isinstance(token, str):
            if not token.strip():
                raise RockwareError("usage", "A token is required")
        elif not callable(token):
            raise RockwareError("usage", "A token is required")
        if not timeout > 0:
            raise RockwareError("usage", "timeout must be more than 0")
        self._token = token
        self._timeout = timeout
        self._retry = retry
        self._user_agent = f"{user_agent.strip()} {SDK_AGENT}" if user_agent and user_agent.strip() else SDK_AGENT
        self._hooks = hooks or Hooks()

    @property
    def _url(self) -> str:
        return f"{self.host}/graphql"

    def _attempts(self) -> int:
        return RETRY["attempts"] if self._retry else 1

    def _request(self, operation: Operation, variables: dict[str, Any], token: str) -> tuple[dict[str, str], bytes]:
        if not isinstance(token, str) or not token.strip():
            raise RockwareError("usage", "A token is required")
        sent = {key: value for key, value in variables.items() if value is not None}
        body = json.dumps(
            {"query": operation.document, "variables": sent, "operationName": operation.name},
            default=_json_default,
        ).encode()
        headers = {
            "authorization": f"Bearer {token}",
            "content-type": "application/json",
            "accept": "application/json",
            "user-agent": self._user_agent,
        }
        return headers, body

    def _network_error(self, error: Exception) -> RockwareError:
        if isinstance(error, httpx.TimeoutException):
            message = f"{self.host} didn't answer within {self._timeout:g} seconds"
        else:
            message = f"Can't reach {self.host}: {error}"
        return RockwareError("network", message, retryable=True, hint=hint_for("network"))

    def _hook(self, name: str, *args: Any) -> None:
        try:
            getattr(self._hooks, name, lambda *_: None)(*args)
        except Exception:  # noqa: BLE001 — a hook's own failure never changes the call.
            pass


class Rockware(SyncOperations, _Base):
    """Rockware's developer API.

    ::

        rockware = Rockware(host="https://acme-api.rockware.io", token=os.environ["ROCKWARE_TOKEN"])
        for product in rockware.list_all_products(updated_since=since):
            print(product["sku"])
    """

    def __init__(
        self,
        *,
        host: str,
        token: str | Callable[[], str],
        timeout: float = DEFAULT_TIMEOUT,
        retry: bool = True,
        user_agent: str | None = None,
        hooks: Hooks | None = None,
        transport: httpx.BaseTransport | None = None,
    ) -> None:
        super().__init__(host, token, timeout, retry, user_agent, hooks)
        self._http = httpx.Client(timeout=timeout, follow_redirects=False, transport=transport)

    def close(self) -> None:
        self._http.close()

    def __enter__(self) -> Rockware:
        return self

    def __exit__(self, *_: object) -> None:
        self.close()

    def call(self, name: str, variables: dict[str, Any] | None = None) -> Any:
        """Send any operation from operations/ by name. The methods are easier; this is for tools."""
        return self._run(_operation(name), variables or {})

    def _run(self, operation: Operation, variables: dict[str, Any]) -> Any:
        token = self._token if isinstance(self._token, str) else self._token()
        headers, body = self._request(operation, variables, token)
        attempt = 1
        while True:
            info = RequestInfo(operation.name, attempt, self._url)
            self._hook("on_request", info)
            started = time.monotonic()
            status: int | None = None
            try:
                response = self._http.post(self._url, headers=headers, content=body)
                status = response.status_code
                data, error = _read_answer(response)
            except httpx.TransportError as caught:
                data, error = None, self._network_error(caught)
            if error:
                error = _redact(error, token)
            self._hook("on_response", info, ResponseInfo(status, (time.monotonic() - started) * 1000, error))
            if not error:
                return data[operation.root]  # type: ignore[index]
            delay = _retry_delay(error, operation, attempt) if attempt < self._attempts() else None
            if delay is None:
                raise error
            self._hook("on_retry", info, error, delay * 1000)
            time.sleep(delay)
            attempt += 1

    def _run_pages(self, operation: Operation, variables: dict[str, Any], max_pages: int) -> Iterator[Any]:
        if max_pages < 1:
            raise RockwareError("usage", "max_pages must be more than 0")
        return self._pages(operation, variables, max_pages)

    def _pages(self, operation: Operation, variables: dict[str, Any], max_pages: int) -> Iterator[Any]:
        after: str | None = None
        for page in range(1, max_pages + 1):
            connection = self._run(operation, {**variables, "after": after})
            yield from connection["nodes"]
            after = connection["pageInfo"]["endCursor"]
            if not connection["pageInfo"]["hasNextPage"] or not after or page >= max_pages:
                return


class AsyncRockware(AsyncOperations, _Base):
    """Rockware's developer API, for asyncio.

    ::

        async with AsyncRockware(host="https://acme-api.rockware.io", token=token) as rockware:
            async for product in rockware.list_all_products():
                print(product["sku"])
    """

    def __init__(
        self,
        *,
        host: str,
        token: str | Callable[[], str] | Callable[[], Awaitable[str]],
        timeout: float = DEFAULT_TIMEOUT,
        retry: bool = True,
        user_agent: str | None = None,
        hooks: Hooks | None = None,
        transport: httpx.AsyncBaseTransport | None = None,
    ) -> None:
        super().__init__(host, token, timeout, retry, user_agent, hooks)
        self._http = httpx.AsyncClient(timeout=timeout, follow_redirects=False, transport=transport)

    async def aclose(self) -> None:
        await self._http.aclose()

    async def __aenter__(self) -> AsyncRockware:
        return self

    async def __aexit__(self, *_: object) -> None:
        await self.aclose()

    async def call(self, name: str, variables: dict[str, Any] | None = None) -> Any:
        """Send any operation from operations/ by name. The methods are easier; this is for tools."""
        return await self._run(_operation(name), variables or {})

    async def _run(self, operation: Operation, variables: dict[str, Any]) -> Any:
        token = self._token
        if not isinstance(token, str):
            token = token()
            if inspect.isawaitable(token):
                token = await token
        headers, body = self._request(operation, variables, token)
        attempt = 1
        while True:
            info = RequestInfo(operation.name, attempt, self._url)
            self._hook("on_request", info)
            started = time.monotonic()
            status: int | None = None
            try:
                response = await self._http.post(self._url, headers=headers, content=body)
                status = response.status_code
                data, error = _read_answer(response)
            except httpx.TransportError as caught:
                data, error = None, self._network_error(caught)
            if error:
                error = _redact(error, token)
            self._hook("on_response", info, ResponseInfo(status, (time.monotonic() - started) * 1000, error))
            if not error:
                return data[operation.root]  # type: ignore[index]
            delay = _retry_delay(error, operation, attempt) if attempt < self._attempts() else None
            if delay is None:
                raise error
            self._hook("on_retry", info, error, delay * 1000)
            await asyncio.sleep(delay)
            attempt += 1

    def _run_pages(self, operation: Operation, variables: dict[str, Any], max_pages: int) -> AsyncIterator[Any]:
        if max_pages < 1:
            raise RockwareError("usage", "max_pages must be more than 0")
        return self._pages(operation, variables, max_pages)

    async def _pages(self, operation: Operation, variables: dict[str, Any], max_pages: int) -> AsyncIterator[Any]:
        after: str | None = None
        for page in range(1, max_pages + 1):
            connection = await self._run(operation, {**variables, "after": after})
            for node in connection["nodes"]:
                yield node
            after = connection["pageInfo"]["endCursor"]
            if not connection["pageInfo"]["hasNextPage"] or not after or page >= max_pages:
                return


def _operation(name: str) -> Operation:
    if name not in OPERATIONS:
        raise RockwareError("usage", f"No operation named {name}")
    return OPERATIONS[name]


def _check_host(host: str) -> str:
    try:
        url = urlsplit(host)
    except ValueError:
        raise RockwareError("usage", f"host isn't a URL: {host}") from None
    if not url.scheme or not url.hostname:
        raise RockwareError("usage", f"host isn't a URL: {host}")
    if url.scheme != "https" and not (url.scheme == "http" and url.hostname in _LOCAL_HOSTS):
        raise RockwareError("usage", "host must use https://, except localhost")
    return host.rstrip("/")


def _json_default(value: Any) -> Any:
    if isinstance(value, datetime):
        if value.tzinfo is None:
            raise RockwareError("usage", "A datetime needs a time zone, like datetime.now(timezone.utc)")
        return value.astimezone(timezone.utc).isoformat().replace("+00:00", "Z")
    if isinstance(value, Decimal):
        return str(value)
    raise TypeError(f"Can't send a {type(value).__name__}")


def _read_answer(response: httpx.Response) -> tuple[dict[str, Any] | None, RockwareError | None]:
    """Turn an HTTP answer into the data, or the error it means."""
    status = response.status_code
    request_id = response.headers.get("x-request-id")
    retry_after = _parse_retry_after(response.headers.get("retry-after"))
    try:
        body = response.json() if response.content else None
    except ValueError:
        body = None
    errors = body.get("errors") if isinstance(body, dict) else None
    errors = errors if isinstance(errors, list) else []
    first = errors[0] if errors and isinstance(errors[0], dict) else {}
    extensions = first.get("extensions")
    server_code = extensions.get("code") if isinstance(extensions, dict) else None
    message = "; ".join(str(e.get("message", "")) for e in errors if isinstance(e, dict))
    fields: dict[str, Any] = {
        "http_status": status,
        "request_id": request_id,
        "retry_after": retry_after,
        "server_code": server_code,
        "errors": errors,
    }

    if not 200 <= status < 300:
        code = code_for_status(status)
        return None, RockwareError(
            code,
            message or f"The server answered HTTP {status}",
            retryable=code == "rate_limit" or status >= 500,
            hint=hint_for(code, retry_after),
            **fields,
        )
    if not isinstance(body, dict):
        return None, RockwareError("api_error", f"The server's answer isn't JSON (HTTP {status})", **fields)
    if errors:
        code = code_for_server_code(server_code)
        return None, RockwareError(code, message, hint=hint_for(code), **fields)
    data = body.get("data")
    if not isinstance(data, dict):
        return None, RockwareError("api_error", "The server's answer has no data", **fields)
    return data, None


def _parse_retry_after(value: str | None) -> int | None:
    """Seconds from a Retry-After header: whole seconds, or an HTTP date still ahead."""
    if not value:
        return None
    value = value.strip()
    if value.isdigit():
        return int(value)
    try:
        date = parsedate_to_datetime(value)
    except (TypeError, ValueError):
        return None
    seconds = -int(-(date.timestamp() - time.time()) // 1)  # round up
    return seconds if seconds > 0 else None


def _retry_delay(error: RockwareError, operation: Operation, attempt: int) -> float | None:
    """Seconds to wait before trying again, or None to stop. SPEC.md section 5."""
    refused_before_running = error.code == "rate_limit"
    might_have_run = error.code == "network" or (error.http_status is not None and error.http_status >= 500)
    if not refused_before_running and not (might_have_run and operation.safe_to_repeat):
        return None
    if error.retry_after is not None:
        return None if error.retry_after > RETRY["maxRetryAfterSeconds"] else float(error.retry_after)
    return (RETRY["baseDelayMs"] * 2.0 ** (attempt - 1) + random.random() * RETRY["maxJitterMs"]) / 1000


def _redact(error: RockwareError, token: str) -> RockwareError:
    """The token never leaves in an error."""
    if token not in error.message:
        return error
    hidden = error.message.replace(token, "[hidden]")
    errors = [{**e, "message": str(e.get("message", "")).replace(token, "[hidden]")} for e in error.errors]
    return RockwareError(
        error.code,
        hidden,
        hint=error.hint,
        http_status=error.http_status,
        retryable=error.retryable,
        retry_after=error.retry_after,
        request_id=error.request_id,
        server_code=error.server_code,
        errors=errors,
    )
