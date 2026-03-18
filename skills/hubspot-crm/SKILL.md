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

## Workflow
1. Install: `robomotion install hubspot`
2. Connect: `robomotion hubspot connect` → returns a `client-id`
3. Search contacts: `robomotion hubspot search_contacts --client-id <id> --query <query>`
4. Create deal: `robomotion hubspot create_deal --client-id <id> --properties <json>`
5. Disconnect: `robomotion hubspot disconnect --client-id <id>`

## Commands Reference
- `robomotion hubspot hubspot_connect`
  Connects to HubSpot CRM and returns a client ID for use in other nodes
- `robomotion hubspot hubspot_disconnect --client-id`
  Closes the HubSpot connection and releases resources
- `robomotion hubspot hubspot_create_contact --client-id --email --first-name --last-name --phone --company --website --properties`
  Creates a new contact in HubSpot CRM
- `robomotion hubspot hubspot_get_contact --client-id --contact-id --properties`
  Retrieves a contact from HubSpot by ID
- `robomotion hubspot hubspot_update_contact --client-id --contact-id --email --first-name --last-name --phone --company --properties`
  Updates an existing contact in HubSpot CRM
- `robomotion hubspot hubspot_delete_contact --client-id --contact-id`
  Deletes a contact from HubSpot CRM
- `robomotion hubspot hubspot_list_contacts --client-id --properties --after [--100]`
  Lists contacts from HubSpot CRM with pagination
- `robomotion hubspot hubspot_search_contacts --client-id --query --filters --properties --after [--100] [--sort-by] [--sort-direction]`
  Searches for contacts in HubSpot CRM using filters
- `robomotion hubspot hubspot_create_company --client-id --company-name --domain --industry --phone --city --country --description --properties`
  Creates a new company in HubSpot CRM
- `robomotion hubspot hubspot_get_company --client-id --company-id --properties`
  Retrieves a company from HubSpot by ID
- `robomotion hubspot hubspot_update_company --client-id --company-id --company-name --domain --industry --phone --properties`
  Updates an existing company in HubSpot CRM
- `robomotion hubspot hubspot_delete_company --client-id --company-id`
  Deletes a company from HubSpot CRM
- `robomotion hubspot hubspot_list_companies --client-id --properties --after [--100]`
  Lists companies from HubSpot CRM with pagination
- `robomotion hubspot hubspot_search_companies --client-id --query --filters --properties --after [--100] [--sort-by] [--sort-direction]`
  Searches for companies in HubSpot CRM using filters
- `robomotion hubspot hubspot_create_deal --client-id --deal-name --amount --deal-stage --pipeline --close-date --deal-type --properties`
  Creates a new deal in HubSpot CRM
- `robomotion hubspot hubspot_get_deal --client-id --deal-id --properties`
  Retrieves a deal from HubSpot by ID
- `robomotion hubspot hubspot_update_deal --client-id --deal-id --deal-name --amount --deal-stage --close-date --properties`
  Updates an existing deal in HubSpot CRM
- `robomotion hubspot hubspot_delete_deal --client-id --deal-id`
  Deletes a deal from HubSpot CRM
- `robomotion hubspot hubspot_list_deals --client-id --properties --after [--100]`
  Lists deals from HubSpot CRM with pagination
- `robomotion hubspot hubspot_search_deals --client-id --query --filters --properties --after [--100] [--sort-by] [--sort-direction]`
  Searches for deals in HubSpot CRM using filters
- `robomotion hubspot hubspot_create_ticket --client-id --subject --content --pipeline --status --priority --category --properties`
  Creates a new support ticket in HubSpot
- `robomotion hubspot hubspot_get_ticket --client-id --ticket-id --properties`
  Retrieves a ticket from HubSpot by ID
- `robomotion hubspot hubspot_update_ticket --client-id --ticket-id --subject --content --status --priority --properties`
  Updates an existing ticket in HubSpot
- `robomotion hubspot hubspot_delete_ticket --client-id --ticket-id`
  Deletes a ticket from HubSpot
- `robomotion hubspot hubspot_list_tickets --client-id --properties --after [--100]`
  Lists tickets from HubSpot with pagination
- `robomotion hubspot hubspot_create_association --client-id --contacts --from-object-id --companies --to-object-id [--association-type]`
  Creates an association between two HubSpot CRM objects
- `robomotion hubspot hubspot_delete_association --client-id --contacts --from-object-id --companies --to-object-id [--association-type]`
  Removes an association between two HubSpot CRM objects

## Environment
- ROBOMOTION_API_TOKEN (if vault credentials are needed)
