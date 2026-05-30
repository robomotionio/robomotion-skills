---
name: seo-content-audit
description: Produce a company's complete SEO footprint analysis in one report — full content inventory, SEO performance signals, competitor comparison, topic/keyword and content-type gap matrices, an optional brand-voice profile, and prioritized recommendations. Crawls sitemaps, deep-analyzes top pages, and runs SERP rank checks (keyless); backlink/authority precision needs a paid API (no free fallback). Foundational input to seo-content-engine.
metadata:
  version: 1.1.1
  category: seo
  type: composite
---

# SEO Content Audit

The full organic-footprint report. Scripts inventory the site, pull page-level signals,
and probe SERP rankings; **you, the agent, classify content, build the gap matrices,
extract brand voice, and write the prioritized recommendations.**

## When to use

- "Run an SEO content audit for [company]", "audit our SEO footprint", "how does our
  content compare to competitors?", quarterly SEO health check.
- Foundational input to `seo-content-engine` (consumes the gap matrices + brand voice);
  complements `aeo-visibility` for a full organic picture.

## How to run

Python 3 stdlib only. Use `${WORKSPACE}` for scratch files. Steps 1 and 3 are independent —
run them in parallel.

### 1. Content inventory (deterministic crawl)

```bash
python3 ${SKILL_DIR}/scripts/crawl_sitemap.py --domain example.com \
  --max-urls 5000 --titles --output ${WORKSPACE}/inventory.json
```

robots.txt `Sitemap:` → sitemap.xml (recursing) → RSS → blog-index. `--titles` fetches
page titles where the sitemap lacks them. You then classify each page's content type +
topic cluster and compute publishing cadence from `lastmod`.

### 2. Deep-analyze top pages (deterministic fetch, agent scores)

```bash
python3 ${SKILL_DIR}/scripts/fetch_page.py --urls-file ${WORKSPACE}/top_pages.json \
  --output ${WORKSPACE}/top_signals.json
```

Word count, headers, lists, internal/external links, schema types per page → funnel stage,
CTA presence, depth. Limit to ~20 top pages.

### 3. SEO performance signals (directional, keyless)

```bash
# Actual Google rank for each target keyword
python3 ${SKILL_DIR}/scripts/serp_probe.py --query "target keyword" \
  --rank-for example.com --max-results 20
# site: indexation count as an authority/coverage proxy
python3 ${SKILL_DIR}/scripts/serp_probe.py --query "site:example.com" --count-only
```

**Directional only.** Authority score, traffic estimate, and the **backlink profile**
require a paid SEO API (no Robomotion package). The backlink profile is the one signal with
**no free SERP fallback** — mark it "requires paid API", never fabricate numbers.

### 3b. (Optional) Enrichment — measured metrics (paid, off by default)

The keyless path above is the DEFAULT and produces a complete audit. **If, and only if,**
`DATAFORSEO_LOGIN`/`DATAFORSEO_PASSWORD` are set, run the bundled DataForSEO adapter to
replace directional signals with MEASURED data — this is the one way to fill the backlink
profile that otherwise has no free fallback:

```bash
python3 ${SKILL_DIR}/scripts/paid_seo.py keywords --keywords "kw1,kw2,kw3" \
  --output ${WORKSPACE}/paid_keywords.json     # real volume, CPC, competition, difficulty
python3 ${SKILL_DIR}/scripts/paid_seo.py domain --domain example.com \
  --output ${WORKSPACE}/paid_domain.json       # authority/rank + organic-traffic overview
python3 ${SKILL_DIR}/scripts/paid_seo.py backlinks --target example.com \
  --output ${WORKSPACE}/paid_backlinks.json     # referring domains, backlinks, domain rank
```

If creds are absent the adapter prints "paid enrichment unavailable — keyless path still
applies" and exits non-zero **without breaking this flow** — just skip it and proceed.
When the JSON IS produced, the agent merges it into the report and **upgrades the
"directional" labels to "measured"** for every metric present (volume/difficulty/authority/
backlinks); the backlink profile changes from "requires paid API" to the real numbers.
(Semrush/Ahrefs are alternative providers — not implemented in the adapter.)

### 4. Competitor crawl (same as Step 1, lighter)

Crawl each competitor (3–5 max; start with 3) for content-type breakdown, topic clusters,
and cadence — structure + volume only, no deep analysis.

### 5. Agent builds gap matrices + voice + report

- **Topic/keyword gap matrix**: per topic, your coverage + rank vs each competitor; flag gaps.
- **Content-type gap matrix**: count per type per company; flag zeros/laggards.
- **Brand voice (optional, `include_brand_voice`)**: fetch 10–15 best posts with
  `fetch_page.py`, then extract tone/vocabulary/structure into do/don't guidelines.
- Synthesize the prioritized Tier 1/2/3 recommendations.

## Outputs

- SEO Content Audit report (workspace markdown): exec summary; content inventory (counts by
  type/topic, cadence, depth); SEO performance (rank/indexation signals; backlink profile
  marked "requires paid API"); competitor comparison; topic/keyword + content-type gap
  matrices; optional brand-voice profile; Tier 1/2/3 recommendations.
- Supporting JSON: `inventory.json`, `top_signals.json`, competitor inventories, brand-voice notes.

## Credentials / env

- **Required:** none for the scripts — inventory, page signals, and rank checks are keyless
  and the default. (Classification, gap reasoning, voice extraction, and synthesis are done
  by you, the agent.)
- **Optional (each with a keyless fallback):**
  - `DATAFORSEO_LOGIN`/`DATAFORSEO_PASSWORD` — if set → the bundled `scripts/paid_seo.py`
    adapter (DataForSEO, HTTP Basic auth) returns measured volume/difficulty/authority/
    backlinks (step 3b); if not → SERP-derived rank/indexation (default), and the backlink
    profile (the one signal with no free fallback) stays "requires paid API" — never
    fabricated. `SEMRUSH_API_KEY`/`AHREFS_API_TOKEN`/`KEYWORD_ANALYSIS_API_KEY` are
    alternative providers (out-of-band, not implemented in the adapter).
  - `APIFY_API_TOKEN` — if set → hostile-site sitemap-crawl fallback; if not → the keyless
    `crawl_sitemap.py` + `serp_probe.py` path (default).

## Notes & edge cases

- **Run Steps 1 and 3 in parallel** — inventory crawl and rank checks are independent.
- **Start with 3 competitors**; add more only if gaps warrant — crawl cost scales with count.
- **The gap matrices are the highest-value output** — they feed `seo-content-engine` directly.
- **Backlink data has no free SERP fallback** — explicitly mark "requires paid API".
- **Brand voice is optional** — skip if pressed, include when the audit feeds drafting.
- **Anti-block**: scripts use a browser UA + 429 backoff; throttle via `--delay`. For volume,
  route through Robomotion Proxy + geo. Re-run quarterly; pair with `aeo-visibility`.
