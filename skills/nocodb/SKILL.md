---
name: "nocodb"
description: "NocoDB — manage tables, records, and databases in NocoDB (open-source Airtable alternative). Supports CRUD, filtering, sorting, and table management via `robomotion nocodb`. Do NOT use for Airtable, Baserow, Google Sheets, or other no-code databases."
---

# NocoDB

The `robomotion nocodb` CLI connects to NocoDB for database and record management. It supports listing, creating, updating, and deleting records in tables; filtering and sorting data; and managing table schemas.

## When to use
- List, create, update, or delete records in NocoDB tables
- Search and filter records with conditions
- Manage tables and view schemas

## Prerequisites
- `robomotion` CLI installed
- Package installed: `robomotion install nocodb`
- NocoDB instance URL and API token configured via Robomotion vault

## IMPORTANT: Session Mode Required for Multi-Step Operations
Each CLI command runs as a **separate process** — connection IDs from `connect` do NOT persist across calls.
You MUST use `--session` on `connect` and pass `--session-id` to all subsequent commands.

## Workflow
1. Install (once): `robomotion install nocodb`
2. Connect with session:
   ```
   robomotion nocodb nocodb_connect --session --output json
   # → {"outClientId":"<client-id>","session_id":"<session-id>"}
   ```
3. Use the returned `client-id` and `session-id` in all subsequent commands:
   ```
   robomotion nocodb nocodb_list_records --client-id "<client-id>" --table-id <table> --session-id "<session-id>" --output json
   ```
4. Disconnect when done:
   ```
   robomotion nocodb nocodb_disconnect --client-id "<client-id>" --session-id "<session-id>" --output json
   ```

**Always** append `--output json` to get structured JSON results.

## Commands Reference
- `robomotion nocodb nocodb_connect --http://localhost:8080 --session --output json`
  Connects to NocoDB and returns a client ID for subsequent operations
- `robomotion nocodb nocodb_disconnect --client-id --session-id "<session-id>" --output json`
  Closes the NocoDB connection and releases resources
- `robomotion nocodb nocodb_create_record --client-id --table-id --record-data [--base-url] [--60] --session-id "<session-id>" --output json`
  Creates a new record in a NocoDB table
- `robomotion nocodb nocodb_get_record --client-id --table-id --record-id [--base-url] [--fields] [--60] --session-id "<session-id>" --output json`
  Retrieves a single record from a NocoDB table by ID
- `robomotion nocodb nocodb_update_record --client-id --table-id --record-id --record-data [--base-url] [--60] --session-id "<session-id>" --output json`
  Updates an existing record in a NocoDB table
- `robomotion nocodb nocodb_delete_record --client-id --table-id --record-id [--base-url] [--60] --session-id "<session-id>" --output json`
  Deletes a record from a NocoDB table
- `robomotion nocodb nocodb_list_records --client-id --table-id [--base-url] [--where] [--25] [--0] [--sort] [--fields] [--60] --session-id "<session-id>" --output json`
  Retrieves multiple records from a NocoDB table with optional filtering，sorting，and pagination
- `robomotion nocodb nocodb_bulk_create_records --client-id --table-id --records [--base-url] [--120] --session-id "<session-id>" --output json`
  Creates multiple records in a NocoDB table at once
- `robomotion nocodb nocodb_bulk_update_records --client-id --table-id --records [--base-url] [--120] --session-id "<session-id>" --output json`
  Updates multiple records in a NocoDB table at once
- `robomotion nocodb nocodb_bulk_delete_records --client-id --table-id --record-ids [--base-url] [--120] --session-id "<session-id>" --output json`
  Deletes multiple records from a NocoDB table at once

## Environment
- ROBOMOTION_API_TOKEN (if vault credentials are needed)
