---
name: champion-tracker
description: Detect when known product champions change jobs (a high-intent re-sell signal) and qualify their new company against ICP. Baseline each champion's LinkedIn profile, then on a recurring cadence re-scrape and diff company/title to surface movers with an ICP fit verdict, ready for warm outreach.
metadata:
  version: 1.0.1
  category: lead-generation
  type: capability
---

# Champion Tracker

Track a maintained champion list for job changes. `init` records a baseline of each
champion's current company + title; `track` re-scrapes and emits only the movers. You (the
agent) score each mover's new company against the ICP rubric and write the verdict.

## When to use

- "Tell me when our champions change companies."
- "Track these power users for job changes and score their new employers."
- A recurring cadence over a champion CSV (built from reviews, posts, or CRM exports).

## How to run

### Phase 1 — baseline (`init`)

Primary (Phantombuster LinkedIn Profile Scraper):

```bash
python3 ${SKILL_DIR}/scripts/pb_profiles.py \
  --agent-id "$PB_PROFILE_AGENT_ID" \
  --urls ${WORKSPACE}/champions.csv \
  --mode init \
  --output ${WORKSPACE}/baseline.json
```

`champions.csv` needs a `linkedin_url` column (a `name` column is used as a fallback label).

### Phase 2 — detect changes (`track`)

```bash
python3 ${SKILL_DIR}/scripts/pb_profiles.py \
  --agent-id "$PB_PROFILE_AGENT_ID" \
  --urls ${WORKSPACE}/champions.csv \
  --mode track \
  --baseline ${WORKSPACE}/baseline.json \
  --output ${WORKSPACE}/movers.json
```

Emits `{movers: [...], new_baseline: [...]}`. A mover has `old_company → new_company`
(and/or title). Movers with no usable new-company data get `needs_review: true`.

### Degrade — no Phantombuster key (Playwright)

```bash
cd ${SKILL_DIR}/scripts && npm install && npx playwright install chromium
LI_AT="<your li_at cookie>" node ${SKILL_DIR}/scripts/pb_profiles_pw.mjs \
  --urls ${WORKSPACE}/champions.csv --output ${WORKSPACE}/snapshot.json
```

Run it once per cadence to produce a snapshot, then diff snapshots in-agent using the same
old/new company+title comparison `pb_profiles.py --mode track` performs.

### Score & emit (you, the agent)

For each mover, score the **new** company against the ICP rubric on a 0–4 scale, attach a
verdict, and return a movers table. Movers flagged `needs_review` (no new-company data)
score 0 and are surfaced for manual review. Persist `new_baseline.json` for the next run.

## Outputs

- `baseline.json` — `[{linkedin_url, name, company, title}]` snapshot for diffing.
- `movers.json` — movers with old/new company+title + your 0–4 ICP score and verdict.

## Credentials / env

- **Required:** none. The keyless degrade (`pb_profiles_pw.mjs` Playwright + an `LI_AT`
  cookie) is the fallback LinkedIn-profile source.
- **Optional:**
  - `PHANTOMBUSTER_API_KEY` (+ a LinkedIn cookie on the phantom) or `APIFY_API_TOKEN` — if set
    → managed LinkedIn profile scraper (higher volume/reliability — recommended). If not →
    keyless `pb_profiles_pw.mjs` Playwright with `LI_AT`.
  - `LI_AT` — LinkedIn `li_at` session cookie for the Playwright degrade.
  - `PB_PROFILE_AGENT_ID` — configured profile-scraper agent (or pass `--agent-id`).
  - `SUPABASE_URL` + `SUPABASE_SERVICE_ROLE_KEY` (or an Airtable key) — durable baseline store
    (degrades to a workspace `baseline.json` for a single cadence).
  - `ANTHROPIC_API_KEY` only if the LLM scoring isn't platform-provided.

## Notes & edge cases

- Always run `init` before `track` — without a baseline there's nothing to diff.
- Proxy + throttle LinkedIn scrapes; randomize cadence to avoid blocks (the Playwright
  script jitters its per-profile wait).
- Dedup champions by normalized LinkedIn URL; rows lacking a profile URL are skipped.
- A move with no usable new-company data scores 0 and is flagged for manual review.
- Phantom result schemas vary by build; if a phantom uses non-standard field names, pass a
  downloaded result file via `--results-json` and re-map in-agent.
