---
name: x-mention-tracker
description: Search and scrape X posts for a query with reliable native date filtering (since:/until:) — ranked by likes. Use to find posts, track brand mentions, monitor competitors, and feed the kol-content-monitor (from:<handle> feeds). Apify tweet-scraper when APIFY_API_TOKEN is set (reliable); keyless Playwright degrade otherwise (best-effort behind X's login wall).
metadata:
  version: 1.1.1
  category: monitoring
  type: capability
---

# X Mention Tracker

Search X for a query in a date range and return posts ranked by likes. Date filtering is
done with native advanced-search operators (`since:`/`until:`) appended to the query —
do not rely on actor-native date params. Two paths share one normalized schema:

- **Apify (when `APIFY_API_TOKEN` is set):** a tweet-scraper actor (`searchTerms`,
  `maxTweets`, `searchMode=live`) run via a **managed async run/poll lifecycle** (start,
  poll to terminal with backoff + a wall-clock timeout, then fetch the dataset) under a
  **cost gate** — the reliable path; costs Apify credits. Replaces the old `run-sync` call
  that could time out or overspend on large jobs.
- **Keyless (default):** a bundled Playwright scraper (`scripts/x_scrape.mjs`). X is
  login-walled and anti-bot, so this is best-effort — expect partial/empty results.
  **Never cost-gated.**

## When to use

- You need posts matching a query/handle in a date range.
- Brand-mention or competitor monitoring on X.
- A sub-step of `kol-content-monitor` (`from:<handle>` feeds).
- Recurring mention monitoring with dedup across runs.

## How to run

```bash
python3 ${SKILL_DIR}/scripts/x_search.py --query "<query>" [options]
```

| Flag | Default | Meaning |
|---|---|---|
| `--query` | (required) | Search query; `since:`/`until:` appended automatically. |
| `--since` / `--until` | — | Date bounds `YYYY-MM-DD` (server-side via query). |
| `--max-posts` | `50` | Cap on returned posts. |
| `--keywords` | `""` | Comma-separated OR client-side filter on text. |
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

Keyless path setup (once):

```bash
cd ${SKILL_DIR}/scripts && npm install && npx playwright install chromium
```

### Examples

```bash
# Brand mentions in a window (Apify if token set, else keyless)
python3 ${SKILL_DIR}/scripts/x_search.py --query "robomotion" --since 2025-01-01 --until 2025-02-01

# KOL feed (drives kol-content-monitor)
python3 ${SKILL_DIR}/scripts/x_search.py --query "from:levelsio" --max-posts 30 --output summary

# Competitor sweep with keyword tightening, reliable path — preview then confirm spend
APIFY_API_TOKEN=$APIFY_API_TOKEN python3 ${SKILL_DIR}/scripts/x_search.py \
  --query "rpa" --use-apify --estimate-only
APIFY_API_TOKEN=$APIFY_API_TOKEN python3 ${SKILL_DIR}/scripts/x_search.py \
  --query "rpa" --keywords "uipath,automation anywhere" --use-apify --yes --max-cost-usd 0.50
```

## Outputs

JSON array sorted by `likeCount` desc; each item:
`{id, text, fullText, likeCount, retweetCount, replyCount, viewCount, createdAt,
author:{userName,name}, url}`. Deduped by post id.

## Recurring / monitoring mode

```bash
python3 ${SKILL_DIR}/scripts/x_search.py --query "robomotion" > ${WORKSPACE}/run.json
python3 ${SKILL_DIR}/scripts/dedup_history.py --input ${WORKSPACE}/run.json \
  --history ${WORKSPACE}/x_seen.csv --key id > ${WORKSPACE}/new.json
```

## Credentials / env

- **Required:** none — keyless Playwright degrade exists (best-effort).
- **Optional (paid, if-set/else):**
  - `APIFY_API_TOKEN` — **if set → Apify tweet-scraper actor** (cost-gated, reliable);
    **else → keyless Playwright** (the default, best-effort behind X's login wall, never gated).
  - `APIFY_TWITTER_ACTOR` — override the default actor slug.
  - `SUPABASE_URL` / `SUPABASE_KEY` — **if set → Supabase cross-run history**;
    **else → workspace CSV** via `dedup_history.py` (the default).

## Notes & edge cases

- Date filtering MUST go in the query via `since:`/`until:` — the script appends them.
- Dedup by post id (reposts/quote chains produce repeats) — handled.
- `from:<handle>` queries drive the KOL-feed use case.
- X aggressively blocks unauthenticated scraping — prefer Apify; route the keyless
  Playwright fallback through a proxy and expect lower volume.
