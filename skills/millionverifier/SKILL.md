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

## IMPORTANT: Session Mode Required for Multi-Step Operations
Each CLI command runs as a **separate process** — connection IDs from `connect` do NOT persist across calls.
You MUST use `--session` on `connect` and pass `--session-id` to all subsequent commands.

## Workflow
1. Install (once): `robomotion install millionverifier`
2. Connect with session:
   ```
   robomotion millionverifier millionverifier_connect --session --output json
   # → {"outClientId":"<client-id>","session_id":"<session-id>"}
   ```
3. Use the returned `client-id` and `session-id` in all subsequent commands:
   ```
   robomotion millionverifier verify_email --client-id "<client-id>" --email <email> --session-id "<session-id>" --output json
   ```
4. Disconnect when done:
   ```
   robomotion millionverifier millionverifier_disconnect --client-id "<client-id>" --session-id "<session-id>" --output json
   ```

**Always** append `--output json` to get structured JSON results.

## Commands Reference
- `robomotion millionverifier millionverifier_connect --session --output json`
  Connects to MillionVerifier API and returns a client ID
- `robomotion millionverifier millionverifier_disconnect --client-id --session-id "<session-id>" --output json`
  Closes the MillionVerifier connection and releases resources
- `robomotion millionverifier verify_email --client-id --email [--20] --session-id "<session-id>" --output json`
  Verifies a single email address and returns quality，verdict，and details
- `robomotion millionverifier get_credits --client-id --session-id "<session-id>" --output json`
  Retrieves the remaining API credit balance
- `robomotion millionverifier bulk_upload --client-id --file-path --session-id "<session-id>" --output json`
  Uploads a file containing email addresses for bulk verification
- `robomotion millionverifier bulk_get_file_info --client-id --file-id --session-id "<session-id>" --output json`
  Retrieves processing status and statistics for a bulk verification file
- `robomotion millionverifier bulk_list_files --client-id [--50] [--0] [--status] --session-id "<session-id>" --output json`
  Lists uploaded bulk verification files with optional filtering
- `robomotion millionverifier bulk_download_report --client-id --file-id --save-to-path [--filter] --session-id "<session-id>" --output json`
  Downloads bulk verification results to a local file
- `robomotion millionverifier bulk_delete_file --client-id --file-id --session-id "<session-id>" --output json`
  Deletes a bulk verification file from MillionVerifier
- `robomotion millionverifier bulk_stop_verification --client-id --file-id --session-id "<session-id>" --output json`
  Stops an in-progress bulk email verification

## Environment
- ROBOMOTION_API_TOKEN (if vault credentials are needed)
