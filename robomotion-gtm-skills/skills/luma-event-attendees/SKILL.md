---
name: luma-event-attendees
description: Find speakers, hosts, and guest profiles at Luma events for outreach prospecting. Two modes — a free direct page scrape (event metadata + hosts) and a paid Apify search mode returning full guest profiles with LinkedIn/X/bio. The attendee-sourcing front end of the event-prospecting and Luma lead pipelines.
metadata:
  version: 1.0.0
  category: lead-generation
  type: capability
---

# Luma Event Attendees

Source people from Luma events. Direct-scrape mode is keyless (hosts + metadata); search
mode (Apify) discovers events by topic+location and returns full guest profiles.

## When to use

- "Get attendees/hosts/speakers from [Luma event]." / "Find [topic] events in [city]."
- Feeds `event-prospecting-pipeline` and `get-qualified-leads-from-luma`.

## How to run

### Direct-scrape mode (free) — a single event URL

```bash
cd ${SKILL_DIR}/scripts && npm install && npx playwright install chromium
node ${SKILL_DIR}/scripts/luma_scrape_pw.mjs \
  --event-url https://lu.ma/abc123 \
  --output ${WORKSPACE}/people.json
```

Renders the Luma event page, reads its embedded `__NEXT_DATA__`, and extracts event
metadata + hosts (+ any publicly embedded guests). **Hosts/metadata only** — not the full
registered-guest list.

### Search mode (paid) — topic + location → full guest profiles

```bash
python3 ${SKILL_DIR}/scripts/luma_search.py \
  --search "AI agents San Francisco" \
  --max-events 20 \
  --output json   # json | csv
```

Runs the Apify Luma actor (requires `APIFY_API_TOKEN`) to discover events and return full
guest profiles with LinkedIn/X/bio. Override the actor with `APIFY_LUMA_ACTOR`.

## Outputs

- Direct-scrape: `{event_name, event_url, event_date, mode, people: [...]}`.
- Search: `{mode, search, people: [...]}` (or CSV).
- Each person: `{name, bio, linkedin_url, x, instagram, website, company,
  event_date, role}`. People are deduped across events; null names are skipped.

## Credentials / env

- **Required:** none — direct-scrape mode runs keylessly via the headless browser.
- **Optional:** `APIFY_API_TOKEN` — required for **search mode** and full guest-profile
  extraction; `APIFY_LUMA_ACTOR` to override the actor. Without the token, only
  direct-scrape (hosts + metadata) is available.

## Notes & edge cases

- Direct scrape yields hosts/metadata only; full registered-guest profiles need the Apify
  search-mode actor.
- Luma is JS-heavy — direct scraping uses the browser/proxy.
- Luma search returns events from all time periods — downstream pipelines must filter by
  `event_date` for recency.
- Handle null names (skipped) and dedup people across multiple event results (both done).
