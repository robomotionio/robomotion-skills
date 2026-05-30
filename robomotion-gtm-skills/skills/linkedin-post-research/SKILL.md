---
name: linkedin-post-research
description: Search LinkedIn posts by keyword, sorted by engagement or date, returning author, post text, reaction/comment/share counts, URL, and date. Use to research what people say about a topic, find high-engagement content, spot thought leaders, or seed a warm-lead pipeline. Apify actor primary with a keyless web-search degrade.
metadata:
  version: 1.0.1
  category: outreach
  type: capability
---

# LinkedIn Post Research

Search public LinkedIn posts for one or more keywords. Primary path is an **Apify
posts-search actor** (cookieless, full engagement metrics); degrades to a **keyless web
search** over public `linkedin.com/posts` URLs (titles/URLs only, no engagement counts).

## When to use

- "What are people saying about [topic] on LinkedIn?" / "search LinkedIn posts."
- "Find high-engagement posts on [topic]" / "who's posting about [topic]?"
- Feeds `linkedin-commenter-extractor` (posts -> commenters) and `kol-discovery`.

## How to run

Python 3 stdlib only — no install:

```bash
python3 ${SKILL_DIR}/scripts/post_search.py \
  --keywords "rpa,workflow automation" \
  --max-items 50 --sort-by relevance --output json
```

| Flag | Default | Meaning |
|---|---|---|
| `--keywords` | (required) | Comma-separated search keywords. |
| `--max-items` | `50` | Cap per keyword. |
| `--sort-by` | `relevance` | `relevance` (engagement) or `date_posted`. |
| `--actor` | apimaestro posts-search | Override the Apify actor id. |
| `--output` | `json` | `json` / `csv` / `summary`. |

Results are deduped across keywords by `activity_id` and sorted. The agent then judges
relevance and picks the posts worth acting on.

## Outputs

Per post: `{author, author_headline, author_profile_url, keyword, reactions, comments,
shares, date, post_preview, full_text, url, activity_id, hashtags, is_repost, source}`.
`source` is `apify` (full metrics) or `serp-degrade` (URL/title only).

## Credentials / env

- `env.required`: **none** — the keyless serp degrade always works (Robomotion Proxy is
  platform-provided in production).
- `env.optional`: `APIFY_API_TOKEN` — **if set → cookieless Apify posts-search actor with full
  engagement metrics; else → keyless public `site:linkedin.com/posts` search** (the default;
  no reaction/comment counts, prints a fidelity warning).

## Notes & edge cases

- Engagement counts and `activity_id` are only reliable via Apify (or web-automation against
  the logged-in app); the serp fallback returns titles/URLs only — fidelity is flagged in
  `source` and on stderr.
- Too-specific keywords return zero results — broaden and retry.
- Apify path costs ~credits per ~50 posts; note before running at volume.
- The bundled degrade uses DuckDuckGo HTML; in a Robomotion flow this maps to
  `robomotion-serp` Search behind the platform proxy.
