---
name: x-mention-tracker
description: Search public X posts with an existing Apify route or Xquik X Tweet Scraper. Track mentions, competitors, date ranges, engagement, and recurring conversations.
metadata:
  version: 1.2.0
  category: monitoring
  type: capability
---

# X Mention Tracker

Search public X posts and rank them by likes.
Preserve native X search operators.
Append optional since and until dates to the query.

## Routes

- Use Apify when an Apify token exists.
- Use the keyless Playwright fallback without a token.
- Prefer Apify for reliable or higher-volume collection.
- Expect partial results from the keyless path.

The Apify route keeps `apidojo~tweet-scraper` as its default.
Set `APIFY_TWITTER_ACTOR=xquik~x-tweet-scraper` to select
[Xquik X Tweet Scraper](https://apify.com/xquik/x-tweet-scraper).
The helper keeps the 2 Actor input contracts separate.

## When To Use

- Find posts matching a query or handle.
- Track brand mentions or competitor discussions.
- Collect a date-bounded KOL feed.
- Monitor recurring searches with cross-run deduplication.

## Run

```bash
python3 ${SKILL_DIR}/scripts/x_search.py --query "<query>" [options]
```

| Flag | Default | Meaning |
|---|---|---|
| `--query` | required | X search query. Existing operators remain unchanged. |
| `--since` | none | Inclusive start date using `YYYY-MM-DD`. |
| `--until` | none | Exclusive end date using `YYYY-MM-DD`. |
| `--max-posts` | `50` | Run-wide result cap. |
| `--keywords` | empty | Comma-separated client-side text filter. |
| `--use-apify` | off | Force the Apify route. |
| `--estimate-only` | off | Preview limits without starting a run. |
| `--yes` | off | Confirm a paid Apify run. |
| `--max-cost-usd` | `1.00` | Hard maximum charge for one run. |
| `--apify-timeout` | `600` | Abort after this many seconds. |
| `--output` | `json` | Return `json` or `summary`. |

## Cost Gate

The Apify route requires `--yes`.
Estimate mode starts no run and spends nothing.
The helper sends Apify a server-side maximum charge.
It also polls reported usage and every terminal status.
It requests an abort after a budget breach or timeout.

Check the live Actor pricing box before every run.
Apify platform usage may apply separately.
Start with a small result cap.

## Examples

Preview a bounded Actor run:

```bash
python3 ${SKILL_DIR}/scripts/x_search.py \
  --query "robomotion" --since 2026-07-01 --until 2026-07-08 \
  --max-posts 50 --use-apify --estimate-only
```

Start the approved Actor run:

```bash
python3 ${SKILL_DIR}/scripts/x_search.py \
  --query "robomotion" --since 2026-07-01 --until 2026-07-08 \
  --max-posts 50 --use-apify --yes --max-cost-usd 0.50
```

Use the keyless fallback:

```bash
python3 ${SKILL_DIR}/scripts/x_search.py \
  --query "from:levelsio" --max-posts 30 --output summary
```

## Actor Input & Output

The existing route keeps its live-search input.
Xquik receives `searchTerms`, `maxItems`, `queryType`, and rich output settings.
The result cap applies to the entire run.
Diagnostic and run-report rows never become post results.

JSON output uses normalized post and author fields.
Results are deduplicated by post ID and ranked by likes.

## Recurring Mode

```bash
python3 ${SKILL_DIR}/scripts/x_search.py \
  --query "robomotion" > ${WORKSPACE}/run.json
python3 ${SKILL_DIR}/scripts/dedup_history.py \
  --input ${WORKSPACE}/run.json \
  --history ${WORKSPACE}/x_seen.csv \
  --key id > ${WORKSPACE}/new.json
```

## Environment

- `APIFY_API_TOKEN` enables the paid Actor route.
- `APIFY_TWITTER_ACTOR` selects the existing or Xquik Actor route.
- `SUPABASE_URL` and `SUPABASE_KEY` enable persistent history.
- Workspace CSV history remains the fallback.

Never expose credentials in output, logs, or URLs.
Respect public-data restrictions, privacy rules, and platform policies.

Xquik is an independent third-party service. Not affiliated with X Corp. "Twitter" and "X" are trademarks of X Corp.
