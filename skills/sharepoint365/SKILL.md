---
name: "sharepoint365"
description: "Microsoft SharePoint 365 — manage sites, lists, list items, document libraries, and files via Microsoft Graph API. Supports site search, list CRUD, and file operations via `robomotion sharepoint365`. Do NOT use for OneDrive personal, Google Drive, or Confluence."
---

# Microsoft SharePoint 365

The `robomotion sharepoint365` CLI connects to Microsoft SharePoint 365 via the Graph API for site and content management. It manages sites, lists, list items, document libraries, and files — supporting search, CRUD operations, and file upload/download.

## When to use
- List, search, and manage SharePoint sites
- Create, read, update, and delete list items
- Upload and download files from document libraries
- Manage lists, views, and site content

## Prerequisites
- `robomotion` CLI installed
- Package installed: `robomotion install sharepoint365`
- Microsoft 365 OAuth2 credentials configured via Robomotion vault

## IMPORTANT: Session Mode Required for Multi-Step Operations
Each CLI command runs as a **separate process** — connection IDs from `connect` do NOT persist across calls.
You MUST use `--session` on `connect` and pass `--session-id` to all subsequent commands.

## Workflow
1. Install (once): `robomotion install sharepoint365`
2. Connect with session:
   ```
   robomotion sharepoint365 sp_connect --session --output json
   # → {"outClientId":"<client-id>","session_id":"<session-id>"}
   ```
3. Use the returned `client-id` and `session-id` in all subsequent commands:
   ```
   robomotion sharepoint365 sp_list_sites --client-id "<client-id>" --session-id "<session-id>" --output json
   ```
4. Disconnect when done:
   ```
   robomotion sharepoint365 sp_disconnect --client-id "<client-id>" --session-id "<session-id>" --output json
   ```

**Always** append `--output json` to get structured JSON results.

## Commands Reference
- `robomotion sharepoint365 sharepoint_connect --session --output json`
  Establishes a connection to SharePoint 365 and returns a connection ID for use in other nodes
- `robomotion sharepoint365 sharepoint_disconnect --connection-id --session-id "<session-id>" --output json`
  Closes a SharePoint connection and releases resources
- `robomotion sharepoint365 sharepoint_list_sites --connection-id --search-query --session-id "<session-id>" --output json`
  Lists SharePoint sites accessible to the authenticated user
- `robomotion sharepoint365 sharepoint_get_site --connection-id --site-url --session-id "<session-id>" --output json`
  Retrieves information about a specific SharePoint site
- `robomotion sharepoint365 sharepoint_list_lists --connection-id --site-id --session-id "<session-id>" --output json`
  Lists all lists in a SharePoint site
- `robomotion sharepoint365 sharepoint_get_list --connection-id --site-id --list-id [--include-columns] --session-id "<session-id>" --output json`
  Retrieves information about a specific SharePoint list including columns
- `robomotion sharepoint365 sharepoint_create_list --connection-id --site-id --display-name --description [--template] --session-id "<session-id>" --output json`
  Creates a new list in a SharePoint site
- `robomotion sharepoint365 sharepoint_list_items --connection-id --site-id --list-id --filter --top [--expand-fields] --session-id "<session-id>" --output json`
  Lists items in a SharePoint list
- `robomotion sharepoint365 sharepoint_get_item --connection-id --site-id --list-id --item-id [--expand-fields] --session-id "<session-id>" --output json`
  Retrieves a specific item from a SharePoint list
- `robomotion sharepoint365 sharepoint_create_item --connection-id --site-id --list-id --fields --session-id "<session-id>" --output json`
  Creates a new item in a SharePoint list
- `robomotion sharepoint365 sharepoint_update_item --connection-id --site-id --list-id --item-id --fields --session-id "<session-id>" --output json`
  Updates an existing item in a SharePoint list
- `robomotion sharepoint365 sharepoint_delete_item --connection-id --site-id --list-id --item-id --session-id "<session-id>" --output json`
  Deletes an item from a SharePoint list
- `robomotion sharepoint365 sharepoint_list_libraries --connection-id --site-url --session-id "<session-id>" --output json`
  Lists all document libraries in a SharePoint site
- `robomotion sharepoint365 sharepoint_get_library --connection-id --site-url --library-name --session-id "<session-id>" --output json`
  Retrieves information about a document library
- `robomotion sharepoint365 sharepoint_list_files --connection-id --site-url --library-name --folder-path --session-id "<session-id>" --output json`
  Lists files and folders in a SharePoint document library
- `robomotion sharepoint365 sharepoint_upload_file --connection-id --site-url --library-name --file-path --local-file-path --session-id "<session-id>" --output json`
  Uploads a file to a SharePoint document library
- `robomotion sharepoint365 sharepoint_download_file --connection-id --site-url --library-name --file-path --local-file-path --session-id "<session-id>" --output json`
  Downloads a file from a SharePoint document library
- `robomotion sharepoint365 sharepoint_delete_file --connection-id --site-url --library-name --file-path --session-id "<session-id>" --output json`
  Deletes a file from a SharePoint document library

## Environment
- ROBOMOTION_API_TOKEN (if vault credentials are needed)
