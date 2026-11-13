"""What the shared tests don't cover: hooks, token functions, datetimes, calls
by name, and parse_webhook."""

from __future__ import annotations

import asyncio
import json
from datetime import datetime, timezone

import httpx
import pytest

from rockware import AsyncRockware, Hooks, Rockware, RockwareError, parse_webhook

SITE = {"data": {"site": {"id": "site_1"}}}
HOST = "https://acme-api.example.com"


def answering(*answers: httpx.Response) -> tuple[httpx.MockTransport, list[httpx.Request]]:
    sent: list[httpx.Request] = []

    def handle(request: httpx.Request) -> httpx.Response:
        sent.append(request)
        return answers[len(sent) - 1]

    return httpx.MockTransport(handle), sent


def test_a_token_function_is_asked_on_each_call() -> None:
    transport, sent = answering(httpx.Response(200, json=SITE), httpx.Response(200, json=SITE))
    tokens = iter(["rw_app_1", "rw_app_2"])
    client = Rockware(host=HOST, token=lambda: next(tokens), transport=transport)
    client.get_site()
    client.get_site()
    assert [r.headers["authorization"] for r in sent] == ["Bearer rw_app_1", "Bearer rw_app_2"]


def test_the_async_client_takes_an_async_token_function() -> None:
    transport, sent = answering(httpx.Response(200, json=SITE))

    async def token() -> str:
        return "rw_app_async"

    async def go() -> None:
        async with AsyncRockware(host=HOST, token=token, transport=transport) as client:
            assert await client.get_site() == {"id": "site_1"}

    asyncio.run(go())
    assert sent[0].headers["authorization"] == "Bearer rw_app_async"


def test_hooks_are_called_and_a_broken_one_changes_nothing() -> None:
    seen: list[str] = []

    class Watch(Hooks):
        def on_request(self, info):  # type: ignore[no-untyped-def]
            seen.append(f"request {info.operation} {info.attempt}")
            raise RuntimeError("a broken hook")

        def on_response(self, info, result):  # type: ignore[no-untyped-def]
            seen.append(f"response {info.attempt} {result.http_status} {result.error.code if result.error else 'ok'}")

        def on_retry(self, info, error, delay_ms):  # type: ignore[no-untyped-def]
            seen.append(f"retry {info.attempt} {error.code} {delay_ms >= 1000}")

    transport, _ = answering(httpx.Response(503), httpx.Response(200, json=SITE))
    client = Rockware(host=HOST, token="rw_app_test", hooks=Watch(), transport=transport)
    assert client.get_site() == {"id": "site_1"}
    assert seen == [
        "request GetSite 1",
        "response 1 503 api_error",
        "retry 1 api_error True",
        "request GetSite 2",
        "response 2 200 ok",
    ]


def test_a_datetime_is_sent_as_utc() -> None:
    nodes = {"data": {"orders": {"nodes": [], "pageInfo": {"hasNextPage": False, "endCursor": None}}}}
    transport, sent = answering(httpx.Response(200, json=nodes))
    client = Rockware(host=HOST, token="rw_app_test", transport=transport)
    client.list_orders(updated_since=datetime(2026, 11, 1, 12, 0, tzinfo=timezone.utc))
    assert json.loads(sent[0].content)["variables"]["updatedSince"] == "2026-11-01T12:00:00Z"


def test_a_datetime_without_a_time_zone_is_refused() -> None:
    transport, sent = answering()
    client = Rockware(host=HOST, token="rw_app_test", transport=transport)
    with pytest.raises(RockwareError) as caught:
        client.list_orders(updated_since=datetime(2026, 11, 1))
    assert caught.value.code == "usage"
    assert sent == []


def test_any_operation_can_be_sent_by_name() -> None:
    transport, _ = answering(httpx.Response(200, json=SITE))
    client = Rockware(host=HOST, token="rw_app_test", transport=transport)
    assert client.call("GetSite") == {"id": "site_1"}
    with pytest.raises(RockwareError, match="No operation named Nope"):
        client.call("Nope")


BODY = (
    '{"id":"evt_1","type":"order.updated","occurredAt":"2026-11-09T15:00:00.000Z",'
    '"siteId":"site_1","data":{"object":"order","id":"ord_1"}}'
)
HEADER = "t=1700000000,v1=236c14c5656906da5cdf38cecc494968b3b4c55aeef1d83818a866f6e046d75e"


def test_parse_webhook_gives_back_the_event() -> None:
    event = parse_webhook("whsec_test", BODY.encode(), HEADER, now=1700000000)
    assert event["id"] == "evt_1"
    assert event["data"] == {"object": "order", "id": "ord_1"}


def test_parse_webhook_refuses_a_wrong_signature() -> None:
    with pytest.raises(RockwareError) as caught:
        parse_webhook("whsec_other", BODY, HEADER, now=1700000000)
    assert caught.value.code == "forbidden"
