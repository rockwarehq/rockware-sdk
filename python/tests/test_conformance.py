"""Runs the repo's shared tests (conformance/) against both clients. A fake
httpx transport plays the server. See conformance/README.md for the format."""

from __future__ import annotations

import asyncio
import email.utils
import json
import math
import re
import time
from datetime import datetime
from pathlib import Path
from typing import Any

import httpx
import pytest

from rockware import AsyncRockware, Rockware, RockwareError, verify_webhook

CONFORMANCE = Path(__file__).resolve().parents[2] / "conformance"


def snake(name: str) -> str:
    return re.sub(r"(?<=[a-z0-9])([A-Z])", r"_\1", name).lower()


def resolve(value: str) -> str:
    """{{httpdate+Ns}}: an HTTP date N + 1 seconds after now, on whole seconds."""
    return re.sub(
        r"\{\{httpdate\+(\d{1,9})s\}\}",
        lambda m: email.utils.formatdate(math.floor(time.time()) + int(m.group(1)) + 1, usegmt=True),
        value,
    )


class FakeServer:
    def __init__(self, answers: list[dict[str, Any]]) -> None:
        self.answers = answers
        self.sent: list[dict[str, Any]] = []

    def handle(self, request: httpx.Request) -> httpx.Response:
        self.sent.append(
            {
                "at": time.monotonic(),
                "method": request.method,
                "url": str(request.url),
                "headers": request.headers,
                "body": json.loads(request.content),
            }
        )
        if len(self.sent) > len(self.answers):
            raise AssertionError(f"The test has no answer for request {len(self.sent)}")
        answer = self.answers[len(self.sent) - 1]
        if answer.get("networkError"):
            raise httpx.ConnectError("connection dropped", request=request)
        headers = {name: resolve(value) for name, value in answer.get("headers", {}).items()}
        if "rawBody" in answer:
            content = answer["rawBody"].encode()
        elif "body" in answer:
            content = json.dumps(answer["body"]).encode()
        else:
            content = b""
        return httpx.Response(answer.get("status", 200), headers=headers, content=content)


def at(value: Any, path: str) -> Any:
    if path == "":
        return value
    current = value
    for key in path.split("."):
        if current is None:
            return None
        if key == "length" and isinstance(current, list):
            current = len(current)
        elif isinstance(current, list):
            current = current[int(key)] if int(key) < len(current) else None
        elif isinstance(current, dict):
            current = current.get(key, _MISSING)
            if current is _MISSING:
                return _MISSING
        else:
            return None
    return current


_MISSING = object()


def instant(value: Any) -> datetime:
    return datetime.fromisoformat(str(value).replace("Z", "+00:00"))


def client_settings(test: dict[str, Any]) -> dict[str, Any]:
    client = test.get("client", {})
    settings: dict[str, Any] = {
        "host": client.get("host", "https://acme-api.example.com"),
        "token": client.get("token", "rw_app_test"),
        "user_agent": client.get("userAgent"),
    }
    if "retry" in client:
        settings["retry"] = client["retry"]
    return settings


def run_sync(test: dict[str, Any], server: FakeServer) -> tuple[Any, BaseException | None]:
    kwargs = {snake(k): v for k, v in test.get("variables", {}).items()}
    collected: list[Any] = []
    try:
        client = Rockware(**client_settings(test), transport=httpx.MockTransport(server.handle))
        if test.get("paginate"):
            all_method = getattr(client, "list_all_" + snake(test["operation"].removeprefix("List")))
            for record in all_method(**kwargs, **({"max_pages": test["maxPages"]} if "maxPages" in test else {})):
                collected.append(record)
            return collected, None
        return getattr(client, snake(test["operation"]))(**kwargs), None
    except Exception as error:  # noqa: BLE001
        return (collected if test.get("paginate") else None), error


def run_async(test: dict[str, Any], server: FakeServer) -> tuple[Any, BaseException | None]:
    async def go() -> tuple[Any, BaseException | None]:
        kwargs = {snake(k): v for k, v in test.get("variables", {}).items()}
        collected: list[Any] = []
        try:
            client = AsyncRockware(**client_settings(test), transport=httpx.MockTransport(server.handle))
            if test.get("paginate"):
                all_method = getattr(client, "list_all_" + snake(test["operation"].removeprefix("List")))
                extra = {"max_pages": test["maxPages"]} if "maxPages" in test else {}
                async for record in all_method(**kwargs, **extra):
                    collected.append(record)
                return collected, None
            return await getattr(client, snake(test["operation"]))(**kwargs), None
        except Exception as error:  # noqa: BLE001
            return (collected if test.get("paginate") else None), error

    return asyncio.run(go())


CASES = [
    pytest.param(test, id=f"{path.stem}: {test['name']}")
    for path in sorted((CONFORMANCE / "tests").glob("*.json"))
    for test in json.loads(path.read_text())
]


@pytest.mark.parametrize("mode", ["sync", "async"])
@pytest.mark.parametrize("test", CASES)
def test_conformance(test: dict[str, Any], mode: str) -> None:
    server = FakeServer(test["responses"])
    result, error = (run_sync if mode == "sync" else run_async)(test, server)
    sent = server.sent
    for assertion in test["assertions"]:
        kind = assertion["type"]
        index = assertion.get("index", 0)
        if kind == "requestCount":
            assert len(sent) == assertion["expected"], f"requests: {len(sent)}"
        elif kind == "requestMethod":
            assert sent[0]["method"] == assertion["expected"]
        elif kind == "requestUrl":
            assert sent[0]["url"] == assertion["expected"]
        elif kind == "requestHeader":
            value = sent[index]["headers"].get(assertion["name"])
            if "expected" in assertion:
                assert value == assertion["expected"]
            if "pattern" in assertion:
                assert value is not None and re.search(assertion["pattern"], value), value
        elif kind == "requestBody":
            value = at(sent[index]["body"], assertion["path"])
            if assertion.get("absent"):
                assert value is _MISSING, f"{assertion['path']} is {value!r}"
            if "expected" in assertion:
                assert value == assertion["expected"], assertion["path"]
            if "pattern" in assertion:
                assert re.search(assertion["pattern"], str(value))
            if "expectedInstant" in assertion:
                assert instant(value) == instant(assertion["expectedInstant"]), assertion["path"]
        elif kind == "delayBetweenRequests":
            gap = (sent[index + 1]["at"] - sent[index]["at"]) * 1000
            assert gap >= assertion["minMs"], f"gap {gap:.0f}ms"
            if "maxMs" in assertion:
                assert gap <= assertion["maxMs"], f"gap {gap:.0f}ms"
        elif kind == "noError":
            assert error is None, repr(error)
        elif kind == "error":
            assert isinstance(error, RockwareError), repr(error)
            fields = {
                "code": "code",
                "httpStatus": "http_status",
                "retryable": "retryable",
                "retryAfter": "retry_after",
                "requestId": "request_id",
                "serverCode": "server_code",
            }
            for name, attribute in fields.items():
                if name in assertion:
                    assert getattr(error, attribute) == assertion[name], name
        elif kind == "errorMessage":
            message = str(error)
            if "pattern" in assertion:
                assert re.search(assertion["pattern"], message), message
            if "excludes" in assertion:
                assert assertion["excludes"] not in message
        elif kind == "errorMessageLength":
            assert len(str(error)) <= assertion["max"]
        elif kind == "errorCount":
            assert isinstance(error, RockwareError) and len(error.errors) == assertion["expected"]
        elif kind == "result":
            assert at(result, assertion["path"]) == assertion["expected"], assertion["path"] or "result"
        else:
            raise AssertionError(f"Unknown assertion type {kind}")


WEBHOOK_CASES = json.loads((CONFORMANCE / "webhooks.json").read_text())["cases"]


@pytest.mark.parametrize("case", WEBHOOK_CASES, ids=[c["name"] for c in WEBHOOK_CASES])
def test_webhook_signatures(case: dict[str, Any]) -> None:
    valid = verify_webhook(
        case["secret"], case["body"], case["header"], now=case["now"], tolerance=case.get("tolerance", 300)
    )
    assert valid is case["valid"]
