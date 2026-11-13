# Rockware SDK for TypeScript

Read and send a plant's records from your own code: orders, production runs, the catalog, the layout, custom entities and webhooks. It works in Node 20.3+, Bun, Deno and edge workers.

```sh
npm install @rockwarehq/sdk
```

## Start

You need the plant's API host and an API token. A plant admin makes the token in IMM under **Settings → Developers**, with the scopes you need: `data:read` to read, `data:write` to send, `webhooks:write` to manage webhooks.

```ts
import { RockwareClient } from "@rockwarehq/sdk";

const rockware = new RockwareClient({
  host: "https://acme-api.rockware.io",
  token: process.env.ROCKWARE_TOKEN!,
  userAgent: "acme-erp-sync/1.0",
});

const site = await rockware.getSite();
console.log(site?.name);
```

Each method returns what you asked for: `getProduct` gives the product, or `null` if there isn't one.

## Read

```ts
// One page.
const page = await rockware.listOrders({ first: 50 });

// Every record, page by page.
for await (const product of rockware.listAllProducts()) {
  console.log(product.sku, product.name);
}
```

**Stay in step with your system.** Pass the time of your last sync. Records come oldest change first, so you can save the newest `updatedAt` as you go:

```ts
let since = await loadLastSync();
for await (const order of rockware.listAllOrders({ updatedSince: since })) {
  await saveOrder(order);
  since = order.updatedAt;
}
await saveLastSync(since);
```

## Send

Records are found by **your** id (`externalId`) and the name of your system (`source`, `"erp"` if you leave it out). Sending the same thing twice gives the same result.

```ts
const result = await rockware.upsertOrder({
  order: {
    externalId: "SO-1001",
    orderNumber: "1001",
    customer: { externalId: "C-42", name: "Globex" },
    lines: [{ product: "P-100", targetQuantity: 500 }],
  },
});

if (result.errors.length) {
  // All or nothing: nothing was saved.
  for (const error of result.errors) console.error(error.field, error.message);
} else {
  console.log(result.action, result.order?.id); // CREATED, UPDATED or UNCHANGED
}
```

**A refused write isn't an exception.** Check `errors` on every write.

## Errors

Anything else that goes wrong throws a `RockwareError`:

```ts
import { RockwareError } from "@rockwarehq/sdk";

try {
  await rockware.listProducts();
} catch (error) {
  if (error instanceof RockwareError) {
    console.error(error.code, error.message, error.hint, error.requestId);
  }
}
```

| `code` | Meaning |
| --- | --- |
| `auth_required` | The token is wrong, revoked or for another plant |
| `forbidden` | The token is missing a scope |
| `not_found` | The thing you named isn't there |
| `validation` | The request isn't right: a bad argument, or too big a query |
| `rate_limit` | Too many requests. `retryAfter` says how long to wait. |
| `network` | No answer from the host |
| `api_error` | The server failed. `serverCode` has its own code. |
| `usage` | A bad setting, found before sending |

## Retry

The client tries up to 3 times. It retries when:

- the server says to slow down (429), waiting as long as it asks, up to 60 seconds
- the server fails (5xx) or the connection drops, for reads and for writes that are safe to send twice

Turn it off with `retry: false`.

## Webhooks

Check every delivery before you trust it. Pass the **raw** body, before any JSON parsing:

```ts
import { parseWebhook } from "@rockwarehq/sdk";

app.post("/rockware", express.raw({ type: "application/json" }), async (req, res) => {
  const event = await parseWebhook(process.env.ROCKWARE_WEBHOOK_SECRET!, req.body, req.get("Rockware-Signature"));
  res.sendStatus(200); // Answer within 10 seconds, then do the work.

  if (await alreadyHandled(event.id)) return; // The same event can arrive twice.
  if (event.data.object === "order") await syncOrder(await rockware.getOrder({ id: event.data.id }));
});
```

`parseWebhook` throws with `code: "forbidden"` if the signature is wrong or more than 5 minutes old. `verifyWebhook` gives `true` or `false` instead.

## Settings

| Setting | Default | |
| --- | --- | --- |
| `host` | required | `https://` only, except `localhost` |
| `token` | required | A string, or a function that returns one (or a promise of one) |
| `userAgent` | none | Your app's name and version |
| `timeout` | `30000` | Milliseconds for each attempt |
| `retry` | `true` | |
| `hooks` | none | `onRequest`, `onResponse`, `onRetry`, for logs and metrics |
| `fetch` | global `fetch` | |

Every method also takes `{ signal }` to stop it, and `listAll…` takes `{ maxPages }`.

## More

- [How every SDK behaves](../SPEC.md)
- [Upgrading](../MIGRATING.md)

MIT licensed.
