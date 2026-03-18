---
name: "calcom"
description: "Cal.com scheduling platform — manage bookings, event types, availability slots, and schedules. Supports creating, rescheduling, and canceling bookings via `robomotion calcom`. Do NOT use for Calendly, Google Calendar, Outlook Calendar, or other scheduling tools."
---

# Cal.com

The `robomotion calcom` CLI connects to Cal.com for scheduling management. It handles creating and managing bookings, event types with custom durations and buffers, availability schedules with timezone support, and available slot queries.

## When to use
- Create, reschedule, or cancel bookings on Cal.com
- List and manage event types with durations and buffer times
- Query available time slots for specific event types
- Manage availability schedules and overrides

## Prerequisites
- `robomotion` CLI installed
- Package installed: `robomotion install calcom`
- Cal.com API key configured via Robomotion vault

## IMPORTANT: Session Mode Required for Multi-Step Operations
Each CLI command runs as a **separate process** — connection IDs from `connect` do NOT persist across calls.
You MUST use `--session` on `connect` and pass `--session-id` to all subsequent commands.

## Workflow
1. Install (once): `robomotion install calcom`
2. Connect with session:
   ```
   robomotion calcom calcom_connect --session --output json
   # → {"outClientId":"<client-id>","session_id":"<session-id>"}
   ```
3. Use the returned `client-id` and `session-id` in all subsequent commands:
   ```
   robomotion calcom calcom_list_bookings --client-id "<client-id>" --session-id "<session-id>" --output json
   ```
4. Disconnect when done:
   ```
   robomotion calcom calcom_disconnect --client-id "<client-id>" --session-id "<session-id>" --output json
   ```

**Always** append `--output json` to get structured JSON results.

## Commands Reference
- `robomotion calcom calcom_connect --session --output json`
  Connects to Cal.com API and returns a client ID
- `robomotion calcom calcom_disconnect --client-id --session-id "<session-id>" --output json`
  Closes the Cal.com connection and releases resources
- `robomotion calcom calcom_create_booking --client-id --event-type-id --start-time --attendee-name --attendee-email --attendee-time-zone --guests --metadata [--duration-(minutes)] [--attendee-language] [--60] --session-id "<session-id>" --output json`
  Creates a new booking on Cal.com
- `robomotion calcom calcom_get_booking --client-id --booking-uid --session-id "<session-id>" --output json`
  Retrieves a booking by its UID from Cal.com
- `robomotion calcom calcom_list_bookings --client-id [--status-filter] [--25] [--skip] --session-id "<session-id>" --output json`
  Lists bookings from Cal.com with optional filters
- `robomotion calcom calcom_cancel_booking --client-id --booking-uid --cancellation-reason --session-id "<session-id>" --output json`
  Cancels an existing booking on Cal.com
- `robomotion calcom calcom_reschedule_booking --client-id --booking-uid --new-start-time --rescheduling-reason --session-id "<session-id>" --output json`
  Reschedules an existing booking to a new time on Cal.com
- `robomotion calcom calcom_list_event_types --client-id --session-id "<session-id>" --output json`
  Lists all event types from Cal.com
- `robomotion calcom calcom_create_event_type --client-id --title --slug --duration-(minutes) --description [--slot-interval-(minutes)] [--before-buffer-(minutes)] [--after-buffer-(minutes)] --session-id "<session-id>" --output json`
  Creates a new event type on Cal.com
- `robomotion calcom calcom_update_event_type --client-id --event-type-id --title --slug --duration-(minutes) --description [--slot-interval-(minutes)] --session-id "<session-id>" --output json`
  Updates an existing event type on Cal.com
- `robomotion calcom calcom_get_available_slots --client-id --start-time --end-time --event-type-id --event-type-slug --username [--time-zone] [--duration-(minutes)] --session-id "<session-id>" --output json`
  Gets available time slots from Cal.com for booking
- `robomotion calcom calcom_list_schedules --client-id --session-id "<session-id>" --output json`
  Lists all availability schedules from Cal.com
- `robomotion calcom calcom_create_schedule --client-id --name --time-zone --availability --overrides --session-id "<session-id>" --output json`
  Creates a new availability schedule on Cal.com

## Environment
- ROBOMOTION_API_TOKEN (if vault credentials are needed)
