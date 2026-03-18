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

## Workflow
1. Install: `robomotion install mautic`
2. Connect: `robomotion mautic mautic_connect` → returns a `client-id`
3. Create contact: `robomotion mautic mautic_create_contact --client-id <id> --fields <json>`
4. List segments: `robomotion mautic mautic_list_segments --client-id <id>`
5. Disconnect: `robomotion mautic mautic_disconnect --client-id <id>`

## Commands Reference
- `robomotion mautic mautic_connect`
  Connects to Mautic API and returns a client ID
- `robomotion mautic mautic_disconnect --client-id`
  Closes the Mautic connection and releases resources
- `robomotion mautic mautic_create_contact --client-id --email --first-name --last-name --additional-fields [--ip-address]`
  Creates a new contact in Mautic
- `robomotion mautic mautic_update_contact --client-id --contact-id --email --first-name --last-name --update-fields`
  Updates an existing contact in Mautic
- `robomotion mautic mautic_get_contact --client-id --contact-id`
  Retrieves a single contact from Mautic by ID
- `robomotion mautic mautic_list_contacts --client-id [--search] [--30] [--0] [--order-by] [--order-direction]`
  Lists contacts from Mautic with optional search and pagination
- `robomotion mautic mautic_delete_contact --client-id --contact-id`
  Permanently deletes a contact from Mautic
- `robomotion mautic mautic_send_email --client-id --email-id --contact-id --tokens`
  Sends a Mautic email to a specific contact
- `robomotion mautic mautic_edit_contact_points --client-id --contact-id --points [--action]`
  Adds or subtracts points from a Mautic contact
- `robomotion mautic mautic_edit_dnc --client-id --contact-id [--action] [--channel] [--reason] [--comments]`
  Adds or removes a contact from the Do Not Contact list
- `robomotion mautic mautic_create_company --client-id --company-name --additional-fields`
  Creates a new company in Mautic
- `robomotion mautic mautic_get_company --client-id --company-id`
  Retrieves a single company from Mautic by ID
- `robomotion mautic mautic_list_companies --client-id [--search] [--30] [--0] [--order-direction]`
  Lists companies from Mautic with optional search and pagination
- `robomotion mautic mautic_delete_company --client-id --company-id`
  Permanently deletes a company from Mautic
- `robomotion mautic mautic_add_contact_to_segment --client-id --segment-id --contact-id`
  Adds a contact to a Mautic segment
- `robomotion mautic mautic_remove_contact_from_segment --client-id --segment-id --contact-id`
  Removes a contact from a Mautic segment
- `robomotion mautic mautic_add_contact_to_campaign --client-id --campaign-id --contact-id`
  Adds a contact to a Mautic campaign
- `robomotion mautic mautic_remove_contact_from_campaign --client-id --campaign-id --contact-id`
  Removes a contact from a Mautic campaign

## Environment
- ROBOMOTION_API_TOKEN (if vault credentials are needed)
