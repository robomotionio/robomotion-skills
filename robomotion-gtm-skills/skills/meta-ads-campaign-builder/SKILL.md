---
name: meta-ads-campaign-builder
description: Build a complete Meta (Facebook/Instagram) Ads campaign structure — objective, audience layering, ad-set architecture, placement-aware copy framework, and budget/bidding plan — from ICP + objective. Focused on the strategic architecture that decides success before a single ad runs, not on creative generation. Produces a plan/brief the user executes in Ads Manager.
metadata:
  version: 1.0.1
  category: ads
  type: composite
---

# Meta Ads Campaign Builder

Composite: **objective selection → audience strategy → copy framework → budget/bidding →
plan.** This is a **planning** skill — almost entirely the agent's reasoning. The only
script is an optional competitor Meta Ad Library scrape for angle/audience cues. There is
**no Meta write API** in the Robomotion map, so the deliverable is the structured plan +
checklists the user executes in Ads Manager.

## When to use

- "Set up Meta Ads for our product" / "Build a Facebook/Instagram campaign."
- "Help me structure a Meta campaign for lead gen / launch / awareness."

## How to run

### 1 — Objective & structure (you, the agent)

Map the business goal to a Meta objective (awareness / traffic / lead-gen / conversions /
app-installs) and design the ad-set tree: interest prospecting / lookalike / website
retargeting / engagement retargeting.

### 2 — (Optional) competitor Meta ad research

```bash
cd ${SKILL_DIR}/scripts && npm install && npx playwright install chromium   # one-time
node ${SKILL_DIR}/scripts/scrape_meta_ads.mjs --query "Asana" --country US --max-ads 40 --output ${WORKSPACE}/meta_asana.json
```

Use it for angle/audience cues. **If blocked: if `APIFY_API_TOKEN` is set → use the Apify
actor; if not → degrade to a `site:facebook.com/ads/library` web search (default).** For
**evidence-grounded angles**, call the `ad-angle-miner` composite upstream and feed its
angle bank into the copy framework.

### 3 — Audience strategy (you)

Seed interest/behavior ideas via web search (`<category> Meta targeting interests`, `<ICP
role> Facebook audience`) — **if `DATAFORSEO_LOGIN`/`DATAFORSEO_PASSWORD` (or
`SERPER_API_KEY`) is set → structured SERP API; else → the agent's keyless web search
(default)** — then layer interest/behavior/demographic targeting (aim
**500K–2M** prospecting), lookalike sources + %, retargeting windows. **B2B on Meta is weak
on native targeting — prefer customer-list lookalikes + layered interest/behavior, and
recommend LinkedIn for precision, Meta for retargeting/awareness.**

### 4 — Copy framework (you)

Per-placement limits (Feed / Stories / Reels / Right-column / Audience-Network); structure
each as Hook → Pain/Outcome → Proof → CTA; produce **3–5 variants per ad set** across
pain / outcome / social-proof / contrarian / product-led angles. Respect per-placement char
limits so variants don't truncate.

### 5 — Budget & bidding (you)

Allocate prospecting / retargeting / testing by `monthly_budget` tier; pick bidding
strategy; give learning-phase guidance (~50 conv/week/ad set). **If the budget can't sustain
~50 conv/week/ad set, recommend consolidating ad sets or optimizing on an earlier funnel
event** — flag it explicitly.

### 6 — Render

Write `meta-campaign-plan-<YYYY-MM-DD>.md` to `${WORKSPACE}` and attach to the Agent Teams
channel.

## Outputs

`meta-campaign-plan-<YYYY-MM-DD>.md` — campaign overview, structure tree (prospecting/
lookalike/retargeting ad sets), audience targeting per ad set, 3–5 placement-aware copy
variants per ad set, budget allocation + bidding by tier, tracking-setup checklist, launch
checklist, week 1–2 monitoring plan.

## Credentials / env

- **Required:** none — this is a planning skill; producing the plan needs no Meta API. The
  optional competitor scrape is keyless.
- **Optional (each with a keyless default fallback):**
  - `APIFY_API_TOKEN` — if set → Apify actor when the optional Meta competitor pass is
    blocked; else → keyless Playwright scraper degrading to `site:` web search (default).
  - `DATAFORSEO_LOGIN`/`DATAFORSEO_PASSWORD` (or `SERPER_API_KEY`) — if set → structured SERP
    API for audience/interest research; else → the agent's keyless web search (default).
  - `HTTPS_PROXY` — Robomotion Proxy for the scraper / research.

## Notes & edge cases

- Output is a campaign plan/brief, not a live push — there is no Meta Ads write API in the
  Robomotion map.
- B2B targeting is weak on Meta — favor customer-list lookalikes; recommend LinkedIn for
  precision.
- Respect per-placement copy limits so variants don't truncate.
- Flag the learning-phase constraint when budget is thin.
- The competitor Meta Ad Library scrape is JS/anti-bot — throttle + proxy; degrade to `site:`
  snippets if blocked.
