---
name: "lemlist"
description: "Lemlist email outreach — manage campaigns, leads, and email sequences. Supports lead management and campaign operations via `robomotion lemlist`. Do NOT use for Instantly, Mailchimp, Gmail, or other email platforms."
---

# Lemlist

The `robomotion lemlist` CLI connects to Lemlist for email outreach management. It lists and manages campaigns, adds and removes leads from campaigns, and handles outreach sequence operations.

## When to use
- List campaigns and view campaign details
- Add or remove leads from email campaigns
- Manage lead data and outreach sequences

## Prerequisites
- `robomotion` CLI installed
- Package installed: `robomotion install lemlist`
- Lemlist API key configured via Robomotion vault

## IMPORTANT: Session Mode Required for Multi-Step Operations
Each CLI command runs as a **separate process** — connection IDs from `connect` do NOT persist across calls.
You MUST use `--session` on `connect` and pass `--session-id` to all subsequent commands.

## Workflow
1. Install (once): `robomotion install lemlist`
2. Connect with session:
   ```
   robomotion lemlist lemlist_connect --session --output json
   # → {"outClientId":"<client-id>","session_id":"<session-id>"}
   ```
3. Use the returned `client-id` and `session-id` in all subsequent commands:
   ```
   robomotion lemlist lemlist_list_campaigns --client-id "<client-id>" --session-id "<session-id>" --output json
   ```
4. Disconnect when done:
   ```
   robomotion lemlist lemlist_disconnect --client-id "<client-id>" --session-id "<session-id>" --output json
   ```

**Always** append `--output json` to get structured JSON results.

## Commands Reference
- `robomotion lemlist connect --session --output json`
  Connect to Lemlist API using an API key and return a client ID for subsequent operations
- `robomotion lemlist disconnect --client-id --session-id "<session-id>" --output json`
  Disconnect from Lemlist API and release the client connection
- `robomotion lemlist get_team --client-id [--user-url] --session-id "<session-id>" --output json`
  Get information about the current Lemlist team
- `robomotion lemlist list_campaigns --client-id [--0] [--100] --session-id "<session-id>" --output json`
  List all campaigns in Lemlist with pagination support
- `robomotion lemlist unsubscribe_lead_from_campaign --client-id [--campaign-id] [--email-address] --session-id "<session-id>" --output json`
  Unsubscribe a lead from a Lemlist campaign (lead can be re-added later)
- `robomotion lemlist remove_lead_from_campaign --client-id [--campaign-id] [--email-address] --session-id "<session-id>" --output json`
  Remove a lead from a Lemlist campaign permanently

## Environment
- ROBOMOTION_API_TOKEN (if vault credentials are needed)
