---
name: industry-scanner
description: A daily or weekly industry-intelligence scanner that sweeps web, social, news, blogs, and communities for everything relevant to a client's industry, consolidates and categorizes the signal into nine types, then generates a small set of genuine, actionable GTM opportunities. Outputs a dated intelligence briefing. Keyless collectors; the agent categorizes, rates relevance, and drafts opportunities.
metadata:
  version: 1.0.1
  category: competitive-intel
  type: composite
---

# Industry Scanner

Composite: deterministic collectors gather signal across configured sources; **you, the
agent, dedup, categorize into the nine types, rate relevance, and draft opportunities.** It
orchestrates collection — it does not reimplement other skills. A zero-opportunity day is a
valid, honest outcome.

## When to use

- "Run an industry scan for [client]." / "Run a weekly industry scan with lookback 7."
- Daily/weekly competitive + market awareness: competitor trouble, events, trends,
  funding/M&A, regulation, people moves, pain points, content openings.

## How to run

`lookback` = `1` (daily, default) or `7` (weekly deep). Parallelize collectors; skip any
source not in the client config.

### Collectors (run in parallel)

```bash
# Industry blogs — cadence + recent topics (one per configured blog)
python3 ${SKILL_DIR}/scripts/fetch_feed.py  --url https://industryblog.com --output ${WORKSPACE}/blog1.json
# Blog/landing pages that aren't feeds
python3 ${SKILL_DIR}/scripts/fetch_pages.py --url https://site.com/news --output ${WORKSPACE}/pages.json
# Hacker News — date-filtered per keyword/competitor
python3 ${SKILL_DIR}/scripts/hn_fetch.py    --query "<industry keyword>" --days 7 --output ${WORKSPACE}/hn.json
# RSS news feeds — same fetch_feed.py (auto-probes feed paths)
python3 ${SKILL_DIR}/scripts/fetch_feed.py  --url https://news-source.com/feed --output ${WORKSPACE}/news.json
```

- **Web search** (time-modified queries + each competitor): use your own web search.
- **Reddit**: web search `site:reddit.com <keyword>`; `APIFY_API_TOKEN` Reddit actor for
  subreddit/date depth.
- **X**: `node ${SKILL_DIR}/scripts/render_page.mjs --url <query-url> --wait 6000` or
  `APIFY_API_TOKEN` X actor for date-bounded queries.
- **LinkedIn**: `PHANTOMBUSTER_API_KEY` or Apify LinkedIn-post-search actor with date filter.
- **Review sites**: `render_page.mjs` on G2/Capterra/Trustpilot; Apify fallback.
- **Newsletter inbox**: only if the client has an email connector configured; else skip.

### Consolidate + categorize (you, the agent — no script)

Dedup (note multi-source items as higher signal), categorize each item into the nine types
(competitor news, events, trends, funding/M&A, regulatory, technology, people moves, pain
points, content opportunities), rate relevance High/Med/Low against the client's ICP/value
props, drop noise.

### Generate opportunities (you, the agent)

Only where a real, actionable play exists — match a strategy pattern (competitor-in-trouble,
event, viral post, M&A, regulation, pain point, trend, funding) to the trigger. Do not force
one per item.

### Briefing (you, the agent)

Write `industry-scan-[YYYY-MM-DD].md`: executive summary, categorized intelligence tables,
strategic growth opportunities (trigger, strategy, tactics, urgency, effort, expected
impact), and scan statistics. Empty categories and zero-opportunity days are acceptable.

## Outputs

- `${WORKSPACE}/blog1.json`, `hn.json`, `news.json`, `pages.json` — collected signal.
- `${WORKSPACE}/industry-scan-[date].md` — the briefing (your synthesis).

## Credentials / env

- **Required:** none — the core scan (keyless collectors + agent synthesis) needs no key.
- **Optional:** `APIFY_API_TOKEN` (Reddit/X/LinkedIn/review depth); `PHANTOMBUSTER_API_KEY`
  + LinkedIn cookie (structured LinkedIn post search); `DATAFORSEO_LOGIN`/`DATAFORSEO_PASSWORD`
  or `SERPER_API_KEY` for the time-modified industry/competitor sweep searches (if set -> paid
  SERP; if not -> the agent's own web search, the default); email/IMAP credential (only if
  newsletter-inbox monitoring is configured).

## Notes & edge cases

- Parallelize collectors aggressively; sources are independent and wall-clock time matters.
- Signal over volume: drop Low-relevance items unless genuinely noteworthy; a zero-opportunity
  day is a valid outcome — the briefing has standalone value.
- Multi-source items (e.g. on both Reddit and X) are higher signal — flag them.
- Tune noisy-source keywords in config rather than dropping a source.
- Daily (`lookback 1`) misses slow-developing stories; pair with a weekly (`lookback 7`) scan.
- Apify degrade (when set): `curl -s "https://api.apify.com/v2/acts/<actor>/run-sync-get-dataset-items?token=$APIFY_API_TOKEN" -d '{...}'`.
