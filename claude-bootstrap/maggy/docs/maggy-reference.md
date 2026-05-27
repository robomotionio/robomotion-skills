# Maggy — Full Reference

## CLI Commands

| Command | Description |
|---------|-------------|
| `maggy` | Interactive REPL (auto-detects project) or starts dashboard |
| `maggy serve` | Start server + web dashboard |
| `maggy chat <project>` | Chat with a specific project |
| `maggy status` | Server health and config summary |
| `maggy inbox [--refresh]` | AI-ranked task inbox |
| `maggy sessions` | List active AI sessions |
| `maggy execute <task-id>` | Run TDD pipeline on a task |
| `maggy execute <task-id> --plan` | Plan mode (no code changes) |
| `maggy spawn <task>` | Spawn a background AI session |
| `maggy ps` | List all managed sessions |
| `maggy kill <session-id>` | Stop a managed session |
| `maggy route <blast> [--type bug]` | Get routing decision for a complexity score |
| `maggy budget` | Per-provider token budget |
| `maggy models` | Model performance heatmap |
| `maggy competitors [--briefing]` | Competitor intelligence |
| `maggy process <project>` | Process health for a project |
| `maggy config` | Show current config (redacted) |

All commands accept `--json` for machine-readable output.

## REPL Slash Commands

Inside the interactive chat:

| Command | Description |
|---------|-------------|
| `/stats` | Budget + model performance summary |
| `/budget` | Per-provider spend breakdown |
| `/route` | Routing rules and model strengths |
| `/models` | Reward heatmap (model x task type x blast tier) |
| `/use claude,codex` | Restrict to specific models this session |
| `/use all` | Remove model restriction |
| `/health` | Memory health + Mnemos fatigue |
| `/config` | Configuration summary |
| `/screenshot <path> [prompt]` | Analyze image via Qwen3-VL |
| `/claude-md` | Render project's CLAUDE.md |
| `/help` | List all commands |

## Routing Details

Every message gets a **semantic blast score** (1-10) via the local Ollama model, then routes to the cheapest model that can handle it:

| Blast Score | Tier | Models |
|-------------|------|--------|
| 0-3 | Low | Local (Qwen3-Coder), Kimi |
| 4-6 | Medium | Codex, Kimi |
| 7-10 | High | Claude, Codex |

**Semantic blast score** — the local Ollama model rates task complexity (1-10) semantically instead of keyword matching. Understands nuance: "refactor the entire auth system" → 8, "fix the typo in README" → 2. Falls back to keyword heuristics when Ollama is down.

**Semantic intent classification** — same local model classifies task type (review, security, search, docs, tests, frontend) for routing specialization. Falls back to keywords when Ollama is down.

**Inline model forcing** — type "use claude" / "use codex" / "use kimi" / "use local" anywhere in your message to override routing. The directive is stripped before sending to the model.

**Ghost-text suggestions** — after each response, the chat input shows a context-aware suggestion in gray (like Claude Code). Press Tab to accept. Suggestions are based on the last 10 messages and recent response content.

The router learns from outcomes — every completed task records a reward that shifts future routing decisions. Security-sensitive tasks always route to premium models.

## Configuration

Full `~/.maggy/config.yaml` example:

```yaml
org:
  name: "Acme Corp"
  domain: "fintech"

issue_tracker:
  provider: "github"
  github:
    org: "acmecorp"
    repos: ["acmecorp/api", "acmecorp/web"]

codebases:
  - { path: "~/dev/acmecorp/api", key: "api" }
  - { path: "~/dev/acmecorp/web", key: "web" }

competitors:
  categories: ["fintech", "embedded-finance"]

budget:
  plan: "subscription"  # or set daily_limit_usd: 10.0

dashboard:
  host: "127.0.0.1"
  port: 8080

mesh:
  enabled: true
  port: 8080
  orgs: ["my-team"]
  git_discovery: true
  share_interval: 600
```

## Dashboard Tabs

| Group | Tabs | Purpose |
|-------|------|---------|
| **Work** | Chat, Tasks, Watching | Do things — chat with Claude, triage issues |
| **Intel** | Competitors, Insights | Learn things — competitor news, session analytics |
| **System** | Budget, Models, Forge, Settings | Configure — spend limits, model routing, MCP gaps |

Chat is the default tab — auto-connects to all running CLI sessions on load.

## Architecture

- **Provider abstraction** — `IssueTrackerProvider` Protocol (GitHub, Asana)
- **Multi-model routing** — semantic blast-score + intent classification + reward learning across 4 tiers
- **Polyphony orchestration** — parallel container execution for complex tasks (blast>=7)
- **Config-driven** — zero hardcoded IDs, orgs, or competitor lists
- **iCPG integration** — context enrichment from code property graph
- **Engram memory** — SQLite-backed persistent memory with amnesia diagnostics
- **SQLite-first** — single-user local install, zero infrastructure
- **Auto-bootstrap** — all services seed on startup, no empty tabs

See [architecture-v5.md](./architecture-v5.md) for the full architecture reference.

## Hardening

- **Working dir whitelist** — Execute and Chat validate paths against configured codebase roots
- **Chat streaming lock** — per-session `asyncio.Lock` prevents concurrent subprocess spawning
- **SSRF protection** — RSS/blog feed URLs validated before fetch (blocks loopback, private-network)
- **Host-safety check** — refuses to bind to non-loopback with local auth mode
- **Process lifecycle** — Claude subprocesses killed on timeout; non-zero exits marked failed
- **Input validation** — execute mode `Literal["tdd", "plan"]`; malformed IDs return 404

## Subsystems

| Subsystem | Purpose |
|-----------|---------|
| **CIKG** | Code Intelligence Knowledge Graph — codebase nodes, technology detection |
| **Forge** | MCP capability gap detection — suggests tools to fill gaps |
| **History** | CLI session history parsers for Claude, Codex, Kimi |
| **Improve** | Self-improvement — signal collection, health scoring |
| **Budget** | Daily token spend limits with per-provider breakdown |
| **Model Router** | Reward-based heatmap for model selection by task type |
| **Heartbeat** | Scheduled jobs — history refresh, engram expiry, mesh sync |
| **Engram** | Persistent memory with typed records, namespace isolation |
| **Event Spine** | Structured event emission and querying across all services |
| **P2P Mesh** | Multi-node session sync via WebSocket, org-scoped |
