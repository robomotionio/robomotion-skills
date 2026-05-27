#!/usr/bin/env bash
# verify-envelope.sh — smoke-test the v2 JSON envelope contract.
#
# Runs a handful of --json invocations against the local build and greps the
# output for envelope shape tells. Not a full test suite — an executable
# version of the manual verification checklist in the v2 migration plan.
#
# Requires a working `pnpm build` first. Run from any cwd — the script cd's
# into the helius-cli package.
#
# Usage: bash helius-cli/scripts/verify-envelope.sh [pubkey]
#
# Exits 0 on all-pass, nonzero on first failure.

set -u

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR/.."

CLI="node dist/bin/helius.js"
PUBKEY="${1:-So11111111111111111111111111111111111111112}"  # wSOL mint — always exists
PASS=0
FAIL=0

check() {
  local label="$1"
  local expected="$2"
  local output="$3"
  if echo "$output" | grep -q -- "$expected"; then
    echo "  ok   $label"
    PASS=$((PASS + 1))
  else
    echo "  FAIL $label"
    echo "       expected match: $expected"
    echo "       got: $(echo "$output" | head -5)"
    FAIL=$((FAIL + 1))
  fi
}

if [ ! -f dist/bin/helius.js ]; then
  echo "dist/bin/helius.js not found — run pnpm build first." >&2
  exit 1
fi

echo "Envelope contract smoke tests"
echo "============================="

echo "Success envelope (balance):"
out=$($CLI balance "$PUBKEY" --json 2>/dev/null || true)
check "ok: true present" '"ok": true' "$out"
check "v: 1 present"     '"v": 1'     "$out"
check "data present"     '"data":'    "$out"

echo "Success envelope (config show):"
out=$($CLI config show --json 2>/dev/null || true)
check "ok: true present" '"ok": true' "$out"
check "v: 1 present"     '"v": 1'     "$out"

echo "Error envelope (invalid address → validation):"
out=$($CLI balance not-a-valid-address --json 2>/dev/null || true)
check "ok: false present"         '"ok": false'                  "$out"
check "v: 1 present"              '"v": 1'                       "$out"
check "error_code present"        '"error_code":'                "$out"
check "category: validation"      '"category": "validation"'     "$out"
check "recoverable: false"        '"recoverable": false'         "$out"

echo "Error envelope (invalid api key → auth):"
out=$($CLI balance "$PUBKEY" --api-key invalid_key_here --json 2>/dev/null || true)
check "ok: false present"         '"ok": false'                  "$out"
check "category: auth"            '"category": "auth"'           "$out"

echo "Commander boundary (unknown flag):"
out=$($CLI --not-a-real-flag --json 2>/dev/null || true)
check "ok: false present"         '"ok": false'                  "$out"
check "category: validation"      '"category": "validation"'     "$out"

echo ""
echo "Passed: $PASS   Failed: $FAIL"
[ "$FAIL" -eq 0 ]
