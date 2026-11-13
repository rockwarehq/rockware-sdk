"""The README's examples, so a change that breaks them fails mypy. Not run."""

from __future__ import annotations

from rockware import AsyncRockware, Rockware, RockwareError, parse_webhook


def examples(rockware: Rockware, secret: str, body: bytes, header: str | None, since: str | None) -> None:
    site = rockware.get_site()
    print(site["name"] if site else "no site")
    page = rockware.list_orders(first=50)
    print(len(page["nodes"]))
    for product in rockware.list_all_products():
        print(product["sku"], product["name"])
    for order in rockware.list_all_orders(updated_since=since):
        since = order["updatedAt"]
    result = rockware.upsert_order(
        order={
            "externalId": "SO-1001",
            "orderNumber": "1001",
            "customer": {"externalId": "C-42", "name": "Globex"},
            "lines": [{"product": "P-100", "targetQuantity": 500}],
        }
    )
    for error in result["errors"]:
        print(error["field"], error["message"])
    if result["order"]:
        print(result["action"], result["order"]["id"])
    try:
        rockware.list_products()
    except RockwareError as error:
        print(error.code, error.message, error.hint, error.request_id)
    event = parse_webhook(secret, body, header)
    print(event["data"]["id"])


async def async_examples(token: str) -> None:
    async with AsyncRockware(host="https://acme-api.rockware.io", token=token) as rockware:
        site = await rockware.get_site()
        print(site)
        async for product in rockware.list_all_products():
            print(product["sku"])
