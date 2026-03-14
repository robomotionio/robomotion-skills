---
name: "slack"
description: "Use when the user wants to call the Robomotion Slack package to send messages or manage channels via the `robomotion slack` CLI. Do NOT use for Discord, Teams, or other messaging platforms."
---

# Slack Skill

## When to use
- Send messages to Slack channels or users
- Read messages from Slack channels
- List Slack channels or users
- Upload files to Slack

## Prerequisites
- `robomotion` CLI installed
- Package installed: `robomotion install slack`
- Credentials configured via Robomotion vault or environment variables

## Workflow
1. Install the package: `robomotion install slack`
2. Run commands: `robomotion slack <command> [flags]`

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
