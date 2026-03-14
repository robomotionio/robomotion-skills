---
name: "apollo"
description: "Use when the user wants to call the Robomotion Apollo package to search for leads or enrich contacts via the `robomotion apollo` CLI. Do NOT use for HubSpot, Salesforce, or other CRM systems."
---

# Apollo Skill

## When to use
- Search for leads or contacts in Apollo
- Enrich contact data using Apollo
- Manage Apollo outreach sequences

## Prerequisites
- `robomotion` CLI installed
- Package installed: `robomotion install apollo`
- Credentials configured via Robomotion vault or environment variables

## Workflow
1. Install the package: `robomotion install apollo`
2. Run commands: `robomotion apollo <command> [flags]`

## Commands Reference
- `robomotion apollo apollo_connect`
  Connects to Apollo.io and returns a client ID for subsequent operations
- `robomotion apollo apollo_disconnect --client-id`
  Closes the Apollo.io connection and releases resources
- `robomotion apollo apollo_search_people --client-id --job-titles --person-locations --company-name --keywords [--1] [--25]`
  Searches Apollo's 265M+ person database using filters like job title，company，location，and seniority
- `robomotion apollo apollo_enrich_person --client-id --email --first-name --last-name --domain --linked-in-url --organization-name`
  Enriches a person's data using Apollo's database. Provide at least one identifier: email，name+domain，or LinkedIn URL
- `robomotion apollo apollo_create_contact --client-id --first-name --last-name --email --job-title --organization-name --phone --account-id --owner-id`
  Creates a new contact in your Apollo workspace
- `robomotion apollo apollo_update_contact --client-id --contact-id --first-name --last-name --email --job-title --organization-name --phone --account-id --owner-id`
  Updates an existing contact in your Apollo workspace
- `robomotion apollo apollo_search_contacts --client-id --keywords [--sort-by] [--1] [--25]`
  Searches contacts in your Apollo workspace by keywords，stage，or sort options
- `robomotion apollo apollo_create_account --client-id --name --domain --phone --owner-id`
  Creates a new account (company) in your Apollo workspace
- `robomotion apollo apollo_search_accounts --client-id --company-name-keywords [--sort-by] [--1] [--25]`
  Searches accounts (companies) in your Apollo workspace
- `robomotion apollo apollo_enrich_organization --client-id --domain`
  Enriches an organization's data by domain using Apollo's database
- `robomotion apollo apollo_create_deal --client-id --deal-name --amount --owner-id --account-id --stage-id --close-date`
  Creates a new deal/opportunity in your Apollo workspace
- `robomotion apollo apollo_list_deals --client-id [--1] [--25]`
  Lists deals/opportunities in your Apollo workspace

## Environment
- ROBOMOTION_API_TOKEN (if vault credentials are needed)
