---
name: programmatic-seo-planner
description: Decide which programmatic-SEO page patterns are worth building for a product (/vs/, /integrations/, /for-{industry}/, /alternatives-to/, /use-cases/, /glossary/) and design the template structure, data model, and priority order. Crawls competitor pSEO patterns, expands keyword variations via Google Autocomplete, probes demand, then the agent scores patterns and designs templates. Outputs a full pSEO blueprint + buildout roadmap. Keyless (paid keyword APIs optional).
metadata:
  version: 1.1.1
  category: seo
  type: composite
---

# Programmatic SEO Planner

The build-side counterpart to `programmatic-seo-spy`. Scripts do the deterministic
recon (competitor patterns, keyword expansion, demand probes); **you, the agent, map
patterns to the category, score them, and design the templates + roadmap.**

## When to use

- "How do we scale SEO pages without writing each manually?", "should we build vs/ pages?",
  "plan our pSEO strategy", "how can we rank for hundreds of long-tail keywords?".
- A growth team wanting a validated blueprint before a buildout. Can feed `seo-content-engine`.

## How to run

Python 3 stdlib only. Use `${WORKSPACE}` for scratch files.

### 1. Discover competitor patterns (deterministic)

```bash
python3 ${SKILL_DIR}/scripts/crawl_sitemap.py --domain competitor1.com \
  --max-urls 5000 --output ${WORKSPACE}/urls_comp1.json
python3 ${SKILL_DIR}/scripts/cluster_url_patterns.py \
  --input ${WORKSPACE}/urls_comp1.json --output ${WORKSPACE}/patterns_comp1.json
```

Per pattern: page count, varying data axis, URL-consistency, sample URLs — your evidence
of which pSEO plays exist in the category.

### 2. Map patterns to the category + mine customer language (agent + deterministic)

You enumerate the standard pSEO pattern types that fit the product's category. To mine
how the ICP phrases the problem and to generate keyword variations per candidate pattern:

```bash
python3 ${SKILL_DIR}/scripts/expand_keywords.py \
  --seeds "project management,task tracking" \
  --modifiers base,question,comparison,commercial,guide \
  --max-per-seed 120 --output ${WORKSPACE}/variations.json
```

### 3. Validate demand per variation (directional, keyless)

```bash
python3 ${SKILL_DIR}/scripts/serp_probe.py --queries-file ${WORKSPACE}/variations.json \
  --max-results 10 --output ${WORKSPACE}/demand.json
```

Confirms each variation returns real results (demand proxy) and lets you spot-check SERP
competition. **Directional only** — exact volumes need a paid keyword API (no Robomotion
package); mark such numbers as estimates in the blueprint.

### 3b. (Optional) Enrichment — measured volume (paid, off by default)

The keyless demand proxy (Autocomplete + SERP existence) is the DEFAULT. **Only if**
`DATAFORSEO_LOGIN`/`DATAFORSEO_PASSWORD` are set, run the bundled DataForSEO adapter to
attach REAL per-variation search volume + difficulty — turning the pattern score's "search
demand 30%" input from directional to measured:

```bash
python3 ${SKILL_DIR}/scripts/paid_seo.py keywords \
  --keywords "variation 1,variation 2,variation 3" \
  --output ${WORKSPACE}/paid_volume.json       # real volume, CPC, competition, difficulty
```

If creds are absent the adapter prints "paid enrichment unavailable — keyless path still
applies" and exits non-zero **without breaking this flow** — skip it and proceed keyless.
When the JSON IS produced, join measured volume/difficulty onto each variation in the
blueprint and **upgrade the "estimate"/"directional" volume labels to "measured"**; the
pattern scoring is unchanged, only its volume input gets sharper. (Semrush/Ahrefs are
alternative providers, not implemented in the adapter.)

### 4. Sample competitor template quality (optional, deterministic)

```bash
python3 ${SKILL_DIR}/scripts/fetch_page.py --url https://competitor1.com/vs/page-a \
  --output ${WORKSPACE}/template_sample.json
```

Gives you the section structure / data-richness signals to model your own templates on.

### 5. Agent builds the blueprint

- score each candidate pattern: search demand 30%, intent quality 25%, template feasibility
  20%, data availability 15%, competitive gap 10%; rank;
- for each pattern scoring ≥ 50: design URL structure, title/meta/H1 templates, the
  content-section framework, required per-page data fields + their sources (manual list /
  scrape / internal product data), and content guidelines;
- build the priority matrix (pages, volume/page, total volume, effort, priority) and a
  month-by-month buildout sequence; factor CMS feasibility (Webflow item caps, static-gen).

## Outputs

- pSEO blueprint (workspace markdown): per-pattern URL structure, title/meta/H1 templates,
  content-section framework, per-page data fields + sources, build effort, time-to-rank.
- Prioritized pattern ranking (0–100) + a month-by-month buildout sequence.
- Per-pattern data-source plan.
- Raw artifacts: `patterns_*.json`, `variations.json`, `demand.json`.

## Credentials / env

- **Required:** none for the scripts — the whole recon flow is keyless and the default.
  (Pattern mapping, scoring, and template design are done by you, the agent.)
- **Optional (each with a keyless fallback):**
  - `DATAFORSEO_LOGIN`/`DATAFORSEO_PASSWORD` — if set → the bundled `scripts/paid_seo.py`
    adapter (DataForSEO, HTTP Basic auth) returns measured per-variation volume/difficulty
    (step 3b); if not → directional demand from Google Autocomplete + SERP probes (default).
    `SEMRUSH_API_KEY`/`AHREFS_API_TOKEN`/`KEYWORD_ANALYSIS_API_KEY`/`KEYWORDS_EVERYWHERE_API_KEY`
    are alternative providers (out-of-band, not implemented in the adapter).
  - `APIFY_API_TOKEN` — if set → hostile-site sitemap-crawl / Reddit-mining fallback; if not →
    the keyless `crawl_sitemap.py` + `serp_probe.py` path (default).

## Notes & edge cases

- **Degrade gracefully on volume** — without a paid keyword API, per-variation volume is
  directional (Autocomplete presence + SERP-result existence + competitor page count as a
  demand proxy); mark such numbers as estimates.
- **pSEO ≠ content spinning** — each pattern must have a real data axis with genuine demand
  and a differentiated answer; flag patterns that would produce thin pages.
- **Cap discovery** (top N per pattern) to control crawl cost; note total est. page count
  rather than enumerating every URL.
- **CMS feasibility** constrains which patterns are realistic — surface it in the roadmap.
- **Anti-block**: scripts use a browser UA + 429 backoff; for volume, route through
  Robomotion Proxy + geo (the `robomotion-serp` package).
