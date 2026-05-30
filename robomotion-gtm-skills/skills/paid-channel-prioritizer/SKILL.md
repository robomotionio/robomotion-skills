---
name: paid-channel-prioritizer
description: Answer "where should I run ads?" for early-stage founders — analyze product, ICP, competitor ad presence, and budget to recommend the right 1–2 paid channels to start with and a 90-day ramp plan. Prevents the classic mistake of spreading a small budget too thin across platforms.
metadata:
  version: 1.0.1
  category: ads
  type: composite
---

# Paid Channel Prioritizer

Composite: **channel scoring → recommendation → budget allocation → 90-day plan.** The
script gathers competitor ad-presence evidence (Meta) deterministically; the buyer-intent
read, the 6-factor channel scoring, the recommendation, and the ramp plan are the agent's
reasoning. **The whole point is concentration — don't spread a small budget thin.**

## When to use

- "Where should I run ads?" / "Which ad platform is best for us?"
- "I have $X/month — where should I spend it?" / "Google Ads or Facebook Ads?"
- "Help me pick a paid channel."

## Sub-skills it chains

- **`google-ad-scraper`** capability (Google presence / ad count) — call by path.
- Bundled `scrape_meta_ads.mjs` (Meta presence / active-ad count).

## How to run

One-time browser setup:

```bash
cd ${SKILL_DIR}/scripts && npm install && npx playwright install chromium
```

### 1 — Buyer-intent analysis (you, the agent)

From product / ICP / business model / B2B-or-B2C, map where this buyer looks (search vs.
passive social vs. professional vs. video vs. short-form) → candidate channels.

### 2 — Competitor ad-presence map (per competitor × channel)

```bash
# Meta presence (count of active ads ~ presence signal)
node ${SKILL_DIR}/scripts/scrape_meta_ads.mjs --query "Linear" --country US --max-ads 80 --output ${WORKSPACE}/meta_linear.json

# Google presence (reuse the google-ad-scraper capability)
node ${SKILL_DIR}/../google-ad-scraper/scripts/scrape_google_ads.mjs --domain linear.app --max-ads 50 --output ${WORKSPACE}/google_linear.json
```

For LinkedIn / X / YouTube / TikTok presence, the agent uses web search
(`site:linkedin.com`, `<competitor> LinkedIn Ads/sponsored`, etc.) — **if `DATAFORSEO_LOGIN`/
`DATAFORSEO_PASSWORD` (or `SERPER_API_KEY`) is set → structured SERP API; else → the agent's
keyless web search (default)**. For deep/auth-walled checks: **if `APIFY_API_TOKEN` is set →
use an Apify actor; if not → stay on the keyless `site:` search (default).** **Tabulate a competitor × channel map
(active / ad count) across Google, Meta, LinkedIn, X, YouTube, TikTok.** Competitor
presence cuts both ways — where they spend = validated; where they're absent = white space
or a dead end; weigh which.

### 3 — Channel scoring matrix (you)

Score each channel: **buyer intent 25 / targeting precision 20 / competitor validation 15 /
budget efficiency 15 / ICP reachability 15 / creative needs 10**, with min-viable-budget and
creative-need context. Pull category CPA/CPC benchmarks via web search where needed (same
SERP path: `DATAFORSEO_*`/`SERPER_API_KEY` if set, else keyless web search by default).

### 4 — Recommendation + budget + 90-day plan (you)

Pick **#1** (top score + budget viable + creative-ready). Add **#2 only if budget > $3K AND
it serves a different funnel stage.** **At < $1.5K/mo recommend exactly one channel.** Never
recommend a channel the budget can't sustain even if it scores well (e.g. LinkedIn
~$3K/mo min). Allocate by budget level; build a 90-day ramp (foundation / optimize /
scale-or-pivot).

### 5 — Render

Write `channel-strategy-<YYYY-MM-DD>.md` to `${WORKSPACE}` and attach to the Agent Teams
channel.

## Outputs

`channel-strategy-<YYYY-MM-DD>.md` — channel scoring table with PRIMARY/SECONDARY verdicts,
"why [primary]" + competitor evidence + min viable budget + expected CPA range, "why NOT
[obvious choice]", budget allocation table, 90-day ramp plan, pre-launch checklist.

## Credentials / env

- **Required:** none — ad libraries are public; the Meta scraper and `google-ad-scraper` are
  keyless. Scoring/recommendation/ramp are the agent's reasoning.
- **Optional (each with a keyless default fallback):**
  - `APIFY_API_TOKEN` — if set → Apify actor for LinkedIn/TikTok presence checks too hostile
    for search/Playwright; else → keyless `site:` search + Playwright/google-ad-scraper
    presence checks (default).
  - `DATAFORSEO_LOGIN`/`DATAFORSEO_PASSWORD` (or `SERPER_API_KEY`) — if set → structured SERP
    API for presence + CPA/CPC-benchmark queries; else → the agent's keyless web search
    (default).
  - `HTTPS_PROXY` — Robomotion Proxy for geo-correct library/SERP checks.

## Notes & edge cases

- Concentration is the goal: one channel under ~$1.5K/mo; a secondary only above ~$3K and
  only if it covers a different funnel stage.
- Honor min-viable-budget gates — never recommend a channel the budget can't sustain.
- Use a proxy + geo on all library/SERP checks so presence reflects the target market;
  degrade to `site:` snippets when a JS library blocks the scraper.
