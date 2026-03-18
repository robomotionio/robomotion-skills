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

## Workflow
1. Install: `robomotion install lemlist`
2. Connect: `robomotion lemlist lemlist_connect` → returns a `client-id`
3. List campaigns: `robomotion lemlist lemlist_list_campaigns --client-id <id>`
4. Add lead: `robomotion lemlist lemlist_add_lead --client-id <id> --campaign-id <camp> --email <email>`
5. Disconnect: `robomotion lemlist lemlist_disconnect --client-id <id>`

## Commands Reference
- `robomotion lemlist connect`
  Connect to Lemlist API using an API key and return a client ID for subsequent operations
- `robomotion lemlist disconnect --client-id`
  Disconnect from Lemlist API and release the client connection
- `robomotion lemlist get_team --client-id [--user-url]`
  Get information about the current Lemlist team
- `robomotion lemlist list_campaigns --client-id [--0] [--100]`
  List all campaigns in Lemlist with pagination support
- `robomotion lemlist unsubscribe_lead_from_campaign --client-id [--campaign-id] [--email-address]`
  Unsubscribe a lead from a Lemlist campaign (lead can be re-added later)
- `robomotion lemlist remove_lead_from_campaign --client-id [--campaign-id] [--email-address]`
  Remove a lead from a Lemlist campaign permanently

## Environment
- ROBOMOTION_API_TOKEN (if vault credentials are needed)
