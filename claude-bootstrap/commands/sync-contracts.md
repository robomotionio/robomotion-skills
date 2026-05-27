# /sync-contracts

> Lightweight incremental update of workspace contracts without full re-analysis.

## Purpose

Fast contract synchronization that:
- Checks only contract source files (not full workspace)
- Updates CONTRACTS.md with changes
- Validates consistency
- Takes ~15 seconds instead of ~2 minutes

## When to Use

| Scenario | Command |
|----------|---------|
| After modifying API endpoints | `/sync-contracts` |
| After changing shared types | `/sync-contracts` |
| Session start shows stale contracts | `/sync-contracts` |
| Post-commit hook (automatic) | `/sync-contracts --lightweight` |
| Before pushing changes | `/sync-contracts --validate` |
| See what changed without updating | `/sync-contracts --diff` |

## Behavior

### Step 1: Load Existing Topology

```
🔄 Loading workspace context...

Workspace: myapp (Monorepo)
Last full analysis: 2026-01-18T10:00:00Z
Last sync: 2026-01-20T14:32:00Z
```

Does NOT re-discover workspace structure - uses existing TOPOLOGY.md.

### Step 2: Check Contract Sources

```
📋 Checking contract sources...

Monitored files (from .contract-sources):
  ✓ apps/api/openapi.json (modified 2h ago)
  ✓ packages/shared-types/src/index.ts (modified 2h ago)
  ○ packages/db/schema/campaigns.ts (unchanged)
  ○ packages/db/schema/users.ts (unchanged)
  ○ apps/api/app/schemas/campaign.py (unchanged)

Changes detected: 2 files
```

### Step 3: Extract Changes

```
📝 Extracting contract changes...

apps/api/openapi.json:
  + POST /api/campaigns/bulk (new endpoint)
  ~ GET /api/campaigns (added 'status' query param)

packages/shared-types/src/index.ts:
  ~ Campaign interface (added 'tags: string[]' field)
  + CampaignBulkCreate interface (new)
```

### Step 4: Update Artifacts

```
✏️  Updating workspace artifacts...

Updated: _project_specs/workspace/CONTRACTS.md
  - Added POST /api/campaigns/bulk to endpoints
  - Updated Campaign type definition
  - Added CampaignBulkCreate type

Updated: _project_specs/workspace/CROSS_REPO_INDEX.md
  - Added bulk create capability

Timestamps updated:
  Last sync: 2026-01-20T16:45:00Z
```

### Step 5: Validate Consistency

```
✅ Validating contract consistency...

Checks:
  ✓ OpenAPI endpoint count matches routes (48/48)
  ✓ All Pydantic models have TypeScript equivalents
  ✓ No orphaned types in shared-types
  ⚠️  Frontend types may need regeneration

Validation: PASSED (1 warning)
```

## Final Output

```
════════════════════════════════════════════════════════════════
  CONTRACT SYNC COMPLETE
════════════════════════════════════════════════════════════════

Sources checked: 5
Changes detected: 2
Files updated: 2

Changes Summary:
  + POST /api/campaigns/bulk (new endpoint)
  ~ Campaign interface (added 'tags' field)
  + CampaignBulkCreate interface (new)

Freshness: 🟢 Fresh
Last sync: 2026-01-20T16:45:00Z

⚠️  Note: Frontend types may need regeneration
   Run: cd apps/web && npm run generate:types

════════════════════════════════════════════════════════════════
```

## Flags

| Flag | Description |
|------|-------------|
| `--lightweight` | Skip validation, minimal output (for hooks) |
| `--diff` | Show changes without updating files |
| `--validate` | Only validate, don't update |
| `--force` | Update even if no changes detected |
| `--verbose` | Show detailed extraction output |

## Diff Mode

Preview changes without applying:

```bash
/sync-contracts --diff
```

Output:

```
📋 Contract Changes (not applied)

apps/api/openapi.json:
  + POST /api/campaigns/bulk
    Request: CampaignBulkCreate[]
    Response: Campaign[]

  ~ GET /api/campaigns
    + query param: status (string, optional)

packages/shared-types/src/index.ts:
  ~ interface Campaign {
      id: string;
      name: string;
  +   tags: string[];        // NEW
      status: CampaignStatus;
    }

  + interface CampaignBulkCreate {
      campaigns: CampaignCreate[];
    }

To apply these changes: /sync-contracts
```

## Validate Mode

Check consistency without updating:

```bash
/sync-contracts --validate
```

Output:

```
🔍 Contract Validation

Endpoint Consistency:
  ✓ OpenAPI spec: 48 endpoints
  ✓ Route files: 48 handlers
  ✓ Match: YES

Type Consistency:
  ✓ Pydantic models: 23
  ✓ TypeScript types: 34
  ✓ Shared types exported: 34
  ⚠️  2 types only in backend (internal)

Cross-Module References:
  ✓ Frontend imports valid types: YES
  ✓ Backend codegen up to date: YES

Overall: ✅ VALID (2 warnings)
```

## Lightweight Mode

For hooks - minimal output, fast execution:

```bash
/sync-contracts --lightweight
```

Output:

```
✓ Contracts synced (2 changes)
```

Or if no changes:

```
✓ Contracts up to date
```

## Contract Sources File

The sync uses `.contract-sources` to know what to check:

```bash
# _project_specs/workspace/.contract-sources
# Auto-generated by /analyze-workspace
# Edit to add/remove monitored files

# OpenAPI specs
apps/api/openapi.json

# Type definitions
packages/shared-types/src/index.ts
packages/shared-types/src/api.ts
packages/shared-types/src/campaign.ts

# Pydantic schemas (Python)
apps/api/app/schemas/campaign.py
apps/api/app/schemas/user.py
apps/api/app/schemas/auth.py

# Database schema
packages/db/schema/campaigns.ts
packages/db/schema/users.ts
```

To add a new source:

```bash
echo "apps/api/app/schemas/new_model.py" >> _project_specs/workspace/.contract-sources
```

## Error Handling

### No Contract Sources

```
⚠️  No contract sources configured

Run /analyze-workspace first to set up contract monitoring.
```

### Source File Missing

```
⚠️  Contract source not found: apps/api/openapi.json

Options:
  1. Generate it: cd apps/api && python -m app.generate_openapi
  2. Remove from monitoring: Edit .contract-sources
  3. Skip this file: /sync-contracts --skip apps/api/openapi.json
```

### Validation Failed

```
❌ Contract validation failed

Issues found:
  1. OpenAPI has 48 endpoints, routes have 47
     Missing: DELETE /api/campaigns/:id (in spec, not in routes)

  2. Type mismatch: Campaign.status
     OpenAPI: "draft" | "active" | "paused"
     TypeScript: "draft" | "active" | "paused" | "archived"

Fix these issues, then run /sync-contracts again.
Or force update: /sync-contracts --force
```

## Integration with Hooks

### Post-Commit Hook

Automatically runs after commits that touch contract sources:

```bash
# hooks/post-commit
CONTRACT_SOURCES=$(cat _project_specs/workspace/.contract-sources 2>/dev/null)
COMMITTED=$(git diff-tree --no-commit-id --name-only -r HEAD)

for source in $CONTRACT_SOURCES; do
  if echo "$COMMITTED" | grep -q "$source"; then
    echo "📝 Contract source changed, syncing..."
    claude --silent "/sync-contracts --lightweight"
    break
  fi
done
```

### Pre-Push Hook

Validates before push:

```bash
# hooks/pre-push
echo "🔍 Validating contracts..."
claude --silent "/sync-contracts --validate"

if [ $? -ne 0 ]; then
  echo "❌ Contract validation failed"
  echo "Run /sync-contracts to fix"
  exit 1
fi
```

## Comparison: sync-contracts vs analyze-workspace

| Aspect | /sync-contracts | /analyze-workspace |
|--------|-----------------|-------------------|
| Time | ~15 seconds | ~2 minutes |
| Scope | Contract files only | Full workspace |
| Discovers new modules | No | Yes |
| Updates TOPOLOGY.md | No | Yes |
| Updates CONTRACTS.md | Yes | Yes |
| Rebuilds dependency graph | No | Yes |
| When to use | Frequent (daily) | Occasional (weekly) |
