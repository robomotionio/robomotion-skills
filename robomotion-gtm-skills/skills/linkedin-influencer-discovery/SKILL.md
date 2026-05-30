---
name: linkedin-influencer-discovery
description: Discover top LinkedIn influencers and voices by topic, industry, country, and follower count — to build the top-N voices in a space, assemble influencer lists for outreach, or identify thought leaders to engage. Apify influencer-database actor primary (accurate follower counts + email flags); keyless web-search degrade.
metadata:
  version: 1.0.1
  category: outreach
  type: capability
---

# LinkedIn Influencer Discovery

Find the top voices for a topic. Primary path is an **Apify influencer-database actor**
(indexed profiles, accurate follower counts and email flags). Degrade is a **keyless web
search** for candidate `/in/` profiles — no follower precision, so the agent ranks by serp
prominence + relevance instead.

## When to use

- "Find the top 100 voices in [space]" / "who are the LinkedIn thought leaders for [topic]?"
- "Build an influencer list" filtered by follower range / country / email-available.
- Pairs with `linkedin-profile-post-scraper` (enrich recent posts) and `kol-discovery`
  (post-engagement-based ranking).

## How to run

Python 3 stdlib only — no install:

```bash
python3 ${SKILL_DIR}/scripts/influencer_discovery.py \
  --topic "artificial intelligence" \
  --min-followers 50000 --country US --has-email \
  --max-results 100 --output json
```

| Flag | Default | Meaning |
|---|---|---|
| `--topic` | (required) | The space, e.g. "saas", "marketing". |
| `--category` | `""` | Coarse category (technology, business, ...). |
| `--country` / `--language` | `""` | Geo / language filters. |
| `--min-followers` / `--max-followers` | `0` | Follower-range filter (0 = unbounded). |
| `--has-email` | off | Only profiles with an email. |
| `--max-results` | `100` | Cap (up to 1000). |
| `--actor` | apimaestro influencers-database | Override Apify actor id. |
| `--output` | `json` | `json` / `summary`. |

## Outputs

Ranked by follower count desc: `{full_name, username, biography, follower_count,
following_count, main_topic, topics, category, linkedin_url, has_email, external_url,
country, city, is_verified, source}`. `source` is `apify-index` or `serp-degrade`.

## Credentials / env

- `env.required`: **none** — the serp degrade always runs (Robomotion Proxy is platform-provided).
- `env.optional`: `APIFY_API_TOKEN` — **if set → indexed influencer-database actor (accurate
  follower counts + email flags); else → keyless serp candidate discovery** (the default; no
  follower metrics, so `min/max-followers` and `has-email` filters effectively no-op).

## Notes & edge cases

- The Apify index is pre-built (not live LinkedIn search); follower counts can be
  cross-platform, not LinkedIn-specific — flagged via `source`.
- `min/max-followers` and `has-email` filter client-side after results return.
- On the serp degrade there are no follower counts — rank by serp prominence + relevance and
  treat the list as lower-confidence candidates.
