---
name: competitor-ad-intelligence
description: Scrape competitor ads from the Meta Ad Library and Google Ads Transparency Center, analyze creative patterns (hooks, formats, CTAs), reverse-engineer landing-page funnels, and produce a strategic teardown — positioning bets, vulnerabilities, creative white-space, and counter-plays. For paid/creative teams sizing up the competitive ad landscape before they launch or refresh.
metadata:
  version: 1.0.1
  category: ads
  type: composite
---

# Competitor Ad Intelligence

Composite teardown: **Meta scrape + Google scrape → creative-pattern analysis → LP/funnel
reconstruction → strategic gap/vulnerability analysis → report**. Scripts do the
deterministic scraping/parsing; **you (the agent) do all clustering, scoring, funnel
inference, and the teardown narrative.**

## When to use

- "What ads are my competitors running?" / "Tear down `<competitor>`'s ad strategy."
- "Find new creative angles" / "Reverse-engineer `<competitor>`'s paid funnel."
- "What hooks/formats are dominant in our space?" / "Find weaknesses in their ad strategy."

## Sub-skills it chains

- **`google-ad-scraper`** capability (Google Transparency Center) — call its script by path.
- Bundled `scrape_meta_ads.mjs` (Meta Ad Library) and `fetch_landing_page.py` (LP extract).

## How to run

One-time browser setup:

```bash
cd ${SKILL_DIR}/scripts && npm install && npx playwright install chromium
```

### 1 — Scrape ads per competitor (channels: meta / google / both)

```bash
# Meta Ad Library (this skill's bundled scraper)
node ${SKILL_DIR}/scripts/scrape_meta_ads.mjs --query "Notion" --country US --max-ads 60 --output ${WORKSPACE}/meta_notion.json

# Google Ads Transparency Center (reuse the google-ad-scraper capability)
node ${SKILL_DIR}/../google-ad-scraper/scripts/scrape_google_ads.mjs --domain notion.so --max-ads 50 --country US --output ${WORKSPACE}/google_notion.json
```

Captured per Meta ad: `libraryId, visualType, adText, cta, landingUrl, startDate,
platforms, daysRunning`. **`daysRunning` (first-seen → still-running) is the key
"what's working" signal — longer runs weight higher in the teardown.**

If a library blocks the scraper: **if `APIFY_API_TOKEN` is set → use the Apify ad-library
actor (or the Apify fallback in `google-ad-scraper`) for the blocked library; if not →
degrade to a `site:facebook.com/ads/library "<competitor>"` / `site:adstransparency.google.com
"<domain>"` web search (default; less structured, lower coverage — note it).** That degrade
search itself can use the optional SERP upgrade: **if `DATAFORSEO_LOGIN`/`DATAFORSEO_PASSWORD`
(or `SERPER_API_KEY`) is set → structured SERP API; else → the agent's keyless web search.**

### 2 — Cluster hooks, tabulate formats & CTAs (you, the agent)

Read the scraped JSON. Classify each ad's hook into
`Fear / Outcome / Question / Social-proof / Contrarian / Empathy / Product-led`; build
hook-distribution, format-distribution, and CTA-taxonomy tables per competitor. Surface
the longest-running ads.

### 3 — Fetch each unique landing page

```bash
# Collect unique landingUrl values into urls.txt, then:
python3 ${SKILL_DIR}/scripts/fetch_landing_page.py --urls ${WORKSPACE}/urls.txt --output ${WORKSPACE}/lps.json
```

Returns hero/subhead/primary-CTA/proof/form-field-count/page stats per LP. For JS-rendered
or gated LPs, escalate that URL to a Playwright fetch (reuse `scrape_meta_ads.mjs`'s browser
pattern) or capture a screenshot so visual continuity reflects what a clicker sees.

### 4 — Cluster into campaigns, infer funnels & budget, write the teardown (you)

Cluster ads into inferred campaigns by **LP destination + theme**. Per campaign infer
intent, persona, positioning bet, hook, conversion path, longevity, and A/B signals; infer
platform budget allocation from ad volume × platform. Then do the strategic pass: creative
white-space, overcrowded angles, format gaps, and vulnerabilities. In **deep** mode, add
historical positioning change by fetching `web.archive.org` snapshots of competitor LPs
(`fetch_landing_page.py --url "https://web.archive.org/web/<ts>/<lp>"`) and propose
counter-plays with headline/body/LP strategy.

### 5 — Render

Write `competitor-ad-intel-<YYYY-MM-DD>.md` to `${WORKSPACE}` and attach it to the Agent
Teams channel. Optionally persist scraped ads (dedup by `libraryId`/`creativeId` + LP) so
monitoring across runs shows true new vs. retired campaigns.

## Outputs

`competitor-ad-intel-<YYYY-MM-DD>.md` — coverage summary, Meta + Google ad analysis (hook
distribution, longest-running ads, CTA taxonomy, format distribution), per-campaign funnel
map, budget-allocation inference, creative gap analysis, vulnerability report, and (deep
mode) counter-plays.

## Credentials / env

- **Required:** none for the scripts — both ad libraries are public; Playwright + a proxy
  carry the scrape. Hook clustering, funnel inference, and the teardown are the agent's
  reasoning (no LLM key needed in scripts).
- **Optional (each with a keyless default fallback):**
  - `APIFY_API_TOKEN` — if set → Apify ad-library actor when a library page is too anti-bot;
    else → the keyless Playwright scrapers, degrading to `site:` web search (default).
  - `SUPABASE_URL`/`SUPABASE_KEY` — if set → persist ad history for cross-run new-vs-retired
    monitoring; else → single-run workspace JSON (default).
  - `DATAFORSEO_LOGIN`/`DATAFORSEO_PASSWORD` (or `SERPER_API_KEY`) — if set → structured SERP
    API for the `site:` degrade/archive searches; else → the agent's keyless web search
    (default).
  - `HTTPS_PROXY` — Robomotion Proxy for the Playwright scrapers.

## Notes & edge cases

- Meta Ad Library and Google Transparency Center are heavy JS SPAs with active anti-
  scraping — randomize timing, rotate the proxy, set the library `country` to your target
  market. If blocked, degrade to `site:` snippets and note lower coverage.
- Apify Meta-Ad-Library actors are unreliable under Meta's countermeasures — last resort.
- Longevity is the load-bearing signal; capture `daysRunning` per ad.
- Dedup ads by library/creative id + LP across runs so monitoring is accurate.
