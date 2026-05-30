---
name: meeting-brief
description: A daily meeting-prep system — reads the calendar, filters out internal team members, deep-researches each external attendee (LinkedIn, company, GitHub, recent news), generates an AI relationship brief per person, and delivers it (email per person, optional Slack), building a lightweight personal CRM over time. This is "who is this person", not "how do I sell to them" (for that, see sales-call-prep). Deterministic fetchers; the brief writing is the agent's.
metadata:
  version: 1.0.1
  category: research
  type: composite
---

# Meeting Brief

Deterministic helpers fetch GitHub + web pages; **you, the agent, read the calendar (via
the Google Calendar MCP), research each external attendee, write the brief, and deliver
it.** This is a relationship brief, not a sales strategy.

## When to use

- "Prep me for today's meetings." / automated daily morning run (cron).
- Background context on people you're about to meet.

## How to run

### Step 1 — calendar + attendee filter (you, the agent)

Read today's events via the Google Calendar MCP (time, title, attendees, description,
link). Extract attendees and drop your configured `team_members` / `team_domains` →
external list. Honor a sent-log so a double-firing cron doesn't re-send.

### Step 2 — research each external person (deterministic helpers + agent)

- **Company / news / about pages** — keyless page fetch:

  ```bash
  python3 ${SKILL_DIR}/scripts/fetch_url.py --url https://theircompany.com/about \
    --output ${WORKSPACE}/company.json
  ```

- **GitHub (standard+ depth)** — keyless GitHub API:

  ```bash
  python3 ${SKILL_DIR}/scripts/github_profile.py --user theirhandle \
    --max-repos 6 --output ${WORKSPACE}/gh.json
  ```

- **LinkedIn** — anti-bot; route via `phantombuster` (with a LinkedIn session cookie) or
  `web-automation` + Robomotion Proxy; degrade to search-snippet text if neither is
  available.
- **Recent news + past notes** — your search tool + Memory/workspace notes (deep depth).

Depth gates cost: `quick` skips GitHub + notes; raise only when briefs feel thin. Cache
research per person across days.

### Step 3 — write + deliver the brief (you, the agent)

Per external attendee, write two formats: email bullets (Quick Overview, Background,
Conversation Starters, Notes/Action Items) and a richer Slack narrative. Deliver: one
email per person (subject "Meeting Brief: [Name] - [Title]") via `sendgrid`/`resend` or
the Gmail MCP; optional Slack. Dry-run = render without sending.

### Step 4 — persist (you, the agent)

Save each researched person as a markdown personal-CRM record and append to the sent-log
(dedup). Records land in workspace / Agent Teams channel attachments.

## Outputs

- One brief per external attendee (email bullets + optional Slack narrative).
- A personal-CRM markdown record per person + a sent-log. Workspace + Agent Teams attachment.

## Credentials / env

- **Required (conditional):** calendar access — the Google Calendar MCP (agent-authed) is
  needed to know the meetings. An email-channel key (`SENDGRID_API_KEY` /
  `RESEND_API_KEY`, or the Gmail MCP) is required **when `send_email` is on** (delivery is
  the point). No LLM key — the brief writing is your job as the agent. The fetch scripts
  are keyless.
- **Optional:** if `GITHUB_TOKEN` is set → 5000/hr GitHub rate limit; if not → keyless
  60/hr (default). If `PHANTOMBUSTER_API_KEY` + LinkedIn cookie are set → reliable LinkedIn
  person scrape; if not → keyless serp/fetch on the person (default). `SLACK_BOT_TOKEN` /
  `slack_webhook` (when `send_slack` is on). The fetch scripts run keyless by default.

## Notes & edge cases

- `github_profile.py` works without a token (60 req/hr); set `GITHUB_TOKEN` for volume.
- Cache research per person to avoid re-fetching across days; honor the sent-log to prevent
  duplicate emails.
- Distinguish from `sales-call-prep`: this is "who is this person", not "how do I sell to them".
