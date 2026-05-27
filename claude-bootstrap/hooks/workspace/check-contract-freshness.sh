#!/bin/bash

# Contract Freshness Check - Session Start Hook
# Checks if workspace contracts are stale and advises user
# Run time: ~5 seconds

WORKSPACE_DIR="_project_specs/workspace"
STALENESS_THRESHOLD=86400  # 24 hours in seconds
WARNING_THRESHOLD=604800   # 7 days in seconds

# Colors
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
GREEN='\033[0;32m'
RED='\033[0;31m'
NC='\033[0m'

# Check if workspace is configured
if [ ! -f "$WORKSPACE_DIR/CONTRACTS.md" ]; then
    # No workspace configured - silent exit
    exit 0
fi

if [ ! -f "$WORKSPACE_DIR/.contract-sources" ]; then
    echo -e "${YELLOW}⚠️  Workspace configured but no contract sources defined${NC}"
    echo "   Run /analyze-workspace to set up contract monitoring"
    exit 0
fi

# Get last analysis timestamp
LAST_ANALYSIS=$(stat -f %m "$WORKSPACE_DIR/CONTRACTS.md" 2>/dev/null || stat -c %Y "$WORKSPACE_DIR/CONTRACTS.md" 2>/dev/null)
NOW=$(date +%s)
AGE=$((NOW - LAST_ANALYSIS))

# Check for stale analysis
if [ "$AGE" -gt "$WARNING_THRESHOLD" ]; then
    DAYS=$((AGE / 86400))
    echo -e "${RED}📅 Workspace contracts are ${DAYS} days old${NC}"
    echo "   Run /analyze-workspace for full refresh"
    echo ""
fi

# Check if any contract sources changed since last sync
CHANGED_FILES=""
CHANGED_COUNT=0

while IFS= read -r source || [ -n "$source" ]; do
    # Skip comments and empty lines
    [[ "$source" =~ ^#.*$ ]] && continue
    [[ -z "$source" ]] && continue

    if [ -f "$source" ]; then
        SOURCE_MTIME=$(stat -f %m "$source" 2>/dev/null || stat -c %Y "$source" 2>/dev/null)
        if [ "$SOURCE_MTIME" -gt "$LAST_ANALYSIS" ]; then
            CHANGED_FILES="$CHANGED_FILES\n  - $source"
            CHANGED_COUNT=$((CHANGED_COUNT + 1))
        fi
    fi
done < "$WORKSPACE_DIR/.contract-sources"

# Report changes
if [ "$CHANGED_COUNT" -gt 0 ]; then
    echo -e "${YELLOW}🔄 Contract sources changed since last sync:${NC}"
    echo -e "$CHANGED_FILES"
    echo ""
    echo -e "   Run ${BLUE}/sync-contracts${NC} to update"
    echo ""
elif [ "$AGE" -gt "$STALENESS_THRESHOLD" ]; then
    HOURS=$((AGE / 3600))
    echo -e "${YELLOW}📅 Last contract sync: ${HOURS} hours ago${NC}"
    echo -e "   Consider running ${BLUE}/sync-contracts${NC}"
    echo ""
else
    # Fresh - silent success
    :
fi

exit 0
