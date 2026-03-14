---
name: "google-drive"
description: "Use when the user wants to call the Robomotion Google Drive package to upload, download, list, or manage files in Google Drive via the `robomotion googledrive` CLI. Do NOT use for S3, Dropbox, or local file operations."
---

# Google Drive Skill

## When to use
- Upload or download files from Google Drive
- List files and folders in Google Drive
- Share files or manage permissions
- Create folders in Google Drive

## Prerequisites
- `robomotion` CLI installed
- Package installed: `robomotion install googledrive`
- Credentials configured via Robomotion vault or environment variables

## Workflow
1. Install the package: `robomotion install googledrive`
2. Run commands: `robomotion googledrive <command> [flags]`

## Commands Reference
- `robomotion googledrive connect`
  Connects to Google Drive using OAuth2 or Service Account credentials
- `robomotion googledrive list_folder --drive-id --folder-id`
  Lists all files and folders within a specified folder
- `robomotion googledrive upload_file --drive-id --file-path --parent-folder-id`
  Uploads a local file to Google Drive
- `robomotion googledrive download_file --drive-id --file-id --file-path [--pattern]`
  Downloads a file from Google Drive to local storage
- `robomotion googledrive delete_file --drive-id --file-id`
  Permanently deletes a file or folder from Google Drive
- `robomotion googledrive create_folder --drive-id --folder-name [--parent-folder-id]`
  Creates a new folder in Google Drive
- `robomotion googledrive create_file_permission --drive-id --file-id --role --type --email-address [--email-message]`
  Creates a permission for a file or folder in Google Drive
- `robomotion googledrive delete_file_permission --drive-id --file-id --permission`
  Removes a permission from a file or folder in Google Drive
- `robomotion googledrive list_file_permissions --drive-id --file-id`
  Lists all permissions for a file or folder
- `robomotion googledrive search --drive-id --query`
  Searches for files in Google Drive using a query string
- `robomotion googledrive copy_file --drive-id --file-id [--file-name] [--mime-type] [--parent-folder-id]`
  Creates a copy of a file in Google Drive
- `robomotion googledrive export_file --drive-id --file-id --file-path [--mime-type]`
  Exports a Google Workspace document to a specified format
- `robomotion googledrive disconnect --drive-id`
  Closes the Google Drive connection and releases resources
- `robomotion googledrive move_file --drive-id --file-id --from-parent-id --to-parent-id`
  Moves a file or folder to a different location in Google Drive

## Environment
- ROBOMOTION_API_TOKEN (if vault credentials are needed)
