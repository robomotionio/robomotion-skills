---
name: "outlook365"
description: "Microsoft Outlook 365 — send, read, search, and manage emails, calendar events, and mail folders via Microsoft Graph API. Supports attachments, replies, and event scheduling via `robomotion outlook365`. Do NOT use for Gmail, generic SMTP, or non-Microsoft email."
---

# Microsoft Outlook 365

The `robomotion outlook365` CLI connects to Microsoft Outlook 365 via the Graph API for email and calendar management. It sends, reads, replies to, and searches emails; manages mail folders; handles attachments; and creates, lists, and manages calendar events.

## When to use
- Send emails with recipients, CC/BCC, and attachments
- Read, search, reply to, or delete emails
- Manage mail folders and email organization
- Create, list, and manage calendar events

## Prerequisites
- `robomotion` CLI installed
- Package installed: `robomotion install outlook365`
- Microsoft 365 OAuth2 credentials configured via Robomotion vault

## IMPORTANT: Session Mode Required for Multi-Step Operations
Each CLI command runs as a **separate process** — connection IDs from `connect` do NOT persist across calls.
You MUST use `--session` on `connect` and pass `--session-id` to all subsequent commands.

## Workflow
1. Install (once): `robomotion install outlook365`
2. Connect with session:
   ```
   robomotion outlook365 outlook_connect --session --output json
   # → {"outClientId":"<client-id>","session_id":"<session-id>"}
   ```
3. Use the returned `client-id` and `session-id` in all subsequent commands:
   ```
   robomotion outlook365 outlook_send_email --client-id "<client-id>" --to <email> --subject <subj> --body <body> --session-id "<session-id>" --output json
   ```
4. Disconnect when done:
   ```
   robomotion outlook365 outlook_disconnect --client-id "<client-id>" --session-id "<session-id>" --output json
   ```

**Always** append `--output json` to get structured JSON results.

## Commands Reference
- `robomotion outlook365 list_messages --folder --output json`
  Lists email messages from Outlook 365 mailbox or folder
- `robomotion outlook365 get_message --message-id --output json`
  Retrieves a specific email message by ID from Outlook 365
- `robomotion outlook365 search_messages --folder --search-query --from --output json`
  Searches for email messages in Outlook 365 using subject٫ sender٫ or keywords
- `robomotion outlook365 send_mail --to --cc --bcc --subject --body --attachments [--body-type] --output json`
  Sends a new email message via Outlook 365
- `robomotion outlook365 reply_message --message-id --reply --attachments --output json`
  Replies to an email message in Outlook 365
- `robomotion outlook365 forward_message --message-id --to --comment --output json`
  Forwards an email message in Outlook 365
- `robomotion outlook365 delete_message --message-id --output json`
  Deletes an email message from Outlook 365
- `robomotion outlook365 move_message --message-id --destination-folder --output json`
  Moves an email message to a different folder in Outlook 365
- `robomotion outlook365 get_attachments --message-id --output json`
  Lists all attachments for an email message without downloading them
- `robomotion outlook365 save_attachments --message-id --download-folder --output json`
  Downloads and saves all attachments from an email message to a folder
- `robomotion outlook365 list_folders --parent-folder --output json`
  Lists mail folders in Outlook 365 mailbox
- `robomotion outlook365 get_folder --folder --output json`
  Retrieves a specific mail folder from Outlook 365 by ID or well-known name
- `robomotion outlook365 list_events --calendar-id --output json`
  Lists calendar events from Outlook 365
- `robomotion outlook365 get_event --event-id --output json`
  Retrieves a specific calendar event from Outlook 365 by ID
- `robomotion outlook365 create_event --subject --body --start-time --end-time --location --attendees [--body-type] [--importance] --output json`
  Creates a new calendar event in Outlook 365
- `robomotion outlook365 update_event --event-id --subject --body --start-time --end-time --location --output json`
  Updates an existing calendar event in Outlook 365
- `robomotion outlook365 delete_event --event-id --output json`
  Deletes a calendar event from Outlook 365

## Environment
- ROBOMOTION_API_TOKEN (if vault credentials are needed)
