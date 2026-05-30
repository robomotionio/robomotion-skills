---
name: google-search-ads-builder
description: Build a complete, import-ready Google Search Ads campaign from scratch — deep keyword research (competitor mining, review/community/HN language, site audit, autocomplete), keyword architecture with funnel + intent classification, ad-group structure, RSA copy (15 headlines / 4 descriptions per group), negative-keyword lists, bid strategy, and a Google Ads Editor import CSV. For early-stage teams who'd otherwise waste their first $5K.
metadata:
  version: 1.0.1
  category: ads
  type: composite
---

# Google Search Ads Builder

Composite: **keyword research → architecture → structure → copy → negatives → bid →
export.** Scripts cover the deterministic research primitives (HN terminology, autocomplete
expansion) and the export (RSA-limit validation + Google Ads Editor CSV). **The
architecture, intent/funnel classification, ad-group design, RSA copywriting, negatives,
and bid strategy are the agent's reasoning** — then validated and serialized by the export
script.

## When to use

- "Set up Google Search Ads for `<product>`" / "Build a PPC campaign."
- "Do keyword research for Google Ads" / "What keywords should we bid on?"
- "Generate Google Ads copy" / "I need an import file for Google Ads Editor."

## How to run

### 1 — Keyword research

Seeds + competitor/review/community mining are agent-driven via web search (Robomotion
Proxy, `geo`): `site:<competitor>`, `<competitor> alternative/vs`, `best <category> tools`,
`site:g2.com`/`site:capterra.com`, `site:reddit.com`. **SERP path: if `DATAFORSEO_LOGIN`/
`DATAFORSEO_PASSWORD` (or `SERPER_API_KEY`) is set → structured SERP API and real keyword
volume/difficulty; if not → the agent's keyless web search with directional volume (default).** Reuse the **`google-ad-scraper`**
capability for competitor ad terms, and **`fetch_landing_page.py`** from
`../ad-to-landing-page-auditor/scripts/` (or web search) for the own-site / competitor
content audit.

Deterministic research primitives:

```bash
# Technical-buyer framing from Hacker News (keyless)
python3 ${SKILL_DIR}/scripts/hn_terms.py --query "workflow automation" --days 365 --output ${WORKSPACE}/hn.json

# Autocomplete / modifier / long-tail expansion (keyless Google Suggest)
python3 ${SKILL_DIR}/scripts/autocomplete_expand.py --seeds "workflow automation,rpa software" \
  --geo US --alpha --output ${WORKSPACE}/expanded.json
```

For Reddit/review depth beyond search: **if `APIFY_API_TOKEN` is set → use an Apify actor
(better depth); if not → degrade to `site:` web search over public pages (default).**

### 2 — Architecture, structure, copy, negatives, bid (you, the agent)

From the pooled keywords: classify funnel stage + intent, estimate competitive density (from
SERP density + autocomplete + HN/review frequency — **paid keyword-volume/difficulty is an
optional enrichment: if `DATAFORSEO_*` is set use its real metrics, else derive directional
volume from the keyless signals**), score keywords, pull
a quick-wins list. Build ad groups (**≤15 single-theme keywords each, one LP per group**).
Write **3 RSAs per ad group: 15 headlines ≤30 chars, 4 descriptions ≤90 chars.** Build
negatives (universal + category + intent + competitor + cross-ad-group). Recommend bid
strategy + budget split by `monthly_budget` tier.

Emit the campaign as a JSON tree (see `build_import_csv.py` header for the shape) to
`${WORKSPACE}/campaign.json`.

### 3 — Validate limits + emit the import CSV

```bash
python3 ${SKILL_DIR}/scripts/build_import_csv.py --input ${WORKSPACE}/campaign.json \
  --csv ${WORKSPACE}/google-ads-import-$(date +%F).csv \
  --report ${WORKSPACE}/validation.json
```

This **enforces RSA char limits and ad-group caps before writing the CSV** so the import
won't reject rows. If `ok:false`, fix the flagged headlines/descriptions and rerun — the CSV
is not written on validation failure (exit code 1).

### 4 — Render the strategy doc

Write `google-search-campaign-<YYYY-MM-DD>.md` to `${WORKSPACE}` (overview, research
summary, competitive density map, campaign tree, keywords with match type/funnel stage/
intent/priority, RSA copy, negatives, bid + budget split, top-10 quick-wins, launch
checklist) and attach both it and the CSV to the Agent Teams channel.

## Outputs

- `google-search-campaign-<YYYY-MM-DD>.md` — the strategy doc.
- `google-ads-import-<YYYY-MM-DD>.csv` — Google Ads Editor import file.

## Credentials / env

- **Required:** none — keyword research runs on web search + the keyless HN API + Google
  Suggest; the export is stdlib. Architecture/copy/bid are the agent's reasoning.
- **Optional (each with a keyless default fallback):**
  - `APIFY_API_TOKEN` — if set → Apify Reddit/review actor for depth; else → `site:` web
    search over public pages (default).
  - `DATAFORSEO_LOGIN`/`DATAFORSEO_PASSWORD` (or `SERPER_API_KEY`) — if set → structured SERP
    API + real keyword volume/difficulty; else → keyless web search + directional volume from
    SERP density + Google Suggest + HN/review frequency (default).
  - `HTTPS_PROXY` — Robomotion Proxy for geo-correct SERP/autocomplete/research.

## Notes & edge cases

- Paid search-volume is optional enrichment: with `DATAFORSEO_*` set, use real keyword
  volume/difficulty; without it (default), derive volume/competition directionally from SERP
  density + autocomplete + HN/review frequency.
- RSA limits are enforced by `build_import_csv.py` (headline ≤30, description ≤90); fix and
  rerun on failure rather than shipping a rejecting import.
- Cap each ad group at 15 single-theme keywords; cross-negative between groups to stop
  cannibalization.
- Use a proxy + `geo` so SERP/review/autocomplete results reflect the target market.
