---
name: job-posting-intent
description: Detect buying intent from job postings — when a company posts a role in your problem area they've allocated budget and acknowledged the problem. Finds those companies, aggregates postings into a per-company signal strength, then (agent) qualifies vs. ICP and extracts personalization context + decision-maker suggestions. Outputs leads; does not do outreach.
metadata:
  version: 1.0.0
  category: lead-generation
  type: capability
---

# Job-Posting Intent

The strongest signal source in `signal-detection-pipeline`. Source postings for intent
titles, aggregate them per company into a transparent signal strength, then qualify and
add outreach context.

## When to use

- "Find companies hiring for [role] — that's a budget signal for us."
- "Detect intent from job postings in [problem area]."

## How to run

### Step 1 — source postings (per intent title)

```bash
python3 ${SKILL_DIR}/scripts/jobs.py \
  --query "Data Engineer" --location "United States" \
  --num-results 25 --output ${WORKSPACE}/jobs_de.json
# repeat per intent title, or pass several and merge in-agent
```

With `APIFY_API_TOKEN` this uses the LinkedIn/Indeed actors (estimate cost first, cap
`--num-results`); without it, the keyless `site:` degrade.

### Step 2 — aggregate into per-company signals

```bash
python3 ${SKILL_DIR}/scripts/aggregate_intent.py \
  --input ${WORKSPACE}/jobs_de.json \
  --intent-titles "data engineer,ml engineer" \
  --output ${WORKSPACE}/companies.json
```

Signal strength = posting count × intent-title diversity × recency boost, sorted desc.
This is a transparent rule you can override.

### Step 3 — qualify & contextualize (you, the agent)

For each company in `companies.json`: set `icp_verdict` vs. ICP; extract `personalization`
from the posting text; suggest a `decision_maker` (invoke `company-contact-finder` with
`APOLLO_API_KEY`); and write an `outreach_angle`. Then export the qualified set.

## Outputs

`companies.json` — `[{company, posting_count, matched_intent_titles, signal_strength,
postings[], icp_verdict, decision_maker, outreach_angle, personalization}]`. Outputs leads
only — no outreach.

## Credentials / env

- **Required:** none — `jobs.py` sources postings keylessly.
- **Optional:** `APIFY_API_TOKEN` (LinkedIn/Indeed job actors — richer, structured jobs;
  estimate cost first); `APOLLO_API_KEY` (decision-maker suggestions via
  `company-contact-finder`); `ANTHROPIC_API_KEY` only if LLM qualification isn't
  platform-provided.

## Notes & edge cases

- Always estimate Apify cost before running the actor; cap jobs-per-title.
- Signal strength scales with count + recency + title diversity per company.
- Dedup companies posting the same role across boards (jobs.py dedups postings).
- Outputs leads only — feed qualified companies to outreach skills downstream.
