---
name: tam-builder
description: Build and maintain a scored Total Addressable Market — discover ICP-matching companies via Apollo Company Search, score fit 0-100, assign tiers (1/2/3), and auto-build a persona watchlist for Tier 1-2 companies via free Apollo People Search. Outputs to a store/CSV. Foundation for signal-scanner.
metadata:
  version: 1.0.1
  category: lead-generation
  type: capability
---

# TAM Builder

Discover → score → tier → watchlist. Company Search is the primary (and only metered) call;
People Search for the watchlist is free, so build it liberally for Tier 1-2. Apollo is
**optional**: with a key you get full firmographics (recommended); without one the skill
degrades to keyless serp company + people discovery and still builds a scored TAM.

## When to use

- "Build our TAM." / "Score the addressable market for [segment]."
- "Refresh the TAM — re-score, detect tier changes, deprecate stale companies."
- Foundation for `signal-scanner` (which scans the TAM for buying signals).

## How to run (`build` mode)

### Step 1 — discover companies (Apollo Company Search)

```bash
python3 ${SKILL_DIR}/scripts/apollo_companies.py \
  --employee-ranges "51,200" "201,500" \
  --keyword-tags "saas,b2b" \
  --locations "United States" \
  --num-results 1000 \
  --output ${WORKSPACE}/companies.json
```

**Keyless degrade (no `APOLLO_API_KEY`):** run `serp_companies.py` — keyless web search
returning candidate companies (name/domain/keywords) in the same shape; firmographics
(employees/industry/funding) come back blank for the agent / `score_tam.py` to estimate.

```bash
python3 ${SKILL_DIR}/scripts/serp_companies.py \
  --keyword-tags "saas,b2b" --locations "United States" \
  --num-results 50 --output ${WORKSPACE}/companies.json
```

### Step 2 — score + tier (deterministic)

Write a scoring config (`scoring.json`): weights, tier thresholds, target
industries/sizes/stages/geos. Then:

```bash
python3 ${SKILL_DIR}/scripts/score_tam.py \
  --input ${WORKSPACE}/companies.json \
  --config ${WORKSPACE}/scoring.json \
  --output ${WORKSPACE}/scored.json
```

Produces `fit_score` 0-100 + `tier` 1/2/3 with an auditable `scoring_breakdown`. For fuzzy
industry-fit calls you can re-score in-agent and merge.

### Step 3 — build the persona watchlist (free People Search)

```bash
python3 ${SKILL_DIR}/scripts/apollo_watchlist.py \
  --input ${WORKSPACE}/scored.json \
  --titles "VP Sales,Head of RevOps,CRO" \
  --max-tier 2 --per-company 5 \
  --output ${WORKSPACE}/watchlist.json
```

`apollo_watchlist.py` auto-degrades: with `APOLLO_API_KEY` it runs free Apollo People
Search; without it, a keyless `site:linkedin.com/in "<company>" "<title>"` search per
company (LinkedIn-profile candidates, agent resolves names, no email).

### Step 4 — persist (you, the agent)

Upsert `scored.json` (companies) + `watchlist.json` (people) into Supabase/Airtable with
snapshots so `refresh` can detect tier changes and `signal-scanner` can diff. Without a
durable store, deliver CSVs + a channel attachment (single build, no refresh).

### `refresh` / `status`

`refresh` = re-run steps 1-3, diff `fit_score`/`tier` vs. the stored snapshot, flag tier
changes, and **deprecate (don't delete)** companies no longer returned. `status` = a
read-only report from the stored TAM.

## Outputs

- `scored.json` — `[{name, domain, employees, industry, ..., fit_score, tier,
  scoring_breakdown}]`.
- `watchlist.json` — `[{name, title, company, company_domain, tier, linkedin_url}]` for
  Tier 1-2.

## Credentials / env

- **Required:** none. The skill runs keyless via `serp_companies.py` (discovery) +
  `apollo_watchlist.py`'s serp degrade (watchlist).
- **Optional:**
  - `APOLLO_API_KEY` — if set → Apollo Company + People Search (full firmographics: employees,
    industry, funding stage, etc. — recommended, higher quality). If not → keyless serp
    company/people discovery with blank firmographics (default).
  - `SUPABASE_URL` + `SUPABASE_SERVICE_ROLE_KEY` (or an Airtable key) — durable store enabling
    `refresh` tier-change detection and `signal-scanner` downstream (degrades to CSV-only
    single build).
  - `ANTHROPIC_API_KEY` only if LLM-assisted fuzzy scoring is not platform-provided.

## Notes & edge cases

- People Search is free — build the watchlist liberally for Tier 1-2; Company Search is the
  metered call. Stay within Apollo plan/rate limits.
- Persist snapshots so `refresh` detects tier changes and `signal-scanner` can diff.
- Deprecate (don't delete) stale companies on refresh to preserve history.
- The scoring breakdown is stored per company so tier assignments are auditable.
- Keyless path: firmographic depth is limited; `score_tam.py` weights on whatever fields are
  present, so prefer the Apollo path when employee/industry/funding precision matters.
