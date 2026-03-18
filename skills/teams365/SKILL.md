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

## Workflow
1. Install: `robomotion install teams365`
2. Connect: `robomotion teams365 teams_connect` → returns a `client-id`
3. Send message: `robomotion teams365 teams_send_message --client-id <id> --team-id <team> --channel-id <channel> --message <text>`
4. List teams: `robomotion teams365 teams_list_teams --client-id <id>`
5. Disconnect: `robomotion teams365 teams_disconnect --client-id <id>`

## Commands Reference
- `robomotion teams365 teams_connect`
  Establishes a connection to Microsoft Teams and returns a client ID for use in other nodes
- `robomotion teams365 teams_disconnect --client-id`
  Closes a Microsoft Teams connection and releases resources
- `robomotion teams365 list_teams --client-id`
  Lists all Microsoft Teams the authenticated user or app has access to
- `robomotion teams365 get_team --client-id --team-id`
  Gets details of a specific Microsoft Team by ID
- `robomotion teams365 list_channels --client-id --team-id`
  Lists all channels in a Microsoft Team
- `robomotion teams365 get_channel --client-id --team-id --channel-id`
  Gets details of a specific channel in a Microsoft Team
- `robomotion teams365 create_channel --client-id --team-id --channel-name --description [--membership-type]`
  Creates a new channel in a Microsoft Team
- `robomotion teams365 update_channel --client-id --team-id --channel-id --new-name --new-description`
  Updates a channel's display name or description
- `robomotion teams365 delete_channel --client-id --team-id --channel-id`
  Deletes a channel from a Microsoft Team (cannot delete the General channel)
- `robomotion teams365 send_channel_message --client-id --team-id --channel-id --message-content [--content-type]`
  Sends a message to a Microsoft Teams channel
- `robomotion teams365 list_channel_messages --client-id --team-id --channel-id [--50]`
  Lists messages in a Microsoft Teams channel
- `robomotion teams365 reply_to_message --client-id --team-id --channel-id --message-id --reply-content [--content-type]`
  Replies to a message in a Microsoft Teams channel
- `robomotion teams365 list_team_members --client-id --team-id`
  Lists all members of a Microsoft Team
- `robomotion teams365 add_team_member --client-id --team-id --user-id-or-email [--role]`
  Adds a member to a Microsoft Team
- `robomotion teams365 remove_team_member --client-id --team-id --membership-id`
  Removes a member from a Microsoft Team
- `robomotion teams365 list_chats --client-id`
  Lists all chats for the authenticated user (requires delegated permissions)
- `robomotion teams365 send_chat_message --client-id --chat-id --message-content [--content-type]`
  Sends a message to a Microsoft Teams chat (requires delegated permissions)

## Environment
- ROBOMOTION_API_TOKEN (if vault credentials are needed)
