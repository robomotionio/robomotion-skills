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

## Workflow
1. Install: `robomotion install baserow`
2. Connect: `robomotion baserow baserow_connect --https://api-baserow-io` → returns a `client-id`
3. List rows: `robomotion baserow baserow_list_rows --client-id <id> --table-id <table>`
4. Create row: `robomotion baserow baserow_create_row --client-id <id> --table-id <table> --row-data <json>`
5. Disconnect: `robomotion baserow baserow_disconnect --client-id <id>`

## Commands Reference
- `robomotion baserow baserow_connect --https://api-baserow-io`
  Connects to a Baserow instance and returns a client ID for subsequent operations
- `robomotion baserow baserow_disconnect --client-id`
  Closes the Baserow connection and releases resources
- `robomotion baserow baserow_list_rows --client-id --table-id [--base-url] [--1] [--100] [--search] [--order-by] [--filter-type] [--filters] [--60]`
  Retrieves multiple rows from a Baserow table with optional filtering，sorting，searching，and pagination
- `robomotion baserow baserow_get_row --client-id --table-id --row-id [--base-url] [--60]`
  Retrieves a single row by ID from a Baserow table
- `robomotion baserow baserow_create_row --client-id --table-id --row-data [--base-url] [--60]`
  Creates a new row in a Baserow table with the provided field data
- `robomotion baserow baserow_update_row --client-id --table-id --row-id --row-data [--base-url] [--60]`
  Updates an existing row in a Baserow table with the provided field data
- `robomotion baserow baserow_delete_row --client-id --table-id --row-id [--base-url] [--60]`
  Deletes a row from a Baserow table by its ID
- `robomotion baserow baserow_list_fields --client-id --table-id [--base-url] [--60]`
  Lists all fields (columns) and their types for a Baserow table

## Environment
- ROBOMOTION_API_TOKEN (if vault credentials are needed)
