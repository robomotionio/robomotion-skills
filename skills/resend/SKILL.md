---
name: "resend"
description: "Resend email API — send transactional emails, manage contacts, audiences, and domains. Supports HTML/text emails, batch sending, and domain verification via `robomotion resend`. Do NOT use for Gmail, Outlook, SendGrid, or other email services."
---

# Resend

The `robomotion resend` CLI connects to Resend for transactional email delivery. It sends emails (HTML and text), manages contacts and audiences, handles domain verification, and supports batch email operations.

## When to use
- Send transactional emails with HTML or plain text content
- Manage contacts and audience lists
- Verify and manage sending domains
- Send batch emails to multiple recipients

## Prerequisites
- `robomotion` CLI installed
- Package installed: `robomotion install resend`
- Resend API key configured via Robomotion vault

## Workflow
1. Install: `robomotion install resend`
2. Connect: `robomotion resend resend_connect` → returns a `client-id`
3. Send email: `robomotion resend resend_send_email --client-id <id> --from <from> --to <to> --subject <subj> --html <body>`
4. Disconnect: `robomotion resend resend_disconnect --client-id <id>`

## Commands Reference
- `robomotion resend resend_connect`
  Connects to Resend API and returns a client ID
- `robomotion resend resend_disconnect --client-id`
  Closes the Resend connection and releases resources
- `robomotion resend resend_send_email --client-id --from --to --subject --body [--content-type] [--cc] [--bcc] [--reply-to] [--scheduled-at] [--tags]`
  Sends an email through Resend
- `robomotion resend resend_send_batch_email --client-id --emails`
  Sends up to 100 emails in a single API call
- `robomotion resend resend_get_email --client-id --email-id`
  Retrieves details of a previously sent email by ID
- `robomotion resend resend_create_contact --client-id --email [--first-name] [--last-name] [--unsubscribed]`
  Creates a new contact in Resend
- `robomotion resend resend_list_contacts --client-id [--20] [--after-cursor]`
  Lists contacts from Resend with pagination support
- `robomotion resend resend_get_contact --client-id --contact-id-or-email`
  Retrieves a contact by ID or email address
- `robomotion resend resend_update_contact --client-id --contact-id-or-email [--first-name] [--last-name] [--unsubscribed]`
  Updates an existing contact's information
- `robomotion resend resend_delete_contact --client-id --contact-id-or-email`
  Deletes a contact by ID or email address
- `robomotion resend resend_list_domains --client-id [--20]`
  Lists all verified sending domains in Resend

## Environment
- ROBOMOTION_API_TOKEN (if vault credentials are needed)
