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

## Workflow
1. Install: `robomotion install pushover`
2. Connect: `robomotion pushover pushover_connect` → returns a `client-id`
3. Send: `robomotion pushover pushover_send --client-id <id> --message <text> --title <title>`
4. Disconnect: `robomotion pushover pushover_disconnect --client-id <id>`

## Commands Reference
- `robomotion pushover pushover_connect`
  Connects to Pushover API and returns a client ID for reuse
- `robomotion pushover pushover_disconnect --client-id`
  Closes the Pushover connection and releases resources
- `robomotion pushover pushover_send_message --client-id --user-key --message --title --url --url-title --device [--priority] [--sound] [--60] [--3600] [--0] [--0]`
  Sends a push notification to a user or group via Pushover
- `robomotion pushover pushover_cancel_emergency --client-id --receipt`
  Cancels an active emergency priority notification by receipt ID
- `robomotion pushover pushover_get_limits --client-id`
  Gets the current monthly message limits and remaining quota for your Pushover application

## Environment
- ROBOMOTION_API_TOKEN (if vault credentials are needed)
