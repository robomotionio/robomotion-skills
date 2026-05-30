---
name: newsletter-signal-scanner
description: Turn newsletter subscriptions into an ongoing intelligence feed — monitor a dedicated IMAP inbox, extract signal-relevant content by keyword campaign (competitor mentions, ICP pain language, market shifts, brand mentions), and deliver a weekly themed digest with recommended actions. Use to stop manually reading industry newsletters.
metadata:
  version: 1.0.1
  category: monitoring
  type: composite
---

# Newsletter Signal Scanner

Scans a monitoring mailbox, extracts per-campaign signal snippets, and produces a weekly
digest. It differs from `newsletter-monitor` by organizing matches into a themed digest
(grouped per campaign, with topic-volume) rather than a flat match list. The rich synthesis
— top trending topic, recommended actions — is the **host agent's** job over the structured
snippets; a templated `--digest` is the LLM-free fallback.

## When to use

- "Monitor industry newsletters for competitor mentions."
- "Alert me when newsletters mention [topic] or [company]."
- "What are newsletters writing about this week in our space?"

Sibling `sponsored-newsletter-finder` discovers which newsletters to subscribe to first.

## How to run

1. **Fetch inbox** (IMAP — requires `IMAP_HOST`/`IMAP_USER`/`IMAP_PASSWORD`), optionally
   scoped to known newsletter senders:

```bash
python3 ${SKILL_DIR}/scripts/imap_fetch.py --days 7 --limit 150 \
  --from-domains "substack.com,beehiiv.com" --output ${WORKSPACE}/messages.json
```

2. **Scan signals.** Provide a keyword-campaigns JSON object, e.g.:

```json
{ "competitors": ["uipath","automation anywhere"],
  "pain_language": ["manual process","too many tools"],
  "market_shifts": ["ai agents","consolidation"],
  "brand_mentions": ["robomotion"] }
```

```bash
# structured snippets (let the agent synthesize the digest)
python3 ${SKILL_DIR}/scripts/signal_scan.py --input ${WORKSPACE}/messages.json \
  --campaigns ${WORKSPACE}/campaigns.json --output ${WORKSPACE}/signals.json

# or a templated, LLM-free markdown digest
python3 ${SKILL_DIR}/scripts/signal_scan.py --input ${WORKSPACE}/messages.json \
  --campaigns ${WORKSPACE}/campaigns.json --digest \
  --output ${WORKSPACE}/newsletter-signals-$(date +%F).md
```

3. **Synthesize digest (agent).** Read `signals.json` + `topic_volume`, identify the top
   trending topic and week-over-week shifts (using history), write recommended actions, and
   render to `markdown` / Slack / email per the requested format.

## Outputs

- `signals.json` — `{topic_volume, signals[], scanned}`; each signal carries
  `{campaign, keyword, newsletter, subject, date, message_id, context}`.
- Or a templated weekly markdown digest (summary + per-campaign sections + topic volume).

## Recurring mode (week-over-week)

```bash
python3 ${SKILL_DIR}/scripts/dedup_history.py --input ${WORKSPACE}/signals.json \
  --history ${WORKSPACE}/nss_seen.csv --key message_id > ${WORKSPACE}/new.json
```

Market-shift "topic gaining coverage" needs persisted per-topic counts across runs
(`SUPABASE_*` or the workspace CSV); first run reports current-week mentions only.

## Credentials / env

- **Required (inherent — no fallback):** `IMAP_HOST`, `IMAP_USER`, `IMAP_PASSWORD`.
  Inbox access is the task; there is **no fallback (inbox access required)**. (`AGENTMAIL_API_KEY`
  below is an optional alternative inbox source, not a keyless substitute.)
- **Optional (if-set/else):**
  - `AGENTMAIL_API_KEY` — **if set → hosted AgentMail inbox** read instead of raw IMAP;
    **else → IMAP** (the default inbox path). Both are inbox sources — one is required.
  - `IMAP_PORT` / `IMAP_FOLDER` — IMAP connection tuning (defaults 993 / INBOX).
  - `ANTHROPIC_API_KEY` / `OPENAI_API_KEY` — **if set → optional script-side LLM synthesis**;
    **else → the host agent synthesizes**, or the templated `--digest` runs LLM-free (the default).
  - `SLACK_BOT_TOKEN` / `SENDGRID_API_KEY` / `RESEND_API_KEY` — **if set → digest delivery to
    Slack/email**; **else → workspace markdown file** (the default).
  - `SUPABASE_URL` / `SUPABASE_KEY` — **if set → Supabase cross-run dedup + topic counts**;
    **else → workspace CSV** via `dedup_history.py` (the default).

## Notes & edge cases

- Requires newsletters to actually arrive in the monitored inbox — first-run setup
  subscribes the address and waits 1-2 weeks before a meaningful digest.
- Scope the scan to known `from_domains` to avoid matching non-newsletter mail.
- Keyword matching is plain substring — tune campaign lists to control false positives.
- Dedup on `message_id` so re-runs don't re-surface the same signals.
