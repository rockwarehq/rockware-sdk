# Shared tests

Every SDK runs these. They're how four languages stay in step: a rule in [SPEC.md](../SPEC.md) that says **(tested)** has a case here.

- `tests/*.json`: calls to make, the fake server's answers, and what must happen.
- `webhooks.json`: signature cases for `verifyWebhook`.

Each SDK has a small runner that reads these files. The runner plays the server: it answers each request with the next answer in the list, in order.

## A test

```json
{
  "name": "a query retries a 503 and then succeeds",
  "client": { "userAgent": "acme-erp-sync/2.1" },
  "operation": "GetSite",
  "variables": {},
  "paginate": false,
  "maxPages": 10000,
  "responses": [{ "status": 503 }, { "status": 200, "body": { "data": { "site": { "id": "site_1" } } } }],
  "assertions": [{ "type": "requestCount", "expected": 2 }]
}
```

| Field | Meaning |
| --- | --- |
| `client` | Settings for the client. Left out: `host` is `https://acme-api.example.com`, `token` is `rw_app_test`. Others: `userAgent`, `retry` (false turns it off). |
| `operation` | The operation to call, by its name in `operations/` |
| `variables` | What to pass it |
| `paginate` | True: page through it with the SDK's paging helper, and collect every record |
| `maxPages` | The paging limit to set, when `paginate` is true |
| `responses` | The fake server's answers, one per request, in order |

An answer has `status`, and may have `headers` and either `body` (sent as JSON) or `rawBody` (sent as it is). `{"networkError": true}` drops the connection instead of answering.

A header value of `{{httpdate+Ns}}` becomes an HTTP date `N + 1` seconds after the moment it's sent, so a test can check `Retry-After` as a date.

If more requests come than there are answers, the runner fails the test.

## Assertions

| Type | Passes when |
| --- | --- |
| `requestCount` | Exactly `expected` requests were made |
| `requestMethod`, `requestUrl` | The first request's method or URL is `expected` |
| `requestHeader` | Request `index` (default 0) has header `name` (any case) equal to `expected`, or matching the regex `pattern` |
| `requestBody` | The JSON body of request `index` (default 0) at `path` is `expected`, matches `pattern`, or is missing when `absent` is true |
| `delayBetweenRequests` | The gap between request `index` and the next is at least `minMs`, and at most `maxMs` if given |
| `noError` | The call didn't fail |
| `error` | The call failed with a `RockwareError`, and each field given (`code`, `httpStatus`, `retryable`, `retryAfter`, `requestId`, `serverCode`) is equal |
| `errorMessage` | The error's message matches `pattern`, or doesn't contain `excludes` |
| `errorMessageLength` | The error's message is at most `max` characters |
| `errorCount` | The error carries `expected` GraphQL errors |
| `result` | The value at `path` in what the call returned is `expected`. `""` is the whole value. With `paginate`, the value is the list of records collected, even if the call failed partway. |

A `path` is dotted: `variables.order.externalId`, `errors.0.code`. `length` gives a list's length.
