# Digital Marketing Pro

> **Your agency just signed a 50-brand client. The previous agency left no playbook. Three brands are bleeding budget, two have stale positioning, one is launching in a regulated jurisdiction next month. Where do you start?**

Run `/digital-marketing-pro:engagement` against each brand. Same 12-Part Strategy Flow, same Four Core Documents, same 61-step structure — auditable across the entire portfolio in ~60 minutes per brand on Claude Opus 4.7. No more inconsistent depth between brands. No more "what did the last agency do?" mysteries. No more compliance gaps in regulated jurisdictions.

Open-source AI marketing plugin — **153 skills, 25 specialist agents, EU AI Act Article 50 ready**. Built for marketing agencies, in-house teams running 50–200 brands, and consultancies. Installs on **Claude Code** (CLI + IDE), **Anthropic Cowork**, **OpenAI Codex**, **Cursor 2.5+**, **GitHub Copilot CLI**, and **Google Antigravity 2.0**. Created by [Indranil Banerjee](https://indranil.in).

[![Version](https://img.shields.io/badge/version-3.9.0-blue.svg)](CHANGELOG.md)
[![License](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)
[![Stars](https://img.shields.io/github/stars/indranilbanerjee/digital-marketing-pro?style=flat&logo=github&color=yellow)](https://github.com/indranilbanerjee/digital-marketing-pro/stargazers)
[![Forks](https://img.shields.io/github/forks/indranilbanerjee/digital-marketing-pro?style=flat&logo=github&color=blue)](https://github.com/indranilbanerjee/digital-marketing-pro/network/members)
[![Issues](https://img.shields.io/github/issues/indranilbanerjee/digital-marketing-pro?logo=github)](https://github.com/indranilbanerjee/digital-marketing-pro/issues)
[![Last commit](https://img.shields.io/github/last-commit/indranilbanerjee/digital-marketing-pro?logo=github)](https://github.com/indranilbanerjee/digital-marketing-pro/commits/main)
[![Cowork](https://img.shields.io/badge/cowork-compatible-purple.svg)](docs/claude-interfaces.md#claude-cowork-full-support)
[![EU AI Act](https://img.shields.io/badge/EU%20AI%20Act-Article%2050%20ready-darkred.svg)](skills/context-engine/compliance-rules.md)

```bash
# Install — one line
/plugin marketplace add indranilbanerjee/neels-plugins
/plugin install digital-marketing-pro@neels-plugins
```

> If this saves you time, [give it a star ⭐](https://github.com/indranilbanerjee/digital-marketing-pro/stargazers) — it's the single thing that helps other marketers find it.

---

## Why Digital Marketing Pro

Most AI marketing tools generate isolated outputs — a campaign brief here, an email there. No canonical sequence, no shared state, no enforced structure. Result: inconsistent depth, missed dependencies, outputs that don't compound.

**DM Pro runs every brand through the same 12 parts, producing the same files in the same order, with explicit dependency rules between them.** That's the whole product. Everything else — the 153 skills, 25 agents, May-2026 compliance updates — exists to make that 12-Part Flow ship cleanly for real agencies on real client work.

| What this gives you that ad-hoc prompts don't | Why it matters |
|---|---|
| **Canonical 12-Part Strategy Flow** producing the Four Core Documents (61 explicit steps) | Every engagement looks the same, so handoffs work and quality is auditable |
| **Two-Views Model** (v1 unbiased + v2 client-validated) | You never lose the original market view when the client pushes back |
| **Decision Matrix** — maps validation responses to re-runs | Stops over-running (wasted hours) and under-running (broken strategy) |
| **Living Project Instruction File** — single source of truth per engagement | All skills read it first; corrections propagate automatically |
| **EU AI Act Article 50 readiness** built in | C2PA provenance signing, deepfake disclosure, draft-guidelines table in compliance |
| **6-platform AEO/GEO audit** (incl. Google AI Mode) | The first marketing plugin to treat AI Mode as a distinct surface from AI Overviews |

---

## What you get in 60 minutes

Run `/digital-marketing-pro:engagement` and the plugin produces a full brand-strategy engagement in roughly 60 minutes on Opus 4.7 — **~50–60 canonical files** organized by part:

- **Part 1** — Stone-vs-Opinion intake (what the client knows for certain vs what they believe)
- **Part 2** — External market research (unbiased, no client docs)
- **Part 3** — Four Core Documents — 61 explicit steps across Business & SBU Analysis, Segmentation Framework, Brand Positioning & Communications, DMFlow
- **Part 4** — Competitive + Customer + Market analysis (4 unbiased docs)
- **Part 5** — Client Validation Document — the one true stop
- **Part 6** — Selective v2 re-runs per Decision Matrix
- **Part 7** — Preparation documents (campaign architecture, KPI tree, content pillars, approval chains)
- **Part 8** — **Growth Plan + 12-month Yearly Planner** (the flagship deliverable)
- **Part 9** — Channel-strategy fan-out (up to 17 channel docs in 7 families)
- **Part 10** — Execution artefacts (ad copy, post copy, headlines, CTAs)
- **Part 11** — AI creative briefs (with Nano Banana Pro / Veo 3.1 / Gemini Omni model guidance and C2PA + deepfake-disclosure clauses)
- **Part 12** — Continuous improvement loop

Cost: roughly **$15–40 in Claude API spend** for a full 12-part engagement using Opus 4.7. The plugin itself is MIT-licensed and free.

---

## Quick start

### 1. Install on Claude Code (canonical)

```bash
/plugin marketplace add indranilbanerjee/neels-plugins
/plugin install digital-marketing-pro@neels-plugins
```

`/plugin` commands work in **Claude Code** (CLI + IDE at [claude.com/code](https://claude.com/code)) and **Anthropic Cowork**. In the standard Claude chat app (browser `claude.ai` OR the installed Claude Desktop app) plugins still install and run, but management is via the **Plugins** UI button at the bottom of the chat — not via `/plugin` slash commands. See the [Updating](#updating) section for the recovery procedure if you accidentally try a slash command in the chat UI.

### 2. Turn on auto-update (recommended)

Third-party marketplaces have auto-update **OFF by default** in Claude Code — no banner tells you when v3.8 ships. Fix it once:

Open `/plugin` → **Marketplaces** tab → find `neels-plugins` → toggle **Enable auto-update**. Done — future releases pull at session start; `/reload-plugins` applies mid-session without restart.

### 3. Set up your first brand

```
/digital-marketing-pro:brand-setup
```

Interactive brand profiling — voice, audience, channels, industry, target jurisdictions, competitors, goals. Quick mode (5 questions) or full mode (17 questions). Optional: `/digital-marketing-pro:import-guidelines` to bulk-load existing brand guidelines, SOPs, or templates.

### 4. Run a full engagement, or jump straight to a workflow

```
/digital-marketing-pro:engagement           # full 12-Part Strategy Flow (~60 min)
```

Or jump straight to one workflow:

```
/digital-marketing-pro:campaign-plan        # multi-channel campaign with budget, timeline, KPIs
/digital-marketing-pro:seo-audit            # technical + content + E-E-A-T + AI visibility audit
/digital-marketing-pro:content-engine       # blog / ad / email / social / landing / video drafts
/digital-marketing-pro:competitor-analysis  # multi-dimensional deep-dive
/digital-marketing-pro:performance-report   # trends + anomalies + recommendations
/digital-marketing-pro:email-sequence       # subject lines, copy, timing, segmentation
/digital-marketing-pro:check                # pre-publish quality gate (hallucination + voice + claims)
/digital-marketing-pro:status               # unified brand snapshot
/digital-marketing-pro:resume               # resume an interrupted long workflow (engagement / campaign-plan / etc.)
/digital-marketing-pro:output-folder        # open the user-visible ~/Documents/DigitalMarketingPro/ folder
```

### 5. Find your output

```
~/.claude-marketing/<brand-slug>/
├── brand-profile.json           ← brand voice, audience, guardrails, jurisdictions
├── engagements/
│   └── <engagement-slug>/
│       ├── 01-client-inputs/    ← Part 1 Stone-vs-Opinion intake
│       ├── 02-research/         ← Part 2 external market research
│       ├── 03-four-core/        ← Part 3 Four Core Documents (61 steps)
│       ├── 04-analysis/         ← Part 4 competitive / customer / market
│       ├── 05-validation/       ← Part 5 Client Validation Document
│       ├── 06-v2-reruns/        ← Part 6 selective v2 re-runs
│       ├── 07-prep/             ← Part 7 internal operating layer
│       ├── 08-growth-plan/      ← Part 8 Growth Plan + Yearly Planner
│       ├── 09-channels/         ← Part 9 channel-strategy fan-out
│       ├── 10-execution/        ← Part 10 ad copy / post copy / headlines / CTAs
│       ├── 11-creative-briefs/  ← Part 11 AI creative instructions
│       ├── 12-improvement/      ← Part 12 continuous improvement loop
│       └── PROJECT_INSTRUCTIONS.md  ← Living Project Instruction File
└── insights/                    ← cross-engagement learnings
```

See the [Multi-Brand & Agency Guide](docs/multi-brand-guide.md) for the multi-client switching workflow.

---

## Supported surfaces (v3.9.0)

| Platform | Install command | Manifest path | Status |
|---|---|---|---|
| **Claude Code** CLI + IDE extensions | `/plugin install digital-marketing-pro@neels-plugins` | `.claude-plugin/plugin.json` | Full support (canonical) |
| **Anthropic Cowork** | Plugins UI → Add marketplace → `indranilbanerjee/neels-plugins` → Install | same `.claude-plugin/` files | Full support — no `/plugin` slash commands in Cowork (UI-only) |
| **OpenAI Codex** CLI + IDE + App | `codex plugin marketplace add indranilbanerjee/neels-plugins` then `codex plugin install digital-marketing-pro@neels-plugins` | `.codex-plugin/plugin.json` (published OpenAI schema) | Full skills + MCP support |
| **Cursor 2.5+** | In any Cursor Agent chat: `/add-plugin digital-marketing-pro@https://github.com/indranilbanerjee/digital-marketing-pro` | `.cursor-plugin/plugin.json` (published Cursor JSON Schema) | Full skills + agents + commands support |
| **GitHub Copilot CLI** | `copilot plugin marketplace add indranilbanerjee/neels-plugins` then `copilot plugin install digital-marketing-pro@neels-plugins` | `.github/plugin/plugin.json` (Copilot CLI also recognizes `.claude-plugin/plugin.json` as fallback) | Full skills + MCP support; subagents need `.agent.md` extension (open issue); custom slash commands not yet supported in Copilot CLI |
| **Google Antigravity 2.0** CLI + IDE | `agy plugin install https://github.com/indranilbanerjee/digital-marketing-pro` | `gemini-extension.json` (at repo root, per Google's reference pattern) | Full skills + hooks support; subagents need `/agent` CLI spawning; slash commands fold into skills via `agy plugin import gemini` |

**Why this works:** Agent Skills became an open standard in December 2025 (donated to the Agentic AI Foundation; adopted by ~40 agent products by May 2026). All 153 SKILL.md files in DM Pro are platform-portable as written. The sibling manifests are thin platform-specific wrappers around the same `skills/` directory — no skill duplication, no maintenance fork. The pattern is borrowed from Google's reference repo [`gemini-cli-extensions/data-agent-kit-starter-pack`](https://github.com/gemini-cli-extensions/data-agent-kit-starter-pack).

---

## The 12-Part Engagement Methodology

| Part | Name | Output |
|------|------|--------|
| 1 | Client Inputs | Stone vs Opinion intake (what client knows for certain vs what they believe) |
| 2 | External Research | Unbiased market research (no client docs used) |
| 3 | **Four Core Documents** | 61 explicit steps — Business & SBU (18), Segmentation (15), Brand Positioning (19), DMFlow (9) |
| 4 | Competitive + Customer + Market | 4 unbiased analysis documents (4.1–4.4) |
| 5 | **Client Validation Document** | The one true stop — client accepts/rejects/edits each finding |
| 6 | Selective v2 Re-runs | Subset of Part 3 + Part 4 docs re-run per the Decision Matrix |
| 7 | Preparation Documents | Internal operating layer (campaign architecture, KPI tree, content pillars, asset inventory, approval chains) |
| 8 | **Growth Plan + Yearly Planner** | The flagship 11-section client-facing strategy + 12-month operational calendar |
| 9 | Channel Strategy Fan-out | Up to 17 channel docs grouped into 7 families |
| 10 | Execution Artefacts | Ad copy, post copy, headlines, CTAs |
| 11 | AI Creative Instructions | Visual asset briefs with C2PA + EU Article 50 clauses |
| 12 | **Continuous Improvement Loop** | Quarterly briefs feeding signals back into product/offering decisions |

**Key architectural concepts:**
- **Two-Views Model** — Every engagement carries v1 (unbiased market view) and v2 (client-validated view) after Part 5. Operating decisions reference v2; ideation references both. v1 is never deleted.
- **Stone vs Opinion** — Every fact captured at intake is tagged with confidence. Stone = client knows for certain. Opinion = client believes (becomes a research question, not ground truth).
- **Decision Matrix** — Maps client validation responses to which v1 documents need v2 re-runs. Prevents over- and under-re-running.
- **Update-Back Rule** — Live operations surface corrections → source documents get versioned (v2.1, v2.2 …) → Living Project Instruction File propagates the change to all downstream skills.
- **Living Project Instruction File** — Single source of truth per engagement. All skills read it first.

15+ strategic-framework reference documents in `skills/context-engine/` support the methodology (Five Digital Markets, Channel Families, In-Market vs Out-Market, Multi-Dimensional Decision Framework, Unit Economics, Actionable Persona Format, B2B Decision-Making Unit, Three-Scenario Forecasting, 30/60/90-Day Framework, Reporting Cadence, Fixed vs Variable Budget, Competitor 3-Question Output, India Market Context, and more).

---

## What's new in May 2026

DM Pro is updated against the **actual May-2026 marketing ecosystem state** — Google I/O 2026, the active broad core algorithm update, EU AI Act draft implementing guidelines, Meta platform expansions, and the latest AI image/video model landscape. No "trained on 2024 data" surprises in your client outputs.

**v3.8.0 — Real native manifests for 5 surfaces (May 27)**
Ships verified-real manifests for OpenAI Codex (`.codex-plugin/plugin.json` per the published OpenAI schema), Google Antigravity 2.0 (`gemini-extension.json` at repo root per Google's `gemini-cli-extensions/data-agent-kit-starter-pack` reference), Cursor 2.5+ (`.cursor-plugin/plugin.json` per the verified Cursor JSON Schema), and GitHub Copilot CLI (`.github/plugin/plugin.json`; Copilot also recognizes `.claude-plugin/plugin.json` as documented fallback). Adds `AGENTS.md` at root (auto-loaded by Codex + Antigravity + Copilot CLI + Cursor). All 153 skills share via the Agent Skills open standard — no duplication.

**v3.7.13 — Honest positioning (May 26)**
Removed the v3.6 / v3.7 era invented manifests for OpenAI Codex (`.codex-plugin/`), Cursor (`.cursor-plugin/`), GitHub Copilot CLI, and Google Antigravity 2.0 (`.antigravity/`). Research confirmed those manifests did not match the platforms' actual install specs (Antigravity uses `gemini-extension.json` at repo root; Codex schema we hand-rolled was invented). Supported surfaces are now accurately advertised as Claude Code + Cowork only. Multi-platform support is on the roadmap — research saved at `memory/`.

**v3.5.0 — May 2026 content modernisation (May 24)** — six discrete updates:
1. **Google AI Mode** added as a 6th first-class AEO/GEO surface (default conversational search since Google I/O on 19 May 2026, ~1B MAUs, Gemini 3.5 Flash backbone). AI Mode vs AI Overviews citations diverge 40–60% on the same query — audit both. `scripts/geo-tracker.py` PLATFORMS list now includes `ai-mode`.
2. **May 2026 broad core algorithm update** triage guidance — wait for rollout + 7–14 days settling before drawing conclusions; segment GSC data pre/in/post; Core Updates reweight existing signals, don't introduce new ones.
3. **EU AI Act Article 50 draft implementing guidelines** (8 May 2026; consultation closes 3 June; final guidelines July; enforcement 2 August 2026) — six-row clarification table covering "substantial AI manipulation", "matters of public interest", C2PA as presumption-of-compliance, deepfake visible disclosure, editorial-responsibility carve-out conditions, plus a five-point action list for brands with EU exposure.
4. **Meta platform updates** — Advantage+ Leads (global availability), Threads ads (global rollout, image-only), brand-safety inventory filters (Expanded/Moderate/Limited tiers with explicit reach cost).
5. **Gemini Omni + Nano Banana Pro + Veo 3.1** added to AI creative-brief skills with consistent C2PA-by-default and EU Article 50 disclosure clauses; influencer briefs ship with three explicit AI-tool clauses (permitted use, required platform disclosures, EU deepfake clause).
6. **Claude Code v2.1.149+ `/usage`** per-model breakdown integrated into `/digital-marketing-pro:agency-dashboard` for brand-attributable AI cost tracking.

See [CHANGELOG.md](CHANGELOG.md) for the full release history.

---

## Architecture — what's actually in the box

### 25 specialist agents
Marketing Strategist · Brand Guardian · Content Creator · Email Specialist · Social Media Manager · PR Outreach · SEO Specialist · CRO Specialist · Analytics Analyst · Marketing Scientist · Competitor Intelligence · Market Intelligence · Influencer Manager · CRM Manager · Growth Engineer · Journey Orchestrator · Agency Operations · Performance Monitor · Quality Assurance · Memory Manager · Execution Coordinator · Intelligence Curator · Localization Specialist · Media Buyer · Competitive Intel

Each agent has scoped responsibilities, explicit input/output contracts, and reads the Living Project Instruction File before acting.

### 153 skills
Skills are invoked by description match through the Skill tool, addressable as `/digital-marketing-pro:<skill-name>` from chat. Coverage: brand setup, content production (blog / ad / email / social / landing / video / PR / case study), SEO / AEO / GEO audits (6 platforms incl. Google AI Mode), competitor monitoring, campaign planning, channel-specific strategies, attribution, churn risk, lifecycle journeys, intelligence reports, eval framework, knowledge management, multi-brand operations, regional configuration, C2PA content provenance.

### 14 top-level commands
| Command | What it does |
|---|---|
| `/digital-marketing-pro:brand-setup` | Set up a new brand profile (voice, audience, competitors, compliance) |
| `/digital-marketing-pro:engagement` | Run the full 12-Part Strategy Flow |
| `/digital-marketing-pro:campaign-plan` | Generate a multi-channel campaign plan with budget, timeline, KPIs |
| `/digital-marketing-pro:seo-audit` | Comprehensive SEO audit — technical, on-page, content, E-E-A-T, AI visibility |
| `/digital-marketing-pro:content-engine` | Draft blog, ad copy, emails, social, landing pages, video scripts |
| `/digital-marketing-pro:performance-report` | Performance report with trends, anomaly detection, recommendations |
| `/digital-marketing-pro:competitor-analysis` | Multi-dimensional competitive analysis (content, SEO, ads, social, pricing) |
| `/digital-marketing-pro:email-sequence` | Complete email sequences (subject lines, copy, timing, segmentation) |
| `/digital-marketing-pro:check` | Pre-publish quality gate (hallucination + brand voice + structure + claims) |
| `/digital-marketing-pro:status` | Unified brand snapshot (profile, engagements, insights, compliance) |
| `/digital-marketing-pro:resume` | Resume an interrupted long workflow from the last checkpoint |
| `/digital-marketing-pro:output-folder` | Print + open the visible output folder for a brand |
| `/digital-marketing-pro:doctor` | Per-action readiness diagnostic (which campaign-audit / launch-campaign actions are live vs need connector setup) |
| `/digital-marketing-pro:execute-action` | Actually fire an action against its real API (stdlib `urllib`, no third-party deps). 8 verified connectors execute end-to-end; 25 OAuth-only connectors fall back to the MCP path with the manifest still returned. |

Plus **140 additional skills** addressable via `/digital-marketing-pro:<skill-name>` — `:competitor-monitor`, `:churn-risk`, `:autopilot-status`, `:agency-dashboard`, `:aeo-audit`, `:geo-monitor`, `:c2pa-metadata`, `:client-onboarding`, `:journey-design` … see `/digital-marketing-pro:help` after install for the full list, or browse `skills/` in the repo.

### 77 Python scripts (optional)
Plugin works fully without Python — all marketing knowledge, frameworks, agent capabilities, and skills work out of the box via the 167 reference knowledge files.

| Mode | Size | Adds |
|---|---|---|
| **Knowledge-only** (default) | 0 MB | All 153 skills + 25 agents + 167 reference files |
| **Lite** (`pip install nltk textstat`) | ~15 MB | Brand-voice scoring, content quality scoring, readability analysis |
| **Full** (`pip install -r scripts/requirements.txt`) | ~50 MB | Competitor scraping, QR generation, AI visibility API checking, GEO tracking, C2PA signing |

### 14 HTTP MCP connectors
Notion · Slack · Canva · Figma · HubSpot · Amplitude · Ahrefs · SimilarWeb · Klaviyo · Google Calendar · Gmail · Stripe · Asana · Webflow

All HTTP, all Cowork-compatible. For services without first-party HTTP MCPs (Google Sheets, Drive, Salesforce, etc.), see `.mcp.json.connectors-reference` for **Pipedream / Composio / Zapier / Make.com** aggregator paths.

For the full ~68-server stdio configuration (Google Ads, Meta Ads, GA4, GSC, Mixpanel, Marketo, Brevo, etc. via npx, Claude Code only — not Cowork-compatible): `cp .mcp.json.example .mcp.json`. See [CONNECTORS.md](CONNECTORS.md) and [Integrations Guide](docs/integrations-guide.md).

---

## Resumable workflows + visible output folder (v3.7.7+)

Two user-team complaints from the v3.7.5 cycle drove this release: "dm pro is taking too long to process" (the 60-minute engagement that breaks midway loses 30+ minutes of work on restart) and the general "where did my 50 deliverable files save?" confusion (everything was landing under the Windows-hidden `~/.claude-marketing/` dotfolder).

**Fix 1 — Resumable workflows.** Every long-running DMP workflow now writes per-part checkpoints to disk so an interrupted session can resume from the next un-checkpointed part instead of restarting from Part 1. Covered workflows: `engagement` (12-Part Strategy Flow), `campaign-plan`, `content-engine`, `seo-audit`, `competitor-analysis`, `campaign-audit` (v3.7.5), `launch-campaign` (v3.7.5), plus a `custom` slot for any other long flow. Resume with:

```
/digital-marketing-pro:resume                              # auto-pick latest in-progress run
/digital-marketing-pro:resume engagement                   # filter to a workflow
/digital-marketing-pro:resume engagement <run-id>          # pick a specific run
```

**Fix 2 — Visible output folder.** Every artifact a workflow produces is now copied to TWO locations: the internal tracking copy under `~/.claude-marketing/{brand}/output/{workflow}/...` (system-of-record), and a user-visible published copy under `~/Documents/DigitalMarketingPro/{brand}/{workflow}/{YYYY-MM}/{filename}` (visible in Windows Explorer / macOS Finder by default). Override the visible root with `DIGITAL_MARKETING_PRO_PUBLISH_DIR=/path` (e.g. a Dropbox share for the team). Reveal the folder any time with:

```
/digital-marketing-pro:output-folder                       # opens ~/Documents/DigitalMarketingPro/{brand}/
/digital-marketing-pro:output-folder <brand> <workflow>    # drill down
```

**Implementation:** `scripts/checkpoint-manager.py` (per-step storage + atomic writes, stdlib only) + `scripts/output-publisher.py` (dual-copy publish + `where` + `open` subcommands). Mirrors the ContentForge v3.12.3 / v3.12.4 patterns. Verified end-to-end with [`_shared/dmp_engagement_simulation.py`](../_shared/dmp_engagement_simulation.py) — 5 scenarios (clean 12-part run / interrupt-resume / 3 parallel workflows / quality-gate fail / all 8 workflows accepted) all pass in ~6 seconds.

---

## Connector-aware action resolver (v3.7.10+)

The `campaign-audit` and `launch-campaign` skills depend on 14 actions that map to real marketing APIs (Google Ads, Meta Marketing, LinkedIn, TikTok, HubSpot, Salesforce, Klaviyo, Mailchimp, Customer.io, Gmail, Cision, Muckrack, Slack, Google Calendar, Ahrefs, Similarweb, SEMrush, Google Search Console). v3.7.5–v3.7.7 shipped these actions as honest stubs that always returned `status: stub_implementation` regardless of which connectors the user had. v3.7.10 introduces a resolver that probes the live state and resolves each action to one of three modes per call:

| mode | what it means |
|------|---------------|
| `real` | runs end-to-end with no external API (currently only `arm-watchdog` which writes a watchdog config to `~/.claude-marketing/{brand}/watchdogs/`) |
| `manifest_ready` | a matching connector is configured — the response includes the exact HTTP request manifest (method, URL, headers, body template, auth pattern) for the orchestrator (Claude via MCP) to execute. Write/launch ops set `approval_required: true`. |
| `stub_unconfigured` | no matching connector is configured — the response includes the manual fallback PLUS copy-paste `.mcp.json` snippet, env-var list, and a Cowork-compatibility note |

Check what's live in your environment any time:

```
/digital-marketing-pro:doctor                              # full readiness table
/digital-marketing-pro:doctor --summary                    # one-line counts
/digital-marketing-pro:doctor --action inventory --channel google_ads  # drill in
```

**Test coverage:** [`_shared/dmp_action_test_harness.py`](../_shared/dmp_action_test_harness.py) exercises all 14 actions across 27 scenarios (unconfigured + configured + local-execution variants) — all pass.

**Implementation:** `scripts/_connector_registry.py` (catalog of 33 connectors, 11 categories, `is_connector_configured()` probe) + `scripts/connector_resolver.py` (`ACTION_SPECS` map + per-action manifest builders + local executors) + `scripts/action-doctor.py` (the doctor command's underlying script).

### v3.7.11 — actions can actually fire HTTP requests from Python

The v3.7.10 resolver returned a manifest of "what would be sent." v3.7.11 adds `scripts/connector_executor.py` (stdlib `urllib.request`, no third-party deps) that takes that manifest and **actually executes** the request against the real API. Public CLI: `/digital-marketing-pro:execute-action`.

**Executes end-to-end from Python (8 connectors, verified vendor docs):**

| Connector | Env var | What it can fire |
|-----------|---------|---|
| Slack | `SLACK_BOT_TOKEN` | `POST chat.postMessage` (with `body.ok` post-check) |
| HubSpot | `HUBSPOT_PRIVATE_APP_TOKEN` | `GET /automation/v4/flows`, `POST /marketing/v3/campaigns` |
| Klaviyo | `KLAVIYO_PRIVATE_KEY` | `GET /api/flows`, `PATCH /api/flows/{id}` (vnd.api+json) |
| SendGrid | `SENDGRID_API_KEY` | `POST /v3/mail/send` (202 success) |
| Brevo | `BREVO_API_KEY` | `POST /v3/smtp/email` (lowercase `api-key:` header) |
| Customer.io | `CUSTOMERIO_APP_API_KEY` | `POST /v1/send/email` (App API key only) |
| Mailchimp | `MAILCHIMP_API_KEY` | `GET /3.0/automations` (Basic auth, dc from suffix) |
| Ahrefs | `AHREFS_API_KEY` | `GET /v3/site-explorer/metrics` |

**Requires the MCP path (25 OAuth-only connectors):** Google Ads, Meta Marketing, LinkedIn Marketing, LinkedIn Publishing, TikTok Ads, Twitter/X, Gmail, Google Calendar, Google Analytics, Google Search Console, Meta Graph, Salesforce, Pipedrive, Zoho CRM, Buffer, Hootsuite, Cision, Muckrack, Amplitude, Similarweb, SEMrush, Moz, Intercom, Canva, Figma. For all of these, the resolver still returns `manifest_ready` so you can see the exact HTTP shape Claude's MCP tool will send — Python just can't execute the OAuth flow itself.

**Safety gates:** read ops auto-execute with `--execute`; write ops require both `--execute --confirm`; missing env vars block with `setup_hint_credential`; unresolved `{VAR}` placeholders block before the request fires. Every fired call logs to `~/.claude-marketing/{brand}/executions/`.

**Test coverage:** [`_shared/dmp_executor_test_harness.py`](../_shared/dmp_executor_test_harness.py) runs 17 tests against a stdlib `http.server` mock — verifies actual HTTP send-and-receive (not just shape inspection): the 8 connector-specific tests (incl. Slack body.ok post-check + Klaviyo vnd.api+json + Brevo lowercase header + Mailchimp Basic), 6 safety-gate tests, and 1 data-substitution test. All pass.

---

## Model curator — no hardcoded model ids (v3.7.4+)

Frontier models change every ~6 weeks. Hardcoding `claude-sonnet-4-5-20250929` or `gemini-2.0-flash` across dozens of scripts means a provider deprecation silently 404s, the user blames the plugin, and the maintainer has to grep three repos. So we don't hardcode.

- **`scripts/model_registry.json`** — single source of truth for every model id used by the plugin, with vendor, tier, modality, status, and `replacement_id` for deprecated entries.
- **`scripts/resolve_model.py`** — Python module + CLI. Resolves human aliases (`latest-balanced-anthropic`, `latest-fast-anthropic`, `latest-text-openai`, `latest-vision-google`, `latest-image-google`, `latest-video-google`) to concrete ids at call time. Deprecated ids passed via `--model` auto-fall-forward to their replacement (with a stderr warning).
- **`scripts/refresh_models.py`** — polls Anthropic / OpenAI / Google list endpoints with your API keys and reports drift versus the registry (NEW models in the provider catalog, STALE models in the registry).

Every script that calls a provider model now accepts `--model` (or `--openai-model` / `--anthropic-model` for `scripts/ai-visibility-checker.py`) and the value is validated against the registry. See [`docs/MODEL-CURATOR.md`](docs/MODEL-CURATOR.md) for the full alias map, curation policy, and worked examples.

```bash
python scripts/resolve_model.py --alias latest-balanced-anthropic    # -> claude-sonnet-4-6
python scripts/resolve_model.py --check gemini-2.0-flash              # -> deprecated (use gemini-3.5-flash)
python scripts/resolve_model.py --list --vendor anthropic --status current
python scripts/refresh_models.py                                      # drift report (needs API keys)
```

---

## Compliance — 16 jurisdictions, EU AI Act Article 50 ready

DM Pro carries jurisdiction-specific compliance rules that auto-apply when a brand declares its target markets. Coverage:

🇪🇺 EU (GDPR + AI Act Article 50) · 🇺🇸 US Federal (CAN-SPAM) · 🇺🇸 California (CCPA/CPRA) · US 20+ state privacy laws · 🇨🇦 Canada (CASL + PIPEDA) · 🇧🇷 Brazil (LGPD) · 🇬🇧 UK (UK GDPR + PECR) · 🇦🇺 Australia (Privacy Act + Spam Act) · 🇸🇬 Singapore (PDPA) · 🇨🇳 China (PIPL) · 🇮🇳 India (DPDPA) · 🇯🇵 Japan (APPI) · 🇰🇷 South Korea (PIPA) · 🇸🇦 Saudi Arabia (PDPL) · 🇦🇪 UAE (Federal Decree-Law No. 45) · 🇹🇭 Thailand (PDPA)

**EU AI Act Article 50 readiness (applicable 2 August 2026):**
- C2PA content-provenance signing via `/digital-marketing-pro:c2pa-metadata` (end-to-end tested against c2pa-python 0.32 — 75-byte test PNG → 42,818-byte signed PNG with `manifest_embedded_and_verified=true`)
- Pre-publish gate (`/digital-marketing-pro:check`) treats missing C2PA on AI-flagged assets in EU campaigns as CRITICAL → BLOCKED
- Draft implementing guidelines (8 May 2026) added as `compliance-rules.md` §1.1b.i with six-row clarification table + five-point action list
- Production cert guide at `docs/c2pa-production-cert-guide.md` covers the four CAI-recognised authorities (Adobe Content Credentials, Truepic, Numbers Protocol, Microsoft Azure Confidential Ledger)

**Other May 2026 regulatory updates baked in:**
- NY synthetic-performer disclosure law (live June 2026, $1K–$5K per violation, $10K repeat) — applies to synthetic influencers + AI endorsements
- FTC May 2026 endorsement guidance — synthetic influencers, AI testimonials, AI-edited creator content
- CJEU March 2026 ruling — pseudonymized cookie IDs are personal data when re-identification is feasible
- CCPA Jan 2026 ADMT amendments + AI-derived sensitive data classification
- DPDP Phase II preparation — consent manager registration opens Nov 2026

---

## AEO / GEO — May 2026 reality

The search landscape pivoted hard in 2025–2026:
- Google AI Overviews appear on ~55% of all Google searches (Seer Interactive, Sept 2025); organic CTR on AI Overview queries dropped ~61% (1.76% → 0.61%); ~58% of Google searches are now zero-click
- **Google AI Mode** became the default conversational search experience for opted-in users at I/O 2026 (19 May 2026), backed by Gemini 3.5 Flash — ~1B MAUs
- ChatGPT search reaches ~883M MAU; Perplexity heavily skews citations to Reddit (47% of factual cites); Wikipedia drives 48% of ChatGPT citations

DM Pro's AEO/GEO skills (`/digital-marketing-pro:aeo-audit`, `:geo-monitor`, `:entity-audit`) reflect this:
- **6-platform audit standard** — ChatGPT, Perplexity, Google AI Mode, Google AI Overviews, Gemini, Microsoft Copilot (was 5 — AI Mode added May 2026)
- Schema strategy refresh — Google's March 2026 core update demoted FAQ/Review/HowTo schema on non-primary pages. Skills emphasise entity-rich JSON-LD (Article + Organization + Person + Product) and produce an **LLMs.txt** companion file
- Citation tracking across all 6 surfaces, with Profound / Otterly / Conductor AgentStack integration paths in the connectors layer
- **Share of AI Voice** as a first-class metric in `/digital-marketing-pro:performance-report`

---

## Channel guidance — May 2026 updates baked in

- **LinkedIn (March 2026 algorithm shift):** external links and engagement bait penalized ~60%. New **Depth Score** measures dwell time. Followers no longer guarantee reach. Skills optimize for relevance and Depth Score.
- **Email:** Apple MPP affects ~64% of B2C opens — open rate is functionally dead as a primary KPI. **DMARC + RFC 8058 one-click POST unsubscribe** mandatory; non-compliant bulk mail to Gmail/Yahoo/Microsoft gets permanent 550 rejections. Spam threshold tightened to <0.10%.
- **TikTok (post Jan 22 2026 USDS Joint Venture closing):** US data + algorithm under USDS LLC; ByteDance retains <20%. AI-generated creators require disclosure label; AI content excluded from Creator Rewards Program; daily shoppable-post limits effective May 11 2026.
- **Meta Advantage+ Leads** (global as of May 2026), **Threads ads** (global, image-only), **brand-safety inventory tiers** (Expanded/Moderate/Limited — Limited costs ~30% reach).
- **WhatsApp** per-message pricing (since 1 July 2025) — India marketing template ≈ USD 0.0118 per message; 72-hour free service window from CTWA ads or Page CTAs.
- **Third-party cookies — deprecation cancelled.** First-party data is the strategic priority. The `attribution-model` skill defaults to first-party + MMM + incrementality stack.
- **Sora dependency note:** OpenAI consumer Sora app discontinued April 26 2026; Sora API September 24 2026. AI creative briefs default to **Veo 3.1, Kling v3.0 Pro, Runway Gen-4, Gemini Omni**.

---

## Documentation

| Guide | Description |
|---|---|
| [Getting Started](docs/getting-started.md) | Installation, first brand setup, first marketing task — with worked examples |
| [Brand Guidelines](docs/brand-guidelines.md) | Importing voice guides, restrictions, channel styles, templates, agency SOPs |
| [Multi-Brand & Agency Guide](docs/multi-brand-guide.md) | Multi-brand corporations and agency multi-client workflows |
| [Strategy & KPI Mapping](docs/strategy-and-kpis.md) | Business objectives → KPI frameworks → campaign strategy → measurement loop |
| [Integrations Guide](docs/integrations-guide.md) | MCP setup for GA4, HubSpot, Google Ads, Meta, and more |
| [Engagement Methodology](docs/engagement-methodology.md) | Deep-dive on the 12-Part Strategy Flow |
| [Competitor Intelligence](docs/competitor-intelligence.md) | Setting up competitors, running analysis, responding to competitive moves |
| [Claude Interfaces](docs/claude-interfaces.md) | What works in Claude Code, Cowork, Desktop, claude.ai |
| [C2PA Production Cert Guide](docs/c2pa-production-cert-guide.md) | Acquiring a CAI-recognised signing certificate for EU production deployment |
| [Architecture](docs/architecture.md) | Technical deep-dive for contributors and power users |
| [Testing Guide](TESTING-GUIDE.md) | Per-phase test checklist for plugin contributors |

Two PDF references at the repo root: `DM_Strategy_Complete_Learning_Guide.pdf` (full methodology) and `DM_Strategy_Flow_v3_2_Visualization_v1_23Apr26.pdf` (one-page visual map).

---

## FAQ

**Q: How does this compare to LangChain marketing templates / CrewAI marketing crews / general AI marketing tools?**
Those are frameworks. DM Pro is a **packaged, opinionated methodology** with explicit dependency rules between every output. You can build something like it in LangChain or CrewAI — at the cost of months of engineering. DM Pro ships it.

**Q: Which Claude interface should I use?**

| | Claude Code | Claude Cowork | Claude Desktop (no Cowork) | claude.ai web |
|-|:-:|:-:|:-:|:-:|
| Full plugin support | yes | yes | partial | no |
| Brand memory | yes | yes | no | no |
| MCP integrations | all | HTTP only | HTTP only | no |
| Document creation (Excel, PPT) | no | yes | no | no |
| Recommended for | Terminal workflows + scripting | Visual desktop workflows | Quick content | One-off questions |

**Q: How much does a full engagement cost in API spend?**
Roughly **$15–40** for a complete 12-part engagement using Opus 4.7 across ~50–60 documents. Track per-brand consumption via Claude Code v2.1.149+ `/usage` (now integrated into `/digital-marketing-pro:agency-dashboard`).

**Q: Can I run multiple brands in parallel?**
Yes. Each brand has its own `~/.claude-marketing/<brand-slug>/` directory and Python script state. Switch with `/digital-marketing-pro:switch-brand`.

**Q: What if I only want a campaign plan, not the full methodology?**
Skip to `/digital-marketing-pro:campaign-plan`. Every individual surface (campaign / SEO / content / competitor / email / report) is independently runnable. The full engagement is the canonical path, not the only path.

**Q: Will this work on Codex / Cursor / Copilot CLI / Antigravity?**
Yes — v3.8.0 (2026-05-27) ships verified-real manifests for all four. See [Supported surfaces](#supported-surfaces-v380) above for per-platform install commands. The earlier v3.6 / v3.7 era manifests were invented (didn't match the platforms' actual install specs) and were correctly removed in v3.7.13; v3.8.0 replaces them with real native manifests against the published schemas (Antigravity: `gemini-extension.json` at repo root per Google's reference; Codex: real OpenAI schema; Cursor: verified Cursor 2.5+ JSON Schema; Copilot CLI: verified GitHub schema with `.claude-plugin/plugin.json` as documented fallback path).

**Q: Is this an Anthropic product?**
No — independent open-source plugin built by [Indranil Banerjee](https://indranil.in). MIT-licensed. Runs on Claude Code + Cowork.

**Q: I found a compliance rule that looks out of date.**
[File an issue](https://github.com/indranilbanerjee/digital-marketing-pro/issues) with the citation. Privacy and AI law change quarterly — DM Pro is actively maintained against the May 2026 reality but enforcement actions and amendments keep coming.

---

## Updating

> **If you see "/plugin isn't available in this environment"** — you're in the standard **Claude chat app** (browser OR installed desktop app). The `/plugin` slash command is **only** supported in two environments: **Claude Code** (the developer CLI / IDE at [claude.com/code](https://claude.com/code), `npm install -g @anthropic-ai/claude-code`) and **Anthropic Cowork**. Everywhere else — `claude.ai` web chat, the Claude Desktop app, mobile — plugins are managed through the UI, not slash commands.
>
> The plugin IS installed (your DM Pro skills work); only the management command is unavailable. Fix:
>
> 1. **In the chat UI** — click the **Plugins** button at the bottom of the chat → **Manage plugins** → find Digital Marketing Pro → look for Update / Refresh / Remove. If no Update button, **Remove** then **Add plugin** → re-install from `indranilbanerjee/neels-plugins`. The re-pull fetches the latest version.
> 2. **For slash-command management** — switch to Claude Code (CLI or IDE) or Cowork. The plugin runs identically across every Anthropic surface; you're choosing where to type management commands.
>
> Once you're in Claude Code or Cowork, the rest of this section applies.

```
/plugin marketplace update neels-plugins
/plugin uninstall digital-marketing-pro@neels-plugins
/plugin install digital-marketing-pro@neels-plugins
/reload-plugins
```

`/plugin marketplace update` only refreshes the catalog — the uninstall + reinstall is what actually pulls the new version. `/reload-plugins` applies the change without restart.

If a version stays the same but content changed (fast-iteration debugging):
```
rm -rf ~/.claude/plugins/cache/neels-plugins
/plugin install digital-marketing-pro@neels-plugins
/reload-plugins
```

---

## Neelverse Marketing Suite

DM Pro is part of a three-plugin suite by [Indranil Banerjee](https://indranil.in) — share the same brand profiles, install together, designed to chain:

| Plugin | What it does |
|---|---|
| **Digital Marketing Pro** (this plugin) | End-to-end engagement methodology — 12-Part Flow, Four Core Documents, Two-Views Model |
| [ContentForge](https://github.com/indranilbanerjee/contentforge) | Publication-ready content via 10-phase pipeline, fact-checker, 29-pattern AI-detection humanizer, .docx export with C2PA signing |
| [SocialForge](https://github.com/indranilbanerjee/socialforge) | Social media calendar with AI image (Vertex AI Nano Banana Pro) + video (WaveSpeed Kling v3.0 Pro) generation, C2PA signing |

```
/plugin marketplace add indranilbanerjee/neels-plugins
/plugin install digital-marketing-pro@neels-plugins
/plugin install contentforge@neels-plugins
/plugin install socialforge@neels-plugins
```

---

## Star history

[![Star History Chart](https://api.star-history.com/svg?repos=indranilbanerjee/digital-marketing-pro&type=Date)](https://star-history.com/#indranilbanerjee/digital-marketing-pro&Date)

If DM Pro saves your team time, [⭐ star the repo](https://github.com/indranilbanerjee/digital-marketing-pro/stargazers) — it's the single most useful thing you can do to help other marketing teams discover it.

---

## About the maintainer

DM Pro is built and maintained by **[Indranil Banerjee](https://indranil.in)** — a digital marketing practitioner shipping engagement methodology as code. The 12-Part Strategy Flow comes from real client engagements across consumer DTC, B2B SaaS, regulated industries (health, finance), and agency multi-brand portfolios.

- 🌐 **Website:** [indranil.in](https://indranil.in)
- 💼 **LinkedIn:** [linkedin.com/in/askneelnow](https://www.linkedin.com/in/askneelnow)
- 🐦 **X / Twitter:** [@askneelnow](https://x.com/askneelnow)
- 💻 **GitHub:** [@indranilbanerjee](https://github.com/indranilbanerjee)
- 📦 **Other plugins:** [ContentForge](https://github.com/indranilbanerjee/contentforge) · [SocialForge](https://github.com/indranilbanerjee/socialforge)
- 💬 **Discussions:** [GitHub Discussions](https://github.com/indranilbanerjee/digital-marketing-pro/discussions)
- 🐛 **Bug reports:** [GitHub Issues](https://github.com/indranilbanerjee/digital-marketing-pro/issues)

**Why this plugin exists:** Most AI marketing tools generate isolated outputs that don't compose. The 12-Part Strategy Flow encodes the canonical sequence a real engagement actually needs — Stone-vs-Opinion intake, Four Core Documents, Client Validation, Two-Views Model, Decision Matrix, Growth Plan + Yearly Planner, channel fan-out, execution artefacts, creative briefs, continuous improvement loop. Once it's a plugin, every engagement looks the same, handoffs work, and quality is auditable. That's the whole product.

If DM Pro saves your team time, [⭐ star the repo](https://github.com/indranilbanerjee/digital-marketing-pro/stargazers) — it's the single most useful thing you can do to help other marketing teams discover it. Sharing on **LinkedIn** ([linkedin.com/in/askneelnow](https://www.linkedin.com/in/askneelnow)) or **X** ([@askneelnow](https://x.com/askneelnow)) helps too — tag me, I'll re-share.

---

## Contributing

PRs welcome — especially on compliance rules (privacy and AI law change fast), industry profiles, and channel-specific updates. See [CONTRIBUTING.md](CONTRIBUTING.md) for the contribution workflow, [`.github/PULL_REQUEST_TEMPLATE.md`](.github/PULL_REQUEST_TEMPLATE.md) for the PR checklist, and [TESTING-GUIDE.md](TESTING-GUIDE.md) for per-phase test checklists. All contributors are expected to follow the [Code of Conduct](CODE_OF_CONDUCT.md). Security issues: please use [Private Security Advisories](https://github.com/indranilbanerjee/digital-marketing-pro/security/advisories/new) per [SECURITY.md](SECURITY.md) — do not file public issues for vulnerabilities.

---

## License

MIT — see [LICENSE](LICENSE). Free to use commercially.

---

## Release notes

**v3.8.0 (2026-05-27)** — Real native manifests for 5 surfaces. Ships verified-real `.codex-plugin/plugin.json` (per the published OpenAI schema), `gemini-extension.json` (at repo root, per Google's `gemini-cli-extensions/data-agent-kit-starter-pack` reference pattern), `.cursor-plugin/plugin.json` (per the verified Cursor 2.5+ JSON Schema), and `.github/plugin/plugin.json` (verified GitHub Copilot CLI schema; Copilot also recognizes `.claude-plugin/plugin.json` as documented fallback). Adds `AGENTS.md` at root (auto-loaded by Codex + Antigravity + Copilot + Cursor agent context chains). All 153 skills share via the Agent Skills open standard — no skill duplication. Replaces the v3.6/v3.7 era invented manifests correctly removed in v3.7.13. Pre-flight verified: 190/190 skills pass the Codex `[a-z0-9-]` regex AND the SKILL.md frontmatter `name` field matches each folder.

**v3.7.13 (2026-05-26)** — Honest positioning. Removed v3.6 / v3.7 era invented manifests (`.codex-plugin/`, `.cursor-plugin/`, `.antigravity/`) + `docs/cross-platform-install.md`. Research confirmed they did not match the platforms' actual install specs. Zero functional changes; the plugin behaved identically in Claude Code + Cowork.

**v3.7.1 (2026-05-24)** — Polish + discoverability pass. README rewritten for organic GitHub/AI-engine discoverability with social-proof badges, install matrix at the top, outcome-focused "What you get in 60 minutes" section, AEO/GEO/compliance keyword density, maintainer block with [indranil.in](https://indranil.in), and ⭐ CTAs. Stale asset counts swept across multiple docs. plugin.json description corrected to 69 scripts (was 71). No functional changes; no breaking changes.

**v3.5.0 (2026-05-24)** — May-2026-ecosystem modernisation pass. Six discrete updates: (1) Google AI Mode as 6th AEO/GEO surface; (2) May 2026 broad core algorithm update triage; (3) EU AI Act Article 50 draft implementing guidelines (8 May; 3 June consultation; 2 Aug enforcement); (4) Meta Advantage+ Leads global + Threads ads + brand-safety filters; (5) Gemini Omni + Nano Banana Pro + Veo 3.1 in creative briefs; (6) Claude Code v2.1.149+ `/usage` per-brand cost tracking in agency dashboard.

**v3.4.1 (2026-05-17)** — Audit & corrections pass on v3.4.0. C2PA script rewritten against the real c2pa-python 0.32 API (Builder + Signer.from_info), end-to-end tested. Unified ads MCP entries corrected. Parallel-dispatch speedup claim softened from flat 6× to honest 4–6× parallelism / ~50–80% wall-clock reduction.

**v3.4.0 (2026-05-16)** — C2PA content-provenance for EU AI Act Article 50 compliance (`scripts/embed-c2pa.py`, `/digital-marketing-pro:c2pa-metadata`, pre-publish gate integration). Unified ads-platform MCPs added. Explicit parallel subagent dispatch in `engagement-workflow` + 4 multi-dimensional commands. Anthropic Software Directory submission packet at `SUBMISSION.md`.

**v3.3.0 (2026-05-15)** — May 2026 modernization sweep. Privacy & compliance updates (EU AI Act, DPDP Phase II, NY synthetic-performer law, FTC May 2026 endorsement guidance, CCPA ADMT, CJEU pseudonymized-cookie ruling). Channel guidance updates (LinkedIn algorithm shift, email DMARC + RFC 8058, TikTok USDS, WhatsApp per-message pricing, schema refresh + LLMs.txt, Sora deprecation). AEO/GEO modernization.

**v3.2.x (May 2026)** — `/dm:` → `/digital-marketing-pro:` namespace sweep (~600 references); manifest install format fix; hook-removal gap closure (`/check`, `/status`, embedded hallucination checks, opt-in `auto_save_insights`).

**v3.1.0 (May 2026)** — Removed all global hooks. Prior `SessionStart` and `PreToolUse mcp_.*` matchers were firing across every project regardless of context. Hook config preserved as reference at `hooks/hooks-reference.example.json`.

**v3.0.0 (April 2026)** — 12-Part Engagement Methodology. Four Core Documents (61 explicit steps). Two-Views Model. Decision Matrix. Update-Back Rule. Living Project Instruction File.

**Earlier versions:** see [CHANGELOG.md](CHANGELOG.md) for v2.7 and earlier.

---

<sub>Made with care by [Indranil Banerjee](https://indranil.in) · Powered by Anthropic Claude · MIT-licensed · [⭐ Star the repo](https://github.com/indranilbanerjee/digital-marketing-pro) if it helps you</sub>
