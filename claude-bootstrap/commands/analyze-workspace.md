# /analyze-workspace

> Full dynamic analysis of workspace topology, dependencies, and contracts.

## Trigger

Run this command when:
- First time setting up workspace awareness
- Major refactor or new module added
- Weekly scheduled refresh
- `/sync-contracts` reports too much drift
- Switching to work on a different workspace

## Behavior

### Phase 1: Topology Discovery (~30 seconds)

```
🔍 Analyzing workspace topology...

Checking workspace indicators:
  ✓ Found turbo.json (Turborepo)
  ✓ Found pnpm-workspace.yaml
  ✗ No nx.json
  ✗ No lerna.json

Workspace type: Monorepo (Turborepo)
Root: /Users/ali/code/myapp

Discovering modules...
  ✓ apps/web (package.json found)
  ✓ apps/api (pyproject.toml found)
  ✓ packages/shared-types (package.json found)
  ✓ packages/db (package.json found)

Modules found: 4
```

### Phase 2: Module Analysis (~60 seconds)

For each module, analyze:

```
📦 Analyzing apps/web...
  Tech stack: Next.js 14, TypeScript, TailwindCSS
  Entry point: src/app/layout.tsx
  Key directories: src/lib/, src/components/, src/types/
  Dependencies: @repo/shared-types, @repo/ui
  External calls: fetch → apps/api (15 files)
  Token estimate: 18K full, 5K summarized

📦 Analyzing apps/api...
  Tech stack: FastAPI, Python 3.12, SQLAlchemy
  Entry point: app/main.py
  Key directories: app/routes/, app/schemas/, app/models/
  Dependencies: packages/db (internal)
  Exposes: OpenAPI spec (47 endpoints)
  Token estimate: 24K full, 7K summarized

📦 Analyzing packages/shared-types...
  Tech stack: TypeScript
  Entry point: src/index.ts
  Exports: 34 types
  Consumed by: apps/web, apps/api (codegen)
  Token estimate: 3K

📦 Analyzing packages/db...
  Tech stack: Drizzle ORM, TypeScript
  Entry point: src/index.ts
  Tables: 12
  Migrations: 23
  Token estimate: 8K full, 2K schema only
```

### Phase 3: Contract Extraction (~45 seconds)

```
📜 Extracting contracts...

OpenAPI Detection:
  ✓ apps/api/openapi.json (47 endpoints, 23 schemas)

GraphQL Detection:
  ✗ No GraphQL schemas found

TypeScript Types:
  ✓ packages/shared-types/src/index.ts (34 exports)

Pydantic Schemas:
  ✓ apps/api/app/schemas/ (23 models)

Database Schema:
  ✓ packages/db/schema/ (12 tables)

Contract sources registered: 5 files
```

### Phase 4: Dependency Graph (~30 seconds)

```
🔗 Building dependency graph...

Internal dependencies:
  apps/web → packages/shared-types (23 imports)
  apps/web → apps/api (15 API calls)
  apps/api → packages/db (12 imports)
  apps/api → packages/shared-types (codegen)
  packages/db → (none)
  packages/shared-types → (none)

Dependency order (for changes):
  1. packages/shared-types (leaf)
  2. packages/db (leaf)
  3. apps/api (depends on db, shared-types)
  4. apps/web (depends on api, shared-types)
```

### Phase 5: Key File Identification (~30 seconds)

```
📁 Identifying key files...

High priority (always relevant):
  ✓ apps/api/openapi.json
  ✓ packages/shared-types/src/index.ts
  ✓ apps/web/src/lib/api/client.ts

Context-specific:
  ✓ API work: apps/api/app/routes/*.py
  ✓ DB work: packages/db/schema/*.ts
  ✓ Auth work: apps/api/app/routes/auth.py + deps
  ✓ Frontend: apps/web/src/components/**

Token budget by context:
  Frontend API: ~8K tokens
  Backend endpoints: ~12K tokens
  Database changes: ~6K tokens
  Shared types: ~4K tokens
```

### Phase 6: Generate Artifacts

```
📝 Generating workspace artifacts...

Created:
  ✓ _project_specs/workspace/TOPOLOGY.md
  ✓ _project_specs/workspace/CONTRACTS.md
  ✓ _project_specs/workspace/DEPENDENCY_GRAPH.md
  ✓ _project_specs/workspace/KEY_FILES.md
  ✓ _project_specs/workspace/CROSS_REPO_INDEX.md
  ✓ _project_specs/workspace/.contract-sources
```

## Final Output

```
════════════════════════════════════════════════════════════════
  WORKSPACE ANALYSIS COMPLETE
════════════════════════════════════════════════════════════════

Workspace: myapp
Type: Monorepo (Turborepo)
Modules: 4 (2 apps, 2 packages)

┌─────────────────────────────────────────────────┐
│ apps/web (Next.js) ←──── apps/api (FastAPI)     │
│      │                        │                 │
│      ▼                        ▼                 │
│ packages/shared-types    packages/db            │
└─────────────────────────────────────────────────┘

Contracts:
  REST API: 47 endpoints
  Shared types: 34 interfaces
  DB tables: 12

Token Estimates:
  Current module only: ~20K tokens
  With cross-module context: ~45K tokens
  Full workspace: ~53K tokens
  Budget remaining: ~100K tokens ✓

Artifacts generated in: _project_specs/workspace/

Next steps:
  • Contracts will auto-sync on commit (if changed)
  • Run /sync-contracts manually to refresh
  • Run /workspace-status for quick check

════════════════════════════════════════════════════════════════
```

## Flags

| Flag | Description |
|------|-------------|
| `--force` | Regenerate all artifacts even if recent |
| `--type <type>` | Override auto-detection: `monorepo`, `multi-repo`, `hybrid` |
| `--repos <paths>` | For multi-repo: comma-separated paths to related repos |
| `--skip-contracts` | Skip contract extraction (faster) |
| `--verbose` | Show detailed analysis output |
| `--json` | Output as JSON (for tooling) |

## Multi-Repo Mode

For workspaces with separate git repositories:

```bash
# Auto-detect sibling repos
/analyze-workspace --type multi-repo

# Specify repo locations explicitly
/analyze-workspace --type multi-repo --repos "../backend,../shared,../mobile"
```

Claude will:
1. Detect related repos in parent directory
2. Set up symlinks in `.workspace/repos/` if needed
3. Analyze each repo
4. Build cross-repo dependency graph
5. Extract contracts from each

## Integration Points

### On First Run

Creates the full workspace context structure:

```
_project_specs/
└── workspace/
    ├── TOPOLOGY.md
    ├── CONTRACTS.md
    ├── DEPENDENCY_GRAPH.md
    ├── KEY_FILES.md
    ├── CROSS_REPO_INDEX.md
    ├── .contract-sources
    └── cache/              # Cached cross-repo files
```

### Updates CLAUDE.md

Adds workspace skill reference:

```markdown
## Skills
- .claude/skills/workspace.md
```

### Sets Up Hooks

Installs contract freshness hooks:
- Session start: Staleness check
- Post-commit: Auto-sync trigger
- Pre-push: Validation gate

## Error Handling

### No Workspace Detected

```
⚠️  No workspace configuration detected

This appears to be a single-repo project.
Use /analyze-repo for single repository analysis.

Or specify workspace type manually:
  /analyze-workspace --type monorepo
  /analyze-workspace --type multi-repo --repos "../other-repo"
```

### Access Denied to Related Repo

```
⚠️  Cannot access related repository: ../backend

Options:
  1. Ensure the repo exists at that path
  2. Create symlink: ln -s /path/to/backend .workspace/repos/backend
  3. Skip this repo: /analyze-workspace --skip-repo backend
```

### Contract Extraction Failed

```
⚠️  Failed to extract contracts from apps/api

Reason: openapi.json not found

Suggestions:
  1. Generate OpenAPI spec: cd apps/api && python -m app.generate_openapi
  2. Skip contract extraction: /analyze-workspace --skip-contracts
  3. Use inferred contracts: /analyze-workspace --infer-contracts
```

## When to Re-run

| Scenario | Action |
|----------|--------|
| Added new module/package | Full `/analyze-workspace` |
| Changed API endpoints | `/sync-contracts` (lightweight) |
| Major refactor | Full `/analyze-workspace --force` |
| Weekly maintenance | Full `/analyze-workspace` |
| Quick check | `/workspace-status` |
