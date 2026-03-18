---
name: "gmail"
description: "Gmail — send, read, search, label, archive, draft, and manage emails and threads. Supports attachments, labels, drafts, and thread operations via `robomotion gmail`. Do NOT use for Outlook, generic SMTP, or non-email messaging."
---

# Gmail

The `robomotion gmail` CLI connects to Gmail via the Google API for full email management. It sends, reads, replies to, and searches emails; manages labels and drafts; handles archiving, trash, and read/unread status; downloads attachments; and operates on email threads.

## When to use
- Send emails with To/CC/BCC recipients, or reply to existing messages
- Search and list emails with query filters and label filtering
- Manage labels — create, list, add/remove from messages
- Create, list, send, or delete email drafts
- Download attachments and manage email threads

## Prerequisites
- `robomotion` CLI installed
- Package installed: `robomotion install gmail`
- Gmail OAuth2 or Service Account credentials configured via Robomotion vault

## IMPORTANT: Session Mode Required for Multi-Step Operations
Each CLI command runs as a **separate process** — connection IDs from `connect` do NOT persist across calls.
You MUST use `--session` on `connect` and pass `--session-id` to all subsequent commands.

## Workflow
1. Install (once): `robomotion install gmail`
2. Connect with session:
   ```
   robomotion gmail gmail_connect --session --output json
   # → {"outClientId":"<client-id>","session_id":"<session-id>"}
   ```
3. Use the returned `client-id` and `session-id` in all subsequent commands:
   ```
   robomotion gmail gmail_send_email --client-id "<client-id>" --to <email> --subject <subj> --body <body> --session-id "<session-id>" --output json
   ```
4. Disconnect when done:
   ```
   robomotion gmail gmail_disconnect --client-id "<client-id>" --session-id "<session-id>" --output json
   ```

**Always** append `--output json` to get structured JSON results.

## Commands Reference
- `robomotion gmail gmail_connect --session --output json`
  Connects to Gmail API using OAuth2 or Service Account credentials
- `robomotion gmail gmail_disconnect --client-id --session-id "<session-id>" --output json`
  Closes the Gmail connection and releases resources
- `robomotion gmail gmail_send_email --client-id --to --subject --body --cc --bcc --session-id "<session-id>" --output json`
  Sends an email message to specified recipients
- `robomotion gmail gmail_get_email --client-id --message-id --session-id "<session-id>" --output json`
  Retrieves a specific email message by ID
- `robomotion gmail gmail_list_emails --client-id --search-query [--50] [--label-filter] --session-id "<session-id>" --output json`
  Lists email messages in the mailbox with optional search query
- `robomotion gmail gmail_reply_email --client-id --message-id --reply-body --session-id "<session-id>" --output json`
  Sends a reply to an existing email message
- `robomotion gmail gmail_delete_email --client-id --message-id --session-id "<session-id>" --output json`
  Permanently deletes an email message. This action cannot be undone. Use Trash Email instead if you want to recover the message later.
- `robomotion gmail gmail_trash_email --client-id --message-id --session-id "<session-id>" --output json`
  Moves an email message to the trash folder. Can be recovered with Untrash Email.
- `robomotion gmail gmail_untrash_email --client-id --message-id --session-id "<session-id>" --output json`
  Removes an email message from the trash folder and restores it
- `robomotion gmail gmail_mark_read --client-id --message-id --session-id "<session-id>" --output json`
  Marks an email message as read by removing the UNREAD label
- `robomotion gmail gmail_mark_unread --client-id --message-id --session-id "<session-id>" --output json`
  Marks an email message as unread by adding the UNREAD label
- `robomotion gmail gmail_add_label --client-id --message-id --label-id --session-id "<session-id>" --output json`
  Adds a label to an email message
- `robomotion gmail gmail_remove_label --client-id --message-id --label-id --session-id "<session-id>" --output json`
  Removes a label from an email message
- `robomotion gmail gmail_archive_email --client-id --message-id --session-id "<session-id>" --output json`
  Archives an email message by removing the INBOX label
- `robomotion gmail gmail_create_label --client-id --label-name [--message-list-visibility] [--label-list-visibility] --session-id "<session-id>" --output json`
  Creates a new label in Gmail
- `robomotion gmail gmail_list_labels --client-id --session-id "<session-id>" --output json`
  Lists all labels in the Gmail account
- `robomotion gmail gmail_get_label --client-id --label-id --session-id "<session-id>" --output json`
  Gets details of a specific label
- `robomotion gmail gmail_delete_label --client-id --label-id --session-id "<session-id>" --output json`
  Permanently deletes a label. System labels cannot be deleted.
- `robomotion gmail gmail_create_draft --client-id --to --subject --body --cc --bcc --session-id "<session-id>" --output json`
  Creates a new email draft
- `robomotion gmail gmail_send_draft --client-id --draft-id --session-id "<session-id>" --output json`
  Sends an existing draft email
- `robomotion gmail gmail_list_drafts --client-id [--50] --session-id "<session-id>" --output json`
  Lists email drafts in the mailbox
- `robomotion gmail gmail_delete_draft --client-id --draft-id --session-id "<session-id>" --output json`
  Permanently deletes a draft email
- `robomotion gmail gmail_get_thread --client-id --thread-id --session-id "<session-id>" --output json`
  Retrieves all messages in an email thread (conversation)
- `robomotion gmail gmail_list_threads --client-id --search-query [--50] --session-id "<session-id>" --output json`
  Lists email threads (conversations) in the mailbox
- `robomotion gmail gmail_download_attachment --client-id --message-id --attachment-id --save-path --session-id "<session-id>" --output json`
  Downloads an email attachment and saves it to a file

## Environment
- ROBOMOTION_API_TOKEN (if vault credentials are needed)
