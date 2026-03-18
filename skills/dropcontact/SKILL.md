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

## IMPORTANT: Session Mode Required for Multi-Step Operations
Each CLI command runs as a **separate process** — connection IDs from `connect` do NOT persist across calls.
You MUST use `--session` on `connect` and pass `--session-id` to all subsequent commands.

## Workflow
1. Install (once): `robomotion install dropcontact`
2. Connect with session:
   ```
   robomotion dropcontact dropcontact_connect --session --output json
   # → {"outClientId":"<client-id>","session_id":"<session-id>"}
   ```
3. Use the returned `client-id` and `session-id` in all subsequent commands:
   ```
   robomotion dropcontact dropcontact_enrich --client-id "<client-id>" --email <email> --session-id "<session-id>" --output json
   ```
4. Disconnect when done:
   ```
   robomotion dropcontact dropcontact_disconnect --client-id "<client-id>" --session-id "<session-id>" --output json
   ```

**Always** append `--output json` to get structured JSON results.

## Commands Reference
- `robomotion dropcontact batch_post --data --output json`
  Submit a batch of contact data to Dropcontact for enrichment and return a request ID
- `robomotion dropcontact batch_result --request-id --output json`
  Retrieve the results of a previously submitted batch request from Dropcontact
- `robomotion dropcontact credits_left --output json`
  Check how many API credits are remaining in your Dropcontact account

## Environment
- ROBOMOTION_API_TOKEN (if vault credentials are needed)
