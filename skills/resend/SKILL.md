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

## IMPORTANT: Session Mode Required for Multi-Step Operations
Each CLI command runs as a **separate process** — connection IDs from `connect` do NOT persist across calls.
You MUST use `--session` on `connect` and pass `--session-id` to all subsequent commands.

## Workflow
1. Install (once): `robomotion install resend`
2. Connect with session:
   ```
   robomotion resend resend_connect --session --output json
   # → {"outClientId":"<client-id>","session_id":"<session-id>"}
   ```
3. Use the returned `client-id` and `session-id` in all subsequent commands:
   ```
   robomotion resend resend_send_email --client-id "<client-id>" --from <from> --to <to> --subject <subj> --html <body> --session-id "<session-id>" --output json
   ```
4. Disconnect when done:
   ```
   robomotion resend resend_disconnect --client-id "<client-id>" --session-id "<session-id>" --output json
   ```

**Always** append `--output json` to get structured JSON results.

## Commands Reference
- `robomotion resend resend_connect --session --output json`
  Connects to Resend API and returns a client ID
- `robomotion resend resend_disconnect --client-id --session-id "<session-id>" --output json`
  Closes the Resend connection and releases resources
- `robomotion resend resend_send_email --client-id --from --to --subject --body [--content-type] [--cc] [--bcc] [--reply-to] [--scheduled-at] [--tags] --session-id "<session-id>" --output json`
  Sends an email through Resend
- `robomotion resend resend_send_batch_email --client-id --emails --session-id "<session-id>" --output json`
  Sends up to 100 emails in a single API call
- `robomotion resend resend_get_email --client-id --email-id --session-id "<session-id>" --output json`
  Retrieves details of a previously sent email by ID
- `robomotion resend resend_create_contact --client-id --email [--first-name] [--last-name] [--unsubscribed] --session-id "<session-id>" --output json`
  Creates a new contact in Resend
- `robomotion resend resend_list_contacts --client-id [--20] [--after-cursor] --session-id "<session-id>" --output json`
  Lists contacts from Resend with pagination support
- `robomotion resend resend_get_contact --client-id --contact-id-or-email --session-id "<session-id>" --output json`
  Retrieves a contact by ID or email address
- `robomotion resend resend_update_contact --client-id --contact-id-or-email [--first-name] [--last-name] [--unsubscribed] --session-id "<session-id>" --output json`
  Updates an existing contact's information
- `robomotion resend resend_delete_contact --client-id --contact-id-or-email --session-id "<session-id>" --output json`
  Deletes a contact by ID or email address
- `robomotion resend resend_list_domains --client-id [--20] --session-id "<session-id>" --output json`
  Lists all verified sending domains in Resend

## Environment
- ROBOMOTION_API_TOKEN (if vault credentials are needed)
