#!/bin/bash
# iCPG PreToolUse Hook — injects intent context before Edit/Write operations.
#
# Shows the agent: what intents exist for this file, what invariants apply,
# and the risk profile of symbols being modified.
#
# Install: add to .claude/settings.json under hooks.PreToolUse
# Timeout: 3 seconds max — never blocks

# Skip if icpg not installed or no DB
if ! command -v icpg &>/dev/null && ! python -m icpg --version &>/dev/null 2>&1; then
    exit 0
fi

if [ ! -f ".icpg/reason.db" ]; then
    exit 0
fi

# Extract file path from tool input
# Claude Code passes tool input as JSON via stdin for PreToolUse hooks
FILE_PATH=""
if [ -n "$CLAUDE_TOOL_INPUT" ]; then
    FILE_PATH=$(echo "$CLAUDE_TOOL_INPUT" | python3 -c "
import sys, json
try:
    data = json.load(sys.stdin)
    print(data.get('file_path', data.get('path', '')))
except:
    pass
")
fi

if [ -z "$FILE_PATH" ]; then
    exit 0
fi

# Run icpg binary or module
ICPG_CMD="icpg"
if ! command -v icpg &>/dev/null; then
    ICPG_CMD="python -m icpg"
fi

# Query context, constraints, and drift (file-scoped fast check)
CONTEXT=$($ICPG_CMD query context "$FILE_PATH")
CONSTRAINTS=$($ICPG_CMD query constraints "$FILE_PATH")
DRIFT=$($ICPG_CMD drift file "$FILE_PATH")

# Only output if we have something
if [ -n "$CONTEXT" ] || [ -n "$CONSTRAINTS" ] || [ -n "$DRIFT" ]; then
    echo "═══ iCPG CONTEXT ═══"
    [ -n "$CONTEXT" ] && echo "$CONTEXT"
    [ -n "$CONSTRAINTS" ] && echo -e "\n$CONSTRAINTS"
    [ -n "$DRIFT" ] && echo -e "\n$DRIFT"
    echo "PRESERVE function signatures unless your task requires changing them."
    echo "═══════════════════"
fi

exit 0
