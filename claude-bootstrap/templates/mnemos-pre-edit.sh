#!/bin/bash
# Mnemos PreToolUse Hook — fatigue-aware pre-edit with iCPG context.
#
# 1. Logs file path to signals.jsonl (for scope scatter + re-read tracking)
# 2. Reads fatigue from observable signals + token data
# 3. Auto-checkpoint when fatigue >= 0.60
# 4. Auto-consolidation when fatigue >= 0.40
# 5. Injects iCPG context, constraints, drift
#
# Install: add to .claude/settings.json under hooks.PreToolUse
# Timeout: 5 seconds max

# ─── Read hook input from stdin ───

HOOK_INPUT=$(cat)

# ─── Extract file path and tool name ───

FILE_PATH=""
TOOL_NAME=""
if [ -n "$HOOK_INPUT" ]; then
    eval $(echo "$HOOK_INPUT" | python3 -c "
import sys, json
try:
    data = json.load(sys.stdin)
    fp = data.get('tool_input', {}).get('file_path', '') or data.get('tool_input', {}).get('path', '')
    tn = data.get('tool_name', '')
    print(f'FILE_PATH=\"{fp}\"')
    print(f'TOOL_NAME=\"{tn}\"')
except:
    print('FILE_PATH=\"\"')
    print('TOOL_NAME=\"\"')
")
fi

if [ -z "$FILE_PATH" ]; then
    exit 0
fi

# ─── Log signal for fatigue computation ───

if [ -d ".mnemos" ] || [ -f ".mnemos/fatigue.json" ]; then
    python3 -c "
import json, time, os
os.makedirs('.mnemos', exist_ok=True)
signal = {
    'tool': '$TOOL_NAME',
    'event': 'pre',
    'file_path': '$FILE_PATH',
    'ts': time.time()
}
with open('.mnemos/signals.jsonl', 'a') as f:
    f.write(json.dumps(signal) + '\n')
"
fi

# ─── Fatigue check (full model from observable signals) ───

FATIGUE_WARNING=""
if [ -f ".mnemos/fatigue.json" ]; then
    FATIGUE_ACTION=$(python3 -c "
import json, sys
sys.path.insert(0, 'scripts')

try:
    from mnemos.fatigue import compute_fatigue, read_fatigue_file
    data = read_fatigue_file('.')
    if not data:
        print('flow')
        sys.exit(0)

    fatigue = compute_fatigue(data, '.')
    print(fatigue.state)
except Exception:
    # Fallback: just use token utilization
    try:
        with open('.mnemos/fatigue.json') as f:
            data = json.load(f)
        used = data.get('used_percentage', 0)
        if used >= 90: print('emergency')
        elif used >= 75: print('rem')
        elif used >= 60: print('pre_sleep')
        elif used >= 40: print('compress')
        else: print('flow')
    except:
        print('flow')
")

    # Auto-checkpoint at pre_sleep or higher
    if [ "$FATIGUE_ACTION" = "pre_sleep" ] || [ "$FATIGUE_ACTION" = "rem" ] || [ "$FATIGUE_ACTION" = "emergency" ]; then
        # Write checkpoint in background (don't block the hook)
        if command -v mnemos &>/dev/null; then
            mnemos checkpoint --force &>/dev/null &
        elif python3 -m mnemos --version &>/dev/null 2>&1; then
            PYTHONPATH=scripts python3 -m mnemos checkpoint --force &>/dev/null &
        fi

        if [ "$FATIGUE_ACTION" = "emergency" ]; then
            FATIGUE_WARNING="EMERGENCY: Context 90%+ full. Checkpoint written. Finish current task and hand off."
        elif [ "$FATIGUE_ACTION" = "rem" ]; then
            FATIGUE_WARNING="WARNING: Context 75%+ full. Checkpoint written. Consider wrapping up."
        else
            FATIGUE_WARNING="NOTICE: Context 60%+ full. Checkpoint written. Keep changes focused."
        fi
    fi

    # Auto-consolidate at compress or higher
    if [ "$FATIGUE_ACTION" = "compress" ] || [ "$FATIGUE_ACTION" = "pre_sleep" ] || [ "$FATIGUE_ACTION" = "rem" ]; then
        if command -v mnemos &>/dev/null; then
            mnemos consolidate &>/dev/null &
        elif python3 -m mnemos --version &>/dev/null 2>&1; then
            PYTHONPATH=scripts python3 -m mnemos consolidate &>/dev/null &
        fi
    fi
fi

# ─── iCPG context ───

CONTEXT=""
CONSTRAINTS=""
DRIFT=""

if command -v icpg &>/dev/null || python3 -m icpg --version &>/dev/null 2>&1; then
    if [ -f ".icpg/reason.db" ]; then
        ICPG_CMD="icpg"
        if ! command -v icpg &>/dev/null; then
            ICPG_CMD="python3 -m icpg"
        fi

        CONTEXT=$($ICPG_CMD query context "$FILE_PATH")
        CONSTRAINTS=$($ICPG_CMD query constraints "$FILE_PATH")
        DRIFT=$($ICPG_CMD drift file "$FILE_PATH")
    fi
fi

# ─── Output ───

HAS_OUTPUT=""
[ -n "$FATIGUE_WARNING" ] && HAS_OUTPUT="1"
[ -n "$CONTEXT" ] && HAS_OUTPUT="1"
[ -n "$CONSTRAINTS" ] && HAS_OUTPUT="1"
[ -n "$DRIFT" ] && HAS_OUTPUT="1"

if [ -n "$HAS_OUTPUT" ]; then
    echo "--- Mnemos + iCPG Context ---"

    if [ -n "$FATIGUE_WARNING" ]; then
        echo "$FATIGUE_WARNING"
        echo ""
    fi

    [ -n "$CONTEXT" ] && echo "$CONTEXT"
    [ -n "$CONSTRAINTS" ] && echo -e "\n$CONSTRAINTS"
    [ -n "$DRIFT" ] && echo -e "\n$DRIFT"

    if [ -n "$CONTEXT" ] || [ -n "$CONSTRAINTS" ]; then
        echo "PRESERVE function signatures unless your task requires changing them."
    fi

    echo "---"
fi

exit 0
