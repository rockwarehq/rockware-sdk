# Rockware SDK for Go

Read and send a plant's records from your own code: orders, production runs, the catalog, the layout, custom entities and webhooks. Go 1.24 or later. It needs nothing outside the standard library.

```sh
go get github.com/rockwarehq/rockware-sdk/go
```

```go
import "github.com/rockwarehq/rockware-sdk/go" // package rockware
```

## Start

You need the plant's API host and an API token. A plant admin makes the token in IMM under **Settings → Developers**, with the scopes you need: `data:read` to read, `data:write` to send, `webhooks:write` to manage webhooks.

```go
client, err := rockware.NewClient(rockware.Config{
	Host:      "https://acme-api.rockware.io",
	Token:     os.Getenv("ROCKWARE_TOKEN"),
	UserAgent: "acme-erp-sync/1.0",
})
if err != nil {
	log.Fatal(err)
}

site, err := client.GetSite(ctx)
```

There's one method per operation. It returns what you asked for: `GetProduct` gives a `*ProductFields`, or `nil` if there isn't one. Required arguments come first. Optional ones go in an options struct, which can be `nil`. `rockware.Ptr` makes a pointer for one: `&rockware.ListOrdersOptions{First: rockware.Ptr(50)}`.

A `Client` is safe to use from many goroutines. Make one and keep it.

## Read

```go
// One page.
page, err := client.ListOrders(ctx, &rockware.ListOrdersOptions{First: rockware.Ptr(50)})

// Every record, page by page.
for product, err := range client.ListAllProducts(ctx, nil) {
	if err != nil {
		return err
	}
	fmt.Println(product.Sku, product.Name)
}
```

**Stay in step with your system.** Pass the time of your last sync. Records come oldest change first, so you can save the newest `UpdatedAt` as you go:

```go
for order, err := range client.ListAllOrders(ctx, &rockware.ListAllOrdersOptions{UpdatedSince: &since}) {
	if err != nil {
		return err
	}
	save(order)
	since = order.UpdatedAt
}
```

Decimals, like `ItemCost`, are strings, so no precision is lost. Parse them with `math/big` or a decimal package.

## Send

Records are found by **your** id (`ExternalID`) and the name of your system (`Source`, `"erp"` if you leave it out). Sending the same thing twice gives the same result.

```go
result, err := client.UpsertOrder(ctx, rockware.OrderInput{
	ExternalID:  "SO-1001",
	OrderNumber: rockware.Ptr("1001"),
	Customer:    &rockware.CustomerInput{ExternalID: "C-42", Name: "Globex"},
	Lines:       []rockware.OrderLineInput{{Product: "P-100", TargetQuantity: 500}},
}, nil)
if err != nil {
	return err
}
if len(result.Errors) > 0 {
	// All or nothing: nothing was saved.
	for _, problem := range result.Errors {
		fmt.Println(problem.Field, problem.Message)
	}
}
```

**A refused write isn't an error.** Check `Errors` on every write.

A field you leave nil isn't sent, so it's left as it is. In Go you can't yet send `null` to clear a field, or an empty list to remove every line: use another SDK, or the API directly, for those.

## Errors

Anything else that goes wrong is a `*rockware.Error`:

```go
var rwErr *rockware.Error
if errors.As(err, &rwErr) {
	fmt.Println(rwErr.Code, rwErr.Message, rwErr.Hint, rwErr.RequestID)
}
```

| `Code` | Meaning |
| --- | --- |
| `CodeAuthRequired` | The token is wrong, revoked or for another plant |
| `CodeForbidden` | The token is missing a scope |
| `CodeNotFound` | The thing you named isn't there |
| `CodeValidation` | The request isn't right: a bad argument, or too big a query |
| `CodeRateLimit` | Too many requests. `RetryAfter` says how long to wait. |
| `CodeNetwork` | No answer from the host |
| `CodeAPIError` | The server failed. `ServerCode` has its own code. |
| `CodeUsage` | A bad setting, found before sending |

A cancelled `ctx` gives back `ctx.Err()`, not a `*rockware.Error`.

## Retry

The client tries up to 3 times. It retries when:

- the server says to slow down (429), waiting as long as it asks, up to 60 seconds
- the server fails (5xx) or the connection drops, for reads and for writes that are safe to send twice

Turn it off with `NoRetry: true`.

## Webhooks

Check every delivery before you trust it. Pass the **raw** body:

```go
http.HandleFunc("/rockware", func(w http.ResponseWriter, r *http.Request) {
	body, _ := io.ReadAll(r.Body)
	event, err := rockware.ParseWebhook(secret, body, r.Header.Get(rockware.SignatureHeader), nil)
	if err != nil {
		http.Error(w, "bad signature", http.StatusUnauthorized)
		return
	}
	w.WriteHeader(http.StatusOK) // Answer within 10 seconds, then do the work.
	queue <- event
})
```

`ParseWebhook` fails with `CodeForbidden` if the signature is wrong or more than 5 minutes old. `VerifyWebhook` gives `true` or `false` instead. The same event can arrive twice, so skip an `ID` you've already handled.

## Settings

| `Config` field | Default | |
| --- | --- | --- |
| `Host` | required | `https://` only, except `localhost` |
| `Token` or `TokenFunc` | required | A token, or a function that gives one for each call |
| `UserAgent` | none | Your app's name and version |
| `Timeout` | 30 seconds | For each attempt |
| `NoRetry` | `false` | |
| `Hooks` | none | `OnRequest`, `OnResponse`, `OnRetry`, for logs and metrics |
| `HTTPClient` | a new one | For proxies or tests. Redirects are never followed. |

`ListAll…` options also take `MaxPages` (default 10,000).

## More

- [How every SDK behaves](https://github.com/rockwarehq/rockware-sdk/blob/main/SPEC.md)
- [Upgrading](https://github.com/rockwarehq/rockware-sdk/blob/main/MIGRATING.md)

MIT licensed.
