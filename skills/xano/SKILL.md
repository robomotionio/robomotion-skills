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

## Workflow
1. Install: `robomotion install xano`
2. Connect: `robomotion xano xano_connect` → returns a `client-id`
3. List records: `robomotion xano xano_list --client-id <id> --table <table>`
4. Create record: `robomotion xano xano_create --client-id <id> --table <table> --data <json>`
5. Disconnect: `robomotion xano xano_disconnect --client-id <id>`

## Commands Reference
- `robomotion xano xano_connect --instance-domain`
  Connects to the Xano Metadata API and returns a client ID
- `robomotion xano xano_disconnect --client-id`
  Closes the Xano connection and releases resources
- `robomotion xano xano_create_row --client-id --workspace-id --table-id --record-data [--instance-domain] [--60]`
  Creates a new record in a Xano database table
- `robomotion xano xano_get_row --client-id --workspace-id --table-id --record-id [--instance-domain] [--60]`
  Retrieves a single record from a Xano database table by ID
- `robomotion xano xano_get_many_rows --client-id --workspace-id --table-id [--instance-domain] [--1] [--50] [--60]`
  Retrieves multiple records from a Xano table with pagination
- `robomotion xano xano_update_row --client-id --workspace-id --table-id --record-id --update-data [--instance-domain] [--60]`
  Updates an existing record in a Xano database table
- `robomotion xano xano_delete_row --client-id --workspace-id --table-id --record-id [--instance-domain] [--60]`
  Deletes a record from a Xano database table by ID
- `robomotion xano xano_search_rows --client-id --workspace-id --table-id --search [--instance-domain] [--sort-by] [--sort-order] [--1] [--50] [--60]`
  Searches records in a Xano table using Metadata API search filters
- `robomotion xano xano_bulk_create --client-id --workspace-id --table-id --items [--instance-domain] [--120]`
  Creates multiple records in a Xano table at once
- `robomotion xano xano_bulk_update --client-id --workspace-id --table-id --items [--instance-domain] [--120]`
  Updates multiple records in a Xano table at once
- `robomotion xano xano_call_api --client-id --api-path --request-body --query-params --custom-headers [--instance-domain] [--http-method] [--60]`
  Calls a custom Xano API endpoint with configurable method，path，headers，and body

## Environment
- ROBOMOTION_API_TOKEN (if vault credentials are needed)
