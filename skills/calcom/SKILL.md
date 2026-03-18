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

## Workflow
1. Install: `robomotion install calcom`
2. Connect: `robomotion calcom calcom_connect` → returns a `client-id`
3. List bookings: `robomotion calcom calcom_list_bookings --client-id <id>`
4. Create booking: `robomotion calcom calcom_create_booking --client-id <id> --event-type-id <type> --start-time <time> --attendee-name <name> --attendee-email <email>`
5. Disconnect: `robomotion calcom calcom_disconnect --client-id <id>`

## Commands Reference
- `robomotion calcom calcom_connect`
  Connects to Cal.com API and returns a client ID
- `robomotion calcom calcom_disconnect --client-id`
  Closes the Cal.com connection and releases resources
- `robomotion calcom calcom_create_booking --client-id --event-type-id --start-time --attendee-name --attendee-email --attendee-time-zone --guests --metadata [--duration-(minutes)] [--attendee-language] [--60]`
  Creates a new booking on Cal.com
- `robomotion calcom calcom_get_booking --client-id --booking-uid`
  Retrieves a booking by its UID from Cal.com
- `robomotion calcom calcom_list_bookings --client-id [--status-filter] [--25] [--skip]`
  Lists bookings from Cal.com with optional filters
- `robomotion calcom calcom_cancel_booking --client-id --booking-uid --cancellation-reason`
  Cancels an existing booking on Cal.com
- `robomotion calcom calcom_reschedule_booking --client-id --booking-uid --new-start-time --rescheduling-reason`
  Reschedules an existing booking to a new time on Cal.com
- `robomotion calcom calcom_list_event_types --client-id`
  Lists all event types from Cal.com
- `robomotion calcom calcom_create_event_type --client-id --title --slug --duration-(minutes) --description [--slot-interval-(minutes)] [--before-buffer-(minutes)] [--after-buffer-(minutes)]`
  Creates a new event type on Cal.com
- `robomotion calcom calcom_update_event_type --client-id --event-type-id --title --slug --duration-(minutes) --description [--slot-interval-(minutes)]`
  Updates an existing event type on Cal.com
- `robomotion calcom calcom_get_available_slots --client-id --start-time --end-time --event-type-id --event-type-slug --username [--time-zone] [--duration-(minutes)]`
  Gets available time slots from Cal.com for booking
- `robomotion calcom calcom_list_schedules --client-id`
  Lists all availability schedules from Cal.com
- `robomotion calcom calcom_create_schedule --client-id --name --time-zone --availability --overrides`
  Creates a new availability schedule on Cal.com

## Environment
- ROBOMOTION_API_TOKEN (if vault credentials are needed)
