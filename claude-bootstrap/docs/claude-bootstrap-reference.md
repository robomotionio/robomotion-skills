# Claude Bootstrap — Full Reference

## TDD Loops via Stop Hooks

No plugins. No fake commands. Claude Code's Stop hook runs a script when Claude finishes a response. Exit code 2 feeds stderr back to Claude and continues the conversation.

```
┌─────────────────────────────────────────────────────────────┐
│  1. You say: "Add email validation to signup"               │
│  2. Claude writes tests + implementation                    │
│  3. Claude finishes response                                │
│  4. Stop hook runs: npm test && npm run lint                │
│  5a. All pass (exit 0) → Done!                              │
│  5b. Failures (exit 2) → stderr fed back to Claude          │
│  6. Claude sees failures, fixes, finishes again             │
│  7. Stop hook runs again → repeat until green               │
└─────────────────────────────────────────────────────────────┘
```

**Configuration** in `.claude/settings.json`:

```json
{
  "hooks": {
    "Stop": [{
      "hooks": [{
        "type": "command",
        "command": "scripts/tdd-loop-check.sh",
        "timeout": 60,
        "statusMessage": "Running tests..."
      }]
    }]
  }
}
```

The `tdd-loop-check.sh` script runs tests, lint, and typecheck. It tracks iteration count (max 25) and distinguishes code errors (loop) from environment errors (stop).

## @include Directives

CLAUDE.md uses `@include` to modularly load skills:

```markdown
# CLAUDE.md
@.claude/skills/base/SKILL.md
@.claude/skills/iterative-development/SKILL.md
@.claude/skills/security/SKILL.md
```

These are **resolved at load time** by Claude Code — the content is recursively inlined (max depth 5, cycle detection built in).

## Conditional Rules

Rules in `.claude/rules/` use YAML frontmatter with `paths:` to activate only when relevant files are being edited:

```yaml
# .claude/rules/react.md
---
paths: ["src/components/**", "**/*.tsx"]
---
Prefer functional components with hooks...
```

**Included rules:**

| Rule | Activates When |
|------|----------------|
| `quality-gates.md` | Always (no paths: filter) |
| `tdd-workflow.md` | Always |
| `security.md` | Always |
| `react.md` | Editing .tsx/.jsx files |
| `typescript.md` | Editing .ts/.tsx files |
| `python.md` | Editing .py files |
| `nodejs-backend.md` | Editing api/routes/server files |

## PreCompact Hook (Smarter Compaction)

Claude Code's built-in compaction fires at ~83% context and summarizes everything into 20K tokens using a generic template. The PreCompact hook injects **project-specific preservation priorities** into the summarizer.

The hook auto-detects:
- **Project type** (TypeScript/Next.js, Python/FastAPI, Flutter, etc.)
- **Schema files** (Drizzle, Prisma, SQLAlchemy) → preserves schema discussion
- **API directories** → preserves endpoint paths and contracts
- **Key Decisions from CLAUDE.md** → references them by name
- **Git state** → injects branch, uncommitted changes, staged files

## Mnemos — Task-Scoped Memory

Claude Code's built-in compaction is lossy and unreliable. Mnemos provides **disk-persistent structured state** that survives crashes, restarts, and compaction failures.

### Typed Node Eviction

| Node Type | Eviction Policy | Example |
|-----------|----------------|---------|
| GoalNode | NEVER evict | "Implement auth module" |
| ConstraintNode | NEVER evict | "API backward compatibility" |
| ResultNode | Compress first | "JWT middleware tested" → summary kept |
| WorkingNode | Compress first | Current reasoning / in-progress analysis |
| ContextNode | Evictable | File contents → re-read from disk |

### Post-Compaction Restoration (Two-Layer Defense)

**Layer 1** (best-effort): PreCompact tells the summarizer what to keep, including inline checkpoint content with typed eviction priorities.

**Layer 2** (guaranteed): Post-compaction injection via PreToolUse re-injects the full checkpoint on the first tool call after compaction.

### Fatigue Model

4 dimensions passively observed from hooks:

| Dimension | Weight | Signal Source | Detects |
|-----------|--------|---------------|---------|
| Token utilization | 0.40 | Statusline JSON | How full the context window is |
| Scope scatter | 0.25 | PreToolUse file paths | Agent bouncing between directories |
| Re-read ratio | 0.20 | PreToolUse Read calls | Agent re-reading files (context loss) |
| Error density | 0.15 | PostToolUse outcomes | Agent struggling (high error rate) |

Fatigue states: **FLOW** (0-0.4) → **COMPRESS** (0.4-0.6) → **PRE-SLEEP** (0.6-0.75) → **REM** (0.75-0.9) → **EMERGENCY** (0.9+).

### CLI

```bash
mnemos init                    # Initialize .mnemos/
mnemos status                  # Node counts + fatigue
mnemos fatigue                 # Detailed 4-dimension breakdown
mnemos checkpoint --force      # Write checkpoint now
mnemos resume                  # Output checkpoint for session inject
mnemos add goal "Build auth"   # Create a GoalNode
mnemos bridge-icpg             # Import iCPG ReasonNodes
```

**Overhead:** ~5ms per tool call (fast path), 84KB on disk.

## iCPG — Intent-Augmented Code Property Graph

iCPG tracks *why* code exists, not just what it does. Every code change is linked to a ReasonNode that captures the intent, postconditions, and invariants.

```bash
icpg create "Implement auth" --scope src/auth/
icpg record src/auth/middleware.ts
icpg query constraints src/auth/middleware.ts
icpg drift
icpg bootstrap
```

**Pre-Task Queries** (injected automatically via PreToolUse hook):
- `icpg query context <file>` — What intents touch this file?
- `icpg query constraints <file>` — What invariants must hold?
- `icpg drift file <file>` — Has this file drifted from its intent?

**6-Dimension Drift Detection:** spec drift, decision drift, ownership drift, test drift, usage drift, dependency drift.

## Agent Teams

Every project runs as a coordinated team of AI agents with proper frontmatter:

```yaml
# .claude/agents/team-lead.md
---
name: team-lead
description: Orchestrates the agent team
model: sonnet
tools: [Read, Glob, Grep, TaskCreate, TaskUpdate, TaskList, TaskGet, SendMessage]
disallowedTools: [Write, Edit, Bash]
maxTurns: 50
effort: high
---
```

**Default Team:**

| Agent | Role | Can Edit Code? |
|-------|------|----------------|
| **Team Lead** | Orchestrates, assigns tasks | No |
| **Quality Agent** | Verifies RED/GREEN TDD phases | No |
| **Security Agent** | OWASP scanning, secrets detection | No |
| **Code Review Agent** | Multi-engine reviews | No |
| **Merger Agent** | Creates feature branches and PRs | No |
| **Feature Agent (x N)** | Follows strict TDD pipeline | Yes |

**Pipeline:** Spec → Spec Review → Tests → RED Verify → Implement → GREEN Verify → Validate → Code Review → Security → Branch+PR

## Cross-Agent Intelligence

### Codex Auto-Review (Stop Hook)

After tests pass, Codex automatically reviews your diff:

```
Stop hook order:
1. tdd-loop-check.sh     → tests pass?
2. codex-auto-review.sh  → Codex reviews diff
3. icpg-stop-record.sh   → record symbols
4. mnemos-checkpoint.sh   → save memory
```

### Kimi Delegation (Token Optimization)

| Blast Radius | Claude's Action |
|-------------|----------------|
| 1-3 files | Delegates to Kimi automatically |
| 4-8 files | Asks user, then delegates or handles |
| 9+ files | Handles directly (needs full context) |

## P2P Mesh Network

Multi-node session sync and handoff across machines. Each Maggy instance is a mesh peer.

| Component | What it does |
|-----------|-------------|
| **Peer Discovery** | Registry of known peers |
| **Git Discovery** | Auto-discovers peers from shared git remotes |
| **WebSocket Server/Client** | Bidirectional real-time communication |
| **Mesh Protocol** | 7 message types: hello, share, request, response, quarantine, promote, heartbeat |
| **Quarantine** | Untrusted data quarantined until reviewed |
| **Org Scoping** | Peers filtered by org key |

## Pre-configured Permissions

`.claude/settings.json` includes permission rules:

```json
{
  "permissions": {
    "allow": [
      "Bash(npm test *)", "Bash(pytest *)",
      "Bash(git status *)", "Bash(gh pr *)"
    ],
    "deny": [
      "Bash(rm -rf *)", "Bash(git push --force *)",
      "Write(.env)", "Write(.env.*)"
    ]
  }
}
```

## Directory Structure

```
your-project/
├── .claude/
│   ├── agents/               # Agent definitions with frontmatter
│   ├── rules/                # Conditional rules (paths: frontmatter)
│   ├── skills/               # Skills loaded via @include
│   └── settings.json         # Permissions + hooks + statusline
├── scripts/
│   ├── tdd-loop-check.sh     # Stop hook script for TDD loops
│   ├── icpg/                 # Intent-Augmented Code Property Graph
│   └── mnemos/               # Task-Scoped Memory Lifecycle
├── .mnemos/                  # Mnemos state (auto-created, gitignored)
├── .github/workflows/
│   ├── quality.yml
│   └── security.yml
├── _project_specs/
├── CLAUDE.md                 # @include directives, project context
└── CLAUDE.local.md           # Private developer overrides (gitignored)
```

## Skills Catalog (62 Skills)

### Core
| Skill | Purpose |
|-------|---------|
| `base.md` | Universal patterns, constraints, TDD workflow, atomic todos |
| `iterative-development.md` | TDD loops via Stop hooks |
| `mnemos.md` | Task-scoped memory lifecycle |
| `icpg.md` | Intent-augmented code property graph |
| `code-review.md` | Mandatory code reviews (Claude, Codex, Gemini) |
| `codex-review.md` | OpenAI Codex CLI code review |
| `gemini-review.md` | Google Gemini CLI code review |
| `workspace.md` | Multi-repo workspace awareness |
| `commit-hygiene.md` | Atomic commits, PR size limits |
| `code-deduplication.md` | Prevent semantic duplication |
| `agent-teams.md` | Agent team workflow |
| `ticket-craft.md` | AI-native ticket writing |
| `maggy.md` | Local AI command center |
| `team-coordination.md` | Multi-person projects, handoffs |
| `code-graph.md` | Persistent code graph via MCP |
| `cpg-analysis.md` | Deep CPG analysis (Joern + CodeQL) |
| `security.md` | OWASP patterns, secrets management |
| `credentials.md` | Centralized API key management |
| `session-management.md` | Context preservation, resumability |
| `project-tooling.md` | gh, vercel, supabase CLI + deployment |
| `existing-repo.md` | Analyze existing repos |
| `cross-agent-delegation.md` | Cross-agent routing (Codex review, Kimi delegation) |
| `polyphony.md` | Multi-agent container orchestration |

### Language & Framework
`python.md` · `typescript.md` · `nodejs-backend.md` · `react-web.md` · `react-native.md` · `android-java.md` · `android-kotlin.md` · `flutter.md`

### UI
`ui-web.md` · `ui-mobile.md` · `ui-testing.md` · `playwright-testing.md` · `user-journeys.md` · `pwa-development.md`

### Database & Backend
`database-schema.md` · `supabase.md` · `supabase-nextjs.md` · `supabase-python.md` · `supabase-node.md` · `firebase.md` · `cloudflare-d1.md` · `aws-dynamodb.md` · `aws-aurora.md` · `azure-cosmosdb.md`

### AI & Agentic
`agentic-development.md` · `llm-patterns.md` · `ai-models.md`

### Content, Integration & Other
`aeo-optimization.md` · `web-content.md` · `site-architecture.md` · `web-payments.md` · `reddit-api.md` · `reddit-ads.md` · `ms-teams-apps.md` · `posthog-analytics.md` · `shopify-apps.md` · `woocommerce.md` · `medusa.md` · `klaviyo.md`

## Evolution

| Version | Date | What Changed |
|---------|------|-------------|
| **v1.0** | Jan 2026 | 30+ skills, `/initialize-project`, TDD via Ralph Wiggum loops |
| **v2.0** | Jan 2026 | Skills restructured, YAML frontmatter, 60+ skills |
| **v3.0** | Mar 2026 | Stop hooks, `@include`, conditional rules, agent teams |
| **v3.3** | Apr 2026 | Mnemos, iCPG, Maggy dashboard MVP |
| **v3.5** | Apr 2026 | PreCompact hook, fatigue model, hook resilience |
| **v3.6** | May 2026 | Cross-tool compatibility (Claude + Kimi + Codex) |
| **v4.0** | May 2026 | Polyphony — container-isolated multi-agent orchestration |
| **v5.0** | May 2026 | Autonomous command center — Chat, P2P Mesh, process intelligence |
