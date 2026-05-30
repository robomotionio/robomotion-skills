---
name: reddit-post-finder
description: Scrape and search Reddit posts from one or more subreddits over a time window — ranked by upvotes with each post's URL preserved. Use to find discussions, track competitor or brand mentions, monitor product feedback, and discover ICP pain points. Keyless by default (public Reddit JSON); uses an Apify Reddit actor when APIFY_API_TOKEN is set for reliable scale.
metadata:
  version: 1.1.1
  category: monitoring
  type: capability
---

# Reddit Post Finder

Search Reddit across subreddits for a time window and return posts ranked by upvotes,
always with the post URL. Two execution paths share one normalized schema:

- **Keyless (default):** Reddit's public listing JSON (`/r/<sub>/<sort>.json`) via
  `urllib` with a browser User-Agent. No key; lower volume/reliability. **Never cost-gated.**
- **Apify (when `APIFY_API_TOKEN` is set):** a Reddit scraper actor run via a **managed
  async run/poll lifecycle** (start the run, poll to terminal with backoff + a wall-clock
  timeout, then fetch the dataset) under a **cost gate** — reliable at scale, costs Apify
  credits. Replaces the old fragile `run-sync` call, which could time out or overspend on
  large jobs.

## When to use

- You need Reddit discussions from specific subreddits.
- Competitor-mention tracking, brand monitoring, or pain-point discovery.
- Recurring subreddit monitoring with dedup across runs.

## How to run

```bash
python3 ${SKILL_DIR}/scripts/reddit_search.py --subreddit "<subs>" [options]
```

| Flag | Default | Meaning |
|---|---|---|
| `--subreddit` | (required) | Comma-separated subreddit name(s), no `r/` prefix. |
| `--keywords` | `""` | Comma-separated OR client-side filter on title+body. |
| `--days` | `30` | Only posts from the last N days. |
| `--max-posts` | `50` | Per-subreddit cap. |
| `--sort` | `top` | `hot`, `top`, `new`, `rising`. |
| `--time` | `week` | Window for `top`: `hour/day/week/month/year/all`. |
| `--use-apify` | off | Force the Apify path (auto-selected when token is set). |
| `--estimate-only` | off | **Cost gate:** print projected cost/limits and exit 0 (no spend). |
| `--yes` | off | **Cost gate:** confirm actual spend — required to start an Apify run. |
| `--max-cost-usd` | `1.00` | **Cost gate:** abort the run if reported usage exceeds this. |
| `--apify-timeout` | `600` | Run/poll wall-clock timeout (s); the run is aborted if it trips. |
| `--output` | `json` | `json` array or `summary` lines. |

## Cost gate & run/poll lifecycle (Apify path only)

The Apify branch no longer uses a blocking `run-sync` call. Instead it starts the actor
run asynchronously, polls it to a terminal state with exponential backoff and a wall-clock
timeout (aborting the run to stop the meter if the timeout trips), then fetches the
dataset only on `SUCCEEDED` — so large jobs can't silently time out.

A **cost gate** guards spend:

- `--estimate-only` prints the projected cost/limits as JSON and **exits 0 without
  spending** — use it to preview before committing.
- Starting an actual run **requires `--yes`**; without it the Apify path refuses and exits
  non-zero.
- During the run, if reported usage-USD exceeds `--max-cost-usd` (or the timeout trips),
  the run is **aborted** and the script exits non-zero. `--max-cost-usd 0` forbids any spend.

The **keyless Reddit-JSON path is never gated** — it runs with no token and no `--yes`.

### Examples

```bash
# Keyless top-of-week sweep across two subs
python3 ${SKILL_DIR}/scripts/reddit_search.py --subreddit "saas,startups" --sort top --time week

# Pain-point discovery with keyword filter, last 14 days
python3 ${SKILL_DIR}/scripts/reddit_search.py --subreddit devops --keywords "ci,pipeline,flaky" --days 14 --output summary

# Preview Apify cost first (exits 0, no spend)
APIFY_API_TOKEN=$APIFY_API_TOKEN python3 ${SKILL_DIR}/scripts/reddit_search.py --subreddit rpa --use-apify --estimate-only

# Reliable scale via Apify — confirm spend with --yes and cap the budget
APIFY_API_TOKEN=$APIFY_API_TOKEN python3 ${SKILL_DIR}/scripts/reddit_search.py --subreddit rpa --use-apify --yes --max-cost-usd 0.50 --max-posts 100
```

## Outputs

JSON array sorted by `upVotes` desc; each item:
`{dataType, title, body, communityName, upVotes, numberOfComments, createdAt, url}`.
Every item carries its original post `url`.

## Recurring / monitoring mode

Pipe the fetch output through the bundled dedup helper to surface only new posts:

```bash
python3 ${SKILL_DIR}/scripts/reddit_search.py --subreddit saas --output json > ${WORKSPACE}/run.json
python3 ${SKILL_DIR}/scripts/dedup_history.py --input ${WORKSPACE}/run.json \
  --history ${WORKSPACE}/reddit_seen.csv --key url > ${WORKSPACE}/new.json
```

`dedup_history.py` keys on `url`, stamps `first_seen`, and prints only new items. If
`SUPABASE_URL` / `SUPABASE_KEY` are set you may persist history there from the host flow
instead; the CSV path needs no key.

## Credentials / env

- **Required:** none — the keyless Reddit-JSON path always works.
- **Optional (paid, if-set/else):**
  - `APIFY_API_TOKEN` — **if set → Apify Reddit actor** (cost-gated, reliable at scale);
    **else → keyless public Reddit listing-JSON** (the default, never gated).
  - `APIFY_REDDIT_ACTOR` — override the default actor slug.
  - `SUPABASE_URL` / `SUPABASE_KEY` — **if set → Supabase cross-run history/dedup**;
    **else → workspace CSV** via `dedup_history.py` (the default).

## Notes & edge cases

- Small/low-traffic subreddits return little with `sort=hot` — use `top` + `time=week/month`.
- Always return post URLs; never a linkless summary.
- Reddit is hostile to scraping: the keyless path paces requests and backs off on 429/503,
  but for volume prefer the Apify actor.
- `--days` filters client-side on `created_utc`; items without a timestamp are kept.
