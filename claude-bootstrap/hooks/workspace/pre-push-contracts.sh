#!/bin/bash

# Pre-Push Contract Validation Hook
# Validates contract consistency before pushing
# Blocks push if contracts are out of sync
# Run time: ~10 seconds

WORKSPACE_DIR="_project_specs/workspace"

# Colors
RED='\033[0;31m'
YELLOW='\033[1;33m'
GREEN='\033[0;32m'
BLUE='\033[0;34m'
NC='\033[0m'

# Check if workspace is configured
if [ ! -f "$WORKSPACE_DIR/CONTRACTS.md" ]; then
    exit 0
fi

if [ ! -f "$WORKSPACE_DIR/.contract-sources" ]; then
    exit 0
fi

echo ""
echo -e "${BLUE}🔍 Validating workspace contracts...${NC}"

VALIDATION_ERRORS=""
WARNING_COUNT=0
ERROR_COUNT=0

# Get last sync timestamp
LAST_SYNC=$(stat -f %m "$WORKSPACE_DIR/CONTRACTS.md" 2>/dev/null || stat -c %Y "$WORKSPACE_DIR/CONTRACTS.md" 2>/dev/null)

# Check if any contract sources changed since last sync
STALE_SOURCES=""
while IFS= read -r source || [ -n "$source" ]; do
    # Skip comments and empty lines
    [[ "$source" =~ ^#.*$ ]] && continue
    [[ -z "$source" ]] && continue

    if [ -f "$source" ]; then
        SOURCE_MTIME=$(stat -f %m "$source" 2>/dev/null || stat -c %Y "$source" 2>/dev/null)
        if [ "$SOURCE_MTIME" -gt "$LAST_SYNC" ]; then
            STALE_SOURCES="$STALE_SOURCES\n   - $source"
            ERROR_COUNT=$((ERROR_COUNT + 1))
        fi
    else
        VALIDATION_ERRORS="$VALIDATION_ERRORS\n⚠️  Contract source missing: $source"
        WARNING_COUNT=$((WARNING_COUNT + 1))
    fi
done < "$WORKSPACE_DIR/.contract-sources"

# Check OpenAPI consistency (if exists)
if [ -f "apps/api/openapi.json" ] || [ -f "openapi.json" ]; then
    OPENAPI_FILE=$([ -f "apps/api/openapi.json" ] && echo "apps/api/openapi.json" || echo "openapi.json")

    if command -v jq &> /dev/null; then
        ACTUAL_ENDPOINTS=$(jq -r '.paths | keys | length' "$OPENAPI_FILE" 2>/dev/null || echo "0")
        DOCUMENTED_ENDPOINTS=$(grep -cE "^\| (GET|POST|PUT|PATCH|DELETE)" "$WORKSPACE_DIR/CONTRACTS.md" 2>/dev/null || echo "0")

        if [ "$ACTUAL_ENDPOINTS" != "0" ] && [ "$DOCUMENTED_ENDPOINTS" != "0" ]; then
            if [ "$ACTUAL_ENDPOINTS" != "$DOCUMENTED_ENDPOINTS" ]; then
                VALIDATION_ERRORS="$VALIDATION_ERRORS\n⚠️  Endpoint count mismatch: OpenAPI has $ACTUAL_ENDPOINTS, CONTRACTS.md has $DOCUMENTED_ENDPOINTS"
                WARNING_COUNT=$((WARNING_COUNT + 1))
            fi
        fi
    fi
fi

# Report results
if [ "$ERROR_COUNT" -gt 0 ]; then
    echo -e "${RED}❌ Contract sources changed but not synced:${NC}"
    echo -e "$STALE_SOURCES"
    echo ""
    echo -e "${RED}Run /sync-contracts before pushing${NC}"
    echo -e "Or bypass with: ${YELLOW}git push --no-verify${NC}"
    echo ""
    exit 1
fi

if [ "$WARNING_COUNT" -gt 0 ]; then
    echo -e "${YELLOW}⚠️  Validation warnings:${NC}"
    echo -e "$VALIDATION_ERRORS"
    echo ""
    echo -e "${YELLOW}Consider running /sync-contracts${NC}"
    echo ""
    # Warnings don't block push
fi

if [ "$ERROR_COUNT" -eq 0 ]; then
    echo -e "${GREEN}✅ Contracts validated${NC}"
fi

exit 0
