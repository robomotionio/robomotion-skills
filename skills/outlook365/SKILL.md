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

## Workflow
1. Install: `robomotion install outlook365`
2. Connect: `robomotion outlook365 outlook_connect` → returns a `client-id`
3. Send email: `robomotion outlook365 outlook_send_email --client-id <id> --to <email> --subject <subj> --body <body>`
4. List emails: `robomotion outlook365 outlook_list_emails --client-id <id>`
5. Disconnect: `robomotion outlook365 outlook_disconnect --client-id <id>`

## Commands Reference
- `robomotion outlook365 list_messages --folder`
  Lists email messages from Outlook 365 mailbox or folder
- `robomotion outlook365 get_message --message-id`
  Retrieves a specific email message by ID from Outlook 365
- `robomotion outlook365 search_messages --folder --search-query --from`
  Searches for email messages in Outlook 365 using subject٫ sender٫ or keywords
- `robomotion outlook365 send_mail --to --cc --bcc --subject --body --attachments [--body-type]`
  Sends a new email message via Outlook 365
- `robomotion outlook365 reply_message --message-id --reply --attachments`
  Replies to an email message in Outlook 365
- `robomotion outlook365 forward_message --message-id --to --comment`
  Forwards an email message in Outlook 365
- `robomotion outlook365 delete_message --message-id`
  Deletes an email message from Outlook 365
- `robomotion outlook365 move_message --message-id --destination-folder`
  Moves an email message to a different folder in Outlook 365
- `robomotion outlook365 get_attachments --message-id`
  Lists all attachments for an email message without downloading them
- `robomotion outlook365 save_attachments --message-id --download-folder`
  Downloads and saves all attachments from an email message to a folder
- `robomotion outlook365 list_folders --parent-folder`
  Lists mail folders in Outlook 365 mailbox
- `robomotion outlook365 get_folder --folder`
  Retrieves a specific mail folder from Outlook 365 by ID or well-known name
- `robomotion outlook365 list_events --calendar-id`
  Lists calendar events from Outlook 365
- `robomotion outlook365 get_event --event-id`
  Retrieves a specific calendar event from Outlook 365 by ID
- `robomotion outlook365 create_event --subject --body --start-time --end-time --location --attendees [--body-type] [--importance]`
  Creates a new calendar event in Outlook 365
- `robomotion outlook365 update_event --event-id --subject --body --start-time --end-time --location`
  Updates an existing calendar event in Outlook 365
- `robomotion outlook365 delete_event --event-id`
  Deletes a calendar event from Outlook 365

## Environment
- ROBOMOTION_API_TOKEN (if vault credentials are needed)
