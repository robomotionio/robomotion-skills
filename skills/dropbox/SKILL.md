---
name: "dropbox"
description: "Dropbox cloud storage — upload, download, copy, move, delete, search, and share files. Supports folder management, file metadata, and shareable link creation via `robomotion dropbox`. Do NOT use for Google Drive, S3, OneDrive, or local filesystem operations."
---

# Dropbox

The `robomotion dropbox` CLI manages files and folders in Dropbox. It supports uploading, downloading, copying, moving, deleting files; creating folders; searching by name/content; getting file metadata; and generating shareable links.

## When to use
- Upload or download files between local filesystem and Dropbox
- Copy, move, or delete files and folders in Dropbox
- Search for files by name or content
- Create shareable links and get file metadata/stats

## Prerequisites
- `robomotion` CLI installed
- Package installed: `robomotion install dropbox`
- Dropbox access token configured via Robomotion vault

## Workflow
1. Install: `robomotion install dropbox`
2. Connect: `robomotion dropbox connect` → returns a `client-id`
3. Upload: `robomotion dropbox upload_file --client-id <id> --file-path <local> --dropbox-path <remote>`
4. List: `robomotion dropbox list_files --client-id <id> --dropbox-path <folder>`
5. Disconnect: `robomotion dropbox disconnect --client-id <id>`

## Commands Reference
- `robomotion dropbox connect`
  Connect to Dropbox using an access token and return a client ID for subsequent operations
- `robomotion dropbox copy_file --client-id --source-path --destination-path`
  Copy a file or folder from one location to another in Dropbox
- `robomotion dropbox create_folder --client-id --dropbox-path`
  Create a new folder at the specified path in Dropbox
- `robomotion dropbox delete_file --client-id --dropbox-path`
  Delete a file or folder at the specified path in Dropbox
- `robomotion dropbox disconnect --client-id`
  Disconnect from Dropbox and release the client connection
- `robomotion dropbox download_file --client-id --dropbox-path --local-path`
  Download a file from Dropbox to the local filesystem
- `robomotion dropbox get_shareable_link --client-id --dropbox-path`
  Create a shareable link for a file or folder in Dropbox
- `robomotion dropbox move_file --client-id --source-path --destination-path`
  Move a file or folder from one location to another in Dropbox
- `robomotion dropbox file_stat --client-id --dropbox-path`
  Get metadata and statistics for a file or folder in Dropbox
- `robomotion dropbox list_files --client-id --dropbox-path`
  List all files and folders in a Dropbox directory
- `robomotion dropbox search --client-id --query --path`
  Search for files and folders in Dropbox by name or content
- `robomotion dropbox upload_file --client-id --dropbox-path --file-path`
  Upload a file from the local filesystem to Dropbox

## Environment
- ROBOMOTION_API_TOKEN (if vault credentials are needed)
