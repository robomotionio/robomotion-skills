---
name: "mautic"
description: "Mautic marketing automation — manage contacts, companies, segments, campaigns, emails, and forms. Supports lead scoring, campaign automation, and email marketing via `robomotion mautic`. Do NOT use for HubSpot Marketing, Mailchimp, or other marketing platforms."
---

# Mautic

The `robomotion mautic` CLI connects to Mautic (open-source marketing automation) for contact and campaign management. It handles contacts, companies, segments, campaigns, email templates, forms, and notes — covering the full marketing automation workflow.

## When to use
- Create, update, search, or delete contacts and companies
- Manage segments and add/remove contacts from them
- List and manage marketing campaigns and email templates
- Handle forms and contact notes

## Prerequisites
- `robomotion` CLI installed
- Package installed: `robomotion install mautic`
- Mautic instance URL and API credentials configured via Robomotion vault

## IMPORTANT: Session Mode Required for Multi-Step Operations
Each CLI command runs as a **separate process** — connection IDs from `connect` do NOT persist across calls.
You MUST use `--session` on `connect` and pass `--session-id` to all subsequent commands.

## Workflow
1. Install (once): `robomotion install mautic`
2. Connect with session:
   ```
   robomotion mautic mautic_connect --session --output json
   # → {"outClientId":"<client-id>","session_id":"<session-id>"}
   ```
3. Use the returned `client-id` and `session-id` in all subsequent commands:
   ```
   robomotion mautic mautic_create_contact --client-id "<client-id>" --fields <json> --session-id "<session-id>" --output json
   ```
4. Disconnect when done:
   ```
   robomotion mautic mautic_disconnect --client-id "<client-id>" --session-id "<session-id>" --output json
   ```

**Always** append `--output json` to get structured JSON results.

## Commands Reference
- `robomotion mautic mautic_connect --session --output json`
  Connects to Mautic API and returns a client ID
- `robomotion mautic mautic_disconnect --client-id --session-id "<session-id>" --output json`
  Closes the Mautic connection and releases resources
- `robomotion mautic mautic_create_contact --client-id --email --first-name --last-name --additional-fields [--ip-address] --session-id "<session-id>" --output json`
  Creates a new contact in Mautic
- `robomotion mautic mautic_update_contact --client-id --contact-id --email --first-name --last-name --update-fields --session-id "<session-id>" --output json`
  Updates an existing contact in Mautic
- `robomotion mautic mautic_get_contact --client-id --contact-id --session-id "<session-id>" --output json`
  Retrieves a single contact from Mautic by ID
- `robomotion mautic mautic_list_contacts --client-id [--search] [--30] [--0] [--order-by] [--order-direction] --session-id "<session-id>" --output json`
  Lists contacts from Mautic with optional search and pagination
- `robomotion mautic mautic_delete_contact --client-id --contact-id --session-id "<session-id>" --output json`
  Permanently deletes a contact from Mautic
- `robomotion mautic mautic_send_email --client-id --email-id --contact-id --tokens --session-id "<session-id>" --output json`
  Sends a Mautic email to a specific contact
- `robomotion mautic mautic_edit_contact_points --client-id --contact-id --points [--action] --session-id "<session-id>" --output json`
  Adds or subtracts points from a Mautic contact
- `robomotion mautic mautic_edit_dnc --client-id --contact-id [--action] [--channel] [--reason] [--comments] --session-id "<session-id>" --output json`
  Adds or removes a contact from the Do Not Contact list
- `robomotion mautic mautic_create_company --client-id --company-name --additional-fields --session-id "<session-id>" --output json`
  Creates a new company in Mautic
- `robomotion mautic mautic_get_company --client-id --company-id --session-id "<session-id>" --output json`
  Retrieves a single company from Mautic by ID
- `robomotion mautic mautic_list_companies --client-id [--search] [--30] [--0] [--order-direction] --session-id "<session-id>" --output json`
  Lists companies from Mautic with optional search and pagination
- `robomotion mautic mautic_delete_company --client-id --company-id --session-id "<session-id>" --output json`
  Permanently deletes a company from Mautic
- `robomotion mautic mautic_add_contact_to_segment --client-id --segment-id --contact-id --session-id "<session-id>" --output json`
  Adds a contact to a Mautic segment
- `robomotion mautic mautic_remove_contact_from_segment --client-id --segment-id --contact-id --session-id "<session-id>" --output json`
  Removes a contact from a Mautic segment
- `robomotion mautic mautic_add_contact_to_campaign --client-id --campaign-id --contact-id --session-id "<session-id>" --output json`
  Adds a contact to a Mautic campaign
- `robomotion mautic mautic_remove_contact_from_campaign --client-id --campaign-id --contact-id --session-id "<session-id>" --output json`
  Removes a contact from a Mautic campaign

## Environment
- ROBOMOTION_API_TOKEN (if vault credentials are needed)
