---
name: product-hunt-scraper
description: Scrape trending products from Product Hunt for a daily, weekly, or monthly window — ranked by upvotes. Use to discover new launches, track competitors, and monitor the startup ecosystem in a space. Keyless by default (Playwright over the leaderboard); uses an Apify Product Hunt actor when APIFY_API_TOKEN is set for reliable scale.
metadata:
  version: 1.1.1
  category: monitoring
  type: capability
---

# Product Hunt Scraper

Discover trending Product Hunt launches for a window and return them ranked by upvotes.
Two execution paths share one normalized schema:

- **Keyless (default):** a bundled Playwright scraper (`scripts/ph_scrape.mjs`) loads the
  leaderboard and extracts product cards. PH is JS-heavy and anti-bot, so this is the
  degrade path — lower reliability/volume. **Never cost-gated.**
- **Apify (when `APIFY_API_TOKEN` is set):** a Product Hunt actor run via a **managed async
  run/poll lifecycle** (start, poll to terminal with backoff + a wall-clock timeout, then
  fetch the dataset) under a **cost gate** — reliable, costs Apify credits. Replaces the
  old `run-sync` call that could time out or overspend on large jobs.

## When to use

- You need to discover new product launches in a window.
- Tracking competitors / a category on Product Hunt.
- Recurring "what launched this week in [space]" monitoring.

## How to run

```bash
python3 ${SKILL_DIR}/scripts/ph_scraper.py --time-period <daily|weekly|monthly> [options]
```

| Flag | Default | Meaning |
|---|---|---|
| `--time-period` | `weekly` | `daily`, `weekly`, `monthly`. |
| `--max-products` | `50` | Cap on returned products. |
| `--keywords` | `""` | Comma-separated OR filter on name+tagline+description. |
| `--use-apify` | off | Force the Apify path (auto when token set). |
| `--estimate-only` | off | **Cost gate:** print projected cost/limits and exit 0 (no spend). |
| `--yes` | off | **Cost gate:** confirm actual spend — required to start an Apify run. |
| `--max-cost-usd` | `1.00` | **Cost gate:** abort the run if reported usage exceeds this. |
| `--apify-timeout` | `600` | Run/poll wall-clock timeout (s); the run is aborted if it trips. |
| `--output` | `json` | `json` array or `summary` lines. |

## Cost gate & run/poll lifecycle (Apify path only)

The Apify branch starts the actor run async, polls to a terminal state with backoff and a
wall-clock timeout (aborting on timeout to stop the meter), then fetches the dataset only
on `SUCCEEDED`. A **cost gate** guards spend: `--estimate-only` prints the projection and
**exits 0 without spending**; starting a run **requires `--yes`** (else it refuses,
non-zero exit); the run is **aborted** if reported usage exceeds `--max-cost-usd` or the
timeout trips (`--max-cost-usd 0` forbids any spend). The **keyless Playwright path is
never gated**.

For the keyless path, install the browser once:

```bash
cd ${SKILL_DIR}/scripts && npm install && npx playwright install chromium
```

### Examples

```bash
# This week's launches (keyless)
python3 ${SKILL_DIR}/scripts/ph_scraper.py --time-period weekly --max-products 50

# Category sweep with keyword filter
python3 ${SKILL_DIR}/scripts/ph_scraper.py --time-period daily --keywords "ai,agent,llm" --output summary

# Preview Apify cost first (exits 0, no spend), then run with --yes
APIFY_API_TOKEN=$APIFY_API_TOKEN python3 ${SKILL_DIR}/scripts/ph_scraper.py --time-period monthly --use-apify --estimate-only
APIFY_API_TOKEN=$APIFY_API_TOKEN python3 ${SKILL_DIR}/scripts/ph_scraper.py --time-period monthly --use-apify --yes --max-cost-usd 0.50
```

## Outputs

JSON array sorted by `upvotes` desc; each item:
`{name, tagline, description, url, upvotes}`.

## Recurring / monitoring mode

Dedup against a workspace CSV to surface only new launches:

```bash
python3 ${SKILL_DIR}/scripts/ph_scraper.py --time-period weekly > ${WORKSPACE}/run.json
python3 ${SKILL_DIR}/scripts/dedup_history.py --input ${WORKSPACE}/run.json \
  --history ${WORKSPACE}/ph_seen.csv --key url > ${WORKSPACE}/new.json
```

`dedup_history.py` keys on product `url`, stamps `first_seen`. Use `SUPABASE_*` from the
host flow for durable history if preferred.

## Credentials / env

- **Required:** none — the keyless Playwright path works without a key.
- **Optional (paid, if-set/else):**
  - `APIFY_API_TOKEN` — **if set → Apify Product Hunt actor** (cost-gated, reliable);
    **else → keyless Playwright leaderboard scraper** (the default, never gated).
  - `APIFY_PH_ACTOR` — override the default actor slug.
  - `SUPABASE_URL` / `SUPABASE_KEY` — **if set → Supabase cross-run history**;
    **else → workspace CSV** via `dedup_history.py` (the default).

## Notes & edge cases

- PH rate-limits / bot-detects aggressively. Route the Playwright path through a proxy
  (`HTTPS_PROXY` / Robomotion Proxy) for volume; prefer the Apify actor when blocked.
- Keyword filtering is client-side over name+tagline+description.
- The keyless scraper depends on PH's DOM; if the layout shifts, prefer the Apify path.
