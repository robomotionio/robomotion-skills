---
name: linkedin-outreach
description: End-to-end LinkedIn outreach campaign builder — take qualified leads, write personalized message sequences (connection request + follow-ups + optional InMail), enforce char limits, export for the user's LinkedIn tool, and log the run. The LinkedIn counterpart to cold-email-outreach; a launch target for the signal composites when the user chooses LinkedIn.
metadata:
  version: 1.0.1
  category: outreach
  type: capability
---

# LinkedIn Outreach

Build a LinkedIn outreach campaign. The **agent** writes the personalized sequences (via
`linkedin-message-writer`); the bundled scripts **lint char limits**, **export the tool
CSV**, and optionally **launch a Phantombuster send**. Default path is the CSV export
(LinkedIn tools are browser-based importers).

## When to use

- "LinkedIn outreach" / "set up a LinkedIn campaign" / "connect with these leads on LinkedIn."
- The LinkedIn counterpart to `cold-email-outreach`; a launch target for the signal composites.

## How it works (agent + scripts)

1. **(agent)** Intake goal, angle, name, tool, lead selection, sequence config, account tier.
2. **(agent)** Load leads (store query / CSV / upstream output).
3. **(agent)** Write per-lead sequences (CR + follow-ups + optional InMail), enforcing limits
   (CR 200/300, message 8000, InMail subj 200 / body 1900). **Lint** them; rewrite over-limit.
4. **(agent)** Present samples for review; iterate.
5. **Export** the tool CSV — or **launch** via Phantombuster (automated send).
6. **(agent)** Log the campaign + contacts; dedup against the outreach log.

## How to run

Lint the drafted sequences (`message` carries the CR / DM text; per-type limits enforced):

```bash
python3 ${SKILL_DIR}/scripts/linkedin_lint.py --input ${WORKSPACE}/sequences.json
```

Export a tool-ready CSV (default path — nothing is sent):

```bash
python3 ${SKILL_DIR}/scripts/export_csv.py --input ${WORKSPACE}/sequences.json \
  --tool dripify --output ${WORKSPACE}/linkedin_campaign.csv
```

Optional automated send via Phantombuster (needs key + LinkedIn session cookie; throttle):

```bash
python3 ${SKILL_DIR}/scripts/phantombuster_send.py \
  --agent-id 1234567890 --leads ${WORKSPACE}/sequences.json \
  --daily-cap 50 --dry-run            # drop --dry-run to actually launch
```

`export_csv --tool`: `generic` | `dripify` | `expandi` | `botdog` | `phantombuster`.

## Outputs

- A tool-ready CSV (`linkedin_url, first_name, last_name, company, title, connection_request,
  followup_1..N, inmail_subject, inmail_body`) — or a Phantombuster launch result — plus an
  outreach-log record for the store.

## Credentials / env

- `env.required`: **none.** The default CSV-export path needs no key (the agent writes the
  copy; lint + export are stdlib).
- `env.optional` (all degrade): **Send — if `PHANTOMBUSTER_API_KEY` (+ `LINKEDIN_SESSION_COOKIE`)
  is set → automated LinkedIn send; else → export a CSV to import manually** (the keyless
  default). `APIFY_API_TOKEN` — if set → cookieless Apify research via
  `linkedin-profile-post-scraper`; else → that skill's keyless Playwright `li_at`-cookie
  degrade. Store creds (`SUPABASE_*`) — if set → read/log; else → CSV/paste.

## Notes & edge cases

- LinkedIn tools are browser-based CSV importers — the default path produces a CSV, not an
  API send. The Phantombuster path needs a key + session cookie and must be throttled
  (`--daily-cap`) to dodge LinkedIn limits/bans.
- Strictly enforce char limits; rewrite to fit, never truncate. Always show samples before
  exporting a large batch.
- Dedup against the outreach log so the same lead isn't re-sequenced.
