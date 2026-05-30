---
name: customer-win-back-sequencer
description: For churned accounts, research what has changed since they left (new funding, team growth, competitor dissatisfaction, product updates that address their original pain), assess re-engagement potential, and generate a personalized, timing-aware win-back sequence — no generic "we miss you" emails. Composite that hands off to cold-email-outreach or linkedin-outreach.
metadata:
  version: 1.0.1
  category: outreach
  type: composite
---

# Customer Win-Back Sequencer

A composite: **scripts filter** the churn list and **research changes / contact status**;
the **agent scores re-engagement, picks the angle, and drafts** a timing-aware win-back
sequence. Only pursue accounts where something material actually changed.

## When to use

- "Which churned customers should we win back?" / "build a win-back campaign for [customer]."
- "Research our churned accounts for re-engagement" / "run the win-back scan."

## How it works (scripts + agent)

1. **Filter** — `filter_churn.py` keeps accounts within the recency window (default 3-18
   months since churn) and at/above `--min-mrr`. Too recent = too soon; too old = stale.
2. **Research company changes** — `detect_signal.py --signal winback` per account (funding,
   growth/hiring, launches). **(agent)** summarize what changed.
3. **Research contact + competitor changes** — `find_contacts.py` against the domain to check
   if the contact is still there / promoted / replaced and re-find the email (likely stale
   post-churn). For competitor-dissatisfaction, `detect_signal.py --signal general --extra
   "{competitor} alternative OR complaints"`. **(agent)** read the evidence.
4. **(agent) Score + pick the angle** — change-triggered / fixed-pain / fresh-DM. Don't
   re-pitch the value that caused churn; anchor on the *fixed* reason or a new change. If the
   contact left, find the new decision-maker.
5. **(agent) Draft** the win-back sequence with `email-drafting` (change as why-now) +
   timing.
6. **Hand off** to `cold-email-outreach` / `linkedin-outreach`; `slack` approval.

## How to run

```bash
# 1 — filter the churn list
python3 ${SKILL_DIR}/scripts/filter_churn.py \
  --input ${WORKSPACE}/churn.csv --min-months 3 --max-months 18 --min-mrr 500 \
  --output ${WORKSPACE}/pursue.json

# 2 — research what changed per account
python3 ${SKILL_DIR}/scripts/detect_signal.py \
  --companies ${WORKSPACE}/pursue.json --signal winback --extract \
  --output ${WORKSPACE}/changes.json

# 3 — re-verify / re-find the contact (email likely stale)
python3 ${SKILL_DIR}/scripts/find_contacts.py \
  --domains ${WORKSPACE}/pursue.json --titles "their role,VP,Director" \
  --enrich --verify --output ${WORKSPACE}/contacts.json
```

## Outputs

- `pursue.json` (recency/MRR-filtered), `changes.json`, `contacts.json`, the agent's ranked
  re-engagement list (per-account findings + angle + score) and win-back sequences with
  timing — handed to the launch skill + review table.

## Credentials / env

- `env.required`: **none.** Change research is keyless, drafting is the agent, and the launch
  step hands off to `cold-email-outreach` (CSV export with no key).
- `env.optional` (all degrade): `APOLLO_API_KEY` — if set → org/contact enrichment; else →
  serp research + pattern-guess. `MILLIONVERIFIER_API_KEY` — if set → verify (re-verify the
  stale post-churn email); else → local syntax/dedup (bounce risk). **Send/launch — if a send
  key (`LEMLIST_API_KEY` / `INSTANTLY_API_KEY` / `SENDGRID_API_KEY` / `RESEND_API_KEY`, or
  `PHANTOMBUSTER_API_KEY` for LinkedIn) is set → launch the sequence; else → export a CSV to
  send manually** (the keyless default).

## Notes & edge cases

- Timing + relevance are everything — only pursue accounts where something material changed.
- Don't re-pitch the value that caused churn — anchor on the *fixed* reason or a new change.
  If the contact left, find the new decision-maker (fresh eyes, no baggage).
- Re-verify the contact email (likely stale post-churn) before send.
