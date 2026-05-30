---
name: competitor-monitoring-system
description: Stand up and run ongoing competitive-intelligence monitoring for a client — maintain a watchlist, establish a baseline, then track competitor content, ads, reviews, social, and product moves on a cadence (content/social/Reddit weekly, ads bi-weekly, reviews monthly, full re-baseline quarterly). Diffs each cycle vs stored snapshots and produces an intelligence report with recommended actions behind human checkpoints.
metadata:
  version: 1.0.1
  category: competitive-intel
  type: playbook
---

# Competitor Monitoring System

Playbook: a stateful, scheduled orchestration over the `competitor-intel` and
`competitive-pricing-intel` engines plus per-channel collectors. Durable snapshot history is
what makes diffs meaningful. **You, the agent, classify change significance, write the
report, and gate actions behind human approval.**

## Sub-skills this chains

- `competitor-intel` — per-competitor baseline + quarterly refresh (run its scripts/flow).
- `competitive-pricing-intel` — pricing-change detection leg.
- Per-channel collectors bundled here: `fetch_pages.py` (content), `fetch_feed.py` (blogs),
  `hn_fetch.py` (Hacker News), `render_page.mjs` (ads/reviews/social), `wayback_fetch.py`
  (pricing history), `snapshot_store.py` (cross-cycle diffing).

## When to use

- "Set up competitor monitoring for [client]." / "Track what [competitors] are doing."
- "Monitor [competitor] content and ads."

## How to run

### 1. Define the watchlist

Per competitor capture: `{name, url, founder_linkedin?, blog_url?, review_urls?,
ad_library_urls?}`. Store it as `${WORKSPACE}/supabase/watchlist.csv` (or Airtable/Supabase
when configured). This is editable by the human.

### 2. Initial baseline (per competitor)

Run the `competitor-intel` engine per competitor (its `fetch_pages.py` / `fetch_feed.py` /
`render_page.mjs`), add a current-ad scrape and latest review pull, then persist each
competitor's tracked fields as the baseline:

```bash
python3 ${SKILL_DIR}/scripts/snapshot_store.py save --entity acme \
  --input ${WORKSPACE}/acme_baseline.json --store ${WORKSPACE}/supabase/monitor_history.csv
```

### 3. Configure cadence

Schedule recurring runs via the host platform cron / monitoring routine, one per cadence:
content weekly, social weekly, Reddit/HN weekly, ads bi-weekly, reviews monthly, full
re-baseline quarterly.

### 4. Run a monitoring cycle (per channel)

```bash
# Content (weekly): refetch blogs + pages
python3 ${SKILL_DIR}/scripts/fetch_feed.py  --url https://acme.com/blog --output ${WORKSPACE}/acme_blog.json
python3 ${SKILL_DIR}/scripts/fetch_pages.py --url https://acme.com https://acme.com/product --output ${WORKSPACE}/acme_pages.json
# Hacker News (weekly)
python3 ${SKILL_DIR}/scripts/hn_fetch.py    --query "acme" --days 7 --output ${WORKSPACE}/acme_hn.json
# Ads (bi-weekly) + Reviews (monthly): render the libraries / review pages
node ${SKILL_DIR}/scripts/render_page.mjs --url "<meta-ad-library-or-g2-url>" --wait 6000 --output ${WORKSPACE}/acme_ads.json
# Pricing (monthly): Wayback history for the pricing leg
python3 ${SKILL_DIR}/scripts/wayback_fetch.py --url https://acme.com/pricing --output ${WORKSPACE}/acme_pricing_hist.json
```

Social (weekly): `render_page.mjs` for LinkedIn founder posts / X, or
`PHANTOMBUSTER_API_KEY` (LinkedIn) / `APIFY_API_TOKEN` (X/Reddit at depth).

### 5. Diff vs previous + flag significant changes

```bash
python3 ${SKILL_DIR}/scripts/snapshot_store.py diff --entity acme \
  --input ${WORKSPACE}/acme_cycle.json --store ${WORKSPACE}/supabase/monitor_history.csv
python3 ${SKILL_DIR}/scripts/snapshot_store.py save --entity acme \
  --input ${WORKSPACE}/acme_cycle.json --store ${WORKSPACE}/supabase/monitor_history.csv
```

From the `added`/`removed`/`changed` output, flag: new features/pricing, content targeting
your keywords, negative review trends (poaching opportunity), new ad campaigns, exec strategy
statements. `first_run: true` = baseline established this cycle.

### 6. Produce the intelligence report (you, the agent)

Write "Competitor Intelligence — [Client] — Week of [Date]": key changes → recommended
actions → per-competitor detailed findings. Deliver to the client's intelligence area
(workspace file / channel attachment; `SLACK_*`/`DISCORD_*`/`TELEGRAM_*` if configured).

### 7. Human checkpoints

Post the watchlist/plan after setup and the recommended actions after each report **and wait
for approval** before executing or routing to outreach skills.

## Outputs

- `${WORKSPACE}/supabase/watchlist.csv`, `monitor_history.csv` — durable watchlist + snapshots.
- Per-cycle `${WORKSPACE}/competitor-intel-[client]-[date].md` reports.

## Credentials / env

- **Required:** none to produce reports — backbone + diffing run keyless on local CSV state.
- **Optional:** `SUPABASE_URL`/`SUPABASE_KEY` or `AIRTABLE_API_KEY` (durable shared watchlist /
  history — strongly recommended); `APIFY_API_TOKEN` (Reddit/X/review depth);
  `PHANTOMBUSTER_API_KEY` + LinkedIn cookie (LinkedIn post monitoring); `DATAFORSEO_LOGIN`/
  `DATAFORSEO_PASSWORD` or `SERPER_API_KEY` for per-cycle discovery searches (if set -> paid
  SERP; if not -> the agent's own web search, the default); `SLACK_*` / `DISCORD_*`
  / `TELEGRAM_*` (report delivery, else workspace file).

## Notes & edge cases

- Stateful + scheduled: durable storage is what makes diffs meaningful — an in-flow-only run
  reports one cycle but can't detect cross-cycle change. The CSV store gives offline history.
- Respect the cadence to control proxy/scrape cost (reviews monthly, baseline quarterly).
- Negative-review trends and competitor-trouble signals are poaching triggers — surface them
  prominently, route to outreach only after the human checkpoint.
- Always gate recommended actions behind human approval (the two checkpoints).
- Apify degrade (when set): `curl -s "https://api.apify.com/v2/acts/<actor>/run-sync-get-dataset-items?token=$APIFY_API_TOKEN" -d '{...}'`.
