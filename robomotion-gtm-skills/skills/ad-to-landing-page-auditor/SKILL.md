---
name: ad-to-landing-page-auditor
description: Audit message match between each ad and its landing page — does the ad's promise carry through to the LP headline, body, and CTA? — and flag every disconnect plus conversion friction that kills click-to-convert rates. For teams getting ad clicks but few conversions.
metadata:
  version: 1.0.1
  category: ads
  type: composite
---

# Ad → Landing Page Auditor

Composite: **ad inventory parse → LP fetch/extract → message-match scoring → friction
analysis → prioritized fixes + rewrites.** Scripts handle the deterministic parse + LP
extraction; **you (the agent) do the 6-dimension message-match scoring, friction
classification, prioritization, and rewrites.**

## When to use

- "Why are my ads getting clicks but no conversions?"
- "Audit my ad-to-landing-page flow" / "Check message match on our campaigns."
- "My conversion rate is low — help me figure out why."

## How to run

### 1 — Parse ads into an inventory + collect unique LP URLs

```bash
# From an ad-platform CSV export:
python3 ${SKILL_DIR}/scripts/parse_ads.py --csv ${WORKSPACE}/ads_export.csv \
  --urls-out ${WORKSPACE}/urls.txt --output ${WORKSPACE}/inventory.json

# Or from a JSON ad list:
python3 ${SKILL_DIR}/scripts/parse_ads.py --json ${WORKSPACE}/ads.json --urls-out ${WORKSPACE}/urls.txt
```

Each row: `{ad_id, platform, headline, headlines[], body, cta, landing_url, conv_rate}`.
`--urls-out` writes the deduped LP list so each LP is fetched once.

### 2 — Fetch + extract each unique landing page

```bash
python3 ${SKILL_DIR}/scripts/fetch_landing_page.py --urls ${WORKSPACE}/urls.txt --output ${WORKSPACE}/lps.json
```

Per LP: hero headline, subhead, primary CTA, above-fold-CTA flag, benefit lists, proof
signals, image/asset count (load-weight proxy), `form_field_count`, `has_video`, nav-link
count, status. **If an LP returns `ok:false` (failed to load), mark its friction "Unknown"
and flag it as a Critical fix — a broken destination — rather than scoring it.**

For JS-rendered / A/B-cloaked / consent-walled LPs, escalate that URL to a Playwright
fetch + screenshot (reuse the browser pattern in
`../competitor-ad-intelligence/scripts/scrape_meta_ads.mjs`) so the audit reflects what a
real clicker sees. Use a proxy + geo matching the ad's target region. **For an LP behind
heavy anti-bot: if `APIFY_API_TOKEN` is set → fall back to an Apify fetch (last resort);
if not → the keyless urllib + Playwright path is the default and remains the only LP fetch.**

### 3 — Score message match (you, the agent)

For each ad→LP pair, score 6 dimensions 1–10 (→ /60): **promise continuity, language
match, visual continuity, CTA alignment, specificity match, emotional match.** Cite the
specific mismatch per dimension. **Visual continuity is N/A for plain search ads — exclude
it from the /60 average rather than penalizing** (use the screenshot when one exists).

### 4 — Friction analysis (you, over the extracted stats)

Per LP, classify Red/Yellow/Green on: load weight (image/asset count), form length
(`form_field_count`), CTA clarity, above-fold conversion, proof placement, nav distraction,
mobile issues. Estimate conversion impact.

### 5 — Prioritize + rewrite (you)

Rank disconnects by **severity × conversion impact** into Critical / Important /
Nice-to-have. Draft a matched ad-headline or LP-headline rewrite for the worst-matching pair.

### 6 — Render

Write `ad-lp-audit-<YYYY-MM-DD>.md` to `${WORKSPACE}` and attach to the Agent Teams channel.

## Outputs

`ad-lp-audit-<YYYY-MM-DD>.md` — per ad→LP Message Match Score (/60) with dimension
breakdown + disconnect + fix; landing-page friction report; prioritized fixes with
estimated conversion impact; rewrite suggestions for the worst pair.

## Credentials / env

- **Required:** none — `parse_ads.py` and `fetch_landing_page.py` are keyless. The scoring,
  friction classification, and rewrites are the agent's reasoning (no LLM key in scripts).
- **Optional (each with a keyless default fallback):**
  - `HTTPS_PROXY` — Robomotion Proxy for geo-matched / escalated LP fetch.
  - `APIFY_API_TOKEN` — if set → Apify fetch as a last resort for an LP behind hostile
    anti-bot; else → keyless `fetch_landing_page.py` (urllib) escalating to Playwright
    fetch + screenshot (default).

## Notes & edge cases

- Prefer the keyless `fetch_landing_page.py` for static / server-rendered LPs; escalate to
  Playwright only when the hero/CTA render client-side or the page is consent/geo-walled.
- Watch for LPs that A/B-rotate or cloak by referrer — capture a screenshot via Playwright
  so the audit reflects the real post-click experience.
- A failed LP load is a Critical finding (broken destination), not a zero score.
