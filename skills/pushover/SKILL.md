---
name: "pushover"
description: "Pushover — send push notifications to Android, iOS, and desktop devices with priority levels, sounds, and attachments. Supports emergency alerts and delivery verification via `robomotion pushover`. Do NOT use for Slack, email, Twilio SMS, or other notification channels."
---

# Pushover

The `robomotion pushover` CLI sends push notifications via Pushover to mobile and desktop devices. It supports priority levels (including emergency with acknowledgment), custom sounds, URL attachments, and delivery receipt verification.

## When to use
- Send push notifications with custom priority, title, and message
- Send emergency notifications that require acknowledgment
- Attach URLs and custom sounds to notifications
- Verify delivery receipts for critical alerts

## Prerequisites
- `robomotion` CLI installed
- Package installed: `robomotion install pushover`
- Pushover API token and user key configured via Robomotion vault

## IMPORTANT: Session Mode Required for Multi-Step Operations
Each CLI command runs as a **separate process** — connection IDs from `connect` do NOT persist across calls.
You MUST use `--session` on `connect` and pass `--session-id` to all subsequent commands.

## Workflow
1. Install (once): `robomotion install pushover`
2. Connect with session:
   ```
   robomotion pushover pushover_connect --session --output json
   # → {"outClientId":"<client-id>","session_id":"<session-id>"}
   ```
3. Use the returned `client-id` and `session-id` in all subsequent commands:
   ```
   robomotion pushover pushover_send --client-id "<client-id>" --message <text> --title <title> --session-id "<session-id>" --output json
   ```
4. Disconnect when done:
   ```
   robomotion pushover pushover_disconnect --client-id "<client-id>" --session-id "<session-id>" --output json
   ```

**Always** append `--output json` to get structured JSON results.

## Commands Reference
- `robomotion pushover pushover_connect --session --output json`
  Connects to Pushover API and returns a client ID for reuse
- `robomotion pushover pushover_disconnect --client-id --session-id "<session-id>" --output json`
  Closes the Pushover connection and releases resources
- `robomotion pushover pushover_send_message --client-id --user-key --message --title --url --url-title --device [--priority] [--sound] [--60] [--3600] [--0] [--0] --session-id "<session-id>" --output json`
  Sends a push notification to a user or group via Pushover
- `robomotion pushover pushover_cancel_emergency --client-id --receipt --session-id "<session-id>" --output json`
  Cancels an active emergency priority notification by receipt ID
- `robomotion pushover pushover_get_limits --client-id --session-id "<session-id>" --output json`
  Gets the current monthly message limits and remaining quota for your Pushover application

## Environment
- ROBOMOTION_API_TOKEN (if vault credentials are needed)
