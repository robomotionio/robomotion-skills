---
name: company-current-gtm-analysis
description: Analyze what a target company is doing across every go-to-market dimension — content, founder thought leadership, SEO/traffic, hiring, social, acquisition channels, podcasts/press, reviews, positioning, partnerships — and grade each A–F to expose white space. Run before designing a GTM strategy so the plan fills real gaps. Keyless backbone; the agent grades and writes the report.
metadata:
  version: 1.0.1
  category: competitive-intel
  type: composite
---

# Company Current GTM Analysis

Composite: deterministic scripts harvest each GTM channel's public footprint; **you, the
agent, grade each dimension (A–F), find white space, and write the report.**

## When to use

- "Run a GTM analysis for [company]." / "What is [company] doing across all of GTM?"
- Before a new client engagement or competitive strategy build.
- When you need a channel-by-channel scorecard plus prioritized white-space opportunities.

## How to run

Work the ten dimensions; parallelize the independent fetches.

### Content / blog

```bash
python3 ${SKILL_DIR}/scripts/fetch_feed.py --url https://company.com/blog \
  --output ${WORKSPACE}/blog_feed.json          # cadence, authors, recent topics
python3 ${SKILL_DIR}/scripts/fetch_pages.py \
  --url https://company.com/blog https://company.com/resources \
  --output ${WORKSPACE}/content_pages.json
```

### Positioning, customers, partnerships, integrations, careers

```bash
python3 ${SKILL_DIR}/scripts/fetch_pages.py \
  --url https://company.com https://company.com/about https://company.com/customers \
        https://company.com/pricing https://company.com/integrations \
        https://company.com/partners https://company.com/careers \
  --output ${WORKSPACE}/gtm_pages.json
```

Pages with `stats.likely_js_rendered: true` (JS ATS boards, JS marketing sites): re-fetch
with `node ${SKILL_DIR}/scripts/render_page.mjs --url <u> --output ...`.

### SEO / traffic

Use the `seo-traffic-analyzer` skill (keyless serp + SimilarWeb) for this section, or do
`site:` probes with your own web search. Do not invent traffic numbers.

### Founder LinkedIn, social, podcasts/press, reviews

- Founder LinkedIn posts: render a profile with `render_page.mjs --url <profile> --wait 6000`
  for a one-off, or use `PHANTOMBUSTER_API_KEY` (+ LinkedIn cookie) for scale. If neither,
  mark the section "[NEEDS VERIFICATION]".
- Social/podcasts/press: your own web search per platform; render specific pages as needed.
- Reviews: `render_page.mjs` on the G2/Capterra review URL (anti-bot, JS) — see Notes for
  the Apify fallback.

### Synthesize (you, the agent — no script)

Read all collected JSON and write `current-gtm-analysis.md`: executive summary, ten
dimension sections, and an A–F scorecard across ~15 dimensions, each graded **with
evidence** and the biggest opportunity. Grade relative to company stage. White space =
impact × effort. Save to `${WORKSPACE}/` and post as a channel attachment.

## Outputs

- `${WORKSPACE}/blog_feed.json`, `gtm_pages.json`, `content_pages.json` — collected signal.
- `${WORKSPACE}/current-gtm-analysis.md` — the graded report (your synthesis).

## Credentials / env

- **Required:** none — fetch/feed/render scripts are keyless; grading is the agent.
- **Optional:** `PHANTOMBUSTER_API_KEY` (+ LinkedIn cookie) for founder-LinkedIn at scale;
  `APIFY_API_TOKEN` for deeper Reddit/YouTube/review/LinkedIn scraping;
  `SUPABASE_URL`/`SUPABASE_KEY` or `AIRTABLE_API_KEY` for run history;
  `DATAFORSEO_LOGIN`/`DATAFORSEO_PASSWORD` or `SERPER_API_KEY` for the per-channel discovery
  searches (if set -> paid SERP; if not -> the agent's own web search, the default). Semrush/
  Ahrefs have no Robomotion package — if the team has a key, treat as optional manual enrichment.

## Notes & edge cases

- Parallelize the independent research threads to cut wall-clock time.
- If `fetch_pages.py` returns empty (`likely_js_rendered`), fall back to `render_page.mjs`.
- Grade relative to stage — a seed startup needs no analyst coverage; a Series-A does.
- Never invent metrics; flag unverifiable items "[NEEDS VERIFICATION]".
- Founder-LinkedIn underinvestment is usually the #1 finding — surface it explicitly when true.
- Apify degrade (when set): `curl -s "https://api.apify.com/v2/acts/<actor>/run-sync-get-dataset-items?token=$APIFY_API_TOKEN" -d '{...}'`.
