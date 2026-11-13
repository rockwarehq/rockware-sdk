# Agent notes

This repo holds Rockware's SDKs for its developer API: one folder per language. Start with [SPEC.md](SPEC.md). It's the rulebook every SDK follows. Write docs and comments in plain, simple language.

## How it fits together

```
schema/developer-api.graphql ─┐
operations/*.graphql ─────────┼─▶ each SDK's generator ─▶ <language>/…/generated/
behavior.json ────────────────┘
                                   hand-written client: send, retry, errors, paging, webhooks
conformance/ ─────────────────────▶ each SDK's runner checks the client
```

| SDK | Folder | Generator | Runner |
| --- | --- | --- | --- |
| TypeScript | `typescript/` | `pnpm generate` (`scripts/generate.ts`) | `test/conformance.test.ts` |
| Python | `python/` | `python scripts/generate.py` (needs `pip install -e ".[dev]"`) | `tests/test_conformance.py`, both clients |
| C# / .NET | `dotnet/` | to come | to come |
| Go | `go/` | to come | to come |

## Hard rules

1. **Never edit generated code** (`*/generated/`). Change `operations/` or `behavior.json`, then regenerate every SDK.
2. **Never edit `schema/developer-api.graphql` by hand.** Copy it from rw-server's `dev` branch (`apps/imm/schema.graphql`) after the server change has merged there.
3. **Every request comes from an operation in `operations/`.** Hand-written code never builds a query string.
4. **No business rules.** The server decides what a write may do, and the SDK passes on its answer. Don't check, fill in or fix inputs.
5. **Never match by name.** Records are found by outside id or IMM id only.
6. **Keep the SDKs in step.** A change to how one SDK behaves changes SPEC.md, adds or changes a case in `conformance/`, and lands in every SDK that's built.
7. **This repo is public.** No secrets, no real customer or plant names (use acme, globex, initech-west), no personal emails. Commit as `Michael Lindenau <michael@rockwarecorp.com>`. gitleaks runs in CI.

## Adding an operation

1. Copy the closest one in `operations/`. Names start with a verb (`Get`, `List`, `Upsert`, …), and each asks for exactly one root field.
2. A write that's safe to send twice goes in `safeToRepeat` in `behavior.json`.
3. Regenerate every SDK. The TypeScript generator also checks the rules above and the server's limits (6 deep, 300 fields).

`pnpm check-operations` in `typescript/` checks without writing anything. Set `RW_SCHEMA` to another schema file to check against it. rw-server's CI does this with each PR's schema, so an API change that breaks an operation fails there before it ships.

## Releasing

Every SDK has the version in `VERSION`. To release:

1. Run `scripts/bump-version.sh <version>`. It updates every package and starts the version's section in MIGRATING.md.
2. Open a PR, and merge it.
3. Push the tag `v<version>`. Each language's release workflow publishes it.
