#!/bin/bash
# TDD Loop Check - Claude Code Stop hook script
# Runs after each Claude response. Exit 0 = done, Exit 2 = failures fed back to Claude.
#
# Install: copy to scripts/tdd-loop-check.sh in your project
# Configure: add Stop hook in .claude/settings.json (see iterative-development skill)

MAX_ITERATIONS=25
ITERATION_FILE=".claude/.tdd-iteration-count"
mkdir -p .claude

# Track iteration count
if [ -f "$ITERATION_FILE" ]; then
    count=$(cat "$ITERATION_FILE")
    count=$((count + 1))
else
    count=1
fi
echo "$count" > "$ITERATION_FILE"

# Safety: stop after max iterations
if [ "$count" -ge "$MAX_ITERATIONS" ]; then
    rm -f "$ITERATION_FILE"
    echo "Max iterations ($MAX_ITERATIONS) reached. Stopping loop." >&2
    exit 0
fi

# Skip if no test files exist yet
if ! find . -name "*.test.*" -o -name "*.spec.*" -o -name "test_*" | grep -q .; then
    rm -f "$ITERATION_FILE"
    exit 0
fi

# Detect project type and run tests
if [ -f "package.json" ]; then
    TEST_OUTPUT=$(npm test 2>&1) || {
        echo "ITERATION $count/$MAX_ITERATIONS - Tests failing:" >&2
        echo "$TEST_OUTPUT" | tail -30 >&2
        echo "" >&2
        echo "Fix the failing tests and try again." >&2
        exit 2
    }

    # Lint
    if grep -q '"lint"' package.json; then
        LINT_OUTPUT=$(npm run lint 2>&1) || {
            echo "ITERATION $count/$MAX_ITERATIONS - Lint errors:" >&2
            echo "$LINT_OUTPUT" | tail -20 >&2
            exit 2
        }
    fi

    # Typecheck
    if [ -f "tsconfig.json" ]; then
        TYPE_OUTPUT=$(npx tsc --noEmit 2>&1) || {
            echo "ITERATION $count/$MAX_ITERATIONS - Type errors:" >&2
            echo "$TYPE_OUTPUT" | tail -20 >&2
            exit 2
        }
    fi

elif [ -f "pyproject.toml" ] || [ -f "setup.py" ]; then
    TEST_OUTPUT=$(pytest -v 2>&1) || {
        echo "ITERATION $count/$MAX_ITERATIONS - Tests failing:" >&2
        echo "$TEST_OUTPUT" | tail -30 >&2
        exit 2
    }

    if command -v ruff &>/dev/null; then
        LINT_OUTPUT=$(ruff check . 2>&1) || {
            echo "ITERATION $count/$MAX_ITERATIONS - Lint errors:" >&2
            echo "$LINT_OUTPUT" | tail -20 >&2
            exit 2
        }
    fi

    if command -v mypy &>/dev/null; then
        TYPE_OUTPUT=$(mypy . 2>&1) || {
            echo "ITERATION $count/$MAX_ITERATIONS - Type errors:" >&2
            echo "$TYPE_OUTPUT" | tail -20 >&2
            exit 2
        }
    fi
fi

# All green - reset counter
rm -f "$ITERATION_FILE"
exit 0
