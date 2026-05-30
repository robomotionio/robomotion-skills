---
name: seo-domain-analyzer
description: Build an SEO performance profile for a domain — authority/traffic estimates, organic keyword footprint, top pages, backlink/referring-domain signals, real per-keyword SERP rankings, and auto-discovered competitors from keyword overlap. Leads with keyless serp-derived ground truth; paid Semrush/Ahrefs APIs are optional enrichment. The agent labels estimates and writes the profile.
metadata:
  version: 1.1.0
  category: competitive-intel
  type: capability
---

# SEO Domain Analyzer

There is **no Semrush/Ahrefs Robomotion package**. The primary path is **serp-derived
ground truth** (real, free SERP positions) via `serp_probe.py`, the SimilarWeb free page
for a rough traffic estimate, and Wayback for traffic-trend signal. Paid SEO data is
optional enrichment. **You, the agent, label estimates vs measured and write the profile.**

## When to use

- "Pull SEO metrics for [domain]." / "How much organic traffic does [domain] get?"
- "Who are [domain]'s SEO competitors?" / "Where does [domain] rank for [keywords]?"
- The SEO data layer inside `company-current-gtm-analysis` or competitive landscape work.

## How to run

### 1. Domain overview — indexed footprint (keyless)

```bash
python3 ${SKILL_DIR}/scripts/serp_probe.py site --domain example.com \
  --output ${WORKSPACE}/indexed.json          # sample of indexed pages + URL patterns
```

### 2. Keyword rank verification — the ground truth (keyless)

For each keyword, run a real SERP and record the domain's position, URL, and co-ranking
competitors:

```bash
python3 ${SKILL_DIR}/scripts/serp_probe.py search --query "best rpa software" \
  --target-domain example.com --output ${WORKSPACE}/kw_rpa.json
```

`target_rank`, `target_url`, and `co_ranking_domains` are the trustworthy data points. If
`--keywords` are not provided, infer them from the domain's content (homepage/blog) and your
own knowledge, then probe each.

### 3. Traffic estimate — SimilarWeb free page (rendered)

```bash
npx playwright install chromium   # first run only
node ${SKILL_DIR}/scripts/render_page.mjs \
  --url "https://www.similarweb.com/website/example.com/" --wait 6000 \
  --output ${WORKSPACE}/similarweb.json
```

Read the visits/rank figures from `paragraphs`/`headings`. **Label them estimates.** If the
page blocks, note reduced confidence and lean on the SERP signals.

### 4. Traffic trend (Wayback snapshot frequency)

```bash
python3 ${SKILL_DIR}/scripts/wayback_fetch.py --url https://example.com \
  --snapshots 5 --output ${WORKSPACE}/wb.json    # snapshot cadence ≈ activity/growth signal
```

### 5. Backlink signals (best-effort, keyless)

`serp_probe.py search --query '"example.com" -site:example.com'` surfaces who links/mentions
the domain. Exact DR/referring-domain counts need a paid source (optional — see Credentials).

### 5b. (Optional) Enrichment — measured metrics (paid, off by default)

Everything above is keyless and yields a complete profile led by SERP ground truth. **Only
if** `DATAFORSEO_LOGIN`/`DATAFORSEO_PASSWORD` are set, run the bundled DataForSEO adapter to
replace the authority/traffic/backlink ESTIMATES with MEASURED numbers — this is the single
biggest precision upgrade for this skill (the estimate columns become real):

```bash
python3 ${SKILL_DIR}/scripts/paid_seo.py domain --domain example.com \
  --output ${WORKSPACE}/paid_domain.json        # measured authority rank + organic traffic
python3 ${SKILL_DIR}/scripts/paid_seo.py ranked --domain example.com --limit 100 \
  --output ${WORKSPACE}/paid_ranked.json         # real ranked-keyword footprint + volumes
python3 ${SKILL_DIR}/scripts/paid_seo.py backlinks --target example.com \
  --output ${WORKSPACE}/paid_backlinks.json      # referring domains, backlinks, domain rank
python3 ${SKILL_DIR}/scripts/paid_seo.py keywords --keywords "kw1,kw2,kw3" \
  --output ${WORKSPACE}/paid_keywords.json       # measured volume/CPC/difficulty for targets
```

If creds are absent the adapter prints "paid enrichment unavailable — keyless path still
applies" and exits non-zero **without breaking this flow** — skip it and keep the
serp-derived profile. When the JSON IS produced, merge it into the profile and **upgrade
every "estimate"/"DR proxy" label to "measured"** (authority/DR, organic traffic, keyword
footprint, exact referring-domain/backlink counts). The SERP rank ground truth still leads.
(Semrush/Ahrefs are alternative providers — not implemented in the adapter.)

### 6. Competitor discovery + comparison

Competitors = SERP co-rankers (step 2 `co_ranking_domains`) ∪ any provided list. Re-run
steps 1–2 (lighter) per competitor and build a comparison table.

### 7. Assemble (you, the agent — no script)

Build the JSON profile + markdown summary: domain metrics (authority/DR proxy, est. organic
traffic, keyword footprint, backlink signals, traffic trend), top pages, per-keyword rankings
with SERP competitors, and the competitor comparison. **Label every estimate as an estimate;**
lead with the SERP rank ground truth, not the guesses.

## Outputs

- `${WORKSPACE}/indexed.json`, `kw_*.json`, `similarweb.json`, `wb.json` — collected signal.
- `${WORKSPACE}/seo-profile-[domain].md` (+ JSON) — the profile (your synthesis).

## Credentials / env

- **Required:** none — the serp-derived path is keyless and produces a complete report.
- **Optional:** `DATAFORSEO_LOGIN`/`DATAFORSEO_PASSWORD` enable the bundled
  `scripts/paid_seo.py` enrichment (Step 5b) — measured authority/traffic/ranked-keywords/
  backlinks that upgrade the estimate labels to "measured". `APIFY_API_TOKEN` (Semrush/Ahrefs
  public-page scraper actors) and a bring-your-own Semrush/Ahrefs key (no Robomotion package
  — alternatives, not wired into the adapter) are further options. All enrichment-only; the
  skill degrades to serp signals.

## Notes & edge cases

- Traffic/authority numbers without a paid source are rough estimates — always label them;
  never present serp-derived guesses as exact metrics.
- SERP rank checks are the trustworthy ground truth; lead the report with those.
- `serp_probe.py` uses a keyless public HTML SERP endpoint that can rate-limit — it backs off;
  in a Robomotion deployment swap it for the robomotion-serp Search node (proxy + geo).
- Run competitors lighter (overview only) — full enrichment on many competitors is costly.
- SERP results are geo-personalized — note the country/language assumption in the report.
