#!/usr/bin/env bash
# Validate the Robomotion skill contract.
# See how-to-write-or-port-a-skill-to-robomotion.md.
#
# Contract:
#   * Every "unit" (group OR standalone skill) has a .robomotion/skill.yaml.
#   * Groups also have inner skills under <group>/skills/<name>/SKILL.md.
#   * SKILL.md has YAML front-matter with `name:` matching the directory.
#   * .robomotion/{LICENSE,CHANGELOG.md} live at the unit root (NOT per inner skill).
#   * env.required / env.optional contain valid env-var names.
#   * Any scripts/*.py compiles; any scripts/*.js passes `node --check`.
#   * Vendored CLI bundles (tools/clis, bin) are syntax-checked.
#   * index.yaml is up-to-date with build-index.py.
set -uo pipefail
cd "$(dirname "$0")"

fail=0
units=0
inner_skills=0
standalone_skills=0

is_valid_env_name() { [[ "$1" =~ ^[A-Za-z_][A-Za-z0-9_]*$ ]]; }

check_env_file() {
  local file="$1"
  [ -f "$file" ] || return 0
  local n=0 line name
  while IFS= read -r line || [ -n "$line" ]; do
    n=$((n+1))
    line="${line#"${line%%[![:space:]]*}"}"
    [ -z "$line" ] && continue
    case "$line" in \#*) continue;; esac
    name="${line%%=*}"
    name="${name%"${name##*[![:space:]]}"}"
    if ! is_valid_env_name "$name"; then
      echo "    FAIL: $(basename "$file"):$n invalid env name: '$name'"; fail=1
    fi
  done < "$file"
}

frontmatter() {
  awk 'NR==1 && $0!="---"{exit} NR==1{next} /^---[[:space:]]*$/{exit} {print}' "$1"
}

check_scripts() {
  local base="$1" vendored="${2:-}"
  [ -d "$base/scripts" ] || return 0
  local py js sev
  sev="FAIL"; [ -n "$vendored" ] && sev="WARN"
  for py in "$base"/scripts/*.py; do
    [ -e "$py" ] || continue
    python3 -c 'import sys; compile(open(sys.argv[1]).read(), sys.argv[1], "exec")' "$py" 2>/dev/null \
      || { echo "    ${sev}: $py does not compile"; [ -z "$vendored" ] && fail=1; }
  done
  if command -v node >/dev/null 2>&1; then
    for js in "$base"/scripts/*.js; do
      [ -e "$js" ] || continue
      node --check "$js" 2>/dev/null || { echo "    ${sev}: $js failed node --check"; [ -z "$vendored" ] && fail=1; }
    done
  fi
}

check_skill_md() {
  # $1 = path/to/skill dir (containing SKILL.md)
  # $2 = optional "vendored" marker (skip strict name/version checks for upstream content)
  local sd="$1" vendored="${2:-}"
  local md="$sd/SKILL.md"
  local skill=$(basename "$sd")
  local rel="${sd#./}"
  local fm name
  echo "• $rel"

  fm="$(frontmatter "$md")"
  if [ -z "$fm" ]; then
    if [ -n "$vendored" ]; then
      echo "    WARN: missing or empty YAML front-matter (vendored — upstream's fault, skill will be unindexed)"
      return
    fi
    echo "    FAIL: missing or empty YAML front-matter"; fail=1; return
  fi

  name="$(printf '%s\n' "$fm" | sed -n 's/^name:[[:space:]]*//p' | head -1 | tr -d '"'"'"' ')"
  if [ -n "$name" ] && [ "$name" != "$skill" ]; then
    if [ -n "$vendored" ]; then
      echo "    WARN: name '$name' != directory '$skill' (vendored — upstream convention)"
    else
      echo "    FAIL: name '$name' != directory '$skill'"; fail=1
    fi
  fi

  if ! printf '%s\n' "$fm" | grep -qE '^version:' \
     && ! printf '%s\n' "$fm" | grep -qE '^[[:space:]]+version:'; then
    [ -z "$vendored" ] && echo "    WARN: no version (top-level 'version:' or 'metadata.version')"
  fi

  check_env_file "$sd/env.required"
  check_env_file "$sd/env.optional"
  check_scripts "$sd" "$vendored"

  if [ -d "$sd/scripts" ] && [ -n "$(ls -A "$sd/scripts" 2>/dev/null)" ]; then
    echo "    mode: container (ships scripts/)"
  elif [ -f "$sd/post-install.sh" ]; then
    echo "    mode: container (ships post-install.sh)"
  else
    echo "    mode: host (knowledge)"
  fi
}

# ---- discover units (anything with .robomotion/skill.yaml) -----------------

while IFS= read -r sy; do
  unit_dir="$(dirname "$(dirname "$sy")")"
  unit_rel="${unit_dir#./}"
  units=$((units+1))
  type="$(sed -n 's/^type:[[:space:]]*//p' "$sy" | head -1 | tr -d '"'"'"' ')"
  echo "▼ UNIT: $unit_rel  (type: ${type:-?})"

  # Group-level required files
  [ -f "$unit_dir/.robomotion/LICENSE" ]      || { echo "    WARN: $unit_rel/.robomotion/LICENSE missing"; }
  [ -f "$unit_dir/.robomotion/CHANGELOG.md" ] || { echo "    WARN: $unit_rel/.robomotion/CHANGELOG.md missing"; }

  if [ "$type" = "group" ]; then
    # walk inner skills — the agentskills.io layout (skills/<name>/),
    # the Claude Code plugin layout (.claude/skills/<name>/),
    # and the Claude Code marketplace meta-group layout
    # (plugins/<plugin>/skills/<name>/).
    for skills_subdir in "$unit_dir/skills" "$unit_dir/.claude/skills"; do
      [ -d "$skills_subdir" ] || continue
      # Walk arbitrarily deep — matches build-index.py's recursive
      # discover_inner_skills. Hermes nests up to 3 levels
      # (skills/mlops/inference/<skill>/SKILL.md). Previous -maxdepth 3
      # silently dropped those 8 skills from the validate count.
      while IFS= read -r md; do
        check_skill_md "$(dirname "$md")" vendored
        inner_skills=$((inner_skills+1))
      done < <(find "$skills_subdir" -name SKILL.md | sort)
    done
    if [ -d "$unit_dir/plugins" ]; then
      while IFS= read -r md; do
        check_skill_md "$(dirname "$md")" vendored
        inner_skills=$((inner_skills+1))
      done < <(find "$unit_dir/plugins" -mindepth 4 -maxdepth 4 -name SKILL.md | sort)
    fi
    # check group's .robomotion/post-install.sh syntactically (best-effort)
    [ -f "$unit_dir/.robomotion/post-install.sh" ] && sh -n "$unit_dir/.robomotion/post-install.sh" \
      || true
    # syntax-check group's CLI bundles
    if command -v node >/dev/null 2>&1; then
      for clidir in "$unit_dir/bin" "$unit_dir/tools/clis"; do
        [ -d "$clidir" ] || continue
        n=0
        for js in "$clidir"/*.js; do
          [ -e "$js" ] || continue
          n=$((n+1))
          node --check "$js" 2>/dev/null || { echo "    FAIL: $js failed node --check"; fail=1; }
        done
        [ "$n" -gt 0 ] && echo "  • ${clidir#./} ($n CLIs checked)"
      done
    fi
  elif [ "$type" = "skill" ]; then
    # standalone — SKILL.md is at the unit root
    # Treated as vendored: name in upstream SKILL.md may not match our directory
    # (we may have renamed for collision uniqueness across the vendored corpus).
    if [ -f "$unit_dir/SKILL.md" ]; then
      check_skill_md "$unit_dir" vendored
      standalone_skills=$((standalone_skills+1))
    else
      echo "    FAIL: $unit_rel declares type: skill but has no SKILL.md"; fail=1
    fi
  else
    echo "    FAIL: $unit_rel/.robomotion/skill.yaml has unknown type '$type'"; fail=1
  fi
done < <(find . \( -name .git -o -name node_modules -o -name docs \) -prune -o -path '*/.robomotion/skill.yaml' -print | sort)

# ---- index.yaml drift check ------------------------------------------------

if command -v python3 >/dev/null 2>&1; then
  echo
  python3 build-index.py --check || fail=1
fi

echo
if [ "$fail" -ne 0 ]; then
  echo "FAILED — $units unit(s), $inner_skills inner + $standalone_skills standalone skill(s), errors above."
  exit 1
fi
echo "OK — $units unit(s) valid · $inner_skills inner + $standalone_skills standalone skill(s)."
