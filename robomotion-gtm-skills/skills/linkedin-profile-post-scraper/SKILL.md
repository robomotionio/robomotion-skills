---
name: linkedin-profile-post-scraper
description: Scrape recent posts from specific LinkedIn profiles to monitor what founders/execs are posting, track activity, or gather post content for competitive intelligence and outreach personalization. Apify profile-posts actor primary; degrades to web-automation + session cookie in a Robomotion flow. Client-side date and keyword filtering.
metadata:
  version: 1.0.1
  category: outreach
  type: capability
---

# LinkedIn Profile Post Scraper

Pull the recent posts of one or more LinkedIn profiles. The feed is JS/auth-walled, so the
primary path is an **Apify profile-posts actor** (cookieless). The keyless degrade is the
bundled **Playwright scraper** (`li_profile_posts_playwright.mjs`) driven by a LinkedIn
`li_at` session cookie — no paid key.

## When to use

- "Monitor what [person] is posting on LinkedIn" / "track founder/exec activity."
- "Pull recent posts from these profiles" / "what has this person been saying lately?"
- Upstream of `linkedin-message-writer` and the signal composites that need recent-post
  context to personalize a touch.

## How to run

Python 3 stdlib only — no install:

```bash
# Apify path if APIFY_API_TOKEN set; else keyless Playwright degrade via LI_AT cookie
# (one-time: npx playwright install chromium)
python3 ${SKILL_DIR}/scripts/profile_posts.py \
  --profiles "https://www.linkedin.com/in/someceo" \
  --max-posts 20 --days 30 --keywords "ai,automation" --output json
```

| Flag | Default | Meaning |
|---|---|---|
| `--profiles` | (required) | Comma-separated canonical `/in/<user>` URLs (rejects vanity/search URLs). |
| `--max-posts` | `20` | Cap per profile. |
| `--keywords` | `""` | Comma-separated OR content filter. |
| `--days` | `30` | Only posts from the last N days (client-side). |
| `--actor` | apimaestro profile-posts | Override Apify actor id. |
| `--output` | `json` | `json` / `summary`. |

## Outputs

Per post: `{author, author_url, text, posted_at, reactions, comments, shares, url}`,
date-filtered and keyword-filtered. Posts with no parseable timestamp are kept and flagged
`_date_unknown` (degrade to relative date).

## Credentials / env

- `env.required`: **none.** The script runs keyless via the bundled Playwright degrade using
  a LinkedIn `li_at` cookie. Supply either an Apify token or an `LI_AT` cookie to run.
- `env.optional` (both degrade; supply one): **if `APIFY_API_TOKEN` is set → Apify cookieless
  profile-posts actor (primary, higher throughput); else → bundled Playwright scraper
  (`li_profile_posts_playwright.mjs`) with the `LI_AT` session cookie** (the keyless default;
  lower throughput, needs `npx playwright install chromium`).

## Notes & edge cases

- LinkedIn has no server-side date filter — filtering is always client-side on `posted_at`;
  some posts lack a precise timestamp (flagged, kept).
- Profile URLs must be canonical `/in/<user>` links; the script rejects vanity/search URLs.
- Throttle + route through Robomotion Proxy to avoid anti-bot blocks. Apify path costs
  ~credits per ~1k posts — note before running.
