#!/bin/bash
# PreCompact Hook — injects project-specific preservation instructions
# into the compaction summarizer so it keeps what actually matters.
#
# How it works:
#   Claude Code's PreCompact hook runs right before compaction.
#   Stdout from this script becomes custom instructions for the summarizer.
#   Exit 0 = instructions accepted. Exit 2 = block compaction (don't use).
#
# The built-in summarizer uses a generic 9-section template.
# This hook tells it: "for THIS project, prioritize these specific things."

# ─── Detect project context ───

PROJECT_TYPE=""
SCHEMA_FILE=""
TEST_CMD=""
KEY_DIRS=""

# Detect tech stack
if [ -f "package.json" ]; then
    PROJECT_TYPE="javascript"
    if [ -f "tsconfig.json" ]; then
        PROJECT_TYPE="typescript"
    fi
    if grep -q '"next"' package.json 2>/dev/null; then
        PROJECT_TYPE="$PROJECT_TYPE/nextjs"
    elif grep -q '"react"' package.json 2>/dev/null; then
        PROJECT_TYPE="$PROJECT_TYPE/react"
    elif grep -q '"express\|fastify"' package.json 2>/dev/null; then
        PROJECT_TYPE="$PROJECT_TYPE/node-backend"
    fi
    TEST_CMD="npm test"
fi

if [ -f "pyproject.toml" ] || [ -f "setup.py" ]; then
    PROJECT_TYPE="python"
    if grep -q "fastapi" pyproject.toml 2>/dev/null; then
        PROJECT_TYPE="python/fastapi"
    elif grep -q "django" pyproject.toml 2>/dev/null; then
        PROJECT_TYPE="python/django"
    fi
    TEST_CMD="pytest"
fi

if [ -f "pubspec.yaml" ]; then
    PROJECT_TYPE="flutter"
    TEST_CMD="flutter test"
fi

# Find schema files
for f in src/db/schema.ts prisma/schema.prisma drizzle/schema.ts supabase/migrations models.py src/models; do
    if [ -e "$f" ]; then
        SCHEMA_FILE="$f"
        break
    fi
done

# Find key directories
KEY_DIRS=""
for d in src/api src/routes src/app/api api routes server/routes; do
    if [ -d "$d" ]; then
        KEY_DIRS="$KEY_DIRS $d"
    fi
done

# ─── Gather live project state ───

# Git state
GIT_BRANCH=""
GIT_CHANGES=""
if command -v git &>/dev/null && git rev-parse --git-dir &>/dev/null 2>&1; then
    GIT_BRANCH=$(git branch --show-current 2>/dev/null)
    GIT_CHANGES=$(git diff --name-only 2>/dev/null | head -15)
    GIT_STAGED=$(git diff --cached --name-only 2>/dev/null | head -10)
fi

# CLAUDE.md key decisions (if they exist)
KEY_DECISIONS=""
if [ -f "CLAUDE.md" ]; then
    # Extract the Key Decisions section
    KEY_DECISIONS=$(sed -n '/^## Key Decisions/,/^## /p' CLAUDE.md | head -20 | tail -n +2)
fi

# ─── Output custom instructions for the summarizer ───
# Everything sent to stdout becomes additional instructions for the compaction prompt

cat <<INSTRUCTIONS
## Project-Specific Preservation Priorities

This is a $PROJECT_TYPE project. When summarizing, prioritize preserving:

### 1. Architectural Decisions (HIGHEST PRIORITY)
Preserve the EXACT reasoning behind architectural choices, not just the choice itself.
If the conversation discussed why we chose X over Y, keep the "why" verbatim.
INSTRUCTIONS

if [ -n "$KEY_DECISIONS" ]; then
cat <<INSTRUCTIONS

These are the project's settled decisions — reference them by name in the summary:
$KEY_DECISIONS
INSTRUCTIONS
fi

if [ -n "$SCHEMA_FILE" ]; then
cat <<INSTRUCTIONS

### 2. Database Schema Context
Schema file: $SCHEMA_FILE
Preserve ALL discussion about schema changes, column names, relationships,
migration decisions, and data model reasoning. These are expensive to re-derive.
INSTRUCTIONS
fi

if [ -n "$KEY_DIRS" ]; then
cat <<INSTRUCTIONS

### 3. API Contract Details
API directories:$KEY_DIRS
Preserve exact endpoint paths, request/response shapes, status codes,
and validation rules discussed. These affect multiple consumers.
INSTRUCTIONS
fi

cat <<INSTRUCTIONS

### 4. Error Context
When summarizing errors and fixes, preserve:
- The EXACT error message (not paraphrased)
- The file and line number
- What fix was applied and why
- Whether the fix was verified (tests passing)

### 5. Current Work State
INSTRUCTIONS

if [ -n "$GIT_BRANCH" ]; then
    echo "Branch: $GIT_BRANCH"
fi

if [ -n "$GIT_CHANGES" ]; then
cat <<INSTRUCTIONS
Uncommitted changes:
$GIT_CHANGES
INSTRUCTIONS
fi

if [ -n "$GIT_STAGED" ]; then
cat <<INSTRUCTIONS
Staged for commit:
$GIT_STAGED
INSTRUCTIONS
fi

cat <<INSTRUCTIONS

### 6. Test Status
Preserve the last known test state — which tests pass, which fail, what coverage was.
Test command: ${TEST_CMD:-"unknown"}

### 7. What NOT to Summarize
- Don't preserve exploration that led nowhere (dead ends)
- Don't preserve full file contents that can be re-read from disk
- Don't preserve tool result formatting — just the key findings
- Compress repeated test-fix-test cycles into: "Fixed X by doing Y, tests now pass"
INSTRUCTIONS

exit 0
