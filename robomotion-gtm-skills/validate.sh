#!/usr/bin/env bash
# Contract checker for the robomotion-gtm-skills group. Run from the group root:
#   bash validate.sh
# Exits non-zero on any failure.
set -uo pipefail
cd "$(dirname "$0")"

fail=0
err() { echo "  ✗ $1"; fail=1; }

# --- group-level ---
[ -f .robomotion/skill.yaml ] || err ".robomotion/skill.yaml missing"

count=0
for d in skills/*/; do
  [ -d "$d" ] || continue
  slug=$(basename "$d")
  count=$((count+1))

  # required files
  [ -f "$d/SKILL.md" ]     || err "$slug: SKILL.md missing"
  [ -f "$d/env.required" ] || err "$slug: env.required missing"
  [ -f "$d/env.optional" ] || err "$slug: env.optional missing"

  # frontmatter keys
  if [ -f "$d/SKILL.md" ]; then
    head -8 "$d/SKILL.md" | grep -q "^name:"   || err "$slug: SKILL.md missing 'name:'"
    grep -q "^  version:"  "$d/SKILL.md"        || err "$slug: SKILL.md missing 'version:'"
    grep -q "^  category:" "$d/SKILL.md"        || err "$slug: SKILL.md missing 'category:'"
    grep -q "^  type:"     "$d/SKILL.md"        || err "$slug: SKILL.md missing 'type:'"
    fname=$(grep -m1 "^name:" "$d/SKILL.md" | sed 's/name: *//' | tr -d ' \r')
    [ "$fname" = "$slug" ] || err "$slug: frontmatter name '$fname' != dir name"
  fi

  # env var names must be valid (ignore blanks/comments)
  for ef in env.required env.optional; do
    if [ -f "$d/$ef" ]; then
      while IFS= read -r line; do
        case "$line" in ''|\#*) continue;; esac
        echo "$line" | grep -qE '^[A-Za-z_][A-Za-z0-9_]*$' || err "$slug/$ef: invalid var name '$line'"
      done < "$d/$ef"
    fi
  done
done

# --- script syntax ---
pys=$(find skills -name '*.py'); [ -n "$pys" ] && { python3 -m py_compile $pys 2>/tmp/gtmpy || { echo "  ✗ py_compile:"; cat /tmp/gtmpy; fail=1; }; }
find skills -name __pycache__ -type d -prune -exec rm -rf {} + 2>/dev/null
if command -v node >/dev/null 2>&1; then
  for m in $(find skills -name '*.mjs'); do node --check "$m" 2>/dev/null || err "node --check failed: $m"; done
fi
for j in $(find skills -name '*.json'); do python3 -c "import json,sys;json.load(open(sys.argv[1]))" "$j" 2>/dev/null || err "invalid JSON: $j"; done

echo "----------------------------------------"
if [ "$fail" -eq 0 ]; then
  echo "✓ robomotion-gtm-skills OK — $count skills, all checks passed"
else
  echo "✗ robomotion-gtm-skills FAILED — see above"
fi
exit "$fail"
