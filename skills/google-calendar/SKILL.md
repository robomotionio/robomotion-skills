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

## Workflow
1. Install: `robomotion install googlecalendar`
2. Connect: `robomotion googlecalendar google_calendar_connect` → returns a `client-id`
3. Create event: `robomotion googlecalendar google_calendar_create_event --client-id <id> --summary <title> --start <time> --end <time>`
4. List events: `robomotion googlecalendar google_calendar_list_events --client-id <id>`
5. Disconnect: `robomotion googlecalendar google_calendar_disconnect --client-id <id>`

## Commands Reference
- `robomotion googlecalendar create_calendar_event --primary --summary --description --start-time --end-time --attendees`
  Creates a new event in Google Calendar with attendees and time settings
- `robomotion googlecalendar get_calendar_event --primary --event-id`
  Retrieves a specific event from Google Calendar by ID
- `robomotion googlecalendar get_all_calendar_events --primary --start-time --end-time --query [--250] [--start-time]`
  Retrieves events from Google Calendar with filters for time range and search query
- `robomotion googlecalendar update_calendar_event --primary --event-id --summary --description --start-time --end-time --attendees --location`
  Updates an existing event in Google Calendar with new details
- `robomotion googlecalendar delete_calendar_event --primary --event-id`
  Deletes an event from Google Calendar by ID
- `robomotion googlecalendar list_calendar_events --primary [--25]`
  Lists upcoming events from a Google Calendar
- `robomotion googlecalendar get_calendar_availability --calendar-ids --time-min --time-max`
  Checks free/busy availability for multiple calendars within a time range

## Environment
- ROBOMOTION_API_TOKEN (if vault credentials are needed)
