#!/bin/bash

# Post-Commit Contract Sync Hook
# Automatically syncs contracts when contract source files are committed
# Run time: ~15 seconds (only when contracts change)

WORKSPACE_DIR="_project_specs/workspace"

# Colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

# Check if workspace is configured
if [ ! -f "$WORKSPACE_DIR/.contract-sources" ]; then
    exit 0
fi

# Get list of committed files
COMMITTED_FILES=$(git diff-tree --no-commit-id --name-only -r HEAD 2>/dev/null)

if [ -z "$COMMITTED_FILES" ]; then
    exit 0
fi

# Check if any committed files are contract sources
CONTRACTS_CHANGED=false
CHANGED_SOURCES=""

while IFS= read -r source || [ -n "$source" ]; do
    # Skip comments and empty lines
    [[ "$source" =~ ^#.*$ ]] && continue
    [[ -z "$source" ]] && continue

    if echo "$COMMITTED_FILES" | grep -q "$source"; then
        CONTRACTS_CHANGED=true
        CHANGED_SOURCES="$CHANGED_SOURCES $source"
    fi
done < "$WORKSPACE_DIR/.contract-sources"

# If contracts changed, run lightweight sync
if [ "$CONTRACTS_CHANGED" = true ]; then
    echo ""
    echo -e "${YELLOW}📝 Contract files changed in this commit:${NC}"
    for src in $CHANGED_SOURCES; do
        echo "   - $src"
    done
    echo ""

    # Check if Claude CLI is available
    if command -v claude &> /dev/null; then
        echo -e "${BLUE}⚡ Running lightweight contract sync...${NC}"

        # Run sync in silent/lightweight mode
        if claude --print "/sync-contracts --lightweight" > /dev/null 2>&1; then
            echo -e "${GREEN}✅ Contracts synced${NC}"
        else
            echo -e "${YELLOW}⚠️  Contract sync failed - run /sync-contracts manually${NC}"
        fi
    else
        echo -e "${YELLOW}⚠️  Claude CLI not found${NC}"
        echo "   Run /sync-contracts manually to update contracts"
    fi
    echo ""
fi

exit 0
