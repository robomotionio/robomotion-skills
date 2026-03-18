---
name: "baserow"
description: "Baserow open-source database — manage rows, tables, and fields in self-hosted or cloud Baserow instances. Supports CRUD, filtering, sorting, search, and field listing via `robomotion baserow`. Do NOT use for Airtable, NocoDB, Google Sheets, or other no-code databases."
---

# Baserow

The `robomotion baserow` CLI connects to Baserow (open-source Airtable alternative) for row and table management. It supports listing rows with filtering/sorting/search, single-row CRUD, and field schema inspection on any self-hosted or cloud Baserow instance.

## When to use
- List, create, update, or delete rows in Baserow tables
- Search and filter rows with custom queries
- Get table field definitions and schema

## Prerequisites
- `robomotion` CLI installed
- Package installed: `robomotion install baserow`
- Baserow instance URL and API token configured via Robomotion vault

## IMPORTANT: Session Mode Required for Multi-Step Operations
Each CLI command runs as a **separate process** — connection IDs from `connect` do NOT persist across calls.
You MUST use `--session` on `connect` and pass `--session-id` to all subsequent commands.

## Workflow
1. Install (once): `robomotion install baserow`
2. Connect with session:
   ```
   robomotion baserow baserow_connect --session --output json
   # → {"outClientId":"<client-id>","session_id":"<session-id>"}
   ```
3. Use the returned `client-id` and `session-id` in all subsequent commands:
   ```
   robomotion baserow baserow_list_rows --client-id "<client-id>" --table-id <table> --session-id "<session-id>" --output json
   ```
4. Disconnect when done:
   ```
   robomotion baserow baserow_disconnect --client-id "<client-id>" --session-id "<session-id>" --output json
   ```

**Always** append `--output json` to get structured JSON results.

## Commands Reference
- `robomotion baserow baserow_connect --https://api-baserow-io --session --output json`
  Connects to a Baserow instance and returns a client ID for subsequent operations
- `robomotion baserow baserow_disconnect --client-id --session-id "<session-id>" --output json`
  Closes the Baserow connection and releases resources
- `robomotion baserow baserow_list_rows --client-id --table-id [--base-url] [--1] [--100] [--search] [--order-by] [--filter-type] [--filters] [--60] --session-id "<session-id>" --output json`
  Retrieves multiple rows from a Baserow table with optional filtering，sorting，searching，and pagination
- `robomotion baserow baserow_get_row --client-id --table-id --row-id [--base-url] [--60] --session-id "<session-id>" --output json`
  Retrieves a single row by ID from a Baserow table
- `robomotion baserow baserow_create_row --client-id --table-id --row-data [--base-url] [--60] --session-id "<session-id>" --output json`
  Creates a new row in a Baserow table with the provided field data
- `robomotion baserow baserow_update_row --client-id --table-id --row-id --row-data [--base-url] [--60] --session-id "<session-id>" --output json`
  Updates an existing row in a Baserow table with the provided field data
- `robomotion baserow baserow_delete_row --client-id --table-id --row-id [--base-url] [--60] --session-id "<session-id>" --output json`
  Deletes a row from a Baserow table by its ID
- `robomotion baserow baserow_list_fields --client-id --table-id [--base-url] [--60] --session-id "<session-id>" --output json`
  Lists all fields (columns) and their types for a Baserow table

## Environment
- ROBOMOTION_API_TOKEN (if vault credentials are needed)
