---
name: inbound-lead-triage
description: Pull all inbound leads from a period (demo requests, trial signups, content downloads, webinar regs, chatbot convos), classify by source urgency, qualify against ICP, enrich with context, and produce a prioritized action queue with a recommended response per lead. Turns a messy form-fill inbox into a who-to-call-first list.
metadata:
  version: 1.0.0
  category: lead-generation
  type: composite
---

# Inbound Lead Triage

A scheduled periodic inbound review. Urgency ranking is deterministic; qualification,
enrichment, and the drafted response are chained from sub-skills and the agent. Urgency
first, then ICP — a hot demo request from a weak-fit account still ranks for a fast reply.

## When to use

- "Triage my inbound leads." / "Review new leads." / "Who should I follow up with first?"
- A scheduled periodic inbound review.

## How to run

### Step 1 — collect + urgency-rank

```bash
python3 ${SKILL_DIR}/scripts/triage.py \
  --inputs demo.csv:demo_request trial.csv:trial_signup content.csv:content_download \
  --output ${WORKSPACE}/queue.json
```

Each input is a `CSV:source_type` pair. Merges sources, assigns source-urgency + recency
boost, dedups by email keeping the highest-urgency entry, and sorts the queue. Override
weights with `--urgency-config <json>`. Collect the CSVs from your configured sources
(HubSpot/Salesforce form exports, form-tool API, chatbot logs) first.

### Step 2 — qualify against ICP

Run `inbound-lead-qualification` over the queue (CRM overlap + ICP scoring). Leads with
missing fields route through `inbound-lead-enrichment` first.

### Step 3 — enrich with context

Run `inbound-lead-enrichment` to add company/person context for the recommended response.

### Step 4 — route + draft (you, the agent)

Fill `icp_score`, `context`, `recommended_response`, and `route` per lead. Drafted responses
are **recommendations for human review, not auto-sent**. Route per `routing_rules` (CRM
patch / Slack handoff). Export the queue + channel attachment.

## Outputs

A prioritized action queue: `[{name, email, company, title, source, created_at,
urgency_score, icp_score, context, recommended_response, route}]`, urgency-ranked.

## Credentials / env

- **Required:** none — runs on CSV exports + serp + the agent if no integrations are wired.
- **Optional:** CRM/form-tool keys (`HUBSPOT_API_KEY` / `SALESFORCE_*` / a form API) for
  source collection; `APOLLO_API_KEY` (enrichment); `SLACK_WEBHOOK_URL` / `SLACK_BOT_TOKEN`
  (handoff alerts); `ANTHROPIC_API_KEY` only if the response-drafting LLM isn't platform-provided.

## Notes & edge cases

- Tool-agnostic, configured once per client — sources/access methods are read from config.
- Urgency first, then ICP: a hot demo request from a weak-fit account still ranks for a fast
  (templated) reply.
- Leads with missing fields route through `inbound-lead-enrichment` before qualification.
- Drafted responses are recommendations for human review, not auto-sent.
