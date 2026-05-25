#!/usr/bin/env bash
# Validate every skill folder against the Robomotion skill contract.
# See how-to-write-or-port-a-skill-to-robomotion.md and README.md.
#
# Checks per skill (a top-level dir containing SKILL.md):
#   - front-matter present; `name:` matches the directory name
#   - a version is declared (top-level `version:` or nested `metadata.version`)
#   - LICENSE and CHANGELOG.md present (repo convention)
#   - env.required / env.optional contain only valid env-var names
#   - any scripts/*.py compile; any scripts/*.js pass `node --check`
# Prints per-skill results and exits non-zero if any check fails.
set -uo pipefail

cd "$(dirname "$0")"

fail=0
skills=0

is_valid_env_name() { [[ "$1" =~ ^[A-Za-z_][A-Za-z0-9_]*$ ]]; }

check_env_file() {
  local file="$1" skill="$2"
  [ -f "$file" ] || return 0
  local n=0 line name
  while IFS= read -r line || [ -n "$line" ]; do
    n=$((n+1))
    line="${line#"${line%%[![:space:]]*}"}"   # ltrim
    [ -z "$line" ] && continue
    case "$line" in \#*) continue;; esac
    name="${line%%=*}"                          # strip inline =VALUE
    name="${name%"${name##*[![:space:]]}"}"     # rtrim
    if ! is_valid_env_name "$name"; then
      echo "    FAIL: $(basename "$file"):$n invalid env name: '$name'"; fail=1
    fi
  done < "$file"
}

frontmatter() {  # print the YAML front-matter block of $1
  awk 'NR==1 && $0!="---"{exit} NR==1{next} /^---[[:space:]]*$/{exit} {print}' "$1"
}

for dir in */; do
  skill="${dir%/}"
  md="$skill/SKILL.md"
  [ -f "$md" ] || continue          # not a skill folder
  skills=$((skills+1))
  echo "• $skill"

  fm="$(frontmatter "$md")"
  if [ -z "$fm" ]; then
    echo "    FAIL: missing or empty YAML front-matter"; fail=1; continue
  fi

  name="$(printf '%s\n' "$fm" | sed -n 's/^name:[[:space:]]*//p' | head -1 | tr -d '"'"'"' ')"
  if [ "$name" != "$skill" ]; then
    echo "    FAIL: name '$name' != directory '$skill'"; fail=1
  fi

  if ! printf '%s\n' "$fm" | grep -qE '^version:' \
     && ! printf '%s\n' "$fm" | grep -qE '^[[:space:]]+version:'; then
    echo "    WARN: no version (top-level 'version:' or 'metadata.version') — cache-busting weakened"
  fi

  [ -f "$skill/LICENSE" ]      || { echo "    FAIL: missing LICENSE"; fail=1; }
  [ -f "$skill/CHANGELOG.md" ] || { echo "    FAIL: missing CHANGELOG.md"; fail=1; }

  check_env_file "$skill/env.required" "$skill"
  check_env_file "$skill/env.optional" "$skill"

  if [ -d "$skill/scripts" ]; then
    for py in "$skill"/scripts/*.py; do
      [ -e "$py" ] || continue
      if ! python3 -m py_compile "$py" 2>/dev/null; then
        echo "    FAIL: $py does not compile"; fail=1
      fi
    done
    if command -v node >/dev/null 2>&1; then
      for js in "$skill"/scripts/*.js; do
        [ -e "$js" ] || continue
        if ! node --check "$js" 2>/dev/null; then
          echo "    FAIL: $js failed node --check"; fail=1
        fi
      done
    fi
    echo "    mode: container (ships scripts/)"
  elif [ -f "$skill/post-install.sh" ]; then
    echo "    mode: container (ships post-install.sh)"
  else
    echo "    mode: host (knowledge)"
  fi
done

echo
if [ "$fail" -ne 0 ]; then
  echo "FAILED — $skills skill(s) checked, errors above."
  exit 1
fi
echo "OK — $skills skill(s) valid."
