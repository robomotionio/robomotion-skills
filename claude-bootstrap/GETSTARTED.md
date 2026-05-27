# Maggy + Claude Bootstrap — AI Agent Quick Start

> **For Claude Code, Codex CLI, and Gemini CLI agents.** Read this first before working on this codebase.

## What This Project Is

Maggy is an autonomous AI engineering command center. It routes tasks across 10 AI models, manages memory persistence, tracks competitors, and orchestrates the full development lifecycle. Claude Bootstrap is the scaffolding — skills, hooks, rules — that makes Claude Code reliable.

**Key numbers:** 10-tier routing, 62+ skills, 96 files in core, ~7K lines. You're reading this because an AI agent needs context fast.

## Architecture (1 minute)

```
maggy/
├── maggy/                    # Main Python package (FastAPI)
│   ├── api/                  # REST routes (routes_*.py — 30+ files)
│   ├── process/              # Model routing (model_router.py — core)
│   ├── services/             # Business logic (ai_client, executor, chat, etc.)
│   ├── mnemos/               # Memory lifecycle — typed nodes, fatigue tracking
│   ├── plugins/              # Plugin manager + built-in plugins
│   ├── adapters/             # PiAdapter (model delegation), CLI discovery
│   ├── heartbeat/            # Background jobs (inbox, competitors, research)
│   └── static/               # Dashboard UI (index.html + app.js)
├── plugins/                  # User-installable plugins (build-in-public)
├── skills/                   # 62 skill definitions (Markdown + YAML)
├── hooks/                    # Claude Code hooks (route-task, auto-review, etc.)
├── bin/                      # Delegation scripts (deepseek, gemini-api, grok, etc.)
├── commands/                 # Slash commands (/initialize-project, /build-in-public)
├── templates/                # CLAUDE.md + hook templates
├── docs/                     # Documentation + generated images
└── CHANGELOG.md              # Version history (6.14 → 6.25+)
```

## Commands You Need

```bash
# Run Maggy dashboard
cd maggy && python3 -m maggy.main
# or: maggy serve

# Run tests (always do this before modifying routing)
cd maggy && python3 -m pytest tests/test_deepseek_routing.py tests/test_routing_service.py -v

# Lint
cd maggy && ruff check .

# Install locally
cd maggy && pip install -e ".[dev]"

# Check build-in-public status
build-in-public-status maggy --live

# Check cross-model usage
maggy-usage --week

# Research a competitor
~/bin/grok "What is Mem0's latest feature launch?"

# Schedule a post manually
~/.claude/hooks/plugin-trigger on_feature_shipped '{"feature":"your feature","outcome":"what it does"}'
```

## Routing System (critical context)

Every prompt goes through a classification pipeline before any model sees it:

```
UserPromptSubmit hook → route-task-hook
  → qwen3 classifies → kimi fallback → deepseek fallback → cache fallback
  → 10-tier decision: QWEN | DEEPSEEK_FLASH | GEMINI_FLASH_LITE |
     DEEPSEEK_PRO | GEMINI_FLASH | GEMINI_CLI | KIMI |
     GROK | GEMINI_PRO_SEARCH | CODEX | CLAUDE
  → Delegation: ~/bin/<model> "prompt"
```

**When you're routed to a tier, delegate immediately — don't process yourself.**

| Tier | Delegation Command | Use For |
|------|-------------------|---------|
| QWEN | `~/bin/qwen3 "prompt"` | grep, shell, syntax, lookups |
| DEEPSEEK_FLASH | `~/bin/deepseek --flash "prompt"` | Simple code, boilerplate |
| GEMINI_FLASH_LITE | `~/bin/gemini-api --flash-lite "prompt"` | Bulk extraction, classification |
| DEEPSEEK_PRO | `~/bin/deepseek --pro "prompt"` | Features, refactors, debugging |
| GEMINI_FLASH | `~/bin/gemini-api --flash "prompt"` | Multimodal, images, video |
| GEMINI_CLI | `~/bin/gemini-cli --pro "prompt"` | Full agent with tools |
| KIMI | `~/bin/kimi --quiet -p "prompt"` | Review, reasoning, commits |
| GROK | `~/bin/grok "prompt"` | Competitor intel, CKG, analysis |
| GEMINI_PRO_SEARCH | `~/bin/gemini-api --pro-search "prompt"` | Deep research |
| CODEX | codex exec | Bulk generation |
| CLAUDE | Handle directly | Architecture, security |

## Key Files by Topic

**If you're modifying routing:**
- `maggy/maggy/process/model_router.py` — DEFAULT_TIERS, route_task(), fatigue + budget logic
- `maggy/maggy/services/chat_router.py` — blast estimation, keyword tiers
- `~/.claude/hooks/route-task-hook` — UserPromptSubmit classification hook

**If you're modifying the plugin system:**
- `maggy/maggy/plugins/manager.py` — PluginManager, HookBus
- `plugins/build-in-public/plugin.py` — BuildInPublic class (reference plugin)
- `plugins/build-in-public/plugin.yaml` — Plugin manifest format

**If you're modifying memory:**
- `maggy/maggy/mnemos/fatigue.py` — 4-dimension fatigue model
- `maggy/maggy/mnemos/checkpoint.py` — Checkpoint serialization
- `maggy/maggy/mnemos/constants.py` — Fatigue thresholds

**If you're modifying the dashboard:**
- `maggy/maggy/static/index.html` — SPA shell (Tailwind CDN)
- `maggy/maggy/static/app.js` — All dashboard logic (~2000 lines vanilla JS)
- `maggy/maggy/main.py` — FastAPI app, router registration, lifespan

## Conventions (non-negotiable)

1. **TDD:** Write failing tests first. Run `pytest` before committing.
2. **Quality gates:** Max 20 lines/function, 3 params, 2 nesting levels, 200 lines/file.
3. **No secrets in code:** Use environment variables. `.env` in `.gitignore`.
4. **mWP not MVP:** Ship at 5-7 on the 11-star scale. Users should think "I need this" — not "it works."
5. **Delegation pattern:** Every external model call goes through `~/bin/<script>`. Same contract: accept prompt, write response to stdout.
6. **Plugin pattern:** New capabilities go in plugins, not core. Drop folder → auto-discovered.
7. **Buffer mutations use this exact GraphQL format:**
```graphql
mutation($input: CreatePostInput!) {
  createPost(input: $input) {
    __typename
    ... on PostActionSuccess { post { id status dueAt channelService } }
  }
}
# Variables: {channelId, text, schedulingType: "automatic", mode: "customScheduled", dueAt}
```

## Bootstrapping a New Project

```bash
cd ~/Documents/new-project
claude
> /initialize-project
> /build-in-public enable
```

This copies skills, hooks, plugins, and CLAUDE.md from the bootstrap package.
