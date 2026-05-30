---
name: blog-feed-monitor
description: Aggregate recent blog posts from one or more sites via RSS/Atom (with an index-scrape fallback) for competitor watch, industry tracking, or keyword-filtered content monitoring — no API key. Returns a normalized, deduped, recency-and-keyword-filtered list of posts. Use to track what vendors are publishing or feed content-brief / campaign-brief skills.
metadata:
  version: 1.0.1
  category: content
  type: capability
---

# Blog Feed Monitor

Aggregate recent posts across blogs/sites — keyless and proxy-friendly. RSS/Atom is the
happy path: the script discovers each site's feed (`<link rel="alternate">` then common
feed paths), parses RSS 2.0 + Atom, and filters by recency + keyword, deduped by canonical
URL. Sites with no feed degrade to a light index-link scrape.

## When to use

- "Monitor competitor blogs" / "track what [vendor] is publishing."
- "Aggregate posts about [keyword] across these blogs."
- As an upstream feeder for `content-brief-factory`, `campaign-brief-generator`, or a
  weekly competitive-content digest.

## How to run

Bundled script `scripts/blog_feed_monitor.py` (Python 3 stdlib only — no install):

```bash
python3 ${SKILL_DIR}/scripts/blog_feed_monitor.py --urls <url> [<url> ...] [options]
```

| Flag | Default | Meaning |
|---|---|---|
| `--urls` | (required) | One or more blog/site URLs. |
| `--keywords` | `""` | Comma-separated OR filter on title+summary. |
| `--days` | `30` | Only posts from the last N days. |
| `--max-posts` | `50` | Cap on returned posts. |
| `--mode` | `auto` | `auto` (feed then index scrape) · `rss` (feed only) · `hostile` (agent runs Apify — see Notes). |
| `--output` | `json` | `json` (`{posts, skipped}`) or `summary` (readable lines). |

### Examples

```bash
# Two competitor blogs, last 30 days
python3 ${SKILL_DIR}/scripts/blog_feed_monitor.py --urls https://a.com https://b.com/blog --days 30

# Keyword-filtered sweep, human-readable
python3 ${SKILL_DIR}/scripts/blog_feed_monitor.py --urls https://a.com --keywords "rpa,automation" --output summary
```

## Outputs

JSON `{ "posts": [...], "skipped": [...] }`. Each post:
`{title, url, canonical_url, date, summary, source}`, deduped by canonical URL and sorted
newest-first. `skipped` lists URLs where no feed/index could be read (the run does not abort).

## Credentials / env

- **Required:** none — RSS/Atom + index fetch are fully keyless (the default).
- **Optional:** `APIFY_API_TOKEN` (paid, with a fallback) — If `APIFY_API_TOKEN` is set →
  the agent runs the hostile-site Apify RSS/blog actor (`--mode hostile`, call
  `https://api.apify.com/v2/acts/<actor>/run-sync-get-dataset-items?token=$APIFY_API_TOKEN`)
  for sites too hostile for feed + index scrape (better coverage on anti-bot sites). If not
  set → degrade to RSS/Atom + index scrape (the keyless default). Route volume through
  Robomotion Proxy at the node.

## Notes & edge cases

- RSS is the happy path — lead with it. RSS often surfaces only the most recent 10–50 posts;
  for a full back-catalog use `site-content-catalog` (sitemap crawl) instead.
- Dedup is by canonical URL (query/UTM + fragment stripped).
- Undated posts (from the index fallback) are kept and sorted to the bottom.
- When all paths fail for a URL it is reported in `skipped`, not fatal.
- `--mode hostile`: the script does not call Apify itself (keeps it dependency-free); it is
  the agent's documented last resort when a site is too hostile for feed + index scrape.
