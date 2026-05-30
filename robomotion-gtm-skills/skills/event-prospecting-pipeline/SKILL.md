---
name: event-prospecting-pipeline
description: End-to-end event-driven prospecting — find attendees/speakers at conferences and events, research and qualify them against ICP, find decision-maker contacts, deduplicate against the contact cache, and hand off a clean qualified list for outreach. Orchestrates the event, qualification, contact-finding, and cache sub-skills.
metadata:
  version: 1.0.0
  category: lead-generation
  type: playbook
---

# Event Prospecting Pipeline

A thin orchestration over existing sub-skills. The pipeline owns no scrapers itself — it
routes to each sub-skill and lets the agent synthesize the final qualified list. (For
Luma-only with Sheets + Slack alerting, use `get-qualified-leads-from-luma`.)

## When to use

- "Find leads from [event/conference]." / "Who's speaking at [conference]? Get contacts."
- "Find AI events in SF and get decision-maker contacts."
- Full pipeline including outreach prep.

## Sub-skills orchestrated

1. **Source people** — `luma-event-attendees` (Luma event/topic → attendees) **or**
   `conference-speaker-scraper` (conference site → speakers).
2. **Research & enrich** — keyless web research (run `inbound-lead-enrichment`'s
   `web_research.py`, or the serp Search/Extract nodes) for funding stage, size, product,
   role, recent news. *Skip this step if the user only wants a raw attendee list.*
3. **Qualify** — `lead-qualification` (score each lead against the ICP).
4. **Find decision-makers** — `company-contact-finder` (Apollo + keyless fallback) for
   qualified companies; verify emails with an email-verify skill if available.
5. **Dedup** — `contact-cache` (`check` op) against known/contacted people by LinkedIn
   URL/email. **Mandatory before outreach.**
6. **Export** — the deduped qualified leads to a sheet/CSV + Agent Teams channel attachment.

## How to run

Invoke each sub-skill's scripts by path, threading the output of one into the next, e.g.:

```bash
# 1. source (conference example)
python3 ${SKILL_DIR}/../conference-speaker-scraper/scripts/scrape_speakers.py \
  --url https://conf.example.com/speakers --output ${WORKSPACE}/people.json

# 3. qualify (after enrich)
python3 ${SKILL_DIR}/../lead-qualification/scripts/qual_prompt.py scaffold \
  --leads ${WORKSPACE}/people.csv --output ${WORKSPACE}/scorecard.json
# ... agent fills verdicts ...

# 4. contacts for qualified companies
python3 ${SKILL_DIR}/../company-contact-finder/scripts/apollo_people.py \
  --company "Acme Corp" --titles "VP Eng,CTO" --output ${WORKSPACE}/contacts.json

# 5. dedup (mandatory)
python3 ${SKILL_DIR}/../contact-cache/scripts/contact_cache.py \
  --store ${WORKSPACE}/contacts.csv check --linkedin-urls "<urls>"
```

Each sub-skill owns its own proxy/rate-limit/anti-block and degrade behavior — follow its
SKILL.md when an optional key is missing.

## Outputs

A qualified, deduplicated lead list (Name, Title, Company, LinkedIn URL, Email, Signal,
Score) exported to a sheet/CSV + channel attachment, ready for outreach.

## Credentials / env

- **Required:** none at the playbook level — gates live in the sub-skills it invokes.
- **Optional (inherited per sub-skill):** `APIFY_API_TOKEN` (Luma search mode / conference
  JS fallback), `APOLLO_API_KEY` (contact-finding), `SUPABASE_URL` +
  `SUPABASE_SERVICE_ROLE_KEY` (cache — required by `contact-cache` for durable cross-run
  dedup), email-verify keys, `ANTHROPIC_API_KEY` if not platform-provided.

## Notes & edge cases

- Skip step 2 if the user only wants a raw attendee list.
- Each sub-skill owns its proxy/rate-limit/anti-block handling.
- Dedup (step 5) is mandatory before outreach to prevent re-contacting known leads.
- Degrade gracefully per each sub-skill's notes when an optional key is missing, and flag
  reduced depth.
