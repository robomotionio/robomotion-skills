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

## Workflow
1. Install: `robomotion install slack`
2. Connect: `robomotion slack connect` → returns a `client-id`
3. Send: `robomotion slack send_message --client-id <id> --channel-name <channel> --message <text>`
4. List channels: `robomotion slack list_channels --client-id <id>`
5. Disconnect: `robomotion slack disconnect --client-id <id>`

## Commands Reference
- `robomotion slack connect`
  Connect to Slack using a bot token
- `robomotion slack disconnect --client-id`
  Disconnect from Slack and cleanup resources
- `robomotion slack list_channels --client-id`
  List all channels in the Slack workspace
- `robomotion slack list_users --client-id`
  List all users in the Slack workspace
- `robomotion slack file_upload --client-id --channel-id --file-path`
  Upload a file to a Slack channel
- `robomotion slack delete_file --client-id --file-id`
  Delete a file from Slack
- `robomotion slack send_message --client-id --channel-name --message`
  Send a message to a Slack channel
- `robomotion slack receive_message [--channel-id] [--user-id]`
  Receive messages from Slack channels using Socket Mode

## Environment
- ROBOMOTION_API_TOKEN (if vault credentials are needed)
