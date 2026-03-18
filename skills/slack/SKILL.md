---
name: "slack"
description: "Slack — send messages, manage channels, list users, upload files, and receive messages via Socket Mode. Supports channel management and file operations via `robomotion slack`. Do NOT use for Discord, Teams, Telegram, or other messaging platforms."
---

# Slack

The `robomotion slack` CLI connects to Slack workspaces for messaging and channel management. It sends messages to channels, lists channels and users, uploads and deletes files, and receives messages via Socket Mode for real-time interaction.

## When to use
- Send messages to Slack channels by name
- List channels, users, and workspace information
- Upload or delete files in channels
- Receive messages via Socket Mode

## Prerequisites
- `robomotion` CLI installed
- Package installed: `robomotion install slack`
- Slack bot token configured via Robomotion vault

## IMPORTANT: Session Mode Required for Multi-Step Operations
Each CLI command runs as a **separate process** — connection IDs from `connect` do NOT persist across calls.
You MUST use `--session` on `connect` and pass `--session-id` to all subsequent commands.

## Workflow
1. Install (once): `robomotion install slack`
2. Connect with session:
   ```
   robomotion slack connect --session --output json
   # → {"outClientId":"<client-id>","session_id":"<session-id>"}
   ```
3. Use the returned `client-id` and `session-id` in all subsequent commands:
   ```
   robomotion slack send_message --client-id "<client-id>" --channel-name <channel> --message <text> --session-id "<session-id>" --output json
   ```
4. Disconnect when done:
   ```
   robomotion slack disconnect --client-id "<client-id>" --session-id "<session-id>" --output json
   ```

**Always** append `--output json` to get structured JSON results.

## Commands Reference
- `robomotion slack connect --session --output json`
  Connect to Slack using a bot token
- `robomotion slack disconnect --client-id --session-id "<session-id>" --output json`
  Disconnect from Slack and cleanup resources
- `robomotion slack list_channels --client-id --session-id "<session-id>" --output json`
  List all channels in the Slack workspace
- `robomotion slack list_users --client-id --session-id "<session-id>" --output json`
  List all users in the Slack workspace
- `robomotion slack file_upload --client-id --channel-id --file-path --session-id "<session-id>" --output json`
  Upload a file to a Slack channel
- `robomotion slack delete_file --client-id --file-id --session-id "<session-id>" --output json`
  Delete a file from Slack
- `robomotion slack send_message --client-id --channel-name --message --session-id "<session-id>" --output json`
  Send a message to a Slack channel
- `robomotion slack receive_message [--channel-id] [--user-id] --output json`
  Receive messages from Slack channels using Socket Mode

## Environment
- ROBOMOTION_API_TOKEN (if vault credentials are needed)
