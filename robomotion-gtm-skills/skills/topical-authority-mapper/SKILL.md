---
name: topical-authority-mapper
description: Map complete topic clusters (pillar pages, spoke articles, supporting glossary/FAQ) and the internal-linking architecture for a subject area, so a site builds the topical depth Google rewards. Catalogs existing + competitor content, expands the subtopic universe via Google Autocomplete, then the agent clusters it into a pillar/cluster tree, gap matrix, and a capacity-bound content calendar. Keyless (no paid SEO API required).
metadata:
  version: 1.1.1
  category: seo
  type: composite
---

# Topical Authority Mapper

Build genuine topical authority: a pillar→cluster→supporting architecture with an
internal-linking plan and a capacity-bound calendar — not a pile of unrelated posts.
The bundled scripts do the deterministic I/O (crawl inventories, expand keywords,
probe SERPs); **you, the agent, do the clustering, architecture design, gap scoring,
and calendar sequencing.**

## When to use

- "What content should we create to dominate [topic]?", "build a topic-cluster strategy",
  "map our topical authority for [category]", "create a content calendar based on clusters".
- Pairs with `seo-opportunity-finder` (gap shortlist) and feeds `seo-content-engine`.

## How to run

All scripts are Python 3 stdlib only (no install). Use `${WORKSPACE}` for scratch files.

### 1. Catalog existing + competitor content (deterministic crawl)

```bash
python3 ${SKILL_DIR}/scripts/crawl_sitemap.py --domain yoursite.com \
  --max-urls 2000 --output ${WORKSPACE}/inventory_self.json
python3 ${SKILL_DIR}/scripts/crawl_sitemap.py --domain competitor1.com \
  --max-urls 2000 --output ${WORKSPACE}/inventory_comp1.json
```

`crawl_sitemap.py` reads robots.txt `Sitemap:` directives → sitemap.xml (recursing
indexes) → RSS/Atom → blog-index HTML, returning `{url, lastmod, title}` rows. Add
`--titles` to fetch `<title>` for a small set when the sitemap has no titles.

### 2. Expand the subtopic universe (Google Autocomplete — keyless)

```bash
python3 ${SKILL_DIR}/scripts/expand_keywords.py \
  --seeds "sales automation,lead scoring" \
  --modifiers base,question,comparison,commercial,guide \
  --max-per-seed 120 --output ${WORKSPACE}/subtopics.json
```

This is the keyword-research primitive — prefix/suffix expansion ("what/how/why/best/
vs/guide/...") around each target topic. Returns the deduplicated suggestion set.

### 3. Probe demand / competitor coverage (directional, keyless)

```bash
# Confirm variations return real results (demand proxy) + competitor rank spot-check
python3 ${SKILL_DIR}/scripts/serp_probe.py --queries-file ${WORKSPACE}/subtopics.json \
  --max-results 10 --output ${WORKSPACE}/probes.json
# site: indexation count as a coverage proxy
python3 ${SKILL_DIR}/scripts/serp_probe.py --query "site:competitor1.com/blog" --count-only
```

### 3b. (Optional) Enrichment — measured volume/difficulty (paid, off by default)

The Autocomplete + SERP demand proxy is the DEFAULT and the interlinked architecture is
fully keyless. **Only if** `DATAFORSEO_LOGIN`/`DATAFORSEO_PASSWORD` are set, run the bundled
DataForSEO adapter to attach REAL per-subtopic volume + difficulty (and optionally the
competitor's ranked keywords), so the gap matrix's volume × difficulty columns are measured:

```bash
python3 ${SKILL_DIR}/scripts/paid_seo.py keywords \
  --keywords "subtopic 1,subtopic 2,subtopic 3" \
  --output ${WORKSPACE}/paid_subtopics.json     # real volume, CPC, competition, difficulty
python3 ${SKILL_DIR}/scripts/paid_seo.py ranked --domain competitor1.com --limit 100 \
  --output ${WORKSPACE}/paid_ranked_comp1.json   # competitor's actual ranking subtopics
```

If creds are absent the adapter prints "paid enrichment unavailable — keyless path still
applies" and exits non-zero **without breaking this flow** — skip it and proceed keyless.
When the JSON IS produced, join measured volume/difficulty onto each subtopic in the gap
matrix and **upgrade the "directional volume" labels to "measured"**; priority scoring is
unchanged but its volume (25%) and difficulty inputs sharpen. (Semrush/Ahrefs are
alternative providers, not implemented in the adapter.)

### 4. Agent builds the map (reasoning — no script)

Read the inventories, subtopics, and probes, then:
- classify your + competitor pages into topics; flag thin/outdated/orphan pages;
- semantically **cluster** the subtopic universe (shared root, intent, hierarchy);
- design the pillar→cluster→supporting tree per target topic, assign content type +
  word-count target, and lay out internal links (pillar↔clusters, cluster↔cluster,
  supporting→clusters) with specific anchor text;
- build the coverage gap matrix (subtopic × your content × each competitor × volume ×
  difficulty → gap flag) and priority-score each piece (volume 25%, competitive gap 25%,
  intent 20%, cluster completeness 15%, effort 15%);
- sequence the calendar against `content_capacity` (front-load pillars before clusters).

## Outputs

- Topical Authority Map (workspace markdown): per topic a pillar→cluster→supporting tree;
  per piece a target keyword (+ directional volume), title, type, word-count, links-to/from
  with anchor text, priority; an internal-linking matrix; a month-by-month calendar; and a
  coverage gap report.
- For 3+ topic areas: a `content-calendar-[YYYY-MM-DD].csv` export (the agent writes it).
- Supporting JSON: `inventory_*.json`, `subtopics.json`, `probes.json`.

## Credentials / env

- **Required:** none for the scripts — the whole crawl/expand/probe flow is keyless and the
  default. (Synthesis/clustering is done by you, the host agent — no LLM key in scripts.)
- **Optional (each with a keyless fallback):**
  - `DATAFORSEO_LOGIN`/`DATAFORSEO_PASSWORD` — if set → the bundled `scripts/paid_seo.py`
    adapter (DataForSEO, HTTP Basic auth) returns measured per-subtopic volume/difficulty;
    if not → directional volume from Google Autocomplete + SERP probes (default).
    `SEMRUSH_API_KEY`/`AHREFS_API_TOKEN`/`KEYWORD_ANALYSIS_API_KEY`/`KEYWORDS_EVERYWHERE_API_KEY`
    are alternative providers (out-of-band, not implemented in the adapter).
  - `APIFY_API_TOKEN` — if set → Reddit question-mining / hostile-site crawl fallback; if not →
    the keyless `crawl_sitemap.py` + `serp_probe.py` path (default).

## Notes & edge cases

- **Authority is depth, not breadth** — the interlinked architecture + anchor-text plan is
  the value and is fully keyless; only per-subtopic volume granularity degrades without a paid API.
- **Autocomplete is the keyword primitive** — lean on `expand_keywords.py` before any paid API.
- **Mark volumes as directional** when no keyword API is connected; prioritize on
  competitive-gap + intent rather than raw volume in that case.
- **Calendar is capacity-bound** — never schedule more pieces/month than `content_capacity`.
- **Anti-block**: SERP/sitemap fetches use a browser User-Agent and back off on 429; throttle
  via `--delay` when crawling many competitors. For volume scraping in production, route through
  Robomotion Proxy with geo-targeting (the Robomotion `robomotion-serp` package).
- **Re-run quarterly**; after each content batch, update the map with published URLs + links.
