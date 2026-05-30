# The GTM Stack

**[agentgtmskills.com](https://agentgtmskills.com)**

Your AI agent can write code, debug systems, and ship features. Ask it to price your product, build a cold outreach sequence, or plan a 16-channel launch, and you get generic advice from 2021 blog posts.

These 18 skills fix that.

Each one is a dense, opinionated playbook (300-900 lines) covering one GTM function. Real frameworks. Current benchmarks (2025-2026). Decision matrices with actual numbers. The kind of context that turns a general-purpose agent into a GTM operator.

**9,800+ lines** across the full revenue surface: positioning, pricing, outbound, inbound, paid, retention, and ops.

**Works with any AI agent.** Claude Code, Codex CLI, Cursor, Windsurf, GitHub Copilot, Gemini CLI, Cline, OpenClaw, Antigravity, and any coding agent that reads `.md` skill files.

## The Stack

```
STRATEGY          What you sell, who you sell to, how you price it
                  positioning-icp / ai-pricing / sales-motion-design

OUTBOUND          Signal-based prospecting with AI agents
                  ai-cold-outreach / ai-sdr / lead-enrichment / video-outreach

INBOUND           Channels that bring buyers to you
                  multi-platform-launch / ai-seo / social-selling / content-to-pipeline

PAID              Creatives that convert at scale
                  ai-ugc-ads / paid-creative-ai

RETENTION         Expand revenue, prevent churn
                  expansion-retention / partner-affiliate

OPERATIONS        The automation layer underneath everything
                  gtm-engineering / solo-founder-gtm / gtm-metrics
```

Skills cross-reference each other. Use them individually or combine them for full-stack GTM workflows.

## Start Here

Pick the workflow closest to what you're building:

| I want to... | Use these skills | Start with |
|---|---|---|
| Launch a new AI product | positioning-icp + ai-pricing + multi-platform-launch | positioning-icp |
| Build an outbound engine | lead-enrichment + ai-cold-outreach + ai-sdr | lead-enrichment |
| Set up AI SDRs with Clay | ai-sdr + lead-enrichment + gtm-engineering | ai-sdr |
| Run my GTM as a solo founder | solo-founder-gtm + ai-cold-outreach + content-to-pipeline | solo-founder-gtm |
| Create a paid creative system | ai-ugc-ads + paid-creative-ai + video-outreach | ai-ugc-ads |
| Grow organic with content + SEO | content-to-pipeline + ai-seo + social-selling | content-to-pipeline |
| Reduce churn and expand accounts | expansion-retention + gtm-metrics | expansion-retention |
| Price my AI product | ai-pricing + positioning-icp + gtm-metrics | ai-pricing |
| Build GTM automation with code | gtm-engineering + ai-sdr + lead-enrichment | gtm-engineering |

## Skills

### Strategy

| Skill | What It Does |
|---|---|
| [positioning-icp](skills/positioning-icp/) | ICP definition with enrichment signals, competitive positioning, messaging architecture, perishable PMF |
| [ai-pricing](skills/ai-pricing/) | Consumption/workflow/outcome charge metrics, copilot vs agent archetypes, BYOK, hybrid models, margin management |
| [sales-motion-design](skills/sales-motion-design/) | PLG vs sales-led vs hybrid vs agent-led selection, value-before-purchase design, time-to-first-value |

### Outbound

| Skill | What It Does |
|---|---|
| [ai-cold-outreach](skills/ai-cold-outreach/) | AI outreach stack (Clay + Instantly/Smartlead), 3-line cold email framework, deliverability, sequence design |
| [ai-sdr](skills/ai-sdr/) | AI SDR deployment (11x, Artisan, AiSDR), 4-week program, signal-to-action routing, qualification automation |
| [lead-enrichment](skills/lead-enrichment/) | Enrichment waterfalls, ICP scoring formulas, Clay workflows, confidence thresholds, contact verification |
| [video-outreach](skills/video-outreach/) | "Made this for you" framework, Tavus/Sendspark/HeyGen, personalized video at scale, async selling |

### Inbound

| Skill | What It Does |
|---|---|
| [multi-platform-launch](skills/multi-platform-launch/) | 16+ channel launches, Product Hunt playbook, Hacker News strategy, waitlist building, AppSumo |
| [ai-seo](skills/ai-seo/) | Programmatic SEO with AI, competitor alternative pages, AI Overviews optimization, DataForSEO + Claude Code |
| [social-selling](skills/social-selling/) | LinkedIn Sales Navigator, DM sequences, content-to-conversation, profile optimization, SSI scoring |
| [content-to-pipeline](skills/content-to-pipeline/) | Content-led GTM, distribution reverse engineering, multi-platform repurposing, newsletter as pipeline |

### Paid

| Skill | What It Does |
|---|---|
| [ai-ugc-ads](skills/ai-ugc-ads/) | AI UGC with Arcads/Creatify, creator recruitment, Spark Ads, whitelisting, creative testing matrix |
| [paid-creative-ai](skills/paid-creative-ai/) | Meta Advantage+, Google Performance Max, TikTok Smart+, modular testing, creative fatigue, budget allocation |

### Retention & Growth

| Skill | What It Does |
|---|---|
| [expansion-retention](skills/expansion-retention/) | Consumption-based upsell triggers, automated CS, churn risk signals, closed-lost re-engagement, NRR |
| [partner-affiliate](skills/partner-affiliate/) | Co-creation partner model, 3-tier comp structure, affiliate programs, PartnerStack/Impact, channel strategy |

### Operations

| Skill | What It Does |
|---|---|
| [gtm-engineering](skills/gtm-engineering/) | GTM automation with n8n/Make/Zapier, instruction stacks, AI agent orchestration, API-first stack design |
| [solo-founder-gtm](skills/solo-founder-gtm/) | $50-450/mo tool stack, AI agent teams as org, taste as moat, when to hire, revenue stage playbooks |
| [gtm-metrics](skills/gtm-metrics/) | Revenue latency, TTFV, pipeline per rep, data health scoring, attribution models, GTM dashboards |

## Install

### Claude Code Plugin

```bash
/plugin marketplace add chadboyda/agent-gtm-skills
/plugin install agent-gtm-skills
```

### CLI

```bash
# All skills
npx add-skill chadboyda/agent-gtm-skills

# Specific skills
npx add-skill chadboyda/agent-gtm-skills --skill ai-cold-outreach ai-sdr lead-enrichment
```

### Manual

```bash
git clone https://github.com/chadboyda/agent-gtm-skills.git
cp -r agent-gtm-skills/skills/* .claude/skills/
```

Or add as a git submodule:

```bash
git submodule add https://github.com/chadboyda/agent-gtm-skills.git .claude/agent-gtm-skills
```

## Usage

Skills activate based on your task. Ask naturally:

```
"Define our ICP and build an enrichment waterfall"    -> positioning-icp, lead-enrichment
"Build a cold outreach sequence for my SaaS"          -> ai-cold-outreach
"How should I price my AI agent product?"              -> ai-pricing
"Set up an AI SDR system with Clay and Instantly"      -> ai-sdr, gtm-engineering
"Plan a multi-platform launch"                         -> multi-platform-launch
```

Or invoke directly: `/ai-cold-outreach`, `/positioning-icp`, `/solo-founder-gtm`

## Contributing

PRs welcome. Each skill lives in `skills/<skill-name>/SKILL.md`:

```markdown
---
name: skill-name
description: "When the user wants to [use case]. Also triggers on '[keyword1],' '[keyword2].' Covers [scope]."
---

[Frameworks, tables, benchmarks, playbooks for the AI agent]
```

All benchmarks are 2025-2026. Refresh annually as the AI GTM landscape shifts.

## License

MIT
