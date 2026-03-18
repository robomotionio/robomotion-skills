---
name: "millionverifier"
description: "MillionVerifier email verification — verify single emails and run bulk email list verification. Supports quality scoring, verdicts, bulk upload, and report download via `robomotion millionverifier`. Do NOT use for Dropcontact, ZeroBounce, or other verification services."
---

# MillionVerifier

The `robomotion millionverifier` CLI connects to MillionVerifier for email address verification. It verifies single emails with quality/verdict scores, uploads email lists for bulk verification, tracks processing status, downloads verification reports, and manages API credits.

## When to use
- Verify single email addresses with quality and verdict scoring
- Upload email lists for bulk verification
- Track bulk verification progress and download reports
- Check remaining API credits

## Prerequisites
- `robomotion` CLI installed
- Package installed: `robomotion install millionverifier`
- MillionVerifier API key configured via Robomotion vault

## Workflow
1. Install: `robomotion install millionverifier`
2. Connect: `robomotion millionverifier millionverifier_connect` → returns a `client-id`
3. Verify email: `robomotion millionverifier verify_email --client-id <id> --email <email>`
4. Bulk upload: `robomotion millionverifier bulk_upload --client-id <id> --file-path <file>`
5. Disconnect: `robomotion millionverifier millionverifier_disconnect --client-id <id>`

## Commands Reference
- `robomotion millionverifier millionverifier_connect`
  Connects to MillionVerifier API and returns a client ID
- `robomotion millionverifier millionverifier_disconnect --client-id`
  Closes the MillionVerifier connection and releases resources
- `robomotion millionverifier verify_email --client-id --email [--20]`
  Verifies a single email address and returns quality，verdict，and details
- `robomotion millionverifier get_credits --client-id`
  Retrieves the remaining API credit balance
- `robomotion millionverifier bulk_upload --client-id --file-path`
  Uploads a file containing email addresses for bulk verification
- `robomotion millionverifier bulk_get_file_info --client-id --file-id`
  Retrieves processing status and statistics for a bulk verification file
- `robomotion millionverifier bulk_list_files --client-id [--50] [--0] [--status]`
  Lists uploaded bulk verification files with optional filtering
- `robomotion millionverifier bulk_download_report --client-id --file-id --save-to-path [--filter]`
  Downloads bulk verification results to a local file
- `robomotion millionverifier bulk_delete_file --client-id --file-id`
  Deletes a bulk verification file from MillionVerifier
- `robomotion millionverifier bulk_stop_verification --client-id --file-id`
  Stops an in-progress bulk email verification

## Environment
- ROBOMOTION_API_TOKEN (if vault credentials are needed)
