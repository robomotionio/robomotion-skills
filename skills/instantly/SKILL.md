---
name: "instantly"
description: "Instantly cold email platform — manage campaigns, leads, email accounts, and track analytics. Supports lead import, campaign management, and deliverability monitoring via `robomotion instantly`. Do NOT use for Lemlist, Mailchimp, Gmail, or other email platforms."
---

# Instantly

The `robomotion instantly` CLI connects to Instantly for cold email outreach management. It manages campaigns (create/update/activate/pause), imports and manages leads, tracks email analytics and sending stats, and handles email account configuration.

## When to use
- Create, update, activate, or pause cold email campaigns
- Add, list, or manage leads in campaigns
- Track campaign analytics — open rates, replies, bounces
- Manage email sending accounts and warm-up settings

## Prerequisites
- `robomotion` CLI installed
- Package installed: `robomotion install instantly`
- Instantly API key configured via Robomotion vault

## IMPORTANT: Session Mode Required for Multi-Step Operations
Each CLI command runs as a **separate process** — connection IDs from `connect` do NOT persist across calls.
You MUST use `--session` on `connect` and pass `--session-id` to all subsequent commands.

## Workflow
1. Install (once): `robomotion install instantly`
2. Connect with session:
   ```
   robomotion instantly instantly_connect --session --output json
   # → {"outClientId":"<client-id>","session_id":"<session-id>"}
   ```
3. Use the returned `client-id` and `session-id` in all subsequent commands:
   ```
   robomotion instantly instantly_list_campaigns --client-id "<client-id>" --session-id "<session-id>" --output json
   ```
4. Disconnect when done:
   ```
   robomotion instantly instantly_disconnect --client-id "<client-id>" --session-id "<session-id>" --output json
   ```

**Always** append `--output json` to get structured JSON results.

## Commands Reference
- `robomotion instantly list_campaigns --client-id [--10] [--search] [--30] [--status] --session-id "<session-id>" --output json`
  Lists all campaigns in the Instantly workspace
- `robomotion instantly get_campaign --client-id --campaign-id [--30] --session-id "<session-id>" --output json`
  Gets details of a specific campaign by ID
- `robomotion instantly activate_campaign --client-id --campaign-id [--30] --session-id "<session-id>" --output json`
  Activates (launches) a paused or draft campaign
- `robomotion instantly pause_campaign --client-id --campaign-id [--30] --session-id "<session-id>" --output json`
  Pauses an active campaign
- `robomotion instantly add_lead --client-id --email --campaign-id [--first-name] [--last-name] [--company-name] [--phone] [--website] [--personalization] [--list-id] [--30] --session-id "<session-id>" --output json`
  Adds a lead to a campaign or lead list
- `robomotion instantly list_leads --client-id [--campaign-id] [--list-id] [--search] [--10] [--30] --session-id "<session-id>" --output json`
  Lists leads with optional filters
- `robomotion instantly get_lead --client-id --lead-id [--30] --session-id "<session-id>" --output json`
  Gets details of a specific lead by ID
- `robomotion instantly update_lead --client-id --lead-id [--first-name] [--last-name] [--company-name] [--phone] [--website] [--email] [--30] --session-id "<session-id>" --output json`
  Updates lead details by ID
- `robomotion instantly delete_lead --client-id --lead-id [--30] --session-id "<session-id>" --output json`
  Deletes a lead by ID
- `robomotion instantly list_emails --client-id [--campaign-id] [--search] [--lead-email] [--10] [--30] [--email-type] --session-id "<session-id>" --output json`
  Lists emails from the Instantly Unibox
- `robomotion instantly reply_to_email --client-id --reply-to-uuid --email-account --subject --body-(html) [--cc] [--bcc] [--60] --session-id "<session-id>" --output json`
  Replies to an email in the Unibox
- `robomotion instantly get_campaign_analytics --client-id --campaign-id [--start-date] [--end-date] [--30] --session-id "<session-id>" --output json`
  Gets analytics data for campaigns

## Environment
- ROBOMOTION_API_TOKEN (if vault credentials are needed)
