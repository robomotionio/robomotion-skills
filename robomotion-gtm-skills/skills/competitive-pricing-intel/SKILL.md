---
name: competitive-pricing-intel
description: Monitor competitor pricing pages over time — capture current plans/tiers/feature-gating, pull Wayback history, and diff against the last snapshot to detect price changes, tier restructuring, model shifts, and gating moves. Produces a living pricing comparison matrix plus change alerts. Keyless backbone; the agent normalizes and writes the report.
metadata:
  version: 1.0.1
  category: competitive-intel
  type: composite
---

# Competitive Pricing Intel

Composite: deterministic scripts capture live + historical pricing pages and diff snapshots
across runs; **you, the agent, normalize heterogeneous pricing, compute ICP-scenario cost,
and write the report.** Two modes: `first_run` (baseline) and `recurring` (diff).

## When to use

- "What are our competitors charging?" / "Has [competitor] changed pricing recently?"
- "Build a pricing comparison matrix." / "Monitor competitor pricing for changes."
- Runs standalone or as a recurring sub-routine inside `competitor-monitoring-system`.

## How to run

### 1. Live capture (per competitor)

```bash
python3 ${SKILL_DIR}/scripts/fetch_pages.py \
  --url https://competitor.com/pricing --output ${WORKSPACE}/acme_pricing.json
```

Interactive pricing (monthly↔annual toggles, currency/region, calculators) is JS — render it:

```bash
npx playwright install chromium   # first run only
node ${SKILL_DIR}/scripts/render_page.mjs \
  --url https://competitor.com/pricing --wait 5000 \
  --output ${WORKSPACE}/acme_pricing_rendered.json
```

### 2. Historical check (Wayback)

```bash
python3 ${SKILL_DIR}/scripts/wayback_fetch.py \
  --url https://competitor.com/pricing --snapshots 3 \
  --output ${WORKSPACE}/acme_pricing_history.json
```

Each snapshot includes `prices_found` and a text excerpt so you can spot tier/price moves.

### 3. Announcement research

Use your own web search for `"[competitor]" "new pricing" OR "updated plans"` and
`site:reddit.com [competitor] "price increase"`. Apify Reddit actor only if you need depth
(see Notes).

### 4. Normalize + analyze (you, the agent — no script)

From the live + historical JSON, build the **normalized matrix**: plan names, monthly/annual
prices, limits, add-ons, free tier, enterprise trigger, model. Reduce per-seat vs usage vs
flat to an **ICP-scenario effective cost** before comparing. Classify each competitor's
packaging strategy.

### 5. Diff across runs (recurring mode)

Write the fields you want to track as a flat JSON object (e.g.
`{"starter_price":"$29/seat/mo","tiers":3,"free_tier":true}`), then:

```bash
# recurring: compare to last saved snapshot, then save the new one
python3 ${SKILL_DIR}/scripts/snapshot_store.py diff --entity acme \
  --input ${WORKSPACE}/acme_fields.json \
  --store ${WORKSPACE}/supabase/pricing_history.csv
python3 ${SKILL_DIR}/scripts/snapshot_store.py save --entity acme \
  --input ${WORKSPACE}/acme_fields.json \
  --store ${WORKSPACE}/supabase/pricing_history.csv
```

`diff` returns `added` / `removed` / `changed` (with prev→current). Rate each change by
severity (price, tier, gating, model, free-tier). `first_run: true` means baseline only — do
not fake a diff.

### 6. Report (you, the agent)

Write `pricing-comparison-[YYYY-MM-DD].md`: change-alert section, normalized matrix,
ICP-scenario cost table, feature-gating comparison, packaging summary, recommendations.

## Outputs

- `${WORKSPACE}/*_pricing.json`, `*_pricing_history.json` — captured signal.
- `${WORKSPACE}/supabase/pricing_history.csv` — durable snapshot history for diffing.
- `${WORKSPACE}/pricing-comparison-[date].md` — the report (your synthesis).

## Credentials / env

- **Required:** none — fetch / render / Wayback / snapshot-store are all keyless.
- **Optional:** `SUPABASE_URL`/`SUPABASE_KEY` or `AIRTABLE_API_KEY` for durable history in a
  shared store (the CSV store works offline without them); `APIFY_API_TOKEN` for deeper
  Reddit reaction mining; `DATAFORSEO_LOGIN`/`DATAFORSEO_PASSWORD` or `SERPER_API_KEY` for the
  pricing-announcement / reaction searches (if set -> paid SERP; if not -> the agent's own web
  search, the default).

## Notes & edge cases

- Pricing pages change infrequently — schedule monthly.
- Wayback may lack recent snapshots; if so the first run is the de-facto baseline and change
  detection starts next cycle. The script returns a "first run — no prior snapshot" note
  rather than faking a diff.
- Normalize before comparing: per-seat vs usage vs flat must be reduced to an ICP-scenario
  effective cost or the matrix misleads.
- Some vendors localize prices by IP — capture the buyer-relevant region/currency with the
  renderer.
- Apify degrade (when set): `curl -s "https://api.apify.com/v2/acts/<actor>/run-sync-get-dataset-items?token=$APIFY_API_TOKEN" -d '{...}'`.
