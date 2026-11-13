# How every Rockware SDK works

This page is the rulebook. Every SDK in this repo, in every language, does what it says. When an SDK can't do something the way this page says, the README's feature table says so.

The shared tests in [`conformance/`](conformance/) check most of these rules. Each rule they check says **(tested)**.

## 1. What the SDKs are for

Rockware's developer API is GraphQL at `POST <host>/graphql`. The SDKs make it easy to call from TypeScript, Python, C# and Go. They:

- send the operations in [`operations/`](operations/), with types for what goes in and what comes back
- turn every kind of failure into one error type
- retry when it's safe
- page through long lists
- check webhook signatures

They add no rules of their own. What a write may do is decided by the server, and the SDK passes on its answer as it is.

## 2. Where things come from

| File | What it is |
| --- | --- |
| `schema/developer-api.graphql` | The API's schema, copied from the server. Never edit it by hand. |
| `operations/*.graphql` | Every operation the SDKs send. This list *is* the SDKs' surface. |
| `behavior.json` | Retry settings, and which writes are safe to send again. |
| `conformance/` | Tests every SDK runs: fake server answers, and what the SDK must do with them. |

Each SDK generates its types and its operation methods from the schema and `operations/`. Generated code is never edited by hand.

**Operation rules.** Each operation:

- has a name in `PascalCase` that starts with what it does: `Get`, `List`, `Upsert`, `Create`, `Update`, `Delete`, and so on
- asks for exactly one root field
- stays within the server's limits: 6 levels deep below the root field, and 300 fields in all (checked in CI)

**To add an operation:** add it to `operations/`, regenerate every SDK, and add it to `safeToRepeat` in `behavior.json` if it's a write that's safe to send twice.

## 3. The client

You make a client with:

| Setting | Default | Notes |
| --- | --- | --- |
| `host` | none, required | The plant's API host, like `https://acme-api.rockware.io`. Must be `https://`, except `localhost` and `127.0.0.1`. A trailing `/` is dropped. |
| `token` | none, required | An API token (`rw_app_…`) or a connected token (`rw_mcp_…`). Either a string or a function that returns one. |
| `timeout` | 30 seconds | For each attempt. |
| `retry` | on | Can be turned off. |
| `userAgent` | none | Your app's name, like `acme-erp-sync/2.1`. It's sent before the SDK's own name. |
| `hooks` | none | See section 8. |

A bad setting fails when the client is made, with error code `usage`.

A token belongs to one plant, so there's no plant or account to choose. Everything the client does happens at that plant.

**Every request (tested):**

- `POST <host>/graphql`
- `Authorization: Bearer <token>`
- `Content-Type: application/json`, `Accept: application/json`
- `User-Agent: <yours> rockware-sdk-<language>/<version>`, or just the SDK's part if you gave none
- a body of `{"query", "variables", "operationName"}`, where `query` is the operation and the fragments it uses

**Methods.** There's one method per operation, named for it in the language's style: `listProducts`, `list_products`, `ListProductsAsync`, `ListProducts`. It returns the operation's root field, not the whole `data` object. So `getProduct` returns the product, or nothing if there isn't one.

**Inputs.** A field of an input you don't set isn't sent, so the server leaves it as it is. Setting one to null sends null, which clears it. Go can't send null or an empty list for an input field yet: a nil one is left out. A top-level argument that's null or unset isn't sent at all.

## 4. Errors

Every failure is one error type: `RockwareError` (C#: `RockwareException`, Go: `*rockware.Error`). Field names follow each language's style: `httpStatus`, `http_status`, `HttpStatus`, `HTTPStatus`.

| Field | What it holds |
| --- | --- |
| `code` | One of the codes below |
| `message` | What went wrong, from the server when it said. Cut to 500 characters. |
| `hint` | What to do about it, when the SDK knows |
| `httpStatus` | The HTTP status, when there was an answer |
| `retryable` | Whether trying again later might work |
| `retryAfter` | Seconds the server asked to wait, from `Retry-After` |
| `requestId` | The server's `X-Request-Id`, when sent. Give it to Rockware support. |
| `serverCode` | The server's own code (`extensions.code` on the first error), as it was sent |
| `errors` | Every GraphQL error the server sent, as it was sent |

**Codes (tested):**

| `code` | When | `retryable` |
| --- | --- | --- |
| `usage` | A bad setting or argument, found before sending | no |
| `auth_required` | HTTP 401, or `serverCode` `UNAUTHENTICATED` | no |
| `forbidden` | HTTP 403, or `serverCode` `FORBIDDEN` | no |
| `not_found` | HTTP 404, or `serverCode` `NOT_FOUND` | no |
| `validation` | HTTP 400, or `serverCode` `BAD_USER_INPUT`, `GRAPHQL_VALIDATION_FAILED` or `GRAPHQL_PARSE_FAILED` | no |
| `rate_limit` | HTTP 429 | yes |
| `api_error` | HTTP 5xx, any other `serverCode`, or an answer the SDK can't read | yes for 5xx, else no |
| `network` | No answer: can't connect, the connection dropped, or the timeout passed | yes |

An answer with `errors` is an error, even with HTTP 200. A `data` that came back alongside the errors is dropped.

**Problems with a write are not errors.** An upsert answers with `errors: [{ code, field, message }]` when it refuses something. Writes are all or nothing, so if that list isn't empty, nothing was saved. The SDK returns the answer as it is, and it's up to you to check the list.

**Never in an error:** the token. Messages and logs show `Bearer [hidden]`.

## 5. Retry

Settings come from `behavior.json`: at most 3 attempts in all, waiting 1 second, then 2, with up to 100 ms of random extra each time.

**When to retry (tested):**

| What happened | Retry? |
| --- | --- |
| HTTP 429 | Always. The server refused before doing anything, so even a write is safe. |
| HTTP 5xx, or `network` | Only queries, and writes in `safeToRepeat` |
| Anything else | Never |

**How long to wait (tested):** `Retry-After` when the server sent it, in seconds or as a date. Otherwise 1 second times 2 for each attempt before, plus the random extra.

**Don't wait too long:** if `Retry-After` asks for more than 60 seconds, don't retry. Fail with `rate_limit`, and its `retryAfter`.

When the attempts run out, the error is the last attempt's.

## 6. Paging

A `List` operation that returns a connection (`nodes` and `pageInfo`) can be paged for you (tested):

- Ask for the first page with the arguments you gave.
- While `pageInfo.hasNextPage` is true, ask again with `after` set to `pageInfo.endCursor`.
- Give back each record as it comes, in the language's own way: an async iterator in TypeScript and Python, an `IAsyncEnumerable` in C#, an iterator function in Go.
- Stop after `maxPages` pages (default 10,000). It's there to stop a loop that never ends.

`first` is at most 100. Leave it out and the server picks.

**Keeping in step with your system.** Pass `updatedSince` with the time of your last sync, and page through. Records come back oldest change first, so you can save the newest `updatedAt` as you go.

## 7. Webhooks

Rockware signs every webhook delivery:

```
Rockware-Signature: t=<unix seconds>,v1=<hex HMAC-SHA256 of "<t>.<raw body>">
```

**`verifyWebhook(secret, rawBody, header, options)` (tested):**

1. Split the header on `,`, then each part on the first `=`. Spaces around parts don't count.
2. `t` must be a whole number, and `v1` must be there. If not, false.
3. `t` must be within `tolerance` of now (default 300 seconds), either way. If not, false.
4. Work out HMAC-SHA256 of `<t>.<raw body>`, with the secret as the key.
5. Compare it with `v1` in constant time. True only if they match.

It never throws on a bad header. It returns false. Use the **raw** body as it arrived: parsing and printing the JSON again changes the bytes.

**`parseWebhook(secret, rawBody, header, options)`** checks the signature, then returns the event:

```json
{ "id": "…", "type": "order.updated", "occurredAt": "2026-11-09T15:00:00.000Z", "siteId": "…", "data": { "object": "order", "id": "…" } }
```

If the signature is wrong, it fails with code `forbidden`. An event holds ids only, so fetch the record to see what changed. The same event can arrive twice, so skip an `id` you've already handled.

## 8. Hooks

Hooks let you log, measure and trace. All are optional, and an error thrown in a hook is ignored.

| Hook | When |
| --- | --- |
| `onRequest(info)` | Before each attempt. `info` has `operation`, `attempt` and `url`. |
| `onResponse(info, result)` | After each attempt. `result` has `httpStatus` (if any), `durationMs` and `error` (if any). |
| `onRetry(info, error, delayMs)` | Before waiting to try again |

## 9. Security

- `https://` only, except `localhost` and `127.0.0.1` (tested).
- The token is never put in an error, a log or a hook's `info`.
- Redirects aren't followed. A 3xx answer is an `api_error`.

## 10. Versions

Every SDK has the same version, from the root `VERSION` file. One tag, `v<version>`, releases them all. Anything that breaks callers gets a section in [MIGRATING.md](MIGRATING.md).

The schema is copied from the server's `dev` branch, after the server change has merged there. Never copy it from a branch that hasn't merged. A new SDK version may need a server that has the newest operations; the README says which.
