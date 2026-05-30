---
name: hiring-signal-outreach
description: Across a list of companies, detect job postings for roles the product augments or replaces, find the right people (hiring manager, budget holder, potential champions), and draft outreach using the open role as the hook — they've already acknowledged and budgeted the problem. Composite that hands off to cold-email-outreach or linkedin-outreach.
metadata:
  version: 1.0.1
  category: outreach
  type: composite
---

# Hiring Signal Outreach

A composite: **scripts detect** job postings and **find contacts**; the **agent matches
the JD to roles, qualifies, and drafts** (via `email-drafting`); then hands off to a launch
skill. Detection is keyless; only the send key gates a launch.

## When to use

- "Check if any of these companies are hiring for roles we replace" / "hiring signal outreach."
- A company list + an upstream monitor surfaces relevant job postings.

## How it works (scripts + agent)

1. **Detect** — `detect_signal.py --signal hiring --extra "<role>"` searches job boards /
   careers pages per company and returns evidence (+ optional JD page text). Run once per
   target role from `roles_replaced` (strongest) and `roles_augmented` (good).
2. **(agent) Match + qualify** — read the JD evidence, confirm the posting is live and within
   `lookback`, match it to `roles_replaced` / `roles_augmented` (careful — false "replace"
   matches produce tone-deaf outreach), and keep the JD snippet as the hook.
3. **Find people** — `find_contacts.py` for the **hiring manager / budget holder / champions**
   (NOT the candidate being hired). `--enrich --verify` for emails; degrades to pattern-guess.
4. **(agent) Draft** sequences with `email-drafting` using the role as "why now"
   (e.g. "before you fill that {role} role…").
5. **Hand off** to `cold-email-outreach` / `linkedin-outreach`; request launch approval.

## How to run

```bash
# 1 — detect postings for a role (keyless); repeat per role
python3 ${SKILL_DIR}/scripts/detect_signal.py \
  --companies ${WORKSPACE}/companies.json --signal hiring --extra "RPA developer" \
  --per-company 4 --extract --output ${WORKSPACE}/hiring_evidence.json

# 3 — find the hiring manager / budget holder
python3 ${SKILL_DIR}/scripts/find_contacts.py \
  --domains ${WORKSPACE}/qualified.json \
  --titles "VP Engineering,Director of Operations,Head of Automation" \
  --per-company 3 --enrich --verify --output ${WORKSPACE}/contacts.json
```

## Outputs

- `hiring_evidence.json`, the agent's `companies-with-hiring-signals` (matched postings +
  JD snippet), `contacts.json`, drafted sequences — handed to the launch skill + review table.

## Credentials / env

- `env.required`: **none.** Detection is keyless, drafting is the agent, and the launch step
  hands off to `cold-email-outreach` (CSV export with no key).
- `env.optional` (all degrade): `APOLLO_API_KEY` — if set → people-finding; else → keyless serp
  + pattern-guess. `MILLIONVERIFIER_API_KEY` — if set → verify; else → local syntax/dedup
  (bounce risk). `APIFY_API_TOKEN` — if set → hostile job-board scraping at volume; else →
  keyless `site:` search. **Send/launch — if a send key (`LEMLIST_API_KEY` /
  `INSTANTLY_API_KEY` / `SENDGRID_API_KEY` / `RESEND_API_KEY`, or `PHANTOMBUSTER_API_KEY` for
  LinkedIn) is set → launch the sequence; else → export a CSV to send manually** (the keyless
  default).

## Notes & edge cases

- Target the hiring manager / budget holder, not the candidate — the open role is evidence of
  budget, not the recipient.
- Confirm the posting is live and within `lookback`; stale postings kill credibility.
- Verify emails; throttle job-board scraping.
