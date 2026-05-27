#!/bin/bash
# Mnemos PreCompact Hook — emergency checkpoint + typed preservation + compaction marker.
#
# TWO-LAYER DEFENSE against lossy compaction:
#   Layer 1 (this script): Write emergency checkpoint, output strong preservation
#           instructions with inline content for the summarizer.
#   Layer 2 (mnemos-post-compact-inject.sh): After compaction, the first tool call
#           re-injects the full checkpoint. See that script for details.
#
# The marker file (.mnemos/just-compacted) bridges the two layers.
#
# Install: add to .claude/settings.json under hooks.PreCompact
# This EXTENDS (not replaces) the existing pre-compact.sh

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"

# ─── 1. Write emergency checkpoint with task narrative ───

MNEMOS_CMD=""
if command -v mnemos &>/dev/null; then
    MNEMOS_CMD="mnemos"
elif PYTHONPATH="${SCRIPT_DIR%/templates}/scripts" python3 -m mnemos --version &>/dev/null 2>&1; then
    MNEMOS_CMD="PYTHONPATH=${SCRIPT_DIR%/templates}/scripts python3 -m mnemos"
fi

if [ -n "$MNEMOS_CMD" ]; then
    eval $MNEMOS_CMD checkpoint --force &>/dev/null
fi

# ─── 2. Write compaction marker for Layer 2 detection ───

python3 -c "
import json, time, os
os.makedirs('.mnemos', exist_ok=True)
with open('.mnemos/just-compacted', 'w') as f:
    json.dump({'timestamp': time.time(), 'reason': 'pre_compact_hook'}, f)
"

# ─── 3. Build inline checkpoint content for summarizer ───
# Use a temp Python script to avoid bash escaping issues with f-strings

CHECKPOINT_CONTENT=""
if [ -f ".mnemos/checkpoint-latest.json" ]; then
    TMPSCRIPT=$(mktemp /tmp/mnemos-precompact-XXXXXX.py)
    cat > "$TMPSCRIPT" << 'PYSCRIPT'
import json, sys, os
try:
    with open('.mnemos/checkpoint-latest.json') as f:
        data = json.load(f)
    lines = []
    goal = data.get('goal', '')
    if goal:
        lines.append('GOAL: ' + goal)
    for c in data.get('active_constraints', []):
        lines.append('CONSTRAINT: ' + c)
    narrative = data.get('task_narrative', '')
    if narrative:
        lines.append('ACTIVITY: ' + narrative)
    subgoal = data.get('current_subgoal', '')
    if subgoal:
        lines.append('CURRENT TASK: ' + subgoal)
    working = data.get('working_memory', '')
    if working:
        lines.append('WORKING MEMORY: ' + working[:300])
    for r in data.get('active_results', [])[:5]:
        lines.append('RESULT: ' + r)
    files = data.get('recent_files', [])[:8]
    if files:
        file_parts = []
        for entry in files:
            p = entry.get('path', '?')
            e = entry.get('edits', 0)
            r = entry.get('reads', 0)
            parts = []
            if e:
                parts.append('edited ' + str(e) + 'x')
            if r:
                parts.append('read ' + str(r) + 'x')
            file_parts.append(p + ' (' + ', '.join(parts) + ')')
        lines.append('FILES: ' + '; '.join(file_parts))
    git = data.get('git_state', {})
    if git.get('branch'):
        lines.append('GIT: branch=' + git['branch'])
        uncommitted = git.get('uncommitted', [])
        if uncommitted:
            lines.append('UNCOMMITTED: ' + ', '.join(uncommitted[:5]))
    print('\n'.join(lines))
except Exception as e:
    print('Error: ' + str(e), file=sys.stderr)
PYSCRIPT
    CHECKPOINT_CONTENT=$(python3 "$TMPSCRIPT")
    rm -f "$TMPSCRIPT"
fi

# ─── 4. Extract typed preservation priorities from MnemoGraph ───

MNEMOS_PRIORITIES=""
if [ -f ".mnemos/mnemo.db" ]; then
    TMPSCRIPT2=$(mktemp /tmp/mnemos-priorities-XXXXXX.py)
    cat > "$TMPSCRIPT2" << PYSCRIPT
import json, sys
sys.path.insert(0, '${SCRIPT_DIR%/templates}/scripts')

try:
    from mnemos.store import MnemosStore
    store = MnemosStore('.')
    if not store.exists():
        sys.exit(0)

    goals = store.get_by_type('goal')
    constraints = store.get_by_type('constraint')
    working = store.get_by_type('working')
    results = store.get_by_type('result')

    lines = []
    if goals:
        lines.append('GOAL (NEVER DROP):')
        for g in goals[:5]:
            lines.append('  - ' + g.content[:200])

    if constraints:
        lines.append('CONSTRAINTS (NEVER DROP):')
        for c in constraints[:10]:
            lines.append('  - ' + c.content[:200])

    if working:
        lines.append('CURRENT TASK (HIGH PRIORITY):')
        for w in working[:3]:
            lines.append('  - ' + w.content[:200])

    if results:
        lines.append('RESULTS (KEEP SUMMARIES):')
        for r in results[:5]:
            summary = r.summary or r.content[:100]
            lines.append('  - ' + summary)

    print('\n'.join(lines))
except Exception:
    pass
PYSCRIPT
    MNEMOS_PRIORITIES=$(python3 "$TMPSCRIPT2")
    rm -f "$TMPSCRIPT2"
fi

# ─── 5. Output preservation instructions for summarizer ───
# Everything to stdout becomes additional instructions for the compaction prompt

cat <<'INSTRUCTIONS'
## CRITICAL: Mnemos Task State Preservation

An emergency checkpoint has been saved to disk (.mnemos/checkpoint-latest.json).
A post-compaction injection hook will re-inject this checkpoint after compaction.

However, your summary should ALSO preserve the following task state. Include
this section VERBATIM in your summary output under a "## Mnemos Task State" heading:

INSTRUCTIONS

if [ -n "$CHECKPOINT_CONTENT" ]; then
cat <<INSTRUCTIONS

### Mnemos Task State (INCLUDE VERBATIM IN SUMMARY)

$CHECKPOINT_CONTENT

INSTRUCTIONS
fi

cat <<'INSTRUCTIONS'

### Typed Eviction Policies

**NEVER EVICT** (include verbatim in summary):
- GoalNodes: The task's primary objective — without this the agent cannot continue
- ConstraintNodes: Invariants and contracts that must not be violated

**COMPRESS BUT KEEP** (include summary, not full content):
- WorkingNodes: Current in-progress reasoning
- ResultNodes: Completed sub-task results (keep summaries)

**OK TO DROP** (can be re-derived from disk):
- ContextNodes: File contents, tool outputs
- Full tool call results (keep only findings)
- Exploration that led nowhere

INSTRUCTIONS

if [ -n "$MNEMOS_PRIORITIES" ]; then
cat <<INSTRUCTIONS

### Active Memory Nodes (from MnemoGraph)

$MNEMOS_PRIORITIES

These nodes represent the agent's active working memory. The summarizer
MUST preserve Goal and Constraint nodes VERBATIM in the output.

INSTRUCTIONS
fi

# ─── 6. Run existing pre-compact.sh if present ───

if [ -f "$SCRIPT_DIR/pre-compact.sh" ]; then
    bash "$SCRIPT_DIR/pre-compact.sh"
fi

exit 0
