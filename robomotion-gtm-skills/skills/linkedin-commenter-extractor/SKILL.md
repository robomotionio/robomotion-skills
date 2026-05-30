---
name: linkedin-commenter-extractor
description: Extract everyone who commented on specific LinkedIn posts — name, title, company, profile URL, and comment text — to surface warm leads who actively engaged with a relevant discussion. Apify post-comments actor; degrades to web-automation + session cookie inside a Robomotion flow. Downstream of linkedin-post-research, upstream of message writers.
metadata:
  version: 1.0.1
  category: outreach
  type: capability
---

# LinkedIn Commenter Extractor

Harvest the commenters on one or more LinkedIn posts into a warm-lead list. Comment
threads are auth/JS-walled, so the primary path is an **Apify post-comments actor**
(cookieless). The keyless degrade is the bundled **Playwright scraper**
(`li_comments_playwright.mjs`) driven by a LinkedIn `li_at` session cookie — no paid key.

## When to use

- "Who commented on this post?" / "pull the commenters from these posts."
- Build a warm-lead list from people engaging with a thought-leadership or competitor post.
- Downstream of `linkedin-post-research` (find high-engagement posts -> harvest commenters);
  upstream of `linkedin-message-writer` / `cold-email-outreach`.

## How to run

Python 3 stdlib only — no install:

```bash
# Apify path if APIFY_API_TOKEN set; else keyless Playwright degrade via LI_AT cookie
# (one-time: npx playwright install chromium)
python3 ${SKILL_DIR}/scripts/extract_commenters.py \
  --post-urls "https://www.linkedin.com/posts/x_y-activity-123,https://www.linkedin.com/posts/..." \
  --max-comments 100 --dedup --output csv
```

| Flag | Default | Meaning |
|---|---|---|
| `--post-urls` | (required) | Comma-separated LinkedIn post URLs. |
| `--max-comments` | `100` | Cap per post. |
| `--dedup` | off | Dedup commenters across posts by profile URL. |
| `--actor` | apimaestro post-comments | Override Apify actor id. |
| `--output` | `json` | `json` / `csv` / `summary`. |

Headlines are parsed heuristically into `title` / `company` on the "X at Y" / "X @ Y"
pattern; ambiguous headlines keep the raw value and leave title/company blank.

## Outputs

Per commenter: `{name, headline, title, company, linkedin_url, comment_text, post_url,
profile_image_url}`, optionally deduped.

## Credentials / env

- `env.required`: **none.** The script runs keyless via the bundled Playwright degrade using
  a LinkedIn `li_at` cookie. Supply either an Apify token or an `LI_AT` cookie to run.
- `env.optional` (both degrade; supply one): **if `APIFY_API_TOKEN` is set → Apify cookieless
  post-comments actor (primary, higher throughput); else → bundled Playwright scraper
  (`li_comments_playwright.mjs`) with the `LI_AT` session cookie** (the keyless default; lower
  volume, needs `npx playwright install chromium`).

## Notes & edge cases

- Comment lists are paginated/lazy-loaded — the actor scrolls/expands up to `max_comments`.
- Headline parsing is heuristic; when "at" is ambiguous, the raw headline is kept and
  title/company left null rather than guessed.
- Dedup across posts matters when harvesting multiple posts from one author's audience.
- Apify path costs ~credits per ~1k comments — note before running at volume.
