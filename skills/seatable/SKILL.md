---
name: "seatable"
description: "SeaTable — manage rows, tables, and bases in SeaTable collaborative databases. Supports CRUD, filtering, linking, file attachments, and view management via `robomotion seatable`. Do NOT use for Airtable, Baserow, NocoDB, or other no-code databases."
---

# SeaTable

The `robomotion seatable` CLI connects to SeaTable for collaborative database management. It manages rows (CRUD with filtering and sorting), tables, bases, links between records, file attachments, and views.

## When to use
- List, create, update, or delete rows in SeaTable tables
- Search and filter rows with SQL-like conditions
- Manage links between records and file attachments
- List tables, views, and manage base schemas

## Prerequisites
- `robomotion` CLI installed
- Package installed: `robomotion install seatable`
- SeaTable API token configured via Robomotion vault

## Workflow
1. Install: `robomotion install seatable`
2. Connect: `robomotion seatable seatable_connect` → returns a `client-id`
3. List rows: `robomotion seatable seatable_list_rows --client-id <id> --table-name <table>`
4. Create row: `robomotion seatable seatable_create_row --client-id <id> --table-name <table> --row <json>`
5. Disconnect: `robomotion seatable seatable_disconnect --client-id <id>`

## Commands Reference
- `robomotion seatable seatable_connect`
  Connects to SeaTable and returns a client ID for subsequent operations
- `robomotion seatable seatable_disconnect --client-id`
  Closes the SeaTable connection and releases resources
- `robomotion seatable seatable_create_row --client-id --table-name --row-data`
  Creates a new row in a SeaTable table
- `robomotion seatable seatable_get_row --client-id --table-name --row-id`
  Retrieves a single row from a SeaTable table by its ID
- `robomotion seatable seatable_list_rows --client-id --table-name [--view-name] [--0] [--100]`
  Retrieves multiple rows from a SeaTable table
- `robomotion seatable seatable_update_row --client-id --table-name --row-id --row-data`
  Updates an existing row in a SeaTable table
- `robomotion seatable seatable_delete_row --client-id --table-name --row-id`
  Deletes a row from a SeaTable table
- `robomotion seatable seatable_lock_row --client-id --table-name --row-id`
  Locks a row in a SeaTable table to prevent changes
- `robomotion seatable seatable_unlock_row --client-id --table-name --row-id`
  Unlocks a row in a SeaTable table
- `robomotion seatable seatable_search_rows --client-id --table-name --search-query [--100]`
  Searches for rows containing a keyword in a SeaTable table
- `robomotion seatable seatable_sql_query --client-id --sql-query`
  Executes a SQL query on a SeaTable base
- `robomotion seatable seatable_create_link --client-id --link-id --table-name --other-table-name --row-id --other-row-id`
  Creates a link between two rows in different tables
- `robomotion seatable seatable_delete_link --client-id --link-id --table-name --other-table-name --row-id --other-row-id`
  Removes a link between two rows in different tables
- `robomotion seatable seatable_upload_file --client-id --file-path`
  Uploads a file to SeaTable storage
- `robomotion seatable seatable_get_asset_url --client-id --asset-path`
  Gets a download URL for a file/image asset stored in SeaTable
- `robomotion seatable seatable_get_metadata --client-id`
  Retrieves the metadata (structure) of a SeaTable base including tables، columns، and links
- `robomotion seatable seatable_api_call --client-id --endpoint [--http-method] [--request-body] [--headers]`
  Makes a custom API call to SeaTable for advanced operations

## Environment
- ROBOMOTION_API_TOKEN (if vault credentials are needed)
