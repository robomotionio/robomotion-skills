---
name: funding-signal-outreach
description: Across a list of companies, detect recent funding events, qualify them against the seller's context, find the right people (buyers/champions/users), and draft personalized outreach using fresh capital as the "why now" — the full chain from signal to outreach-ready. Composite that hands off to cold-email-outreach or linkedin-outreach.
metadata:
  version: 1.0.1
  category: outreach
  type: composite
---

# Funding Signal Outreach

A composite: **scripts detect** funding evidence and **find contacts**; the **agent
qualifies, scores, and drafts** (via `email-drafting`); then it hands off to a launch
skill. Detection is keyless; only the send key gates an actual launch.

## When to use

- "Check if any of these companies raised funding" / "reach out to recently funded companies."
- A company list + an upstream monitor surfaces funding to act on.

## How it works (scripts + agent)

1. **Detect** — `detect_signal.py --signal funding` runs keyless searches per company and
   returns evidence snippets (+ optional page text). **(agent)** read the evidence, extract
   amount/stage/date/investors, and **confirm recency** against `lookback`; drop unconfirmed
   rounds rather than over-claim.
2. **(agent) Qualify + rank** each funded company against ICP and the round's "why now"
   relevance.
3. **Find people** — `find_contacts.py` (Apollo by domain + persona titles; `--enrich
   --verify` for emails). Degrades to email-pattern guesses (unverified) without Apollo.
4. **(agent) Draft** sequences with `email-drafting` using the funding event as the hook
   (Signal-Proof-Ask). Don't target the round itself — connect new capital to a concrete
   budget-now angle (hiring spree, new market, scaling pain).
5. **Hand off** to `cold-email-outreach` (lemlist/instantly) or `linkedin-outreach`; request
   launch approval before sending.

## How to run

```bash
# 1 — detect funding evidence (keyless)
python3 ${SKILL_DIR}/scripts/detect_signal.py \
  --companies ${WORKSPACE}/companies.json --signal funding \
  --per-company 4 --extract --output ${WORKSPACE}/funding_evidence.json

# 3 — find + verify contacts at the companies the agent qualified
python3 ${SKILL_DIR}/scripts/find_contacts.py \
  --domains ${WORKSPACE}/qualified.json \
  --titles "VP Sales,Head of RevOps,COO" \
  --per-company 3 --enrich --verify --output ${WORKSPACE}/contacts.json
```

Then draft (email-drafting) and launch (cold-email-outreach / linkedin-outreach).

## Outputs

- `funding_evidence.json` (raw evidence per company), the agent's `qualified-funded-companies`
  (ranked), `contacts.json` (people + emails/status), drafted sequences — handed to the
  launch skill + a review table to the channel.

## Credentials / env

- `env.required`: **none.** Detection is keyless, drafting is the agent, and the launch step
  hands off to `cold-email-outreach` (CSV export with no key).
- `env.optional` (all degrade): `APOLLO_API_KEY` — if set → real people-finding + structured
  funding data; else → keyless serp + pattern-guess. `MILLIONVERIFIER_API_KEY` — if set →
  verify; else → local syntax/dedup (bounce risk). `DROPCONTACT_API_KEY` — email-finding
  fallback. **Send/launch — if a send key (`LEMLIST_API_KEY` / `INSTANTLY_API_KEY` /
  `SENDGRID_API_KEY` / `RESEND_API_KEY`, or `PHANTOMBUSTER_API_KEY` for LinkedIn) is set →
  launch the sequence; else → export a CSV to send manually** (the keyless default).

## Notes & edge cases

- Funding detection from search can be noisy/stale — the agent must extract the date and
  confirm recency; drop unconfirmed rounds.
- Verify emails before send; dedup people across companies. Throttle search.
