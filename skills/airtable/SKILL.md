---
name: "airtable"
description: "Airtable database client — manage records, tables, and bases in Airtable. Supports CRUD operations, formula-based search, bulk operations, and comments via `robomotion airtable`. Do NOT use for Google Sheets, Excel, Baserow, NocoDB, or other spreadsheet/database tools."
---

# Airtable

The `robomotion airtable` CLI connects to Airtable's API to manage bases, tables, and records. It supports listing, creating, updating, deleting records (including bulk operations), searching with formula filters, and managing record comments.

## When to use
- List, create, update, or delete records in Airtable tables
- Search records using Airtable formula filters
- Bulk create or delete up to 10 records at once
- List bases, get table schemas, and manage comments on records

## Prerequisites
- `robomotion` CLI installed
- Package installed: `robomotion install airtable`
- Airtable API key configured via Robomotion vault

## IMPORTANT: Session Mode Required for Multi-Step Operations
Each CLI command runs as a **separate process** — connection IDs from `connect` do NOT persist across calls.
You MUST use `--session` on `connect` and pass `--session-id` to all subsequent commands.

## Workflow
1. Install (once): `robomotion install airtable`
2. Connect with session:
   ```
   robomotion airtable connect --session --output json
   # → {"outKeyId":"<key-id>","session_id":"<session-id>"}
   ```
3. Use the returned `key-id` and `session-id` in all subsequent commands:
   ```
   robomotion airtable list_records --key-id "<key-id>" --base-id <base> --table-name <table> --session-id "<session-id>" --output json
   ```
4. Disconnect when done:
   ```
   robomotion airtable disconnect --key-id "<key-id>" --session-id "<session-id>" --output json
   ```

**Always** append `--output json` to get structured JSON results.

## Commands Reference
- `robomotion airtable connect --session --output json`
  Connect to Airtable using an API key and return a key ID for subsequent operations
- `robomotion airtable disconnect --key-id --session-id "<session-id>" --output json`
  Disconnect from Airtable and release the API key connection
- `robomotion airtable list_bases --key-id --session-id "<session-id>" --output json`
  List all accessible Airtable bases for the authenticated user
- `robomotion airtable get_base_schema --key-id --base-id --session-id "<session-id>" --output json`
  Get the schema of an Airtable base including tables and fields
- `robomotion airtable create_record --key-id --base-id --table-name --record --session-id "<session-id>" --output json`
  Create a new record in an Airtable table
- `robomotion airtable read_record --key-id --base-id --table-name --record-id --session-id "<session-id>" --output json`
  Read a single record from an Airtable table by its ID
- `robomotion airtable update_record --key-id --base-id --table-name --record --session-id "<session-id>" --output json`
  Update an existing record in an Airtable table
- `robomotion airtable delete_record --key-id --base-id --table-name --record-id --session-id "<session-id>" --output json`
  Delete a record from an Airtable table by its ID
- `robomotion airtable list_records --key-id --base-id --table-name [--view-name] [--query] --session-id "<session-id>" --output json`
  List records from an Airtable table with optional view and query filters
- `robomotion airtable search_records --key-id --base-id --table-name --filter-formula [--max-records] [--sort-field] [--sort-direction] --session-id "<session-id>" --output json`
  Search for records in an Airtable table using a formula filter
- `robomotion airtable bulk_create_records --key-id --base-id --table-name --records --session-id "<session-id>" --output json`
  Create multiple records in an Airtable table at once (up to 10 records per request)
- `robomotion airtable bulk_delete_records --key-id --base-id --table-name --record-ids --session-id "<session-id>" --output json`
  Delete multiple records from an Airtable table at once (up to 10 records per request)
- `robomotion airtable list_comments --key-id --base-id --table-name --record-id --session-id "<session-id>" --output json`
  List all comments on a specific record in an Airtable table
- `robomotion airtable create_comment --key-id --base-id --table-name --record-id --comment-text --session-id "<session-id>" --output json`
  Create a comment on a specific record in an Airtable table

## Environment
- ROBOMOTION_API_TOKEN (if vault credentials are needed)
