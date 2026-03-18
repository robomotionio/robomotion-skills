---
name: "google-drive"
description: "Google Drive — upload, download, list, copy, move, delete, and share files and folders. Supports file search, permission management, and shared drive operations via `robomotion googledrive`. Do NOT use for Dropbox, S3, OneDrive, or local filesystem."
---

# Google Drive

The `robomotion googledrive` CLI connects to Google Drive API for file and folder management. It uploads, downloads, copies, moves, and deletes files; creates folders; searches by name/query; and manages sharing permissions.

## When to use
- Upload or download files between local filesystem and Google Drive
- List, search, copy, move, or delete files and folders
- Create folders and manage file sharing permissions

## Prerequisites
- `robomotion` CLI installed
- Package installed: `robomotion install googledrive`
- Google Drive OAuth2 or Service Account credentials configured via Robomotion vault

## IMPORTANT: Session Mode Required for Multi-Step Operations
Each CLI command runs as a **separate process** — connection IDs from `connect` do NOT persist across calls.
You MUST use `--session` on `connect` and pass `--session-id` to all subsequent commands.

## Workflow
1. Install (once): `robomotion install googledrive`
2. Connect with session:
   ```
   robomotion googledrive connect --session --output json
   # → {"outClientId":"<client-id>","session_id":"<session-id>"}
   ```
3. Use the returned `client-id` and `session-id` in all subsequent commands:
   ```
   robomotion googledrive upload_file --client-id "<client-id>" --file-path <local> --parent-id <folder> --session-id "<session-id>" --output json
   ```
4. Disconnect when done:
   ```
   robomotion googledrive disconnect --client-id "<client-id>" --session-id "<session-id>" --output json
   ```

**Always** append `--output json` to get structured JSON results.

## Commands Reference
- `robomotion googledrive connect --session --output json`
  Connects to Google Drive using OAuth2 or Service Account credentials
- `robomotion googledrive list_folder --drive-id --folder-id --output json`
  Lists all files and folders within a specified folder
- `robomotion googledrive upload_file --drive-id --file-path --parent-folder-id --output json`
  Uploads a local file to Google Drive
- `robomotion googledrive download_file --drive-id --file-id --file-path [--pattern] --output json`
  Downloads a file from Google Drive to local storage
- `robomotion googledrive delete_file --drive-id --file-id --output json`
  Permanently deletes a file or folder from Google Drive
- `robomotion googledrive create_folder --drive-id --folder-name [--parent-folder-id] --output json`
  Creates a new folder in Google Drive
- `robomotion googledrive create_file_permission --drive-id --file-id --role --type --email-address [--email-message] --output json`
  Creates a permission for a file or folder in Google Drive
- `robomotion googledrive delete_file_permission --drive-id --file-id --permission --output json`
  Removes a permission from a file or folder in Google Drive
- `robomotion googledrive list_file_permissions --drive-id --file-id --output json`
  Lists all permissions for a file or folder
- `robomotion googledrive search --drive-id --query --output json`
  Searches for files in Google Drive using a query string
- `robomotion googledrive copy_file --drive-id --file-id [--file-name] [--mime-type] [--parent-folder-id] --output json`
  Creates a copy of a file in Google Drive
- `robomotion googledrive export_file --drive-id --file-id --file-path [--mime-type] --output json`
  Exports a Google Workspace document to a specified format
- `robomotion googledrive disconnect --drive-id --session-id "<session-id>" --output json`
  Closes the Google Drive connection and releases resources
- `robomotion googledrive move_file --drive-id --file-id --from-parent-id --to-parent-id --output json`
  Moves a file or folder to a different location in Google Drive

## Environment
- ROBOMOTION_API_TOKEN (if vault credentials are needed)
