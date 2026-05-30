---
name: icp-website-audit
description: End-to-end "how do our buyers experience our site vs the competition?" audit. Builds personas (if absent), runs a persona-by-persona scorecard of the client site, runs head-to-head comparisons against 1-3 competitors, and consolidates into one report with persona feedback, competitive positioning, at-risk segments, and prioritized recommendations. Keyless crawl; persona scoring and consolidation are the agent's.
metadata:
  version: 1.0.1
  category: research
  type: composite
---

# ICP Website Audit

Crawl all sites once (deterministic, keyless), then **you, the agent, score the site
through each persona, run each head-to-head, and consolidate.** Cost is your reasoning
passes ≈ personas × (1 + competitors) — reuse the captured content; don't re-fetch.

## When to use

- "Run an ICP website audit for [company]. Compare against [competitor 1] and [2]."
- Quarterly site/messaging review; after a site redesign.

## How to run

### Step 1 — personas (sub-skill `buyer-persona-generator`)

If `existing_personas` (`personas.json`) are provided, load + confirm them. Otherwise run
the `buyer-persona-generator` skill first to produce 4-6 personas, e.g.:

```bash
python3 ../buyer-persona-generator/scripts/research_company.py \
  --url <client-url> --company "<client>" --output ${WORKSPACE}/company_bundle.json
```

then synthesize personas per that skill's instructions.

### Step 2 — crawl all sites once (deterministic)

```bash
python3 ${SKILL_DIR}/scripts/crawl_sites.py \
  --client "Acme=https://acme.com" \
  --competitor "Rival=https://rival.com" \
  --competitor "Other=https://other.com" \
  --max-pages 8 --output ${WORKSPACE}/sites.json
```

Python 3 stdlib only. Captures each site's homepage + same-domain high-signal pages
(pricing, product, solutions, about, case-studies, blog, docs) into one bundle. For
JS-heavy / anti-bot competitor pages that come back thin, fall back to a `web-automation`
(Playwright + Robomotion Proxy) fetch; use an `apify` review actor only as a hostile-site
fallback for review-site presence.

### Step 3 — scorecard (you, the agent)

Run each persona (from `personas.json`) through the client pages in `sites.json`, scoring
First Impression, Messaging Relevance, Trust & Credibility, Clarity & Navigation,
Objection Handling, Overall (1-10). Then cross-persona synthesis: consensus issues,
segment gaps, messaging disconnects. Write `<date>-scorecard.md`.

### Step 4 — head-to-head per competitor (you, the agent)

For each competitor, run each persona through both sites (reusing `sites.json`): per-persona
quick takes, dimension scoring for both, "if I had to choose today" verdict, what to steal /
what we do better. Then cross-persona competitive summary + at-risk segments. Write
`<date>-head-to-head-<competitor>.md` each.

### Step 5 — consolidate (you, the agent)

Combine absolute (scorecard) + relative (head-to-head) findings; rank the 3-5
highest-leverage moves by breadth × depth × urgency × feasibility; flag the at-risk
segments (personas leaning to a competitor) prominently — they're the most actionable output.

## Outputs

- `icp-website-audit.md` — exec summary, scorecard matrix, competitive overview matrix,
  persona profiles, cross-persona findings, per-competitor head-to-heads, competitive
  position map, at-risk segments, tiered recommendations.
- Sub-reports: persona assets, `<date>-scorecard.md`, `<date>-head-to-head-<competitor>.md`.
- All persisted to workspace + Agent Teams channel attachment.

## Credentials / env

- **Required:** none. The crawl script is keyless; persona scoring, head-to-head, and
  consolidation are your job as the agent (no LLM key in the script layer).
- **Optional:** if `APIFY_API_TOKEN` is set → Apify review-site scraping when the keyless
  crawl is blocked; if not → keyless crawl/fetch (default). `PINECONE_API_KEY` /
  `QDRANT_URL` — if set → semantic persona dedup; if not → skip (default). The default
  keyless crawl needs no key.

## Notes & edge cases

- Crawl every site once and reuse the captured content across scorecard + all
  head-to-heads — don't re-fetch per pass.
- Start with 1-2 competitors — each adds a full head-to-head pass per persona.
- Re-runnable quarterly — store scores per date to track improvement.
- Use Robomotion Proxy + geo for crawling volume; competitor sites may anti-bot.
