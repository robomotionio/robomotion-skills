---
name: signal-detection-pipeline
description: Monitor multiple buying-signal sources in parallel to find companies actively in-market, combine signals for higher-confidence leads, qualify them, and generate outreach context. Orchestrates job-posting, funding, event, Reddit-pain, and LinkedIn-content sources, then dedups and qualifies the combined set.
metadata:
  version: 1.0.0
  category: lead-generation
  type: playbook
---

# Signal Detection Pipeline

A thin orchestration over signal sub-skills. Run only the sources relevant to the client's
ICP — each is independent and parallelizable. Companies appearing across multiple signals
are the highest-confidence leads. (Pairs with `signal-scanner` for TAM-scoped, scheduled,
storage-backed scanning.)

## When to use

- "Find companies that might need [our product]." / "Run signal detection for [problem area]."
- "Find buying signals in [industry/topic]."

## Sub-skills orchestrated (run relevant ones in parallel)

1. **Job postings** — `job-posting-intent` (Apify jobs / keyless serp).
2. **Funding** — `funding-signal-monitor` (serp + HN + optional Apify).
3. **Event attendance** — `luma-event-attendees` (web-automation / Apify Luma).
4. **Reddit pain** — keyless `site:reddit.com` web search (Extract Content); depth via an
   Apify Reddit actor (optional).
5. **LinkedIn content** — the LinkedIn engager skills (`competitor-post-engagers` /
   `pain-language-engagers`) via Phantombuster, or `web-automation`.

Then:

6. **Dedup** — `contact-cache` / a `datatable` dedup on company; tag the signal stack per
   company. Multi-signal = strongest leads.
7. **Qualify + context** — `lead-qualification` + the agent writes the outreach angle per
   qualified company.
8. **Output** — the ranked combined list + Agent Teams channel attachment.

## How to run

Invoke each relevant sub-skill's scripts by path and merge their outputs in-agent, e.g.:

```bash
# 1. job-posting intent
python3 ${SKILL_DIR}/../job-posting-intent/scripts/jobs.py --query "Data Engineer" \
  --output ${WORKSPACE}/jobs.json
python3 ${SKILL_DIR}/../job-posting-intent/scripts/aggregate_intent.py \
  --input ${WORKSPACE}/jobs.json --intent-titles "data engineer" --output ${WORKSPACE}/job_co.json

# 2. funding
python3 ${SKILL_DIR}/../funding-signal-monitor/scripts/funding_search.py \
  --industries "devtools" --output ${WORKSPACE}/funding.json

# 4. reddit pain (keyless)
python3 ${SKILL_DIR}/../funding-signal-monitor/scripts/funding_search.py --help  # (pattern ref)
```

The agent merges per-company signals, dedups, and tags the signal stack. Each sub-skill owns
its proxy/rate-limit/cost handling — degrade per its notes when an optional key is missing.

## Outputs

A ranked, deduplicated lead list with per-company signal stack and outreach context
(company, signals, score, angle) + Agent Teams channel attachment.

## Credentials / env

- **Required:** none at the playbook level — gates live in the sub-skills it runs.
- **Optional (per sub-skill):** `APIFY_API_TOKEN` (jobs/Luma/Reddit depth),
  `PHANTOMBUSTER_API_KEY` + cookie (LinkedIn content), `SUPABASE_URL` +
  `SUPABASE_SERVICE_ROLE_KEY` (dedup/history), `ANTHROPIC_API_KEY` if not platform-provided.

## Notes & edge cases

- Run only the sources relevant to the client's ICP; each is independent and parallelizable.
- Companies across multiple signals are the highest-confidence leads — rank them up.
- Each sub-skill owns its proxy/rate-limit/cost handling; degrade per its notes.
- Pairs with `signal-scanner` for TAM-scoped, scheduled, storage-backed scanning.
