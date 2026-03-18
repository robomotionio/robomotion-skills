---
name: "apollo"
description: "Apollo.io sales intelligence — search 265M+ contacts, enrich leads, manage contacts/accounts/deals. Supports people search, organization enrichment, and CRM operations via `robomotion apollo`. Do NOT use for HubSpot, Salesforce, or other CRM systems."
---

# Apollo.io

The `robomotion apollo` CLI connects to Apollo.io's sales intelligence platform. It searches a 265M+ person database by job title, company, and location; enriches contacts and organizations; and manages contacts, accounts, and deals in your Apollo workspace.

## When to use
- Search Apollo's database for leads by job title, company, or location
- Enrich person or organization data by email, LinkedIn URL, or domain
- Create and manage contacts, accounts, and deals in Apollo CRM

## Prerequisites
- `robomotion` CLI installed
- Package installed: `robomotion install apollo`
- Apollo.io API key configured via Robomotion vault

## IMPORTANT: Session Mode Required for Multi-Step Operations
Each CLI command runs as a **separate process** — connection IDs from `connect` do NOT persist across calls.
You MUST use `--session` on `connect` and pass `--session-id` to all subsequent commands.

## Workflow
1. Install (once): `robomotion install apollo`
2. Connect with session:
   ```
   robomotion apollo apollo_connect --session --output json
   # → {"outClientId":"<client-id>","session_id":"<session-id>"}
   ```
3. Use the returned `client-id` and `session-id` in all subsequent commands:
   ```
   robomotion apollo apollo_search_people --client-id "<client-id>" --job-titles <titles> --company-name <company> --session-id "<session-id>" --output json
   ```
4. Disconnect when done:
   ```
   robomotion apollo apollo_disconnect --client-id "<client-id>" --session-id "<session-id>" --output json
   ```

**Always** append `--output json` to get structured JSON results.

## Commands Reference
- `robomotion apollo apollo_connect --session --output json`
  Connects to Apollo.io and returns a client ID for subsequent operations
- `robomotion apollo apollo_disconnect --client-id --session-id "<session-id>" --output json`
  Closes the Apollo.io connection and releases resources
- `robomotion apollo apollo_search_people --client-id --job-titles --person-locations --company-name --keywords [--1] [--25] --session-id "<session-id>" --output json`
  Searches Apollo's 265M+ person database using filters like job title，company，location，and seniority
- `robomotion apollo apollo_enrich_person --client-id --email --first-name --last-name --domain --linked-in-url --organization-name --session-id "<session-id>" --output json`
  Enriches a person's data using Apollo's database. Provide at least one identifier: email，name+domain，or LinkedIn URL
- `robomotion apollo apollo_create_contact --client-id --first-name --last-name --email --job-title --organization-name --phone --account-id --owner-id --session-id "<session-id>" --output json`
  Creates a new contact in your Apollo workspace
- `robomotion apollo apollo_update_contact --client-id --contact-id --first-name --last-name --email --job-title --organization-name --phone --account-id --owner-id --session-id "<session-id>" --output json`
  Updates an existing contact in your Apollo workspace
- `robomotion apollo apollo_search_contacts --client-id --keywords [--sort-by] [--1] [--25] --session-id "<session-id>" --output json`
  Searches contacts in your Apollo workspace by keywords，stage，or sort options
- `robomotion apollo apollo_create_account --client-id --name --domain --phone --owner-id --session-id "<session-id>" --output json`
  Creates a new account (company) in your Apollo workspace
- `robomotion apollo apollo_search_accounts --client-id --company-name-keywords [--sort-by] [--1] [--25] --session-id "<session-id>" --output json`
  Searches accounts (companies) in your Apollo workspace
- `robomotion apollo apollo_enrich_organization --client-id --domain --session-id "<session-id>" --output json`
  Enriches an organization's data by domain using Apollo's database
- `robomotion apollo apollo_create_deal --client-id --deal-name --amount --owner-id --account-id --stage-id --close-date --session-id "<session-id>" --output json`
  Creates a new deal/opportunity in your Apollo workspace
- `robomotion apollo apollo_list_deals --client-id [--1] [--25] --session-id "<session-id>" --output json`
  Lists deals/opportunities in your Apollo workspace

## Environment
- ROBOMOTION_API_TOKEN (if vault credentials are needed)
