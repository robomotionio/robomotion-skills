#!/usr/bin/env bash
# Validate every skill folder against the Robomotion skill contract.
# See how-to-write-or-port-a-skill-to-robomotion.md and README.md.
#
# A skill is ANY directory containing SKILL.md (repo root OR nested under a
# group, e.g. marketing-skills/<category>/<skill>/). `_shared/` dirs are not
# skills (no SKILL.md) but their scripts are still syntax-checked.
#
# Checks per skill:
#   - front-matter present; `name:` matches the directory's basename
#   - a version is declared (top-level `version:` or nested `metadata.version`)
#   - LICENSE and CHANGELOG.md present (repo convention)
#   - env.required / env.optional contain only valid env-var names
#   - any scripts/*.py compile; any scripts/*.js pass `node --check`
# Plus: every _shared/scripts/* is syntax-checked.
# Prints per-skill results and exits non-zero if any check fails.
set -uo pipefail

cd "$(dirname "$0")"

fail=0
skills=0

is_valid_env_name() { [[ "$1" =~ ^[A-Za-z_][A-Za-z0-9_]*$ ]]; }

check_env_file() {
  local file="$1"
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

check_scripts() {  # syntax-check scripts in $1/scripts (py + js)
  local base="$1"
  [ -d "$base/scripts" ] || return 0
  local py js
  for py in "$base"/scripts/*.py; do
    [ -e "$py" ] || continue
    # in-memory syntax check — does NOT write __pycache__ (which would pollute index.json)
    python3 -c 'import sys; compile(open(sys.argv[1]).read(), sys.argv[1], "exec")' "$py" 2>/dev/null \
      || { echo "    FAIL: $py does not compile"; fail=1; }
  done
  if command -v node >/dev/null 2>&1; then
    for js in "$base"/scripts/*.js; do
      [ -e "$js" ] || continue
      node --check "$js" 2>/dev/null || { echo "    FAIL: $js failed node --check"; fail=1; }
    done
  fi
}

# Discover skills: any dir with SKILL.md, excluding VCS/docs/node_modules.
while IFS= read -r md; do
  skill_dir="$(dirname "$md")"
  skill="$(basename "$skill_dir")"
  rel="${skill_dir#./}"
  skills=$((skills+1))
  echo "• $rel"

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

  [ -f "$skill_dir/LICENSE" ]      || { echo "    FAIL: missing LICENSE"; fail=1; }
  [ -f "$skill_dir/CHANGELOG.md" ] || { echo "    FAIL: missing CHANGELOG.md"; fail=1; }

  check_env_file "$skill_dir/env.required"
  check_env_file "$skill_dir/env.optional"
  check_scripts "$skill_dir"

  if [ -d "$skill_dir/scripts" ] && [ -n "$(ls -A "$skill_dir/scripts" 2>/dev/null)" ]; then
    echo "    mode: container (ships scripts/)"
  elif [ -f "$skill_dir/post-install.sh" ]; then
    echo "    mode: container (ships post-install.sh)"
  else
    echo "    mode: host (knowledge); container if its nearest _shared ships scripts"
  fi
done < <(find . \( -name .git -o -name node_modules -o -name docs \) -prune -o -name SKILL.md -print | sort)

# Syntax-check shared libraries (not skills themselves).
shared_count=0
while IFS= read -r shdir; do
  shared_count=$((shared_count+1))
  echo "• ${shdir#./} (shared library)"
  check_scripts "$shdir"
done < <(find . \( -name .git -o -name node_modules \) -prune -o -type d -name _shared -print | sort)

echo
if [ "$fail" -ne 0 ]; then
  echo "FAILED — $skills skill(s) + $shared_count shared lib(s) checked, errors above."
  exit 1
fi
echo "OK — $skills skill(s) + $shared_count shared lib(s) valid."
