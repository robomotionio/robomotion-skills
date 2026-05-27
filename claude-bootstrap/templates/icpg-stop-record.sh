#!/bin/bash
# iCPG Stop Hook Extension — auto-records symbols after implementation.
#
# Reads .icpg/.current-intent to know which ReasonNode is active.
# If set, records symbols from git diff to that intent.
#
# Chain this AFTER tdd-loop-check.sh in the Stop hook:
#   tdd-loop-check runs first → if tests pass → this records symbols

# Skip if no active intent
CURRENT_INTENT=$(cat .icpg/.current-intent 2>/dev/null)
if [ -z "$CURRENT_INTENT" ]; then
    exit 0
fi

# Skip if icpg not available
ICPG_CMD=""
if command -v icpg &>/dev/null; then
    ICPG_CMD="icpg"
elif python -m icpg --version &>/dev/null 2>&1; then
    ICPG_CMD="python -m icpg"
else
    exit 0
fi

# Record symbols from current diff
OUTPUT=$($ICPG_CMD record --reason "$CURRENT_INTENT" --base main 2>&1)
if [ $? -eq 0 ]; then
    echo "iCPG: $OUTPUT" >&2
fi

exit 0
