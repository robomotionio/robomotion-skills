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

## Workflow
1. Install: `robomotion install onedrive365`
2. Connect: `robomotion onedrive365 onedrive_connect` → returns a `client-id`
3. Upload: `robomotion onedrive365 onedrive_upload_file --client-id <id> --local-path <file> --remote-path <dest>`
4. List: `robomotion onedrive365 onedrive_list_files --client-id <id> --path <folder>`
5. Disconnect: `robomotion onedrive365 onedrive_disconnect --client-id <id>`

## Commands Reference
- `robomotion onedrive365 list_onedrive_files --folder-path`
  Lists files in a OneDrive folder
- `robomotion onedrive365 get_onedrive_stats --file-path`
  Gets metadata for a file or folder in OneDrive
- `robomotion onedrive365 download_onedrive_file --remote-path --local-path`
  Downloads a file from OneDrive to a local path
- `robomotion onedrive365 upload_onedrive_file --local-path --remote-path`
  Uploads a local file to OneDrive
- `robomotion onedrive365 delete_onedrive_file --file-path`
  Deletes a file from OneDrive
- `robomotion onedrive365 copy_onedrive_file --source-path --destination-path`
  Copies a file to a new location in OneDrive
- `robomotion onedrive365 move_onedrive_file --source-path --destination-path`
  Moves a file to a new location in OneDrive
- `robomotion onedrive365 search_onedrive_files --search-query`
  Searches for files and folders in OneDrive
- `robomotion onedrive365 list_onedrive_folders --folder-path`
  Lists folders in a OneDrive folder
- `robomotion onedrive365 create_onedrive_folder --folder-path`
  Creates a new folder in OneDrive
- `robomotion onedrive365 delete_onedrive_folder --folder-path`
  Deletes a folder from OneDrive
- `robomotion onedrive365 create_onedrive_share_link --file-path [--link-type] [--scope] [--expiration]`
  Creates a shareable link for a file or folder in OneDrive
- `robomotion onedrive365 get_onedrive_share_links --file-path`
  Gets existing share links for a file or folder in OneDrive
- `robomotion onedrive365 delete_onedrive_share_link --file-path --permission-id`
  Deletes a share link from a file or folder in OneDrive

## Environment
- ROBOMOTION_API_TOKEN (if vault credentials are needed)
