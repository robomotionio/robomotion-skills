---
name: inbound-lead-enrichment
description: Fill in missing data on inbound leads — research the company, identify the person's role and seniority, find other buying-committee stakeholders, check the CRM for existing relationships, and update the lead record. Turns a bare email into a full profile. Keyless web research by default; Apollo/CRM keys enrich when present.
metadata:
  version: 1.0.0
  category: lead-generation
  type: composite
---

# Inbound Lead Enrichment

The enrichment arm feeding `inbound-lead-qualification` and `inbound-lead-triage`. Every
step has a keyless web-research degrade; paid tools (Apollo, dropcontact, CRM) only deepen
it. Synthesis is the agent's job — the scripts do deterministic fetch/lookup only.

## When to use

- "Enrich these leads." / "Fill in the missing data on these inbound leads."
- When qualification flags leads `insufficient_data`, or triage finds missing fields.

## How to run

### Step 1 — assess gaps (you, the agent)

Inventory what's missing per lead (company profile, role/seniority, LinkedIn URL, email).

### Step 2 — company + person research (keyless)

```bash
python3 ${SKILL_DIR}/scripts/web_research.py \
  --leads ${WORKSPACE}/leads.csv --fetch-pages \
  --output ${WORKSPACE}/research.json
```

Returns per-lead search hits + extracted company-page text + LinkedIn candidate URLs. You
read these and synthesize the company profile, role/seniority, and LinkedIn URL. When
`APOLLO_API_KEY` / `DROPCONTACT_API_KEY` are set, prefer those structured sources (via
`apollo-lead-finder` / a dropcontact call) and use this to fill gaps. Verify any found email
with an email-verify skill.

### Step 3 — stakeholder discovery (buying committee)

Invoke `company-contact-finder` per company to find the rest of the committee; dedup against
the original lead by LinkedIn URL/email.

### Step 4 — relationship check (CRM)

```bash
python3 ${SKILL_DIR}/scripts/crm_lookup.py \
  --leads ${WORKSPACE}/leads.csv \
  --crm-csv ${WORKSPACE}/customers.csv \
  --output ${WORKSPACE}/relationships.json
```

Uses HubSpot search when `HUBSPOT_API_KEY` is set; otherwise matches a CRM/customer CSV
export by email/company. Flags `existing_relationship` / `company_overlap`.

### Step 5 — compile (you, the agent)

Merge research + stakeholders + relationship flags into enriched records. **Flag rather than
invent** — if a field can't be found, mark it unknown, never fabricate.

## Outputs

- `research.json` — `[{company, person, company_hits, person_hits, linkedin_candidates,
  company_page_text}]`.
- `relationships.json` — `[{name, email, company, existing_relationship, company_overlap,
  source}]`.
- Your compiled enriched records (company profile, role/seniority, stakeholders, flags).

## Credentials / env

- **Required:** none — every step has a keyless serp/CSV degrade.
- **Optional:** `APOLLO_API_KEY` (primary company/person enrichment); `DROPCONTACT_API_KEY`
  + an email-verify key (email finding/verification); a CRM key (`HUBSPOT_API_KEY` /
  `SALESFORCE_*`) for the relationship check; `PHANTOMBUSTER_API_KEY` + cookie (LinkedIn
  profile depth).

## Notes & edge cases

- Tool-agnostic: prefer the configured primary/secondary tool per category; fall through to
  web research when a paid tool is absent.
- Stakeholder discovery must not duplicate the original lead — dedup by LinkedIn URL/email.
- Flag rather than invent: unknown fields stay unknown.
- The keyless serp endpoint rate-limits; in production this maps to the Robomotion serp
  Search + Extract Content nodes with a proxy.
