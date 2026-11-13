# Rockware SDK for .NET

Read and send a plant's records from your own code: orders, production runs, the catalog, the layout, custom entities and webhooks. It runs on .NET 8 and later, and on .NET Framework 4.6.2 and later (through .NET Standard 2.0).

```sh
dotnet add package Rockware.Sdk
```

## Start

You need the plant's API host and an API token. A plant admin makes the token in IMM under **Settings → Developers**, with the scopes you need: `data:read` to read, `data:write` to send, `webhooks:write` to manage webhooks.

```csharp
using Rockware;

using var rockware = new RockwareClient(new RockwareOptions
{
    Host = "https://acme-api.rockware.io",
    Token = Environment.GetEnvironmentVariable("ROCKWARE_TOKEN"),
    UserAgent = "acme-erp-sync/1.0",
});

var site = await rockware.GetSiteAsync();
Console.WriteLine(site?.Name);
```

There's one method per operation, and each returns what you asked for: `GetProductAsync` gives the product, or `null` if there isn't one. Optional arguments are named and can be left out: `ListOrdersAsync(first: 50)`.

A `RockwareClient` is safe to use from many threads. Make one and keep it, for example as a singleton.

## Read

```csharp
// One page.
var page = await rockware.ListOrdersAsync(first: 50);

// Every record, page by page.
await foreach (var product in rockware.ListAllProductsAsync())
    Console.WriteLine($"{product.Sku} {product.Name}");
```

**Stay in step with your system.** Pass the time of your last sync. Records come oldest change first, so you can save the newest `UpdatedAt` as you go:

```csharp
await foreach (var order in rockware.ListAllOrdersAsync(updatedSince: since))
{
    await SaveAsync(order);
    since = order.UpdatedAt;
}
```

Decimals, like `ItemCost`, are `decimal`, so no precision is lost. Enum values are strings, with constants to compare against, like `OrderStatus.Open`, so a value the API adds later still reads.

## Send

Records are found by **your** id (`ExternalId`) and the name of your system (`source`, `"erp"` if you leave it out). Sending the same thing twice gives the same result.

```csharp
var result = await rockware.UpsertOrderAsync(new OrderInput
{
    ExternalId = "SO-1001",
    OrderNumber = "1001",
    Customer = new CustomerInput { ExternalId = "C-42", Name = "Globex" },
    Lines = new List<OrderLineInput> { new() { Product = "P-100", TargetQuantity = 500 } },
});

if (result.Errors.Count > 0)
{
    // All or nothing: nothing was saved.
    foreach (var problem in result.Errors) Console.WriteLine($"{problem.Field} {problem.Message}");
}
else
{
    Console.WriteLine($"{result.Action} {result.Order?.Id}"); // CREATED, UPDATED or UNCHANGED
}
```

**A refused write isn't an exception.** Check `Errors` on every write.

**Only the properties you set are sent.** A field you don't set is left as it is. Setting one to `null` sends `null`, which clears it:

```csharp
await rockware.UpsertOrderAsync(new OrderInput { ExternalId = "SO-1001", Notes = null }); // clears the notes
```

## Errors

Anything else that goes wrong throws a `RockwareException`:

```csharp
try
{
    await rockware.ListProductsAsync();
}
catch (RockwareException error)
{
    Console.WriteLine($"{error.Code} {error.Message} {error.Hint} {error.RequestId}");
}
```

| `Code` | Meaning |
| --- | --- |
| `AuthRequired` | The token is wrong, revoked or for another plant |
| `Forbidden` | The token is missing a scope |
| `NotFound` | The thing you named isn't there |
| `Validation` | The request isn't right: a bad argument, or too big a query |
| `RateLimit` | Too many requests. `RetryAfter` says how long to wait. |
| `Network` | No answer from the host |
| `ApiError` | The server failed. `ServerCode` has its own code. |
| `Usage` | A bad setting, found before sending |

A cancelled `CancellationToken` throws `OperationCanceledException`, as usual.

## Retry

The client tries up to 3 times. It retries when:

- the server says to slow down (429), waiting as long as it asks, up to 60 seconds
- the server fails (5xx) or the connection drops, for reads and for writes that are safe to send twice

Turn it off with `Retry = false`.

## Webhooks

Check every delivery before you trust it. Pass the **raw** body, before any JSON parsing. In ASP.NET Core:

```csharp
app.MapPost("/rockware", async (HttpRequest request) =>
{
    using var buffer = new MemoryStream();
    await request.Body.CopyToAsync(buffer);
    var webhookEvent = RockwareWebhooks.Parse(secret, buffer.ToArray(), request.Headers[RockwareWebhooks.SignatureHeader]);
    queue.Enqueue(webhookEvent); // Answer within 10 seconds, then do the work.
    return Results.Ok();
});
```

`Parse` throws `RockwareException` with `Forbidden` if the signature is wrong or more than 5 minutes old. `Verify` gives `true` or `false` instead. The same event can arrive twice, so skip an `Id` you've already handled.

## Settings

| `RockwareOptions` | Default | |
| --- | --- | --- |
| `Host` | required | `https://` only, except `localhost` |
| `Token` or `TokenProvider` | required | A token, or a function that gives one for each call |
| `UserAgent` | none | Your app's name and version |
| `Timeout` | 30 seconds | For each attempt |
| `Retry` | `true` | |
| `Hooks` | none | `OnRequest`, `OnResponse`, `OnRetry`, for logs and metrics |
| `HttpHandler` | a new one | For proxies or tests. Redirects are turned off on an `HttpClientHandler`. |

Every method also takes a `CancellationToken`, and `ListAll…Async` takes `maxPages` (default 10,000).

## More

- [How every SDK behaves](https://github.com/rockwarehq/rockware-sdk/blob/main/SPEC.md)
- [Upgrading](https://github.com/rockwarehq/rockware-sdk/blob/main/MIGRATING.md)

MIT licensed.
