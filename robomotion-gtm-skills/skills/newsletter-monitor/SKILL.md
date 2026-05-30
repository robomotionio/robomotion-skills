---
name: newsletter-monitor
description: Scan a dedicated monitoring inbox (IMAP) for incoming newsletter emails and extract buying signals via configurable keyword campaigns — matched keywords, 200-char context snippets, and mentioned companies. Use to monitor industry newsletters (acquisitions, migrations, staffing, technology adoption) for actionable signals without manual reading.
metadata:
  version: 1.0.1
  category: monitoring
  type: composite
---

# Newsletter Monitor

Reads a monitoring mailbox over IMAP, matches each message against keyword campaigns, and
returns a flat list of matched messages with context and mentioned companies. Two
deterministic scripts; the host agent does any narrative synthesis and downstream routing.

## When to use

- "Scan our newsletter inbox for [acquisitions / migrations / staffing] signals."
- "What did this week's industry newsletters mention about [topic]?"
- Recurring inbox-signal monitoring for a vertical.

Downstream: when a signal names a company, hand `companies_mentioned` to a
`company-contact-finder` to look up contacts.

## How to run

1. **Fetch inbox** (IMAP — requires `IMAP_HOST`/`IMAP_USER`/`IMAP_PASSWORD`):

```bash
python3 ${SKILL_DIR}/scripts/imap_fetch.py --days 7 --limit 100 \
  --output ${WORKSPACE}/messages.json
```

| Flag | Default | Meaning |
|---|---|---|
| `--days` | `0` (no limit) | Only messages from last N days. |
| `--limit` | `100` | Max messages (newest first). |
| `--from-domains` | `""` | Scope to sender domains (comma-separated). |
| `--output` | stdout | JSON path. |

2. **Match campaigns:**

```bash
python3 ${SKILL_DIR}/scripts/campaign_match.py --input ${WORKSPACE}/messages.json \
  --output json > ${WORKSPACE}/signals.json
```

| Flag | Default | Meaning |
|---|---|---|
| `--input` | (required) | JSON from `imap_fetch.py` (or `-` for stdin). |
| `--campaign` | all | Run one built-in: `acquisitions/sage_intacct/staffing/technology`. |
| `--keywords` | `""` | Ad-hoc comma-separated keywords (overrides campaigns). |
| `--campaigns-file` | `""` | JSON `[{name,description,keywords[]}]` custom defs. |
| `--output` | `json` | `json` or grouped-by-campaign `summary`. |

## Outputs

JSON array of matched messages, each:
`{message_id, from, subject, date, matched_campaigns, matched_keywords,
context_snippets (200-char windows), companies_mentioned}`.

## Recurring / monitoring mode

```bash
python3 ${SKILL_DIR}/scripts/dedup_history.py --input ${WORKSPACE}/signals.json \
  --history ${WORKSPACE}/newsletter_seen.csv --key message_id > ${WORKSPACE}/new.json
```

Dedup keys on `message_id` so re-runs don't re-report the same email.

## Credentials / env

- **Required (inherent — no fallback):** `IMAP_HOST`, `IMAP_USER`, `IMAP_PASSWORD`.
  Inbox access is the task; there is **no fallback (inbox access required)**. (`AGENTMAIL_API_KEY`
  below is an optional alternative inbox source, not a keyless substitute.)
- **Optional (if-set/else):**
  - `AGENTMAIL_API_KEY` — **if set → hosted AgentMail inbox** read instead of raw IMAP;
    **else → IMAP** (the default inbox path). Both are inbox sources — one is required.
  - `IMAP_PORT` (default 993), `IMAP_FOLDER` (default INBOX) — IMAP connection tuning.
  - `SUPABASE_URL` / `SUPABASE_KEY` — **if set → Supabase cross-run dedup/history**;
    **else → workspace CSV** via `dedup_history.py` (the default).

## Notes & edge cases

- Keyword matching is plain case-insensitive substring — broad by design; tune campaign
  lists to control noise.
- Company detection is heuristic (capitalized multi-word phrases near matches) — verify
  before handing names downstream.
- Requires newsletters to already arrive in the monitored inbox (subscriptions set up out
  of band); discovery is `sponsored-newsletter-finder`'s job.
