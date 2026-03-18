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

## Workflow
1. Install: `robomotion install sharepoint365`
2. Connect: `robomotion sharepoint365 sp_connect` → returns a `client-id`
3. List sites: `robomotion sharepoint365 sp_list_sites --client-id <id>`
4. Get list items: `robomotion sharepoint365 sp_get_list_items --client-id <id> --site-id <site> --list-id <list>`
5. Disconnect: `robomotion sharepoint365 sp_disconnect --client-id <id>`

## Commands Reference
- `robomotion sharepoint365 sharepoint_connect`
  Establishes a connection to SharePoint 365 and returns a connection ID for use in other nodes
- `robomotion sharepoint365 sharepoint_disconnect --connection-id`
  Closes a SharePoint connection and releases resources
- `robomotion sharepoint365 sharepoint_list_sites --connection-id --search-query`
  Lists SharePoint sites accessible to the authenticated user
- `robomotion sharepoint365 sharepoint_get_site --connection-id --site-url`
  Retrieves information about a specific SharePoint site
- `robomotion sharepoint365 sharepoint_list_lists --connection-id --site-id`
  Lists all lists in a SharePoint site
- `robomotion sharepoint365 sharepoint_get_list --connection-id --site-id --list-id [--include-columns]`
  Retrieves information about a specific SharePoint list including columns
- `robomotion sharepoint365 sharepoint_create_list --connection-id --site-id --display-name --description [--template]`
  Creates a new list in a SharePoint site
- `robomotion sharepoint365 sharepoint_list_items --connection-id --site-id --list-id --filter --top [--expand-fields]`
  Lists items in a SharePoint list
- `robomotion sharepoint365 sharepoint_get_item --connection-id --site-id --list-id --item-id [--expand-fields]`
  Retrieves a specific item from a SharePoint list
- `robomotion sharepoint365 sharepoint_create_item --connection-id --site-id --list-id --fields`
  Creates a new item in a SharePoint list
- `robomotion sharepoint365 sharepoint_update_item --connection-id --site-id --list-id --item-id --fields`
  Updates an existing item in a SharePoint list
- `robomotion sharepoint365 sharepoint_delete_item --connection-id --site-id --list-id --item-id`
  Deletes an item from a SharePoint list
- `robomotion sharepoint365 sharepoint_list_libraries --connection-id --site-url`
  Lists all document libraries in a SharePoint site
- `robomotion sharepoint365 sharepoint_get_library --connection-id --site-url --library-name`
  Retrieves information about a document library
- `robomotion sharepoint365 sharepoint_list_files --connection-id --site-url --library-name --folder-path`
  Lists files and folders in a SharePoint document library
- `robomotion sharepoint365 sharepoint_upload_file --connection-id --site-url --library-name --file-path --local-file-path`
  Uploads a file to a SharePoint document library
- `robomotion sharepoint365 sharepoint_download_file --connection-id --site-url --library-name --file-path --local-file-path`
  Downloads a file from a SharePoint document library
- `robomotion sharepoint365 sharepoint_delete_file --connection-id --site-url --library-name --file-path`
  Deletes a file from a SharePoint document library

## Environment
- ROBOMOTION_API_TOKEN (if vault credentials are needed)
