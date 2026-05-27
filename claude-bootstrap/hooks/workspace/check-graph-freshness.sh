#!/bin/bash

# Check Graph Freshness - Session Start Advisory
#
# Warns if code graph data is older than the latest commit.
# Run at session start to ensure Claude is working with current data.

GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

# Skip if no graph configured
if [ ! -f ".mcp.json" ] || ! grep -q "codebase-memory" ".mcp.json" 2>/dev/null; then
    exit 0
fi

# Skip if no .code-graph directory (graph not yet built)
if [ ! -d ".code-graph" ]; then
    echo -e "${YELLOW}code-graph: No graph data found. Run index_repository via MCP to build.${NC}"
    exit 0
fi

# Get latest commit timestamp
LATEST_COMMIT=$(git log -1 --format=%ct 2>/dev/null || echo "0")

# Get graph last-updated timestamp (modification time of the DB or marker)
if [ -f ".code-graph/.last-updated" ]; then
    GRAPH_UPDATED=$(cat ".code-graph/.last-updated" 2>/dev/null || echo "0")
elif [ "$(uname)" = "Darwin" ]; then
    # macOS: stat -f %m
    GRAPH_UPDATED=$(stat -f %m ".code-graph/" 2>/dev/null || echo "0")
else
    # Linux: stat -c %Y
    GRAPH_UPDATED=$(stat -c %Y ".code-graph/" 2>/dev/null || echo "0")
fi

# Compare timestamps
DIFF=$((LATEST_COMMIT - GRAPH_UPDATED))

if [ "$DIFF" -gt 300 ]; then
    # More than 5 minutes stale
    MINUTES=$((DIFF / 60))
    echo -e "${YELLOW}code-graph: Graph may be stale (~${MINUTES}m behind latest commit)${NC}"
    echo "  The MCP file watcher should auto-update."
    echo "  If stale, use index_repository to rebuild."
elif [ "$DIFF" -gt 60 ]; then
    # Slightly stale (1-5 minutes) — just a note
    echo -e "${YELLOW}code-graph: Graph is slightly behind latest commit (auto-updating)${NC}"
else
    echo -e "${GREEN}code-graph: Graph data is fresh${NC}"
fi

exit 0
