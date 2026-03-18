---
name: "xano"
description: "Xano — manage database records, search data, and call custom API endpoints on Xano backends. Supports CRUD operations and custom API calls via `robomotion xano`. Do NOT use for Supabase, Firebase, or direct PostgreSQL."
---

# Xano

The `robomotion xano` CLI connects to Xano (no-code backend platform) for database and API operations. It queries, creates, updates, and deletes records; searches data with filters; and calls custom API endpoints built in Xano.

## When to use
- Query, create, update, or delete records in Xano tables
- Search and filter data with conditions
- Call custom API endpoints built in Xano

## Prerequisites
- `robomotion` CLI installed
- Package installed: `robomotion install xano`
- Xano instance URL and API key configured via Robomotion vault

## IMPORTANT: Session Mode Required for Multi-Step Operations
Each CLI command runs as a **separate process** — connection IDs from `connect` do NOT persist across calls.
You MUST use `--session` on `connect` and pass `--session-id` to all subsequent commands.

## Workflow
1. Install (once): `robomotion install xano`
2. Connect with session:
   ```
   robomotion xano xano_connect --session --output json
   # → {"outClientId":"<client-id>","session_id":"<session-id>"}
   ```
3. Use the returned `client-id` and `session-id` in all subsequent commands:
   ```
   robomotion xano xano_list --client-id "<client-id>" --table <table> --session-id "<session-id>" --output json
   ```
4. Disconnect when done:
   ```
   robomotion xano xano_disconnect --client-id "<client-id>" --session-id "<session-id>" --output json
   ```

**Always** append `--output json` to get structured JSON results.

## Commands Reference
- `robomotion xano xano_connect --instance-domain --session --output json`
  Connects to the Xano Metadata API and returns a client ID
- `robomotion xano xano_disconnect --client-id --session-id "<session-id>" --output json`
  Closes the Xano connection and releases resources
- `robomotion xano xano_create_row --client-id --workspace-id --table-id --record-data [--instance-domain] [--60] --session-id "<session-id>" --output json`
  Creates a new record in a Xano database table
- `robomotion xano xano_get_row --client-id --workspace-id --table-id --record-id [--instance-domain] [--60] --session-id "<session-id>" --output json`
  Retrieves a single record from a Xano database table by ID
- `robomotion xano xano_get_many_rows --client-id --workspace-id --table-id [--instance-domain] [--1] [--50] [--60] --session-id "<session-id>" --output json`
  Retrieves multiple records from a Xano table with pagination
- `robomotion xano xano_update_row --client-id --workspace-id --table-id --record-id --update-data [--instance-domain] [--60] --session-id "<session-id>" --output json`
  Updates an existing record in a Xano database table
- `robomotion xano xano_delete_row --client-id --workspace-id --table-id --record-id [--instance-domain] [--60] --session-id "<session-id>" --output json`
  Deletes a record from a Xano database table by ID
- `robomotion xano xano_search_rows --client-id --workspace-id --table-id --search [--instance-domain] [--sort-by] [--sort-order] [--1] [--50] [--60] --session-id "<session-id>" --output json`
  Searches records in a Xano table using Metadata API search filters
- `robomotion xano xano_bulk_create --client-id --workspace-id --table-id --items [--instance-domain] [--120] --session-id "<session-id>" --output json`
  Creates multiple records in a Xano table at once
- `robomotion xano xano_bulk_update --client-id --workspace-id --table-id --items [--instance-domain] [--120] --session-id "<session-id>" --output json`
  Updates multiple records in a Xano table at once
- `robomotion xano xano_call_api --client-id --api-path --request-body --query-params --custom-headers [--instance-domain] [--http-method] [--60] --session-id "<session-id>" --output json`
  Calls a custom Xano API endpoint with configurable method，path，headers，and body

## Environment
- ROBOMOTION_API_TOKEN (if vault credentials are needed)
