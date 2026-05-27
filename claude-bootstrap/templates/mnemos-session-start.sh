#!/bin/bash
# Mnemos SessionStart Hook — loads checkpoint on session resume.
#
# Checks for .mnemos/checkpoint-latest.json and injects it into context.
# Also bridges iCPG state if available.
#
# Install: add to .claude/settings.json under hooks.SessionStart

# ─── Load checkpoint if exists ───

if [ -f ".mnemos/checkpoint-latest.json" ]; then
    MNEMOS_CMD=""
    if command -v mnemos &>/dev/null; then
        MNEMOS_CMD="mnemos"
    elif python3 -m mnemos --version &>/dev/null 2>&1; then
        MNEMOS_CMD="python3 -m mnemos"
    fi

    if [ -n "$MNEMOS_CMD" ]; then
        RESUME_OUTPUT=$($MNEMOS_CMD resume 2>/dev/null)
        if [ -n "$RESUME_OUTPUT" ]; then
            echo "=== MNEMOS SESSION RESUME ==="
            echo "$RESUME_OUTPUT"
            echo ""
            echo "You are resuming from a previous session checkpoint."
            echo "Review the goal and constraints above before proceeding."
            echo "============================="
        fi
    fi
fi

# ─── Bridge iCPG if available and Mnemos DB exists ───

if [ -f ".icpg/reason.db" ] && [ -f ".mnemos/mnemo.db" ]; then
    MNEMOS_CMD=""
    if command -v mnemos &>/dev/null; then
        MNEMOS_CMD="mnemos"
    elif python3 -m mnemos --version &>/dev/null 2>&1; then
        MNEMOS_CMD="python3 -m mnemos"
    fi

    if [ -n "$MNEMOS_CMD" ]; then
        # Bridge in background — don't block session start
        $MNEMOS_CMD bridge-icpg &>/dev/null &
    fi
fi

# ─── Show iCPG status if available ───

if [ -f ".icpg/reason.db" ]; then
    ICPG_CMD=""
    if command -v icpg &>/dev/null; then
        ICPG_CMD="icpg"
    elif python3 -m icpg --version &>/dev/null 2>&1; then
        ICPG_CMD="python3 -m icpg"
    fi

    if [ -n "$ICPG_CMD" ]; then
        STATUS=$($ICPG_CMD status 2>/dev/null)
        if [ -n "$STATUS" ]; then
            echo ""
            echo "=== iCPG STATUS ==="
            echo "$STATUS"
            echo "==================="
        fi
    fi
fi

exit 0
