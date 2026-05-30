---
name: tiktok-influencer-finder
description: Find TikTok influencers/creators matching a specific niche, with follower-range, location, and fit-score filtering — for creator/influencer-marketing outreach lists. Apify TikTok discovery actor primary (built-in fit scoring); keyless web-search degrade where the agent estimates fit. TikTok-only.
metadata:
  version: 1.0.1
  category: outreach
  type: capability
---

# TikTok Influencer Finder

Discover TikTok creators for a niche. Primary path is an **Apify TikTok discovery actor**
(metrics + built-in fit scoring). Degrade is a **keyless web search** for candidate
`tiktok.com/@handle` profiles (no metrics, no actor fit score — the agent estimates fit
from the niche description).

## When to use

- "Find TikTok creators / influencers in [niche]" / "discover TikTok influencers for [campaign]."
- When the user wants TikTok specifically. TikTok-only — for other platforms, route to
  `linkedin-influencer-discovery` / `kol-discovery`.

## How to run

Python 3 stdlib only — no install:

```bash
python3 ${SKILL_DIR}/scripts/tiktok_finder.py \
  --description "B2B SaaS founders sharing growth/automation tips for small teams" \
  --keywords 5 --profiles-per-keyword 10 \
  --min-followers 10000 --min-fit 0.6 --location US --output json
```

| Flag | Default | Meaning |
|---|---|---|
| `--description` | (required) | Detailed niche + content style + target audience. |
| `--keywords` | `5` | Number of search keywords (max 5). |
| `--profiles-per-keyword` | `10` | Profiles per keyword (max 10). |
| `--min-followers` / `--max-followers` | `0` | Follower-range filter (0 = unbounded). |
| `--min-fit` | `0.0` | Minimum fit score 0-1 (0.6 recommended; only applies when the actor returns a score). |
| `--location` | `""` | Country/region filter. |
| `--actor` | clockworks tiktok-scraper | Override Apify actor id. |
| `--output` | `json` | `json` / `csv` / `summary`. |

Prints `analyzed N, matched M` to stderr.

## Outputs

`{analyzed, matched, creators:[{creator, handle, profile_url, followers, engagement_rate,
location, content_focus, fit_score, fit_description, source}]}`, sorted by fit then followers.

## Credentials / env

- `env.required`: **none** — the serp degrade always runs.
- `env.optional`: `APIFY_API_TOKEN` — **if set → TikTok discovery actor with metrics + built-in
  fit scoring; else → keyless serp candidate discovery** (the default; no metrics, `--min-fit`
  no-ops and the agent estimates fit from the description).

## Notes & edge cases

- TikTok-only — if the user wants another platform, say so and route to the LinkedIn/KOL skills.
- Engagement rate can exceed 100% when viral posts outpace follower count — surfaced as-is.
- The discovery actor can take 1-3 minutes; warn before long runs. When few results match,
  broaden the niche or loosen follower/fit filters.
