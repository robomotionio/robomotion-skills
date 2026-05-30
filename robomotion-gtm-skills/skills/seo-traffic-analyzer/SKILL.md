---
name: seo-traffic-analyzer
description: Analyze a website's organic-search visibility, keyword rankings, traffic estimates, and competitive positioning using only SERP probes, public pages, SimilarWeb free tier, and site: queries — no paid SEO subscription. Produces a full SEO report with content-gap analysis. The explicitly free counterpart to seo-domain-analyzer; the agent buckets keywords, finds gaps, and writes the report.
metadata:
  version: 1.1.0
  category: competitive-intel
  type: capability
---

# SEO Traffic Analyzer

The explicitly **free, no-paid-tool** SEO skill. Everything is serp-derived by design via
`serp_probe.py`, the SimilarWeb free page, and Wayback; paid tools are optional supplements.
**You, the agent, organize keywords into buckets, find content gaps, and write the report.**

## When to use

- "Analyze SEO and traffic for [domain]." / "Where does [domain] rank for [keywords]?"
- "Compare [domain]'s SEO against [competitors]." / "Find content gaps vs competitors."
- The free SEO layer for competitive landscape work and `company-current-gtm-analysis`.

## How to run

### 1. Site indexation & structure (keyless)

```bash
python3 ${SKILL_DIR}/scripts/serp_probe.py site --domain example.com \
  --output ${WORKSPACE}/indexed.json
# also probe structure with refined site: queries via the search subcommand, e.g.
python3 ${SKILL_DIR}/scripts/serp_probe.py search --query "site:example.com blog" \
  --output ${WORKSPACE}/blog_pages.json
```

### 2. Keyword ranking probes (brand / category / problem / competitor buckets)

```bash
python3 ${SKILL_DIR}/scripts/serp_probe.py search --query "rpa platform" \
  --target-domain example.com --output ${WORKSPACE}/kw_category.json
```

Record presence / approximate position, ranking URL, and `co_ranking_domains` per keyword.
Auto-infer keywords from domain content + your knowledge if none are provided; expand
category/problem/brand variants yourself.

### 3. Traffic estimation

```bash
npx playwright install chromium   # first run only
node ${SKILL_DIR}/scripts/render_page.mjs \
  --url "https://www.similarweb.com/website/example.com/" --wait 6000 \
  --output ${WORKSPACE}/similarweb.json
python3 ${SKILL_DIR}/scripts/wayback_fetch.py --url https://example.com \
  --snapshots 5 --output ${WORKSPACE}/wb.json     # snapshot frequency = activity signal
```

Also use `serp_probe.py search --query '"example.com" -site:example.com'` for the referral
footprint. **Report traffic as labelled estimates;** if SimilarWeb is rate-limited, note
reduced confidence.

### 4. Backlink & authority signals (keyless)

Web-search for press mentions, awards, and directory listings (G2, Capterra, Product Hunt,
AlternativeTo); categorize the linking domains. Exact numbers need a paid source (optional).

### 4b. (Optional) Enrichment — measured metrics (paid, off by default)

This skill is free, no-paid-tool BY DESIGN; the keyless flow is and stays the DEFAULT.
**Only if** `DATAFORSEO_LOGIN`/`DATAFORSEO_PASSWORD` are set, the bundled DataForSEO adapter
can replace the labelled estimates with MEASURED traffic/authority/backlinks/ranked keywords:

```bash
python3 ${SKILL_DIR}/scripts/paid_seo.py domain --domain example.com \
  --output ${WORKSPACE}/paid_domain.json         # measured authority rank + organic traffic
python3 ${SKILL_DIR}/scripts/paid_seo.py ranked --domain example.com --limit 100 \
  --output ${WORKSPACE}/paid_ranked.json          # real ranking keywords + per-keyword volume
python3 ${SKILL_DIR}/scripts/paid_seo.py backlinks --target example.com \
  --output ${WORKSPACE}/paid_backlinks.json       # referring domains, backlinks, domain rank
```

If creds are absent the adapter prints "paid enrichment unavailable — keyless path still
applies" and exits non-zero **without breaking this flow** — skip it; the free report is
complete. When the JSON IS produced, merge it and **upgrade the "estimate" labels to
"measured"** (traffic, authority, exact backlink/referring-domain counts, ranking keywords).
The content-gap analysis remains the highest-value output regardless. (Semrush/Ahrefs are
alternative providers — not implemented in the adapter.)

### 5. Competitive comparison + content gaps

Repeat steps 1–2 per competitor; build a keyword × domain matrix. For gaps, probe
`serp_probe.py search --query "site:<competitor> [keyword]"` — keywords/topics where
competitors rank but the target doesn't, and missing content types (comparison pages, use
cases, calculators, integrations, case studies, glossary).

### 6. Report (you, the agent — no script)

Write the markdown report: executive summary, site indexation/structure, keyword rankings by
bucket, traffic estimates + sources, competitive comparison matrix, content-gap analysis,
SWOT-style assessment, and prioritized recommendations. Report positions as page-1
presence/approximate rank; traffic as labelled estimates.

## Outputs

- `${WORKSPACE}/indexed.json`, `kw_*.json`, `similarweb.json`, `wb.json` — collected signal.
- The SEO report (markdown) returned as result / saved to `--output_path` if provided.

## Credentials / env

- **Required:** none — the entire capability is serp + browser + Wayback + agent. Free by definition.
- **Optional:** `DATAFORSEO_LOGIN`/`DATAFORSEO_PASSWORD` enable the bundled
  `scripts/paid_seo.py` enrichment (Step 4b) — measured traffic/authority/backlinks/ranked
  keywords that upgrade the estimate labels to "measured". A bring-your-own Semrush/Ahrefs key
  (no Robomotion package — alternative, not wired into the adapter) or `APIFY_API_TOKEN`
  (Semrush/Ahrefs-scraper actor) are further options. The report is complete without any of them.

## Notes & edge cases

- Traffic estimates are rough and exact positions can't be pinned — report page-1 presence and
  approximate rank, label estimates, never present them as precise tool metrics.
- SimilarWeb free tier is rate-limited; if blocked, lean on search-volume inference + referral
  signals and note reduced confidence.
- Content-gap analysis is the highest-value output — comparison pages are usually the top-ROI
  gap for B2B SaaS.
- Results vary by geography/personalization — state the country/language assumption.
- Brand-keyword monitoring matters: if a competitor ranks/bids on the target's brand terms, flag it.
- `serp_probe.py` uses a keyless public HTML SERP endpoint that can rate-limit; in a Robomotion
  deployment swap it for the robomotion-serp Search node (proxy + geo).
