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

## IMPORTANT: Session Mode Required for Multi-Step Operations
Each CLI command runs as a **separate process** — connection IDs from `connect` do NOT persist across calls.
You MUST use `--session` on `connect` and pass `--session-id` to all subsequent commands.

## Workflow
1. Install (once): `robomotion install calendly`
2. Connect with session:
   ```
   robomotion calendly connect --session --output json
   # → {"outClientId":"<client-id>","session_id":"<session-id>"}
   ```
3. Use the returned `client-id` and `session-id` in all subsequent commands:
   ```
   robomotion calendly list_scheduled_events --client-id "<client-id>" --user-url <url> --session-id "<session-id>" --output json
   ```
4. Disconnect when done:
   ```
   robomotion calendly disconnect --client-id "<client-id>" --session-id "<session-id>" --output json
   ```

**Always** append `--output json` to get structured JSON results.

## Commands Reference
- `robomotion calendly connect --session --output json`
  Connect to Calendly API using an API token or OAuth2 and return a client ID for subsequent operations
- `robomotion calendly disconnect --client-id --session-id "<session-id>" --output json`
  Disconnect from Calendly API and release the client connection
- `robomotion calendly get_me --client-id --session-id "<session-id>" --output json`
  Get information about the currently authenticated Calendly user
- `robomotion calendly list_event_types --client-id --user-url --active --count --session-id "<session-id>" --output json`
  List all event types (meeting templates) for a user or organization
- `robomotion calendly list_scheduled_events --client-id --user-url --min-start-time --max-start-time --invitee-email --count [--status] [--sort] --session-id "<session-id>" --output json`
  List scheduled events (booked meetings) for a user or organization
- `robomotion calendly get_scheduled_event --client-id --event-url --session-id "<session-id>" --output json`
  Get details of a specific scheduled event (meeting)
- `robomotion calendly cancel_scheduled_event --client-id --event-url --reason --session-id "<session-id>" --output json`
  Cancel a scheduled event (meeting)
- `robomotion calendly list_invitees --client-id --event-url --email --count [--status] --session-id "<session-id>" --output json`
  List invitees (attendees) for a scheduled event
- `robomotion calendly create_scheduling_link --client-id --event-type-url --max-event-count --session-id "<session-id>" --output json`
  Create a single-use scheduling link for an event type
- `robomotion calendly list_webhook_subscriptions --client-id --organization-url [--user-url] --session-id "<session-id>" --output json`
  List all webhook subscriptions for an organization or user
- `robomotion calendly add_webhook_subscription --client-id --webhook-url --organization-url [--events] [--user-url] --session-id "<session-id>" --output json`
  Add a webhook subscription to receive Calendly event notifications
- `robomotion calendly delete_webhook_subscription --client-id --webhook-id --session-id "<session-id>" --output json`
  Delete an existing webhook subscription from Calendly

## Environment
- ROBOMOTION_API_TOKEN (if vault credentials are needed)
