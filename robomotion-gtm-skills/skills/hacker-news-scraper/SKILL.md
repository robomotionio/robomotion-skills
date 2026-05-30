---
name: hacker-news-scraper
description: Search Hacker News stories and comments for a topic, tool, or brand and return ranked discussions (points, comments, links). Use to track tech-community sentiment, find Show HN / Ask HN launches, and surface buying or competitive signals. Free, no API key.
metadata:
  version: 1.0.1
  category: monitoring
  type: capability
---

# Hacker News Scraper

Search Hacker News via the **public Algolia HN API** — keyless, free. Returns
discussions ranked by points so a GTM/marketing agent can monitor tech-community
sentiment, discover launches, and catch competitive signals.

## When to use

- You need HN discussions on a topic, product, or competitor.
- Tracking mentions of a tool/brand in the tech community.
- Discovering `Show HN` / `Ask HN` launches in a recent window.
- Recurring sentiment monitoring (store ids between runs to report only new threads).

## How to run

The capability is the bundled script `scripts/hn_search.py` (Python 3 stdlib only —
no install). Run it through the terminal tool:

```bash
python3 ${SKILL_DIR}/scripts/hn_search.py --query "<terms>" [options]
```

Options:

| Flag | Default | Meaning |
|---|---|---|
| `--query` | `""` | Search terms. May be empty when `--tags` drives the search. |
| `--days` | `7` | How many days back to search (server-side date filter). |
| `--tags` | `story` | Item type: `story`, `comment`, `ask_hn`, `show_hn`. |
| `--max-results` | `50` | Cap on returned items. |
| `--keywords` | `""` | Comma-separated OR filter applied client-side to title+text. |
| `--output` | `json` | `json` (array) or `summary` (human-readable lines). |

### Examples

```bash
# Topic search, last 30 days, ranked JSON
python3 ${SKILL_DIR}/scripts/hn_search.py --query "robomotion" --days 30

# Launch discovery — recent Show HN posts (empty query, tag-driven)
python3 ${SKILL_DIR}/scripts/hn_search.py --tags show_hn --days 7 --max-results 30 --output summary

# Competitor mention sweep with extra keyword filter
python3 ${SKILL_DIR}/scripts/hn_search.py --query "rpa" --keywords "uipath,automation anywhere,blue prism" --output summary
```

## Output

JSON array sorted by `points` desc; each item:
`{id, title, url, author, points, num_comments, created_at, hn_url, text}`.

## Recurring / monitoring mode

For a recurring monitor, persist returned `id`s between runs and surface only new
ones (dedup). If `SUPABASE_URL` / `SUPABASE_KEY` are set, upsert there keyed on `id`
with a first-seen timestamp; otherwise keep the id list in the agent's workspace for
single-session dedup. The script itself is stateless — orchestrate dedup around it.

## Credentials / env

- **Required:** none — the Algolia HN API is fully public and keyless (no paid service).
- **Optional (if-set/else):** `SUPABASE_URL` / `SUPABASE_KEY` — **if set → Supabase cross-run
  history/dedup**; **else → the agent's workspace id list** (the default; the script is stateless).

## Notes & limits

- The Algolia HN API is free with no hard rate limit "within reason"; the script
  spaces paginated calls and backs off on HTTP 429.
- Date filtering is **server-side** (`numericFilters=created_at_i>cutoff`) — don't
  re-filter by date afterward.
- `--tags` and `--query` are AND-combined server-side. Empty `--query` + `--tags show_hn`
  is the launch-discovery mode.
- Algolia applies **typo tolerance / prefix matching**, so very short queries (≤3 chars)
  match loosely. Prefer the `--keywords` OR-filter to tighten brand/competitor sweeps.
