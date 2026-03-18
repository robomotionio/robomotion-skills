---
name: "teams365"
description: "Microsoft Teams 365 — send messages, manage teams/channels/members, and handle channel conversations via Microsoft Graph API. Supports message threading, channel creation, and member management via `robomotion teams365`. Do NOT use for Slack, Discord, Telegram, or other messaging."
---

# Microsoft Teams 365

The `robomotion teams365` CLI connects to Microsoft Teams via the Graph API for team collaboration. It sends and lists messages in channels, manages teams and channels, handles members and membership, and supports threaded conversations.

## When to use
- Send messages to Teams channels with threading support
- List and manage teams, channels, and members
- Create channels and manage team settings
- Read channel messages and conversations

## Prerequisites
- `robomotion` CLI installed
- Package installed: `robomotion install teams365`
- Microsoft 365 OAuth2 credentials configured via Robomotion vault

## IMPORTANT: Session Mode Required for Multi-Step Operations
Each CLI command runs as a **separate process** — connection IDs from `connect` do NOT persist across calls.
You MUST use `--session` on `connect` and pass `--session-id` to all subsequent commands.

## Workflow
1. Install (once): `robomotion install teams365`
2. Connect with session:
   ```
   robomotion teams365 teams_connect --session --output json
   # → {"outClientId":"<client-id>","session_id":"<session-id>"}
   ```
3. Use the returned `client-id` and `session-id` in all subsequent commands:
   ```
   robomotion teams365 teams_send_message --client-id "<client-id>" --team-id <team> --channel-id <channel> --message <text> --session-id "<session-id>" --output json
   ```
4. Disconnect when done:
   ```
   robomotion teams365 teams_disconnect --client-id "<client-id>" --session-id "<session-id>" --output json
   ```

**Always** append `--output json` to get structured JSON results.

## Commands Reference
- `robomotion teams365 teams_connect --session --output json`
  Establishes a connection to Microsoft Teams and returns a client ID for use in other nodes
- `robomotion teams365 teams_disconnect --client-id --session-id "<session-id>" --output json`
  Closes a Microsoft Teams connection and releases resources
- `robomotion teams365 list_teams --client-id --session-id "<session-id>" --output json`
  Lists all Microsoft Teams the authenticated user or app has access to
- `robomotion teams365 get_team --client-id --team-id --session-id "<session-id>" --output json`
  Gets details of a specific Microsoft Team by ID
- `robomotion teams365 list_channels --client-id --team-id --session-id "<session-id>" --output json`
  Lists all channels in a Microsoft Team
- `robomotion teams365 get_channel --client-id --team-id --channel-id --session-id "<session-id>" --output json`
  Gets details of a specific channel in a Microsoft Team
- `robomotion teams365 create_channel --client-id --team-id --channel-name --description [--membership-type] --session-id "<session-id>" --output json`
  Creates a new channel in a Microsoft Team
- `robomotion teams365 update_channel --client-id --team-id --channel-id --new-name --new-description --session-id "<session-id>" --output json`
  Updates a channel's display name or description
- `robomotion teams365 delete_channel --client-id --team-id --channel-id --session-id "<session-id>" --output json`
  Deletes a channel from a Microsoft Team (cannot delete the General channel)
- `robomotion teams365 send_channel_message --client-id --team-id --channel-id --message-content [--content-type] --session-id "<session-id>" --output json`
  Sends a message to a Microsoft Teams channel
- `robomotion teams365 list_channel_messages --client-id --team-id --channel-id [--50] --session-id "<session-id>" --output json`
  Lists messages in a Microsoft Teams channel
- `robomotion teams365 reply_to_message --client-id --team-id --channel-id --message-id --reply-content [--content-type] --session-id "<session-id>" --output json`
  Replies to a message in a Microsoft Teams channel
- `robomotion teams365 list_team_members --client-id --team-id --session-id "<session-id>" --output json`
  Lists all members of a Microsoft Team
- `robomotion teams365 add_team_member --client-id --team-id --user-id-or-email [--role] --session-id "<session-id>" --output json`
  Adds a member to a Microsoft Team
- `robomotion teams365 remove_team_member --client-id --team-id --membership-id --session-id "<session-id>" --output json`
  Removes a member from a Microsoft Team
- `robomotion teams365 list_chats --client-id --session-id "<session-id>" --output json`
  Lists all chats for the authenticated user (requires delegated permissions)
- `robomotion teams365 send_chat_message --client-id --chat-id --message-content [--content-type] --session-id "<session-id>" --output json`
  Sends a message to a Microsoft Teams chat (requires delegated permissions)

## Environment
- ROBOMOTION_API_TOKEN (if vault credentials are needed)
