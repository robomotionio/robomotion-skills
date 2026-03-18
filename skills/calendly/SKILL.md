---
name: "calendly"
description: "Calendly scheduling — list events, manage event types, handle invitees, and configure webhooks. Supports event scheduling, cancellation, and scheduling link creation via `robomotion calendly`. Do NOT use for Cal.com, Google Calendar, Outlook Calendar, or other scheduling tools."
---

# Calendly

The `robomotion calendly` CLI connects to Calendly for scheduling management. It lists scheduled events and invitees, manages event types, creates single-use scheduling links, cancels meetings, and configures webhook subscriptions for real-time event notifications.

## When to use
- List scheduled events with date range and invitee filters
- Cancel scheduled events or view event details
- Create single-use scheduling links for event types
- Manage webhook subscriptions for event notifications

## Prerequisites
- `robomotion` CLI installed
- Package installed: `robomotion install calendly`
- Calendly API token or OAuth2 credentials configured via Robomotion vault

## Workflow
1. Install: `robomotion install calendly`
2. Connect: `robomotion calendly connect` → returns a `client-id`
3. List events: `robomotion calendly list_scheduled_events --client-id <id> --user-url <url>`
4. Cancel event: `robomotion calendly cancel_scheduled_event --client-id <id> --event-url <url> --reason <text>`
5. Disconnect: `robomotion calendly disconnect --client-id <id>`

## Commands Reference
- `robomotion calendly connect`
  Connect to Calendly API using an API token or OAuth2 and return a client ID for subsequent operations
- `robomotion calendly disconnect --client-id`
  Disconnect from Calendly API and release the client connection
- `robomotion calendly get_me --client-id`
  Get information about the currently authenticated Calendly user
- `robomotion calendly list_event_types --client-id --user-url --active --count`
  List all event types (meeting templates) for a user or organization
- `robomotion calendly list_scheduled_events --client-id --user-url --min-start-time --max-start-time --invitee-email --count [--status] [--sort]`
  List scheduled events (booked meetings) for a user or organization
- `robomotion calendly get_scheduled_event --client-id --event-url`
  Get details of a specific scheduled event (meeting)
- `robomotion calendly cancel_scheduled_event --client-id --event-url --reason`
  Cancel a scheduled event (meeting)
- `robomotion calendly list_invitees --client-id --event-url --email --count [--status]`
  List invitees (attendees) for a scheduled event
- `robomotion calendly create_scheduling_link --client-id --event-type-url --max-event-count`
  Create a single-use scheduling link for an event type
- `robomotion calendly list_webhook_subscriptions --client-id --organization-url [--user-url]`
  List all webhook subscriptions for an organization or user
- `robomotion calendly add_webhook_subscription --client-id --webhook-url --organization-url [--events] [--user-url]`
  Add a webhook subscription to receive Calendly event notifications
- `robomotion calendly delete_webhook_subscription --client-id --webhook-id`
  Delete an existing webhook subscription from Calendly

## Environment
- ROBOMOTION_API_TOKEN (if vault credentials are needed)
