# Rockware SDKs

Connect your own systems to Rockware: an ERP, a data warehouse, a script. These SDKs call Rockware's developer API for you, with types, retries, paging and webhook checks built in.

| Language | Folder | Package | Status |
| --- | --- | --- | --- |
| TypeScript / JavaScript | [`typescript/`](typescript/) | `@rockwarehq/sdk` on npm | Ready |
| Python | [`python/`](python/) | `rockware` on PyPI | Ready |
| C# / .NET | `dotnet/` | `Rockware.Sdk` on NuGet | Coming |
| Go | `go/` | `github.com/rockwarehq/rockware-sdk/go` | Coming |

| Feature | TypeScript | Python | C# | Go |
| --- | :-: | :-: | :-: | :-: |
| Every operation, with types | ✓ | ✓ | | |
| One error type, with codes and hints | ✓ | ✓ | | |
| Safe retries | ✓ | ✓ | | |
| Paging | ✓ | ✓ | | |
| Webhook checks | ✓ | ✓ | | |
| Hooks for logs and metrics | ✓ | ✓ | | |

## What you can do

- **Read** a plant's records: orders, production runs, each station's lineup, products, materials, tools, jobs, customers, workcenters, stations and custom entities. Page through all of them, or only what changed since your last sync.
- **Send** records in, by your own ids: orders, production runs, the catalog, the layout and custom entities. Put a station's runs in order.
- **Get told** when records change, with webhooks, and check that each delivery came from Rockware.

## Getting a token

A plant admin makes one in IMM under **Settings → Developers**. A token belongs to one plant. Give it only the scopes you need:

| Scope | Lets it |
| --- | --- |
| `data:read` | Read records |
| `data:write` | Send records (needs `data:read` too) |
| `webhooks:write` | Make and change webhooks (needs `data:read` too) |

Your host is your plant's API host, like `https://acme-api.rockware.io`.

## Quick start

### TypeScript

```ts
import { RockwareClient } from "@rockwarehq/sdk";

const rockware = new RockwareClient({ host: "https://acme-api.rockware.io", token: process.env.ROCKWARE_TOKEN! });

for await (const product of rockware.listAllProducts()) {
  console.log(product.sku, product.name);
}
```

More in [typescript/README.md](typescript/README.md).

### Python

```python
import os

from rockware import Rockware

rockware = Rockware(host="https://acme-api.rockware.io", token=os.environ["ROCKWARE_TOKEN"])

for product in rockware.list_all_products():
    print(product["sku"], product["name"])
```

More in [python/README.md](python/README.md).

## How it's built

Every SDK is made from the same files, and checked by the same tests:

- [`schema/developer-api.graphql`](schema/developer-api.graphql): the API's schema
- [`operations/`](operations/): every query and mutation the SDKs send
- [`behavior.json`](behavior.json): how to retry, and which writes are safe to send twice
- [`conformance/`](conformance/): tests every SDK runs

[SPEC.md](SPEC.md) says how every SDK behaves. All SDKs share one version. [MIGRATING.md](MIGRATING.md) says what changed between versions.

## Contributing

See [AGENTS.md](AGENTS.md) for how the repo works. Report a security problem privately, with a [security advisory](https://github.com/rockwarehq/rockware-sdk/security/advisories/new), not in an issue.

## License

MIT. See [LICENSE](LICENSE).
