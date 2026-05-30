---
name: funding-signal-monitor
description: Detect recently-funded startups (Series A-C) as buying signals — fresh capital, growth mandate, active vendor evaluation. Aggregates funding announcements across tech press, Crunchbase, and Hacker News (keyless), dedups across sources, then (agent) extracts company/stage/amount/date and ranks for outreach in the post-raise buying window.
metadata:
  version: 1.0.0
  category: lead-generation
  type: composite
---

# Funding Signal Monitor

Surface companies in the ~1-3 month post-raise buying window. The script aggregates + dedups
announcement hits keylessly; the agent extracts the structured fields and ranks.

## When to use

- "Find companies that just raised Series A/B in [industry]."
- "Monitor funding announcements as buying signals." / "Who got funded recently to pitch?"

## How to run

### Step 1 — aggregate announcements (keyless)

```bash
python3 ${SKILL_DIR}/scripts/funding_search.py \
  --industries "fintech,devtools" \
  --stages "Series A,Series B" \
  --recency-days 30 \
  --output ${WORKSPACE}/funding.json
```

Searches tech press / Crunchbase via keyless web search and Hacker News via the free Algolia
API, dedups by company guess, and merges multi-source mentions into a `sources` list. For
X/Reddit depth, optionally run an Apify actor and merge in-agent (`APIFY_API_TOKEN`).

### Step 2 — extract + filter (you, the agent)

For each candidate in `funding.json`, read the source titles/snippets and fill `company`,
`stage`, `amount`, `date`. Drop rounds outside the stage/amount/industry/recency filters and
stale rounds (post-raise window is ~1-3 months).

### Step 3 — qualify + rank (you, the agent)

Rank by round size, stage fit, industry fit, and recency; write a `fit_note`. Multi-source
mentions raise confidence, not count. Export the ranked list + channel attachment.

## Outputs

`funding.json` — `[{company_guess, stage_hint, industry_hint, sources[], titles[],
company, stage, amount, date, fit_note}]`, sorted by source corroboration.

## Credentials / env

- **Required:** none — keyless serp + HN (free Algolia API) carry the bulk of results.
- **Optional:** `APIFY_API_TOKEN` (X/Reddit scraper depth — those sources degrade to
  serp `site:` search without it); `ANTHROPIC_API_KEY` only if the extraction LLM isn't
  platform-provided.

## Notes & edge cases

- The post-raise buying window is ~1-3 months — prioritize recency; drop stale rounds.
- Series A-C is the sweet spot; de-prioritize seed and late-stage unless configured.
- Dedup aggressively — the same round appears across many sources; multi-source mentions
  raise confidence, not count (the script merges into `sources`).
- The keyless serp endpoint rate-limits; in production this maps to the Robomotion serp node
  with a proxy. Apify spend is optional and small.
