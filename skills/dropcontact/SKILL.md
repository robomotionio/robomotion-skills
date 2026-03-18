---
name: "dropcontact"
description: "Dropcontact data enrichment — enrich and verify contact information including emails, phone numbers, and company data. Supports single and batch enrichment via `robomotion dropcontact`. Do NOT use for Apollo, Clearbit, Hunter.io, or other enrichment services."
---

# Dropcontact

The `robomotion dropcontact` CLI connects to Dropcontact for contact data enrichment and verification. It enriches contacts with company information, verifies email deliverability, and finds professional email addresses.

## When to use
- Enrich contacts with company details, job titles, and social profiles
- Verify and clean email addresses
- Find professional email addresses from name and company

## Prerequisites
- `robomotion` CLI installed
- Package installed: `robomotion install dropcontact`
- Dropcontact API key configured via Robomotion vault

## Workflow
1. Install: `robomotion install dropcontact`
2. Connect: `robomotion dropcontact dropcontact_connect` → returns a `client-id`
3. Enrich: `robomotion dropcontact dropcontact_enrich --client-id <id> --email <email>`
4. Disconnect: `robomotion dropcontact dropcontact_disconnect --client-id <id>`

## Commands Reference
- `robomotion dropcontact batch_post --data`
  Submit a batch of contact data to Dropcontact for enrichment and return a request ID
- `robomotion dropcontact batch_result --request-id`
  Retrieve the results of a previously submitted batch request from Dropcontact
- `robomotion dropcontact credits_left`
  Check how many API credits are remaining in your Dropcontact account

## Environment
- ROBOMOTION_API_TOKEN (if vault credentials are needed)
