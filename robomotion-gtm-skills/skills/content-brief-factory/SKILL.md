---
name: content-brief-factory
description: Generate detailed, differentiated content briefs at scale (1–50 keywords per run). Each brief carries real SERP analysis, a competing-page breakdown, a unique angle mined from real customer language, an internal-linking plan, and SERP-feature targets — so a writer knows exactly what to create and why it will rank. A composite: the agent runs SERP/customer-voice steps and synthesizes the brief; bundled keyless scripts handle coverage-matching and competing-page stats.
metadata:
  version: 1.0.1
  category: content
  type: composite
---

# Content Brief Factory

A composite over `site-content-catalog`, `robomotion-serp` Search/Auto-Complete, and
customer-voice mining. **You (the agent) synthesize each brief**; two bundled keyless
scripts do the deterministic glue (coverage match + competing-page stats).

## When to use

- "Create content briefs for these keywords / our Q2 calendar / our pSEO templates."
- "Generate 20 briefs from this keyword list" / "what should we write about [topic]?"
- Downstream of `site-content-catalog` (coverage) and any keyword-discovery skill.

## How to run

### 1 — Existing-coverage check
Catalog the site, then match keywords against it:

```bash
# (a) inventory the site
python3 ${SKILL_DIR}/../site-content-catalog/scripts/site_catalog.py \
  --domain example.com --deep 0 --output ${WORKSPACE}/catalog.json

# (b) normalize keywords + flag new vs update + internal-link candidates
python3 ${SKILL_DIR}/scripts/load_keywords.py \
  --input ${WORKSPACE}/keywords.csv --catalog ${WORKSPACE}/catalog.json \
  --output ${WORKSPACE}/coverage.json
```

### 2 — SERP analysis (agent, via serp)
Per keyword, run `robomotion-serp` **Search** (localized, top-10) → ranked
`{title, description, url}`, and **Auto Complete** to mine PAA-style related queries. This is
the keyless default. If `DATAFORSEO_LOGIN`/`DATAFORSEO_PASSWORD` (or `SERPER_API_KEY`) is set
→ pull the SERP from that paid API instead for richer/cleaner top-10 results; if not set →
keyless `robomotion-serp` (the default). Volume/difficulty have no free source — degrade to
serp-derived signals and label numbers as estimates.

### 3 — Competing-page analysis
Feed the top SERP URLs to the page-stats helper:

```bash
python3 ${SKILL_DIR}/scripts/fetch_pages.py \
  --input ${WORKSPACE}/serp_top10.json --max 5 --output ${WORKSPACE}/pages.json
```

Emits per-page `{title, content_type, word_count, headings, image_count, list_count,
link_count, published_hint}` + `avg_word_count`. For anti-bot pages, the agent escalates to
`web-automation` + Robomotion Proxy.

### 4 — Customer-language mining (agent)
Reddit + reviews for the topic → real questions, pain language, misconceptions, quotable
proof. Lighter path: `robomotion-serp` Search `site:reddit.com <topic>` + Extract Content.
At scale / hostile sites: Apify review/Reddit actor (`APIFY_API_TOKEN`).

### 5 — Synthesize each brief (you)
Fold landscape + gap + customer quotes + ICP + brand voice into: metadata, search-landscape
table, SERP-feature targets, differentiation angle with quotes, recommended outline,
internal-linking plan (from `coverage.json`), content requirements, competitive-advantage
checklist. For covered keywords, emit an **update** brief, not a new-page brief.

### 6 — Batch output
One markdown brief per keyword + a ranked summary table + CSV. Persist to Airtable/Supabase
for the editorial calendar if asked.

`--help` is available on both bundled scripts.

## Outputs

One markdown brief per keyword; batch runs add a ranked summary table + CSV. Saved to
workspace / Agent Teams channel.

## Credentials / env

- **Required:** none — serp Search/Auto-Complete + the bundled keyless scripts cover the
  core; the agent is the synthesis engine.
- **Optional:**
  - `DATAFORSEO_LOGIN`/`DATAFORSEO_PASSWORD` (or `SERPER_API_KEY`) — paid SERP for step 2.
    If set → cleaner/richer top-10 SERP. If not → keyless `robomotion-serp` Search +
    Auto-Complete (the default).
  - `APIFY_API_TOKEN` — Reddit + review-site scraping at scale (hostile-site fallback).
    If set → at-scale voice mining. If not → degrade to serp `site:` searches +
    `web-automation` with thinner voice mining (the default).
  - `ANTHROPIC_API_KEY` / `OPENAI_API_KEY` — not used by any script (the agent is the model).
  - A paid SEO-metrics API (Semrush/Ahrefs/DataForSEO) for volume/difficulty — no Robomotion
    package; out-of-band optional enrichment only. Absent → label metrics as serp-derived
    estimates (the default).

## Notes & edge cases

- A great brief states what ranks, why it wins, the gap, the customer language proving the
  gap matters, and how to structure a page that beats it.
- Run keywords in batch; cap concurrency and route through Robomotion Proxy to avoid blocks.
- Volume/difficulty are best-effort without a paid API — label them estimates.
