---
name: cold-email-outreach
description: The final mile of outbound — take leads from any source, design and write email sequences, verify deliverability, then load the campaign into the user's chosen tool (lemlist/instantly) or send one-off (sendgrid/resend) or export a tool-ready CSV, and launch. The launch target for the signal composites and outbound-prospecting-engine once contacts and drafts exist.
metadata:
  version: 1.0.1
  category: outreach
  type: capability
---

# Cold Email Outreach

Launch (or stage) a cold-email campaign. The **agent** normalizes leads and writes the
sequence (via `email-drafting`); the bundled scripts **verify deliverability** and **build/
launch the campaign** via the provider REST API (or export a CSV if no send key).

## When to use

- "Launch a campaign" / "send outreach" / "email these leads" / "set up cold email."
- The launch target for the signal composites (champion-move / funding / hiring /
  leadership / news) and `outbound-prospecting-engine` once contacts + drafts exist.

## How it works (agent + scripts)

1. **(agent)** Intake goal, tool, lead source, sequence config, sending config, exclusions.
2. **(agent)** Ingest + normalize leads to `{email, first_name, last_name, company, title}`;
   apply exclusions; dedup against prior campaigns / a contact cache; cap.
3. **Verify** deliverability (`verify_emails.py`) before send.
4. **(agent)** Write the sequence with `email-drafting` (frameworks, tiers, char limits) and
   lint it. Present samples for human review; iterate.
5. **Launch** (`launch_campaign.py`) — create campaign, import leads, (for lemlist/instantly)
   ready the sequence — or export a tool-ready CSV.
6. **(agent)** Log the run + notify.

## How to run

Verify first (MillionVerifier if `MILLIONVERIFIER_API_KEY` set, else local syntax/dedup only):

```bash
python3 ${SKILL_DIR}/scripts/verify_emails.py \
  --input ${WORKSPACE}/leads.csv --drop-bad --output ${WORKSPACE}/verified.json
```

Then launch (sequence is the drafted touches as JSON: `[{subject, body, send_day}]`):

```bash
# Sequenced cold email (requires the provider key)
python3 ${SKILL_DIR}/scripts/launch_campaign.py \
  --tool lemlist --campaign-name "Q3 RPA push" \
  --leads ${WORKSPACE}/verified.json --sequence ${WORKSPACE}/seq.json

# Dry run — build the payloads without calling the API
python3 ${SKILL_DIR}/scripts/launch_campaign.py --tool instantly --campaign-name X \
  --leads ${WORKSPACE}/verified.json --sequence ${WORKSPACE}/seq.json --dry-run

# No send key — export a tool-ready import CSV (NOTHING is sent)
python3 ${SKILL_DIR}/scripts/launch_campaign.py \
  --tool generic_csv --leads ${WORKSPACE}/verified.json \
  --sequence ${WORKSPACE}/seq.json --output ${WORKSPACE}/import.csv
```

`--tool`: `lemlist` | `instantly` (sequenced) · `sendgrid` | `resend` (one-off, touch 1 only;
needs `*_FROM_EMAIL`) · `generic_csv` (export, no send).

## Outputs

- A launched/staged campaign in the chosen tool (created, leads imported, sequence readied) —
  or a tool-ready import CSV — plus a launch-summary JSON for the log record.

## Credentials / env

- `env.required`: **none.** The default `--tool generic_csv` path exports a tool-ready import
  CSV with no key, so the skill always produces a usable result.
- `env.optional` (all degrade):
  - Send/sequencing — **if a send key is set → launch the sequence/send; else → export a CSV
    to send manually** (`--tool generic_csv`, the keyless default). `LEMLIST_API_KEY` or
    `INSTANTLY_API_KEY` (sequenced) · `SENDGRID_API_KEY` (+ `SENDGRID_FROM_EMAIL`) or
    `RESEND_API_KEY` (+ `RESEND_FROM_EMAIL`) (one-off, touch 1 only). Drafting is the host agent.
  - `MILLIONVERIFIER_API_KEY` — if set → MillionVerifier; else → local syntax/dedup
    verification (higher bounce risk).

## Notes & edge cases

- Always verify before send to protect domain reputation — the script flags reduced
  confidence when no verifier key is present.
- `sendgrid`/`resend` paths send **touch 1 only** (no follow-up scheduling) — use
  lemlist/instantly for true sequencing.
- No sequencing key -> `generic_csv` mode: produces a CSV + setup instructions and explicitly
  flags that nothing is sent automatically.
- Dedup against prior campaigns / a contact cache so leads aren't double-emailed.
