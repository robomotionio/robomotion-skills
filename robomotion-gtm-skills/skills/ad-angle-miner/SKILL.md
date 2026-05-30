---
name: ad-angle-miner
description: Extract the highest-converting ad angles from real customer-voice data — reviews, Reddit threads, social complaints, and competitor ads — and return a ranked angle bank with verbatim proof quotes and recommended ad formats. For growth/paid-media teams who want ad copy grounded in evidence, not brainstorms.
metadata:
  version: 1.0.1
  category: ads
  type: composite
---

# Ad Angle Miner

Composite: **mine reviews + community + social + competitor ads → tag into angle
categories → score & rank → angle bank.** Mining of public sources is driven by the
agent's web search (keyless, Robomotion Proxy); bundled scripts cover the competitor-ad
scrape and the hostile-source Apify fallback. **The angle extraction, scoring, ranking,
and the bank itself are the agent's reasoning — no LLM call lives in a script.**

## When to use

- "What angles should we run in our ads?" / "Find pain language for ad copy."
- "What are people complaining about with `<competitors>`?"
- "Mine reviews for ad messaging" / "I need fresh angles, not the same tired stuff."

## How to run

One-time browser setup (for the competitor-ad scrape):

```bash
cd ${SKILL_DIR}/scripts && npm install && npx playwright install chromium
```

### 1 — Mine public customer voice (you, the agent — keyless)

Drive these via web search (Robomotion Proxy + geo), then read the pages. **SERP path: if
`DATAFORSEO_LOGIN`/`DATAFORSEO_PASSWORD` (or `SERPER_API_KEY`) is set → use that structured
SERP API for higher coverage/precision; if not → the agent's keyless web search (default).**

- **Reviews** — `site:g2.com` / `site:capterra.com` / `site:trustpilot.com
  "<competitor> reviews"`; pull 1–2★ competitor pain + 4–5★ outcome language.
- **Community** — `site:reddit.com "<category>"`, "I wish", "switching from", pre-buy
  questions.
- **Social** — `site:x.com` / `site:linkedin.com/posts` frustration + praise about the
  category and competitors.

### 2 — Hostile / volume sources (optional Apify fallback)

When a source blocks search depth (Reddit at depth, Amazon reviews, volume review sites):
**if `APIFY_API_TOKEN` is set → use the Apify actor (better depth on hostile/volume
sources); if not → degrade to `site:` web search over public pages (default).** Apify
runner:

```bash
python3 ${SKILL_DIR}/scripts/apify_run.py --actor "trudax~reddit-scraper" \
  --input '{"searches":["uipath alternative"],"maxItems":80}' --output ${WORKSPACE}/reddit.json
```

Without `APIFY_API_TOKEN`, degrade Reddit/Amazon mining to `site:` search over public pages
and note the reduced depth.

### 3 — Competitor ads (Meta Ad Library)

```bash
node ${SKILL_DIR}/scripts/scrape_meta_ads.mjs --query "UiPath" --country US --max-ads 60 --output ${WORKSPACE}/meta_uipath.json
```

This tells you which angles are validated (long-running), tested, or absent. If Meta blocks
the scrape, fall back to a `site:facebook.com/ads/library` search and lower the "freshness"
confidence for that competitor.

### 4 — Ingest provided internal VoC (optional)

If the user pastes/attaches support tickets, NPS, or call notes, read them in as additional
evidence (the agent ingests directly; for PDFs/docs use the platform's document reader).

### 5 — Extract, score, rank (you, the agent)

Tag every snippet into angle categories — **Pain / Outcome / Identity / Fear / Displacement
/ Social-proof / Contrast** — attaching **2–5 verbatim, attributed quotes** each (never
fabricate sources; drop angles with zero retrievable proof to Tier 3). Score each angle:
**evidence 30 / emotional intensity 25 / differentiation 20 / ICP relevance 15 / freshness
10.** Exclude any `tested_angles` the user already ran. Build the competitive angle map
(validated vs. tested vs. absent per competitor) and a test plan. Tier: 1 ≥70, 2 50–69,
3 <50.

### 6 — Render

Write `angle-bank-<YYYY-MM-DD>.md` to `${WORKSPACE}` and attach to the Agent Teams channel.

## Outputs

`angle-bank-<YYYY-MM-DD>.md` — tiered ranked angles, each with category, score, emotional
register, 2–5 proof quotes + source, source count, competitor weakness, recommended format,
sample headline/body; plus a competitive angle map and a test plan.

## Credentials / env

- **Required:** none — public mining runs on web search + the keyless Meta scraper; the
  extraction/scoring/ranking is the agent's reasoning (no LLM key in scripts).
- **Optional (each with a keyless default fallback):**
  - `APIFY_API_TOKEN` — if set → Apify Reddit/Amazon/review-site actor for hostile/volume
    depth; else → `site:` web search + the Playwright Meta scraper (default).
  - `DATAFORSEO_LOGIN`/`DATAFORSEO_PASSWORD` (or `SERPER_API_KEY`) — if set → structured SERP
    API for the mining queries; else → the agent's keyless web search (default).
  - `HTTPS_PROXY` — Robomotion Proxy for the Meta scraper and SERP mining.

## Notes & edge cases

- Always lead with web search + Robomotion Proxy/geo; reserve Apify for sites that block it.
- Quotes must be verbatim and attributed — drop unprovable angles to Tier 3, don't invent.
- Meta Ad Library is JS-heavy and anti-bot — throttle, randomize, proxy; degrade to `site:`
  snippets if blocked and lower the freshness confidence.
- Dedup near-identical angles before ranking so the bank isn't padded with restatements.
