---
name: programmatic-seo-spy
description: Reverse-engineer competitors' programmatic SEO — crawl their sitemaps, cluster URLs into pattern types (vs/, integrations/, for-{industry}/, use-cases/, glossary/, tools/), estimate page count per pattern, sample template quality, infer which patterns drive traffic, and surface the white-space / variation / quality gaps you can exploit. Recon step before a buildout; feeds programmatic-seo-planner. Keyless (paid traffic APIs optional).
metadata:
  version: 1.1.1
  category: seo
  type: composite
---

# Programmatic SEO Spy

Competitive pSEO recon. The scripts crawl sitemaps, cluster URLs into pattern buckets,
and pull template signals from sample pages; **you, the agent, classify programmatic-vs-
editorial, score template quality, infer traffic, and rank the gaps.**

## When to use

- "What programmatic SEO are competitors doing?", "reverse-engineer competitor SEO pages",
  "which pSEO patterns work in our space?", "find pSEO gaps competitors are missing",
  "analyze competitor URL structure".
- Recon before a buildout — feeds `programmatic-seo-planner` (demand validation + templates).

## How to run

Python 3 stdlib only. Use `${WORKSPACE}` for scratch files.

### 1. Crawl each competitor's URLs (deterministic)

```bash
python3 ${SKILL_DIR}/scripts/crawl_sitemap.py --domain competitor1.com \
  --max-urls 5000 --output ${WORKSPACE}/urls_comp1.json
```

Reads robots.txt `Sitemap:` → sitemap.xml (recursing indexes) → RSS → blog-index HTML.

### 2. Cluster URLs into pSEO patterns (deterministic)

```bash
python3 ${SKILL_DIR}/scripts/cluster_url_patterns.py \
  --input ${WORKSPACE}/urls_comp1.json \
  --output ${WORKSPACE}/patterns_comp1.json
```

Buckets URLs by path regex into vs/, alternatives/, integrations/, for_industry/,
use_cases/, templates/, glossary/, tools/, location/ — excluding editorial /blog/, /tag/.
Per pattern: page count, distinct axis values, URL-consistency score, sample URLs.

### 3. Spot-check traffic / indexation (directional, keyless)

```bash
# site: indexation count per pattern as a coverage/traffic proxy
python3 ${SKILL_DIR}/scripts/serp_probe.py --query "site:competitor1.com/vs" --count-only
# does a sample page actually rank for its implied keyword?
python3 ${SKILL_DIR}/scripts/serp_probe.py --query "competitor1 vs rival" \
  --rank-for competitor1.com --max-results 10
```

These are **directional** signals, not measured traffic. Exact ranking-keyword/traffic
data needs a paid domain-analytics API (no Robomotion package) — label estimates accordingly.

### 3b. (Optional) Enrichment — measured traffic per pattern (paid, off by default)

The keyless `site:` indexation + rank spot-checks are the DEFAULT. **Only if**
`DATAFORSEO_LOGIN`/`DATAFORSEO_PASSWORD` are set, run the bundled DataForSEO adapter to
attach REAL ranked-keyword/traffic data per competitor — turning the per-pattern "traffic"
column from directional to measured:

```bash
python3 ${SKILL_DIR}/scripts/paid_seo.py domain --domain competitor1.com \
  --output ${WORKSPACE}/paid_domain_comp1.json   # authority/rank + organic-traffic overview
python3 ${SKILL_DIR}/scripts/paid_seo.py ranked --domain competitor1.com --limit 100 \
  --output ${WORKSPACE}/paid_ranked_comp1.json    # which keywords/URLs actually drive traffic
```

If creds are absent the adapter prints "paid enrichment unavailable — keyless path still
applies" and exits non-zero **without breaking this flow** — skip it and proceed keyless.
When the JSON IS produced, bucket the `ranked_keywords` rows by URL pattern to attribute
measured traffic per pattern, and **upgrade the "directional" traffic labels to "measured"**
in the coverage matrix. Pattern detection/clustering is unchanged — only traffic attribution
sharpens. (Semrush/Ahrefs are alternative providers, not implemented in the adapter.)

### 4. Sample template quality (deterministic fetch, agent scores)

```bash
python3 ${SKILL_DIR}/scripts/fetch_page.py \
  --url https://competitor1.com/vs/page-a \
  --url https://competitor1.com/vs/page-b \
  --output ${WORKSPACE}/quality_vs.json
```

Returns word count, headers, lists, internal/external links, schema types per page.
Sample 3–5 pages per pattern (high/mid/low variation) — **don't exhaustively fetch.**
From these signals you score content depth, unique value, data richness, freshness,
internal linking, CTA, schema → a quality tier per pattern.

### 5. Agent builds the landscape report

Classify each cluster programmatic / semi-programmatic / editorial / auto-generated
(keep the (semi-)programmatic ones). Build the coverage matrix (competitors × patterns ×
you), then rank opportunities: white space (patterns nobody built), variation gaps
(missing variations in an existing pattern), quality gaps (thin/outdated patterns to
out-template), head-to-head. Output the report + action plan.

## Outputs

- Competitive pSEO landscape report (workspace markdown): per-competitor pattern inventory,
  coverage matrix across competitors + you, directional traffic estimates per pattern,
  template-quality tiers, and a ranked opportunity list with an action plan.
- Raw artifacts: `urls_*.json`, `patterns_*.json`, `quality_*.json`.

## Credentials / env

- **Required:** none for the scripts — detection, clustering, and quality-signal extraction
  are all keyless and the default. (Classification, quality scoring, and gap synthesis are
  done by you, the agent.)
- **Optional (each with a keyless fallback):**
  - `DATAFORSEO_LOGIN`/`DATAFORSEO_PASSWORD` — if set → the bundled `scripts/paid_seo.py`
    adapter (DataForSEO, HTTP Basic auth) returns measured per-domain traffic / ranked
    keywords; if not → directional traffic estimates from SERP signals (default).
    `SEMRUSH_API_KEY`/`AHREFS_API_TOKEN`/`SIMILARWEB_API_KEY` are alternative providers
    (out-of-band, not implemented in the adapter).
  - `APIFY_API_TOKEN` — if set → hostile-site crawl fallback; if not → the keyless
    `crawl_sitemap.py` + `serp_probe.py` path (default).

## Notes & edge cases

- **Pattern detection is equally good keyless** — only traffic attribution degrades without
  a paid API; label such numbers "directional".
- **Sample, don't exhaustively fetch** — 3–5 pages per pattern is enough for quality scoring; cap cost.
- **Exclude `/blog/`, tag/archive pages** — editorial/auto-generated noise (cluster script does this by default).
- **White-space patterns are the highest-value finding** but must be demand-validated before
  acting — hand off to `programmatic-seo-planner`'s volume step.
- **Anti-block**: scripts use a browser UA + 429 backoff; throttle via `--delay`. For volume,
  route through Robomotion Proxy + geo (the `robomotion-serp` package).
