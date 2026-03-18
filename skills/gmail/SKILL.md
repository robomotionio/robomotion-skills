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

## Workflow
1. Install: `robomotion install gmail`
2. Connect: `robomotion gmail gmail_connect` → returns a `client-id`
3. Send email: `robomotion gmail gmail_send_email --client-id <id> --to <email> --subject <subj> --body <body>`
4. List emails: `robomotion gmail gmail_list_emails --client-id <id> --search-query <query>`
5. Disconnect: `robomotion gmail gmail_disconnect --client-id <id>`

## Commands Reference
- `robomotion gmail gmail_connect`
  Connects to Gmail API using OAuth2 or Service Account credentials
- `robomotion gmail gmail_disconnect --client-id`
  Closes the Gmail connection and releases resources
- `robomotion gmail gmail_send_email --client-id --to --subject --body --cc --bcc`
  Sends an email message to specified recipients
- `robomotion gmail gmail_get_email --client-id --message-id`
  Retrieves a specific email message by ID
- `robomotion gmail gmail_list_emails --client-id --search-query [--50] [--label-filter]`
  Lists email messages in the mailbox with optional search query
- `robomotion gmail gmail_reply_email --client-id --message-id --reply-body`
  Sends a reply to an existing email message
- `robomotion gmail gmail_delete_email --client-id --message-id`
  Permanently deletes an email message. This action cannot be undone. Use Trash Email instead if you want to recover the message later.
- `robomotion gmail gmail_trash_email --client-id --message-id`
  Moves an email message to the trash folder. Can be recovered with Untrash Email.
- `robomotion gmail gmail_untrash_email --client-id --message-id`
  Removes an email message from the trash folder and restores it
- `robomotion gmail gmail_mark_read --client-id --message-id`
  Marks an email message as read by removing the UNREAD label
- `robomotion gmail gmail_mark_unread --client-id --message-id`
  Marks an email message as unread by adding the UNREAD label
- `robomotion gmail gmail_add_label --client-id --message-id --label-id`
  Adds a label to an email message
- `robomotion gmail gmail_remove_label --client-id --message-id --label-id`
  Removes a label from an email message
- `robomotion gmail gmail_archive_email --client-id --message-id`
  Archives an email message by removing the INBOX label
- `robomotion gmail gmail_create_label --client-id --label-name [--message-list-visibility] [--label-list-visibility]`
  Creates a new label in Gmail
- `robomotion gmail gmail_list_labels --client-id`
  Lists all labels in the Gmail account
- `robomotion gmail gmail_get_label --client-id --label-id`
  Gets details of a specific label
- `robomotion gmail gmail_delete_label --client-id --label-id`
  Permanently deletes a label. System labels cannot be deleted.
- `robomotion gmail gmail_create_draft --client-id --to --subject --body --cc --bcc`
  Creates a new email draft
- `robomotion gmail gmail_send_draft --client-id --draft-id`
  Sends an existing draft email
- `robomotion gmail gmail_list_drafts --client-id [--50]`
  Lists email drafts in the mailbox
- `robomotion gmail gmail_delete_draft --client-id --draft-id`
  Permanently deletes a draft email
- `robomotion gmail gmail_get_thread --client-id --thread-id`
  Retrieves all messages in an email thread (conversation)
- `robomotion gmail gmail_list_threads --client-id --search-query [--50]`
  Lists email threads (conversations) in the mailbox
- `robomotion gmail gmail_download_attachment --client-id --message-id --attachment-id --save-path`
  Downloads an email attachment and saves it to a file

## Environment
- ROBOMOTION_API_TOKEN (if vault credentials are needed)
