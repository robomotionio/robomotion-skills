---
name: "google-calendar"
description: "Google Calendar — create, read, update, delete, and search calendar events. Supports recurring events, attendees, and multi-calendar management via `robomotion googlecalendar`. Do NOT use for Outlook Calendar, Calendly, Cal.com, or other scheduling tools."
---

# Google Calendar

The `robomotion googlecalendar` CLI connects to Google Calendar API for event management. It creates, reads, updates, deletes, and searches events across calendars, with support for attendees, time zones, and calendar listing.

## When to use
- Create, update, or delete calendar events with attendees
- List upcoming events or search by keyword/date range
- Manage multiple calendars — list and select calendars

## Prerequisites
- `robomotion` CLI installed
- Package installed: `robomotion install googlecalendar`
- Google Calendar OAuth2 or Service Account credentials configured via Robomotion vault

## IMPORTANT: Session Mode Required for Multi-Step Operations
Each CLI command runs as a **separate process** — connection IDs from `connect` do NOT persist across calls.
You MUST use `--session` on `connect` and pass `--session-id` to all subsequent commands.

## Workflow
1. Install (once): `robomotion install googlecalendar`
2. Connect with session:
   ```
   robomotion googlecalendar google_calendar_connect --session --output json
   # → {"outClientId":"<client-id>","session_id":"<session-id>"}
   ```
3. Use the returned `client-id` and `session-id` in all subsequent commands:
   ```
   robomotion googlecalendar google_calendar_create_event --client-id "<client-id>" --summary <title> --start <time> --end <time> --session-id "<session-id>" --output json
   ```
4. Disconnect when done:
   ```
   robomotion googlecalendar google_calendar_disconnect --client-id "<client-id>" --session-id "<session-id>" --output json
   ```

**Always** append `--output json` to get structured JSON results.

## Commands Reference
- `robomotion googlecalendar create_calendar_event --primary --summary --description --start-time --end-time --attendees --output json`
  Creates a new event in Google Calendar with attendees and time settings
- `robomotion googlecalendar get_calendar_event --primary --event-id --output json`
  Retrieves a specific event from Google Calendar by ID
- `robomotion googlecalendar get_all_calendar_events --primary --start-time --end-time --query [--250] [--start-time] --output json`
  Retrieves events from Google Calendar with filters for time range and search query
- `robomotion googlecalendar update_calendar_event --primary --event-id --summary --description --start-time --end-time --attendees --location --output json`
  Updates an existing event in Google Calendar with new details
- `robomotion googlecalendar delete_calendar_event --primary --event-id --output json`
  Deletes an event from Google Calendar by ID
- `robomotion googlecalendar list_calendar_events --primary [--25] --output json`
  Lists upcoming events from a Google Calendar
- `robomotion googlecalendar get_calendar_availability --calendar-ids --time-min --time-max --output json`
  Checks free/busy availability for multiple calendars within a time range

## Environment
- ROBOMOTION_API_TOKEN (if vault credentials are needed)
