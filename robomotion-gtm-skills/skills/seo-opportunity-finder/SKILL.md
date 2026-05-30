---
name: seo-opportunity-finder
description: Find the highest-leverage quick-win SEO content opportunities by comparing a site's existing content against competitor topic coverage, then return a prioritized Top 10 list of posts to write or update — filtered for commercial intent against the ICP. A lighter, faster cousin of seo-content-audit focused purely on the gap-to-opportunity list. Keyless (paid SEO APIs optional); feeds seo-content-engine and topical-authority-mapper.
metadata:
  version: 1.1.1
  category: seo
  type: composite
---

# SEO Opportunity Finder

For seed / Series A teams that want to start winning organic traffic without guessing.
Scripts catalog your content, expand the keyword universe, and probe competitor coverage;
**you, the agent, classify gaps, score commercial intent, and build the shortlist + calendar.**

## When to use

- "Find our SEO content gaps vs competitors", "what topics should we write about to rank?",
  "we're starting a blog — where do we focus first?", "what keywords is [competitor] ranking
  for that we're missing?".
- A faster cousin of `seo-content-audit`; feeds `seo-content-engine` and `topical-authority-mapper`.

## How to run

Python 3 stdlib only. Use `${WORKSPACE}` for scratch files.

### 1. Catalog YOUR existing content (deterministic)

```bash
python3 ${SKILL_DIR}/scripts/crawl_sitemap.py --domain yoursite.com \
  --max-urls 3000 --titles --output ${WORKSPACE}/inventory_self.json
```

Knowing what you already have is what makes the recommendations non-redundant — don't skip it.

### 2. Expand the keyword universe + probe competitor footprint (keyless)

```bash
python3 ${SKILL_DIR}/scripts/expand_keywords.py \
  --seeds "in-scope topic 1,in-scope topic 2" \
  --modifiers base,question,comparison,commercial,guide \
  --output ${WORKSPACE}/keywords.json

# Competitor top-ranking pages + site: indexation as a coverage proxy
python3 ${SKILL_DIR}/scripts/serp_probe.py --queries-file ${WORKSPACE}/keywords.json \
  --max-results 10 --output ${WORKSPACE}/serp.json
python3 ${SKILL_DIR}/scripts/serp_probe.py --query "site:competitor1.com/blog" --count-only
```

Optionally catalog competitor inventories with `crawl_sitemap.py` too. Competitor
DR/traffic precision needs a paid SEO API (no Robomotion package) — degrade to these
directional SERP signals when absent and label them as estimates.

### 3. (Optional) inspect a few competitor pages

```bash
python3 ${SKILL_DIR}/scripts/fetch_page.py --url https://competitor1.com/winning-post \
  --output ${WORKSPACE}/comp_page.json
```

### 3b. (Optional) Enrichment — measured metrics (paid, off by default)

Keyless is the DEFAULT. **Only if** `DATAFORSEO_LOGIN`/`DATAFORSEO_PASSWORD` are set, run
the bundled DataForSEO adapter to swap directional volume estimates for MEASURED data so
the Top-10 can be prioritized on real volume/difficulty instead of SERP-presence proxies:

```bash
python3 ${SKILL_DIR}/scripts/paid_seo.py keywords \
  --keywords "opportunity kw 1,opportunity kw 2,opportunity kw 3" \
  --output ${WORKSPACE}/paid_keywords.json     # real volume, CPC, competition, difficulty
python3 ${SKILL_DIR}/scripts/paid_seo.py domain --domain competitor1.com \
  --output ${WORKSPACE}/paid_comp.json          # competitor authority/traffic (not directional)
```

If creds are absent the adapter prints "paid enrichment unavailable — keyless path still
applies" and exits non-zero **without breaking this flow** — skip it and proceed keyless.
When the JSON IS produced, merge measured volume/difficulty into each opportunity row and
**upgrade the "est. volume" / "directional" labels to "measured"**; keep the commercial-
intent filter as the differentiator regardless. (Semrush/Ahrefs are alternative providers,
not implemented in the adapter.)

### 4. Agent identifies gaps + builds the opportunity list

Diff your inventory vs competitor coverage and classify each gap:
- **hard gap** (competitor has it, you have nothing → High),
- **soft gap** (you have thin/old content → Medium),
- **positioning gap** (competitor owns an ICP-exact cluster → High),
- **informational gap** (high traffic, low commercial intent → Low).

Score commercial intent 1–5 against the ICP; **keep only ≥ 3** — the intent filter is the
differentiator, not raw volume. Output the Top 10 opportunities, quick-win updates, and a
90-day content calendar.

## Outputs

- SEO Opportunity Report (workspace markdown): your content snapshot; competitor benchmarks
  (directional unless paid API); Top 10 opportunities (each: keyword target, why-it-matters,
  competitor owning it, est. volume, commercial-intent score 1–5, recommended format, effort);
  quick-win updates; a 90-day content calendar.
- Raw artifacts: `inventory_self.json`, `keywords.json`, `serp.json`.

## Credentials / env

- **Required:** none for the scripts — catalog, keyword expansion, and SERP probes are keyless
  and the default. (Gap classification, intent scoring, and synthesis are done by you, the agent.)
- **Optional (each with a keyless fallback):**
  - `DATAFORSEO_LOGIN`/`DATAFORSEO_PASSWORD` — if set → the bundled `scripts/paid_seo.py`
    adapter (DataForSEO, HTTP Basic auth) returns measured volume/difficulty + competitor
    DR/traffic; if not → directional benchmarks from SERP probes (default).
    `SEMRUSH_API_KEY`/`AHREFS_API_TOKEN`/`SIMILARWEB_API_KEY`/`KEYWORD_ANALYSIS_API_KEY` are
    alternative providers (out-of-band, not implemented in the adapter).
  - `APIFY_API_TOKEN` — if set → hostile-site catalog fallback; if not → the keyless
    `crawl_sitemap.py` + `serp_probe.py` path (default).

## Notes & edge cases

- **Don't start from a blank keyword list** — Step 1 (your inventory) makes recommendations non-redundant.
- **Commercial-intent filter is the differentiator** — prioritize gaps scoring ≥ 3, not raw volume.
- **Degrade gracefully**: without a paid API, competitor DR/traffic are directional (SERP rank
  presence + indexation counts); label them estimates.
- **Output is intentionally a shortlist** (Top 10 + quick wins) — keep it actionable, not exhaustive.
- **Anti-block**: scripts use a browser UA + 429 backoff; for volume, route through Robomotion Proxy + geo.
