#!/usr/bin/env bash
# Thin wrapper so instruction files can say `bash scripts/ledger-append.sh ...`
# whatever the working directory. Needs node 18+.
set -euo pipefail
here="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
if ! command -v node >/dev/null 2>&1; then
  echo "ledger-append: node is required (18+). Install it, or write the entry by hand per references/ledger.md." >&2
  exit 2
fi
exec node "$here/ledger-append.mjs" "$@"
