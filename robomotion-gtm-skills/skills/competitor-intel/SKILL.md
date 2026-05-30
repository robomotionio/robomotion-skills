---
name: competitor-intel
description: Research 2–5 competitors across web, blogs, reviews, and social; build deep per-competitor profiles (overview, positioning, product, content, customer evidence, signals); and translate competitor moves into positioning/pricing/messaging recommendations. The baseline competitive-intel engine reused by battlecard-generator and competitor-monitoring-system. Keyless backbone; the agent profiles and recommends.
metadata:
  version: 1.0.1
  category: competitive-intel
  type: composite
---

# Competitor Intel

Composite and reusable primitive: deterministic scripts collect public signal per
competitor across three layers (data collection, content tracking, optional monitoring);
**you, the agent, write each profile, synthesize the landscape, and recommend actions.**

## When to use

- "Research [competitor]." / "Build a competitor profile for [company]."
- "What are our competitors doing?" / "Competitive landscape analysis."
- Baseline engine invoked per-competitor by `competitor-monitoring-system`; shares its
  review/social/pricing legs with `battlecard-generator` and `company-current-gtm-analysis`.

## How to run

Loop per competitor (2–5). Pick `quick` (website + serp + one review pass) or `deep`
(adds social + full review/ad mining) depth.

### 1. Company / product / positioning pages

```bash
python3 ${SKILL_DIR}/scripts/fetch_pages.py \
  --url https://competitor.com https://competitor.com/about \
        https://competitor.com/pricing https://competitor.com/product \
        https://competitor.com/integrations https://competitor.com/customers \
  --output ${WORKSPACE}/acme_pages.json
```

Use your own web search for `[company] funding`, `[company] founders`, `[company] launch 2026`,
and `[company] vs` / alternatives pages. Re-fetch JS-rendered pages with
`node ${SKILL_DIR}/scripts/render_page.mjs --url <u> --output ...`.

### 2. Content & marketing

```bash
python3 ${SKILL_DIR}/scripts/fetch_feed.py --url https://competitor.com/blog \
  --output ${WORKSPACE}/acme_blog.json     # cadence, authors, recent topics
```

Find social handles via web search. For founder/company LinkedIn activity use
`render_page.mjs` (one-off) or `PHANTOMBUSTER_API_KEY` (scale).

### 3. Customer evidence (reviews)

Render the G2/Capterra review page (anti-bot, JS):

```bash
npx playwright install chromium   # first run only
node ${SKILL_DIR}/scripts/render_page.mjs \
  --url "https://www.g2.com/products/<acme>/reviews" \
  --selector "[itemprop='review']" --output ${WORKSPACE}/acme_g2.json
```

Pull rating + praise/complaint themes. Apify fallback on hard block (see Notes).

### 4. Optional social depth (`deep` only)

Reddit/X/LinkedIn at depth → `APIFY_API_TOKEN` actors or `PHANTOMBUSTER_API_KEY`
(LinkedIn). Without keys, your own web search covers the basics.

### 5. Profile + synthesize (you, the agent — no script)

Per competitor write: overview, positioning, product, content/marketing, customer evidence,
signals, strengths/weaknesses-vs-you, your opportunity. Then synthesize a landscape summary
(positioning map, content comparison, feature comparison, key takeaways) and recommended
actions — **ground every recommendation in a collected signal**. Dedup across sources; an
item on both Reddit and X is higher signal — flag it.

### 6. Optional ongoing monitoring

Write the fields to track as flat JSON, then diff + save across runs:

```bash
python3 ${SKILL_DIR}/scripts/snapshot_store.py diff --entity acme \
  --input ${WORKSPACE}/acme_track.json --store ${WORKSPACE}/supabase/competitor_history.csv
python3 ${SKILL_DIR}/scripts/snapshot_store.py save --entity acme \
  --input ${WORKSPACE}/acme_track.json --store ${WORKSPACE}/supabase/competitor_history.csv
```

## Outputs

- `${WORKSPACE}/*_pages.json`, `*_blog.json`, `*_g2.json` — collected signal per competitor.
- `${WORKSPACE}/competitor-profiles-[date].md` — profiles + landscape + actions (your synthesis).
- `${WORKSPACE}/supabase/competitor_history.csv` — monitoring history (if step 6 used).

## Credentials / env

- **Required:** none — baseline research (fetch / feed / render) is free; synthesis is the agent.
- **Optional:** `APIFY_API_TOKEN` (Reddit/X/LinkedIn/review depth); `PHANTOMBUSTER_API_KEY`
  + LinkedIn cookie (LinkedIn at scale); `SUPABASE_URL`/`SUPABASE_KEY` or `AIRTABLE_API_KEY`
  (durable profile history for monitoring); `DATAFORSEO_LOGIN`/`DATAFORSEO_PASSWORD` or
  `SERPER_API_KEY` for the funding/founders/alternatives searches (if set -> paid SERP; if not
  -> the agent's own web search, the default).

## Notes & edge cases

- Default to the free backbone; reach for Apify/Phantombuster only for social depth or hostile
  review sites.
- `quick` = website + serp + a single review pass; `deep` adds social + full review/ad mining.
- Ground every recommendation in a collected signal — no generic advice.
- Apify degrade (when set): `curl -s "https://api.apify.com/v2/acts/<actor>/run-sync-get-dataset-items?token=$APIFY_API_TOKEN" -d '{...}'`.
