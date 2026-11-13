#!/usr/bin/env bash
# Sets every SDK to one version, and starts its section in MIGRATING.md.
# Usage: scripts/bump-version.sh 0.2.0
set -euo pipefail

VERSION="${1:-}"
if ! [[ "$VERSION" =~ ^[0-9]+\.[0-9]+\.[0-9]+$ ]]; then
  echo "Usage: $0 <version>, like 0.2.0" >&2
  exit 1
fi

cd "$(dirname "$0")/.."

echo "$VERSION" > VERSION

# TypeScript: package.json's version line only, then the generated version file.
sed -i.bak -E "s/^  \"version\": \"[^\"]+\"/  \"version\": \"$VERSION\"/" typescript/package.json
rm -f typescript/package.json.bak
(cd typescript && pnpm --silent generate)

# Python: pyproject.toml, and the generated version file (the same line the
# generator writes, so CI's "generated code is up to date" check still passes).
sed -i.bak -E "s/^version = \"[^\"]+\"/version = \"$VERSION\"/" python/pyproject.toml
sed -i.bak -E "s/^VERSION = \"[^\"]+\"/VERSION = \"$VERSION\"/" python/src/rockware/_generated/version.py
rm -f python/pyproject.toml.bak python/src/rockware/_generated/version.py.bak

# MIGRATING.md: "# Unreleased" becomes this version, and a new one starts above it.
if grep -q '^# Unreleased$' MIGRATING.md; then
  node -e '
    const fs = require("fs");
    const text = fs.readFileSync("MIGRATING.md", "utf8");
    fs.writeFileSync("MIGRATING.md", text.replace(/^# Unreleased$/m, `# Unreleased\n\nNothing yet.\n\n# v${process.argv[1]}`));
  ' "$VERSION"
fi

echo "Every SDK is now $VERSION. Check MIGRATING.md, then open a PR."
