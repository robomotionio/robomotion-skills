---
name: "hubspot-crm"
description: "HubSpot CRM — manage contacts, companies, deals, tickets, and products. Supports CRUD, search, associations, and pipeline management via `robomotion hubspot`. Do NOT use for Salesforce, Apollo, Pipedrive, or other CRM systems."
---

# HubSpot CRM

The `robomotion hubspot` CLI connects to HubSpot CRM for contact, company, deal, and ticket management. It supports creating, reading, updating, and searching CRM objects with property filtering and association management.

## When to use
- Create, update, or search contacts, companies, and deals
- Manage deal pipelines and ticket workflows
- Search CRM records with property filters

## Prerequisites
- `robomotion` CLI installed
- Package installed: `robomotion install hubspot`
- HubSpot API key or OAuth2 token configured via Robomotion vault

## IMPORTANT: Session Mode Required for Multi-Step Operations
Each CLI command runs as a **separate process** — connection IDs from `connect` do NOT persist across calls.
You MUST use `--session` on `connect` and pass `--session-id` to all subsequent commands.

## Workflow
1. Install (once): `robomotion install hubspot`
2. Connect with session:
   ```
   robomotion hubspot connect --session --output json
   # → {"outClientId":"<client-id>","session_id":"<session-id>"}
   ```
3. Use the returned `client-id` and `session-id` in all subsequent commands:
   ```
   robomotion hubspot search_contacts --client-id "<client-id>" --query <query> --session-id "<session-id>" --output json
   ```
4. Disconnect when done:
   ```
   robomotion hubspot disconnect --client-id "<client-id>" --session-id "<session-id>" --output json
   ```

**Always** append `--output json` to get structured JSON results.

## Commands Reference
- `robomotion hubspot hubspot_connect --session --output json`
  Connects to HubSpot CRM and returns a client ID for use in other nodes
- `robomotion hubspot hubspot_disconnect --client-id --session-id "<session-id>" --output json`
  Closes the HubSpot connection and releases resources
- `robomotion hubspot hubspot_create_contact --client-id --email --first-name --last-name --phone --company --website --properties --session-id "<session-id>" --output json`
  Creates a new contact in HubSpot CRM
- `robomotion hubspot hubspot_get_contact --client-id --contact-id --properties --session-id "<session-id>" --output json`
  Retrieves a contact from HubSpot by ID
- `robomotion hubspot hubspot_update_contact --client-id --contact-id --email --first-name --last-name --phone --company --properties --session-id "<session-id>" --output json`
  Updates an existing contact in HubSpot CRM
- `robomotion hubspot hubspot_delete_contact --client-id --contact-id --session-id "<session-id>" --output json`
  Deletes a contact from HubSpot CRM
- `robomotion hubspot hubspot_list_contacts --client-id --properties --after [--100] --session-id "<session-id>" --output json`
  Lists contacts from HubSpot CRM with pagination
- `robomotion hubspot hubspot_search_contacts --client-id --query --filters --properties --after [--100] [--sort-by] [--sort-direction] --session-id "<session-id>" --output json`
  Searches for contacts in HubSpot CRM using filters
- `robomotion hubspot hubspot_create_company --client-id --company-name --domain --industry --phone --city --country --description --properties --session-id "<session-id>" --output json`
  Creates a new company in HubSpot CRM
- `robomotion hubspot hubspot_get_company --client-id --company-id --properties --session-id "<session-id>" --output json`
  Retrieves a company from HubSpot by ID
- `robomotion hubspot hubspot_update_company --client-id --company-id --company-name --domain --industry --phone --properties --session-id "<session-id>" --output json`
  Updates an existing company in HubSpot CRM
- `robomotion hubspot hubspot_delete_company --client-id --company-id --session-id "<session-id>" --output json`
  Deletes a company from HubSpot CRM
- `robomotion hubspot hubspot_list_companies --client-id --properties --after [--100] --session-id "<session-id>" --output json`
  Lists companies from HubSpot CRM with pagination
- `robomotion hubspot hubspot_search_companies --client-id --query --filters --properties --after [--100] [--sort-by] [--sort-direction] --session-id "<session-id>" --output json`
  Searches for companies in HubSpot CRM using filters
- `robomotion hubspot hubspot_create_deal --client-id --deal-name --amount --deal-stage --pipeline --close-date --deal-type --properties --session-id "<session-id>" --output json`
  Creates a new deal in HubSpot CRM
- `robomotion hubspot hubspot_get_deal --client-id --deal-id --properties --session-id "<session-id>" --output json`
  Retrieves a deal from HubSpot by ID
- `robomotion hubspot hubspot_update_deal --client-id --deal-id --deal-name --amount --deal-stage --close-date --properties --session-id "<session-id>" --output json`
  Updates an existing deal in HubSpot CRM
- `robomotion hubspot hubspot_delete_deal --client-id --deal-id --session-id "<session-id>" --output json`
  Deletes a deal from HubSpot CRM
- `robomotion hubspot hubspot_list_deals --client-id --properties --after [--100] --session-id "<session-id>" --output json`
  Lists deals from HubSpot CRM with pagination
- `robomotion hubspot hubspot_search_deals --client-id --query --filters --properties --after [--100] [--sort-by] [--sort-direction] --session-id "<session-id>" --output json`
  Searches for deals in HubSpot CRM using filters
- `robomotion hubspot hubspot_create_ticket --client-id --subject --content --pipeline --status --priority --category --properties --session-id "<session-id>" --output json`
  Creates a new support ticket in HubSpot
- `robomotion hubspot hubspot_get_ticket --client-id --ticket-id --properties --session-id "<session-id>" --output json`
  Retrieves a ticket from HubSpot by ID
- `robomotion hubspot hubspot_update_ticket --client-id --ticket-id --subject --content --status --priority --properties --session-id "<session-id>" --output json`
  Updates an existing ticket in HubSpot
- `robomotion hubspot hubspot_delete_ticket --client-id --ticket-id --session-id "<session-id>" --output json`
  Deletes a ticket from HubSpot
- `robomotion hubspot hubspot_list_tickets --client-id --properties --after [--100] --session-id "<session-id>" --output json`
  Lists tickets from HubSpot with pagination
- `robomotion hubspot hubspot_create_association --client-id --contacts --from-object-id --companies --to-object-id [--association-type] --session-id "<session-id>" --output json`
  Creates an association between two HubSpot CRM objects
- `robomotion hubspot hubspot_delete_association --client-id --contacts --from-object-id --companies --to-object-id [--association-type] --session-id "<session-id>" --output json`
  Removes an association between two HubSpot CRM objects

## Environment
- ROBOMOTION_API_TOKEN (if vault credentials are needed)
