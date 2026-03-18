---
name: "onedrive365"
description: "Microsoft OneDrive 365 — upload, download, list, copy, move, delete, and share files via Microsoft Graph API. Supports folder management, sharing links, and permission control via `robomotion onedrive365`. Do NOT use for Google Drive, Dropbox, S3, or SharePoint document libraries."
---

# Microsoft OneDrive 365

The `robomotion onedrive365` CLI connects to Microsoft OneDrive via the Graph API for file management. It uploads, downloads, lists, copies, moves, and deletes files; creates folders; generates sharing links; and manages file permissions.

## When to use
- Upload or download files between local filesystem and OneDrive
- List, copy, move, or delete files and folders
- Create sharing links and manage file permissions
- Create folders and manage the file hierarchy

## Prerequisites
- `robomotion` CLI installed
- Package installed: `robomotion install onedrive365`
- Microsoft 365 OAuth2 credentials configured via Robomotion vault

## IMPORTANT: Session Mode Required for Multi-Step Operations
Each CLI command runs as a **separate process** — connection IDs from `connect` do NOT persist across calls.
You MUST use `--session` on `connect` and pass `--session-id` to all subsequent commands.

## Workflow
1. Install (once): `robomotion install onedrive365`
2. Connect with session:
   ```
   robomotion onedrive365 onedrive_connect --session --output json
   # → {"outClientId":"<client-id>","session_id":"<session-id>"}
   ```
3. Use the returned `client-id` and `session-id` in all subsequent commands:
   ```
   robomotion onedrive365 onedrive_upload_file --client-id "<client-id>" --local-path <file> --remote-path <dest> --session-id "<session-id>" --output json
   ```
4. Disconnect when done:
   ```
   robomotion onedrive365 onedrive_disconnect --client-id "<client-id>" --session-id "<session-id>" --output json
   ```

**Always** append `--output json` to get structured JSON results.

## Commands Reference
- `robomotion onedrive365 list_onedrive_files --folder-path --output json`
  Lists files in a OneDrive folder
- `robomotion onedrive365 get_onedrive_stats --file-path --output json`
  Gets metadata for a file or folder in OneDrive
- `robomotion onedrive365 download_onedrive_file --remote-path --local-path --output json`
  Downloads a file from OneDrive to a local path
- `robomotion onedrive365 upload_onedrive_file --local-path --remote-path --output json`
  Uploads a local file to OneDrive
- `robomotion onedrive365 delete_onedrive_file --file-path --output json`
  Deletes a file from OneDrive
- `robomotion onedrive365 copy_onedrive_file --source-path --destination-path --output json`
  Copies a file to a new location in OneDrive
- `robomotion onedrive365 move_onedrive_file --source-path --destination-path --output json`
  Moves a file to a new location in OneDrive
- `robomotion onedrive365 search_onedrive_files --search-query --output json`
  Searches for files and folders in OneDrive
- `robomotion onedrive365 list_onedrive_folders --folder-path --output json`
  Lists folders in a OneDrive folder
- `robomotion onedrive365 create_onedrive_folder --folder-path --output json`
  Creates a new folder in OneDrive
- `robomotion onedrive365 delete_onedrive_folder --folder-path --output json`
  Deletes a folder from OneDrive
- `robomotion onedrive365 create_onedrive_share_link --file-path [--link-type] [--scope] [--expiration] --output json`
  Creates a shareable link for a file or folder in OneDrive
- `robomotion onedrive365 get_onedrive_share_links --file-path --output json`
  Gets existing share links for a file or folder in OneDrive
- `robomotion onedrive365 delete_onedrive_share_link --file-path --permission-id --output json`
  Deletes a share link from a file or folder in OneDrive

## Environment
- ROBOMOTION_API_TOKEN (if vault credentials are needed)
