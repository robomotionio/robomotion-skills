---
name: "discord-bot"
description: "Discord bot — send messages, manage channels, handle roles, and interact with Discord servers. Supports message sending, channel management, and server administration via `robomotion discordbot`. Do NOT use for Slack, Teams, Telegram, or other messaging platforms."
---

# Discord Bot

The `robomotion discordbot` CLI operates a Discord bot to send messages, manage channels and roles, and interact with Discord servers. It supports posting messages, listing channels/members, and performing server administration tasks.

## When to use
- Send messages to Discord channels or users
- List channels, members, and roles in a Discord server
- Manage Discord channels and server settings

## Prerequisites
- `robomotion` CLI installed
- Package installed: `robomotion install discordbot`
- Discord bot token configured via Robomotion vault

## IMPORTANT: Session Mode Required for Multi-Step Operations
Each CLI command runs as a **separate process** — connection IDs from `connect` do NOT persist across calls.
You MUST use `--session` on `connect` and pass `--session-id` to all subsequent commands.

## Workflow
1. Install (once): `robomotion install discordbot`
2. Connect with session:
   ```
   robomotion discordbot connect --session --output json
   # → {"outClientId":"<client-id>","session_id":"<session-id>"}
   ```
3. Use the returned `client-id` and `session-id` in all subsequent commands:
   ```
   robomotion discordbot send_message --client-id "<client-id>" --channel-id <channel> --message <text> --session-id "<session-id>" --output json
   ```
4. Disconnect when done:
   ```
   robomotion discordbot disconnect --client-id "<client-id>" --session-id "<session-id>" --output json
   ```

**Always** append `--output json` to get structured JSON results.

## Commands Reference
- `robomotion discordbot connect --session --output json`
  Connect to Discord using a bot token
- `robomotion discordbot create_channel --client-id --server-id --channel-name [--channel-type] --session-id "<session-id>" --output json`
  Create a new text or voice channel in a Discord server
- `robomotion discordbot create_invite_link --client-id --channel-id --session-id "<session-id>" --output json`
  Create an invite link for a Discord channel
- `robomotion discordbot delete_channel --client-id --channel-id --session-id "<session-id>" --output json`
  Delete a Discord channel
- `robomotion discordbot disconnect --client-id --session-id "<session-id>" --output json`
  Disconnect from Discord and close the bot session
- `robomotion discordbot get_channel_info --client-id --channel-id --session-id "<session-id>" --output json`
  Get information about a Discord channel
- `robomotion discordbot get_channel_messages --client-id --channel-id --message-id [--10] [--direction] --session-id "<session-id>" --output json`
  Get messages from a Discord channel
- `robomotion discordbot get_user_info --client-id --user-id --session-id "<session-id>" --output json`
  Get information about a Discord user
- `robomotion discordbot receive_message [--server-id] [--channel-id] [--sender-id] --output json`
  Receive messages from Discord channels
- `robomotion discordbot send_channel_message --client-id --channel-id --message-text [--reply-server-id] [--reply-message-id] [--files] [--embed] [--buttons] --session-id "<session-id>" --output json`
  Send a message to a Discord channel
- `robomotion discordbot delete_channel_message --client-id --channel-id --message-id --session-id "<session-id>" --output json`
  Delete a message from a Discord channel
- `robomotion discordbot create_command --client-id --application-id [--server-id] --session-id "<session-id>" --output json`
  Create a Discord slash command
- `robomotion discordbot send_direct_message --client-id --user-id --message-text [--reply-message-id] [--files] [--embed] [--buttons] --session-id "<session-id>" --output json`
  Send a direct message to a Discord user
- `robomotion discordbot list_commands --client-id --application-id --server-id --session-id "<session-id>" --output json`
  List Discord application commands
- `robomotion discordbot delete_command --client-id --application-id --command-id --server-id --session-id "<session-id>" --output json`
  Delete a Discord slash command
- `robomotion discordbot edit_channel_message --client-id --channel-id --message-id --message-text --session-id "<session-id>" --output json`
  Edit an existing message in a Discord channel
- `robomotion discordbot interaction_in [--server-id] [--channel-id] [--sender-id] [--command-name] [--interaction-type] --output json`
  Receive Discord interactions (commands٫ components٫ modals)
- `robomotion discordbot interaction_out --interaction-id --output json`
  Send a response to a Discord interaction
- `robomotion discordbot add_role_member --client-id --server-id --user-id --role-id --session-id "<session-id>" --output json`
  Add a role to a Discord server member
- `robomotion discordbot remove_role_member --client-id --server-id --user-id --role-id --session-id "<session-id>" --output json`
  Remove a role from a Discord server member
- `robomotion discordbot update_interaction_respond --client-id --application-id --interaction-token --session-id "<session-id>" --output json`
  Update a Discord interaction response
- `robomotion discordbot create_forum_post --client-id --channel-id --post-title --message-text [--0] [--files] [--embed] [--buttons] --session-id "<session-id>" --output json`
  Create a new post in a Discord forum channel

## Environment
- ROBOMOTION_API_TOKEN (if vault credentials are needed)
