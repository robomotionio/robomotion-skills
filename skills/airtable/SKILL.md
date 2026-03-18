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

## Workflow
1. Install: `robomotion install airtable`
2. Connect: `robomotion airtable connect` → returns a `key-id`
3. List records: `robomotion airtable list_records --key-id <id> --base-id <base> --table-name <table>`
4. Create record: `robomotion airtable create_record --key-id <id> --base-id <base> --table-name <table> --record <json>`
5. Disconnect: `robomotion airtable disconnect --key-id <id>`

## Commands Reference
- `robomotion airtable connect`
  Connect to Airtable using an API key and return a key ID for subsequent operations
- `robomotion airtable disconnect --key-id`
  Disconnect from Airtable and release the API key connection
- `robomotion airtable list_bases --key-id`
  List all accessible Airtable bases for the authenticated user
- `robomotion airtable get_base_schema --key-id --base-id`
  Get the schema of an Airtable base including tables and fields
- `robomotion airtable create_record --key-id --base-id --table-name --record`
  Create a new record in an Airtable table
- `robomotion airtable read_record --key-id --base-id --table-name --record-id`
  Read a single record from an Airtable table by its ID
- `robomotion airtable update_record --key-id --base-id --table-name --record`
  Update an existing record in an Airtable table
- `robomotion airtable delete_record --key-id --base-id --table-name --record-id`
  Delete a record from an Airtable table by its ID
- `robomotion airtable list_records --key-id --base-id --table-name [--view-name] [--query]`
  List records from an Airtable table with optional view and query filters
- `robomotion airtable search_records --key-id --base-id --table-name --filter-formula [--max-records] [--sort-field] [--sort-direction]`
  Search for records in an Airtable table using a formula filter
- `robomotion airtable bulk_create_records --key-id --base-id --table-name --records`
  Create multiple records in an Airtable table at once (up to 10 records per request)
- `robomotion airtable bulk_delete_records --key-id --base-id --table-name --record-ids`
  Delete multiple records from an Airtable table at once (up to 10 records per request)
- `robomotion airtable list_comments --key-id --base-id --table-name --record-id`
  List all comments on a specific record in an Airtable table
- `robomotion airtable create_comment --key-id --base-id --table-name --record-id --comment-text`
  Create a comment on a specific record in an Airtable table

## Environment
- ROBOMOTION_API_TOKEN (if vault credentials are needed)
