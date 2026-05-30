---
name: web-archive-scraper
description: Search the Wayback Machine (Internet Archive) for archived snapshots of a URL or domain and optionally fetch cached page content as readable text. Use to recover removed customer lists, testimonials, case studies, and partner directories, and to track how a competitor's messaging evolved over time. Free, no API key.
metadata:
  version: 1.0.1
  category: monitoring
  type: capability
---

# Web Archive Scraper

Query the public **Wayback CDX API** (`web.archive.org/cdx/search/cdx`) for archived
snapshots and, on request, fetch the cached HTML and strip it to readable text. Keyless,
stdlib only — no install.

## When to use

- You need historical/archived versions of a page or domain.
- Recovering customer lists / testimonials / partner directories that were removed.
- Tracking a competitor's messaging change over time.

## How to run

```bash
python3 ${SKILL_DIR}/scripts/wayback_scraper.py --url "<url-or-domain>" [options]
```

| Flag | Default | Meaning |
|---|---|---|
| `--url` | (required) | Target URL/domain to search. |
| `--match` | `exact` | `exact`, `prefix`, `host`, `domain`. |
| `--from` / `--to` | — | Date range `YYYY-MM-DD` (server-side). |
| `--limit` | `25` | Max snapshots. |
| `--fetch` | off | Fetch content of the most recent snapshot. |
| `--fetch-all` | off | Fetch content of ALL matched snapshots. |
| `--status` | `200` | HTTP status filter (`any` to include redirects/errors). |
| `--collapse` | `day` | Dedup level: `none/day/month/year`. |
| `--output` | `json` | `json`, `csv`, or `summary`. |

### Examples

```bash
# Recover an old customers page
python3 ${SKILL_DIR}/scripts/wayback_scraper.py --url "example.com/customers" --fetch --output summary

# Track a domain's messaging across years (one snapshot/year)
python3 ${SKILL_DIR}/scripts/wayback_scraper.py --url "example.com" --match domain \
  --from 2018-01-01 --to 2023-12-31 --collapse year --limit 20

# Enumerate + dump all case-study pages under a path
python3 ${SKILL_DIR}/scripts/wayback_scraper.py --url "example.com/case-studies" \
  --match prefix --fetch-all --limit 10 --output csv
```

## Outputs

JSON/CSV array of snapshots, each:
`{url, timestamp, datetime, status_code, mime_type, archive_url, raw_url, content}`.
`content` is populated only when `--fetch`/`--fetch-all`. `raw_url` uses the `id_`
modifier so fetched HTML excludes the Wayback toolbar chrome.

## Credentials / env

- **Required:** none — the CDX API and content fetch are fully public/keyless (no paid service).
- **Optional (if-set/else):** `SUPABASE_URL` / `SUPABASE_KEY` — **if set → Supabase persistence
  of recovered snapshots across runs**; **else → one-shot stateless extraction** (the default).

## Notes & edge cases

- CDX rate limit is ~15 requests/minute — the script paces `fetch_all` (≈4s between
  fetches) and backs off on 429/503. Keep `--limit` small before `--fetch-all`.
- `--collapse=day` avoids redundant same-day snapshots; widen for long histories.
- `--match=prefix`/`domain` can enumerate many pages — cap `--limit` first.
- Not all snapshots are status 200; use `--status any` to inspect redirects/errors over time.
