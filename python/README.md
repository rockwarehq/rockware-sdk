# Rockware SDK for Python

Read and send a plant's records from your own code: orders, production runs, the catalog, the layout, custom entities and webhooks. Python 3.10 or later. There's a normal client and an asyncio one.

```sh
pip install rockware
```

## Start

You need the plant's API host and an API token. A plant admin makes the token in IMM under **Settings → Developers**, with the scopes you need: `data:read` to read, `data:write` to send, `webhooks:write` to manage webhooks.

```python
import os
from rockware import Rockware

rockware = Rockware(
    host="https://acme-api.rockware.io",
    token=os.environ["ROCKWARE_TOKEN"],
    user_agent="acme-erp-sync/1.0",
)

site = rockware.get_site()
print(site["name"] if site else "no site")
```

Each method returns what you asked for, as plain dicts: `get_product` gives the product, or `None` if there isn't one. Field names are the API's own, like `updatedAt` and `externalId`. Arguments are Python-style: `updated_since`, `include_deleted`.

With asyncio, use `AsyncRockware`. It has the same methods, which you `await`:

```python
from rockware import AsyncRockware

async with AsyncRockware(host="https://acme-api.rockware.io", token=token) as rockware:
    site = await rockware.get_site()
```

## Read

```python
# One page.
page = rockware.list_orders(first=50)

# Every record, page by page.
for product in rockware.list_all_products():
    print(product["sku"], product["name"])
```

With `AsyncRockware`, that's `async for product in rockware.list_all_products():`.

**Stay in step with your system.** Pass the time of your last sync. Records come oldest change first, so you can save the newest `updatedAt` as you go:

```python
since = load_last_sync()
for order in rockware.list_all_orders(updated_since=since):
    save_order(order)
    since = order["updatedAt"]
save_last_sync(since)
```

A `datetime` works too, if it has a time zone.

## Send

Records are found by **your** id (`externalId`) and the name of your system (`source`, `"erp"` if you leave it out). Sending the same thing twice gives the same result.

```python
result = rockware.upsert_order(
    order={
        "externalId": "SO-1001",
        "orderNumber": "1001",
        "customer": {"externalId": "C-42", "name": "Globex"},
        "lines": [{"product": "P-100", "targetQuantity": 500}],
    }
)

if result["errors"]:
    # All or nothing: nothing was saved.
    for error in result["errors"]:
        print(error["field"], error["message"])
else:
    print(result["action"], result["order"]["id"])  # CREATED, UPDATED or UNCHANGED
```

**A refused write isn't an exception.** Check `errors` on every write.

## Errors

Anything else that goes wrong raises a `RockwareError`:

```python
from rockware import RockwareError

try:
    rockware.list_products()
except RockwareError as error:
    print(error.code, error.message, error.hint, error.request_id)
```

| `code` | Meaning |
| --- | --- |
| `auth_required` | The token is wrong, revoked or for another plant |
| `forbidden` | The token is missing a scope |
| `not_found` | The thing you named isn't there |
| `validation` | The request isn't right: a bad argument, or too big a query |
| `rate_limit` | Too many requests. `retry_after` says how long to wait. |
| `network` | No answer from the host |
| `api_error` | The server failed. `server_code` has its own code. |
| `usage` | A bad setting, found before sending |

## Retry

The client tries up to 3 times. It retries when:

- the server says to slow down (429), waiting as long as it asks, up to 60 seconds
- the server fails (5xx) or the connection drops, for reads and for writes that are safe to send twice

Turn it off with `retry=False`.

## Webhooks

Check every delivery before you trust it. Pass the **raw** body, before any JSON parsing:

```python
from flask import Flask, request
from rockware import parse_webhook

app = Flask(__name__)


@app.post("/rockware")
def rockware_webhook():
    event = parse_webhook(SECRET, request.get_data(), request.headers.get("Rockware-Signature"))
    queue.put(event)  # Answer within 10 seconds, then do the work.
    return "", 200
```

`parse_webhook` raises `RockwareError` with `code == "forbidden"` if the signature is wrong or more than 5 minutes old. `verify_webhook` gives `True` or `False` instead. The same event can arrive twice, so skip an `id` you've already handled.

## Settings

| Setting | Default | |
| --- | --- | --- |
| `host` | required | `https://` only, except `localhost` |
| `token` | required | A string, or a function that returns one (`AsyncRockware`: it may be async) |
| `user_agent` | none | Your app's name and version |
| `timeout` | `30.0` | Seconds for each attempt |
| `retry` | `True` | |
| `hooks` | none | A `Hooks` subclass with `on_request`, `on_response`, `on_retry`, for logs and metrics |
| `transport` | httpx's | An httpx transport, for proxies or tests |

`list_all_…` also takes `max_pages` (default 10,000). Close a client with `close()` (`aclose()` for async), or use it in a `with` block.

## More

- [How every SDK behaves](https://github.com/rockwarehq/rockware-sdk/blob/main/SPEC.md)
- [Upgrading](https://github.com/rockwarehq/rockware-sdk/blob/main/MIGRATING.md)

MIT licensed.
