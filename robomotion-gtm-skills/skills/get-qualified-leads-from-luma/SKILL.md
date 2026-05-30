---
name: get-qualified-leads-from-luma
description: End-to-end Luma-based lead prospecting — search Luma for events by topic+location, extract attendees/hosts, qualify against an ICP prompt, export to a sheet, and send a Slack alert with the top leads. The Luma-only path with built-in alerting.
metadata:
  version: 1.0.1
  category: lead-generation
  type: composite
---

# Get Qualified Leads from Luma

Chains `luma-event-attendees` (search mode) → timeframe filter/dedup →
`lead-qualification` → sheet export → Slack alert. Both Apify and Slack are **optional**:
with Apify you get full guest profiles (recommended), else a keyless Luma event-page scrape
(hosts + metadata); with Slack creds the alert is delivered, else it is written to a file.

## When to use

- "Find qualified leads from events." / "Who's attending [topic] events that match our ICP?"
- "Prospect event attendees and alert me with the top ones."

## How to run

### Step 1 — clarify params (you, the agent)

Confirm location, topics (3-5 variations), timeframe, ICP/qualification prompt, Slack
target, and top N. **Always confirm a timeframe** — Luma returns events from all time.

### Step 2 — parallel Luma searches

```bash
# run per topic+location variation (Apify Luma actor; requires APIFY_API_TOKEN)
python3 ${SKILL_DIR}/scripts/luma_search.py --search "AI agents San Francisco" \
  --output ${WORKSPACE}/s1.json
python3 ${SKILL_DIR}/scripts/luma_search.py --search "LLM apps SF" \
  --output ${WORKSPACE}/s2.json
# ... 3-5 variations
```

**Keyless degrade (no `APIFY_API_TOKEN`):** `luma_search.py` requires Apify (full guest
profiles). Without it, collect candidate event URLs (agent web search) and direct-scrape
each with the keyless Playwright scraper — hosts + metadata only, not the full guest list:

```bash
npx playwright install chromium   # one-time
node ${SKILL_DIR}/scripts/luma_scrape_pw.mjs \
  --event-url https://lu.ma/abc123 --output ${WORKSPACE}/s1.json
```

### Step 3 — filter timeframe + dedup

```bash
python3 ${SKILL_DIR}/scripts/filter_dedup.py \
  --inputs ${WORKSPACE}/s1.json ${WORKSPACE}/s2.json ${WORKSPACE}/s3.json \
  --since-days 30 --output ${WORKSPACE}/people.json
```

Filters events by `event_date`, merges, dedups by lowercased name (skips null names).

### Step 4 — qualify (sub-skill)

Run `lead-qualification` over `people.json` with the ICP prompt → verdict + score. Write
the qualified set to `qualified.json`.

### Step 5 — export + Slack alert

Export `qualified.json` to a sheet / channel attachment, then:

```bash
python3 ${SKILL_DIR}/scripts/slack_alert.py \
  --leads ${WORKSPACE}/qualified.json --top-n 5 --channel "#leads"
```

Uses `SLACK_WEBHOOK_URL` (webhook) or `SLACK_BOT_TOKEN` + `--channel`. **Keyless degrade (no
Slack creds):** the alert is written to `--out-file` (default `luma_alert.txt`) and printed
to stdout, so the pipeline still produces a deliverable for the agent to relay.

## Outputs

- `people.json` — merged, timeframe-filtered, deduped attendees.
- A qualified lead sheet (attendee, event, company, verdict/score) + channel attachment.
- A Slack alert listing the top N leads.

## Credentials / env

- **Required:** none. The pipeline runs keyless via the Playwright direct-scrape +
  file-based alert.
- **Optional:**
  - `APIFY_API_TOKEN` — if set → Apify Luma actor search mode (full registered-guest
    profiles: LinkedIn/X/bio — recommended). If not → keyless `luma_scrape_pw.mjs`
    direct-scrape (hosts + metadata only).
  - `SLACK_WEBHOOK_URL` or `SLACK_BOT_TOKEN` — if set → Slack delivery. If not → the alert is
    written to a workspace file (`--out-file`) and printed.
  - `APIFY_LUMA_ACTOR` (actor override); `ANTHROPIC_API_KEY` only if the qualification LLM
    isn't platform-provided; Google-sheet creds if not platform-provided.

## Notes & edge cases

- Always confirm a timeframe — filter by `event_date` to avoid stale leads.
- Run keyword variations in parallel for coverage, then dedup once merged.
- Handle null/None attendee names gracefully (skipped).
- Direct Luma scrape (no Apify) yields hosts + metadata only, not full guest profiles —
  prefer the Apify search mode when full registered-guest coverage matters.
- The Playwright degrade needs `npx playwright install chromium` once.
