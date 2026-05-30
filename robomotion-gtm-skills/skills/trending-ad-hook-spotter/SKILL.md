---
name: trending-ad-hook-spotter
description: Scan X, Reddit, LinkedIn, and Hacker News for trending narratives, viral posts, and hot-button topics in a given space, score each by recency/velocity/relevance, and translate the actionable ones into concrete ad hooks with timing-urgency windows. Tells a paid team what to run ads about right now while the topic is hot.
metadata:
  version: 1.0.1
  category: ads
  type: composite
---

# Trending Ad Hook Spotter

Composite: **multi-platform social scan → trend detection + scoring → hook translation →
report.** The HN scan is a keyless deterministic script; X/Reddit/LinkedIn scanning is
agent-driven web search (with an optional Apify depth fallback). **Trend clustering,
scoring, urgency tiering, and hook writing are the agent's reasoning — no LLM call in a
script. Recency is everything: bound every scan to the last ~7 days.**

## When to use

- "What's trending in our space that we could run ads about?"
- "Find viral hooks for our paid campaigns" / "Newsjacking opportunities for `<client>`."
- "What should we be running ads about this week?"
- Good cron candidate for a weekly "what to run this week" digest.

## How to run

### 1 — Hacker News scan (keyless, recency-bounded)

```bash
python3 ${SKILL_DIR}/scripts/hn_trends.py --keywords "rpa,workflow automation,ai agents" \
  --days 7 --output ${WORKSPACE}/hn.json
# Front-page sweep too:
python3 ${SKILL_DIR}/scripts/hn_trends.py --keywords "observability" --tags front_page --days 3
```

Returns items ranked by an engagement-velocity proxy (points + comments per hour since
posting), so old high-engagement threads don't masquerade as trends.

### 2 — X / Reddit / LinkedIn scan (you, the agent — keyless web search)

Drive via web search bounded to the past ~7 days (Robomotion Proxy). **SERP path: if
`DATAFORSEO_LOGIN`/`DATAFORSEO_PASSWORD` (or `SERPER_API_KEY`) is set → structured SERP API;
if not → the agent's keyless web search (default).**

- **X** — `<keyword> (viral OR thread) site:x.com`, competitor-momentum (launches/outages/
  funding) and frustration queries.
- **Reddit** — `site:reddit.com` topic/hot threads; flag high upvote/comment ratios,
  buying-intent and switching threads.
- **LinkedIn** — `site:linkedin.com/posts` / `site:linkedin.com/pulse` for KOL + competitor
  posts.

For depth beyond search (X/Reddit at volume): **if `APIFY_API_TOKEN` is set → use the Apify
runner (better depth/velocity); if not → degrade to `site:` web search (default).** Apify
runner:

```bash
python3 ${SKILL_DIR}/scripts/apify_run.py --actor "trudax~reddit-scraper" \
  --input '{"searches":["ai agents"],"sort":"hot","maxItems":60}' --output ${WORKSPACE}/reddit.json
```

Without `APIFY_API_TOKEN`, degrade X/Reddit to `site:` search (lower velocity precision —
note it). HN always works key-free. **LinkedIn engagement depth: if `PHANTOMBUSTER_API_KEY`
(+ a LinkedIn session cookie) is set → PhantomBuster path; if not → `site:linkedin.com` web
search (default).**

### 3 — Detect + score trends (you, the agent)

Cluster signals into trends (cross-platform within 7 days, OR one post with ~10×-norm
engagement, OR a breaking event). **Normalize velocity for account size/age** so a small
viral post isn't drowned by a big account's baseline. Score each trend: **recency 25 /
velocity 25 / cross-platform 20 / ICP relevance 20 / product fit 10** → urgency tier
(Run Today 90+, This Week 70–89, Worth Testing 50–69). If `content_velocity` is "weekly",
down-weight 24–48h trends the team can't act on in time.

### 4 — Hook translation (you)

For each trend ≥50: a 2-sentence summary, ad-opportunity rationale, **3 hook variants
(newsjack / contrarian / practical)**, recommended format + platform, and a time window
(gated by `content_velocity`).

### 5 — Render

Write `trending-hooks-<YYYY-MM-DD>.md` to `${WORKSPACE}` and attach to the Agent Teams
channel. For a recurring digest, schedule via the platform cron and dedup seen trends across
runs (`SUPABASE_*` if persisting).

## Outputs

`trending-hooks-<YYYY-MM-DD>.md` — trends grouped by urgency tier, each with a 2-sentence
summary, engagement signal, time window, and 3 hook variants + recommended format/platform;
a trend-velocity dashboard (platform × score × window) and a competitor-trend-involvement
table.

## Credentials / env

- **Required:** none — scanning runs on web search + the keyless HN API. Trend detection,
  scoring, and hook writing are the agent's reasoning (no LLM key in scripts).
- **Optional (each with a keyless default fallback):**
  - `APIFY_API_TOKEN` — if set → Apify Reddit/X actor for depth; else → `site:` web search +
    the keyless HN API (default).
  - `PHANTOMBUSTER_API_KEY` (+ LinkedIn session cookie) — if set → PhantomBuster LinkedIn
    engagement depth; else → `site:linkedin.com` web search (default).
  - `SUPABASE_URL`/`SUPABASE_KEY` — if set → dedup seen trends across cron runs; else →
    single-run output (default).
  - `DATAFORSEO_LOGIN`/`DATAFORSEO_PASSWORD` (or `SERPER_API_KEY`) — if set → structured SERP
    API for the social-scan queries; else → the agent's keyless web search (default).
  - `HTTPS_PROXY` — Robomotion Proxy for SERP scans.

## Notes & edge cases

- Recency is everything — bound every scan to ~7 days; an old high-engagement thread is not
  a trend.
- Normalize engagement velocity for account size/age.
- Without `APIFY_API_TOKEN`, X/Reddit degrade to `site:` search (note lower precision);
  HN always works key-free.
- Throttle + proxy all SERP scans.
