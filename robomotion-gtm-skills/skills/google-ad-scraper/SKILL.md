---
name: google-ad-scraper
description: Scrape a competitor's active Google ads by domain (or company name) from the Google Ads Transparency Center and return structured creatives — copy, format, variants, destination URL, advertiser id. Keyless via headless Chromium. A reusable primitive for Ads composites (competitor-ad-intelligence, paid-channel-prioritizer, google-search-ads-builder).
metadata:
  version: 1.0.1
  category: ads
  type: capability
---

# Google Ad Scraper

Pull a company's currently-running Google ads from the **Google Ads Transparency
Center** (`adstransparency.google.com`). The Center is a public JS single-page app, so
the primary scraper drives a headless Chromium via Playwright. Keyless; deterministic
(scrape + parse only — no LLM).

## When to use

- "What Google ads is `<competitor.com>` running?"
- "Pull competitor ad creatives by domain."
- As a sub-capability whenever an Ads skill needs Google ad inventory for a company.

## How to run

One-time browser setup (per machine):

```bash
cd ${SKILL_DIR}/scripts && npm install && npx playwright install chromium
```

Primary path (keyless, Playwright):

```bash
# By domain (recommended)
node ${SKILL_DIR}/scripts/scrape_google_ads.mjs --domain hubspot.com --max-ads 50 --country US --output ${WORKSPACE}/google_ads.json

# By company name (resolves to an advertiser first; returns candidates if ambiguous)
node ${SKILL_DIR}/scripts/scrape_google_ads.mjs --company "HubSpot" --output summary
```

| Flag | Default | Meaning |
|---|---|---|
| `--domain` | — | target domain (recommended path) |
| `--company` | — | company name; resolved to an advertiser when no domain given |
| `--max-ads` | `50` | cap on creatives returned |
| `--country` | `US` | geo / library region (ad inventory is region-specific) |
| `--output` | `json` | `json` (stdout) / `summary` / a `.json` path |
| `--proxy` | `$HTTPS_PROXY` | proxy URL to dodge IP blocks / set geo (Robomotion Proxy) |
| `--timeout` | `45000` | per-navigation timeout (ms) |

At least one of `--domain` / `--company` is required.

### Fallback (only when the SPA blocks Playwright)

If a run is blocked by anti-bot: **if `APIFY_API_TOKEN` is set → degrade to the Apify
Google-ads actor (better against anti-bot); if not → the keyless Playwright path is the
default and you fall through to the `site:` discovery pass below.** Apify actor:

```bash
python3 ${SKILL_DIR}/scripts/apify_google_ads.py --domain hubspot.com --max-ads 50 --output ${WORKSPACE}/google_ads.json
```

For a quick keyless discovery pass when even that is unavailable, the host agent can
run a `site:adstransparency.google.com "<domain>"` web search and read snippets (lower
structure, lower coverage).

## Outputs

JSON array, one record per creative:
`{advertiserId, advertiserName, creativeId, originalUrl, imageUrl, variantFormat
(TEXT/IMAGE/VIDEO), variantContent, variants[], variantCount, startDate}`. When a
`--company` lookup is ambiguous, the script returns `{advertiser_candidates[], ads:[],
note}` instead so the caller can disambiguate. `--output summary` prints human-readable
lines.

## Credentials / env

- **Required:** none — the Transparency Center is public; Playwright + a proxy carry the
  scrape with no API key.
- **Optional (with a keyless default fallback):** `APIFY_API_TOKEN` — if set → Apify
  fallback actor when the SPA is too anti-bot for Playwright in a given run; else → the
  keyless Playwright scraper, degrading to a `site:` web search (default). `HTTPS_PROXY` —
  Robomotion Proxy for the Playwright scraper (also via `--proxy`).

## Notes & edge cases

- Google only surfaces ads from **verified** advertisers; small advertisers may not appear
  — the script returns an empty/partial set rather than erroring.
- Prefer `--domain`; `--company`→advertiser resolution depends on the SPA and can miss. If
  ambiguous, it returns the candidate advertiser list for you to disambiguate.
- Coverage skews to **recently active** ads; do not present it as full history.
- Set `--country`/proxy geo to the market of interest — inventory is region-specific.
- Throttle and rotate the proxy when looping over many domains; creatives are deduped by
  `creativeId`.
- The Transparency Center markup changes over time; if `variantContent`/`startDate` come
  back sparse, the selectors may need a refresh — degrade to the Apify or `site:` path.
