---
name: inbound-lead-qualification
description: Thoroughly qualify a batch of inbound leads against full ICP criteria (company size, industry, use-case fit, role/seniority), check CRM/customer base for dupes and existing relationships, and output a scored CSV with verdict, reasoning, and pipeline-overlap flags. The deep qualification step, not fast triage.
metadata:
  version: 1.0.0
  category: lead-generation
  type: composite
---

# Inbound Lead Qualification

The deep qualification step. CRM/overlap flags + missing-field research are deterministic
scripts; the verdict + reasoning are the agent's, scored against the ICP rubric with
explicit per-criterion rationale.

## When to use

- "Qualify these inbound leads." / "Check if these leads are ICP." / "Score my inbound."
- After upstream triage, when leads need a thorough qualified/disqualified verdict.

## How to run

### Step 1 — CRM / pipeline overlap

```bash
python3 ${SKILL_DIR}/scripts/crm_lookup.py \
  --leads ${WORKSPACE}/leads.csv \
  --crm-csv ${WORKSPACE}/customers.csv \
  --output ${WORKSPACE}/flags.json
```

Uses HubSpot search when `HUBSPOT_API_KEY` is set; else a CRM/customer CSV export. Flags
prevent qualifying a lead another rep already owns.

### Step 2 — fill missing company/person fields (if needed)

```bash
python3 ${SKILL_DIR}/scripts/web_research.py --leads ${WORKSPACE}/leads.csv \
  --fetch-pages --output ${WORKSPACE}/research.json
```

Keyless degrade for size/industry/role/seniority. With `APOLLO_API_KEY`, prefer Apollo
enrichment. Leads still `insufficient_data` route to `inbound-lead-enrichment` before a final
verdict — do **not** disqualify them outright.

### Step 3 — assemble the scorecard scaffold

```bash
python3 ${SKILL_DIR}/scripts/build_scorecard.py \
  --leads ${WORKSPACE}/leads.csv \
  --relationships ${WORKSPACE}/flags.json \
  --output ${WORKSPACE}/scorecard.json
```

### Step 4 — score (you, the agent)

For each lead, score size/industry/use-case/role against the ICP rubric and fill
`qualification_status`, `score`, and `reasoning`. Reasoning **must cite the criteria each
lead passed/failed** — no opaque scores.

### Step 5 — finalize

```bash
python3 ${SKILL_DIR}/scripts/build_scorecard.py --finalize \
  --scorecard ${WORKSPACE}/scorecard.json --format csv --output ${WORKSPACE}/scored.csv
```

## Outputs

A scored CSV/JSON: `name, email, company, title, linkedin_url, existing_relationship,
company_overlap, qualification_status, score, reasoning`.

## Credentials / env

- **Required:** none — qualification runs on serp-derived data + the agent's scoring.
- **Optional:** a CRM key (`HUBSPOT_API_KEY` / `SALESFORCE_*`) for the overlap check (else a
  CRM CSV export); `APOLLO_API_KEY` (enrich missing fields); `ANTHROPIC_API_KEY` only if the
  scoring LLM isn't platform-provided.

## Notes & edge cases

- Leads with `insufficient_data` route to `inbound-lead-enrichment` first, not disqualified.
- Tool-agnostic: works with any CRM or none (CSV).
- Reasoning must cite criteria per verdict — no opaque scores.
- Pipeline-overlap flags prevent qualifying a lead already owned by another rep.
