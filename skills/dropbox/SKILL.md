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

## IMPORTANT: Session Mode Required for Multi-Step Operations
Each CLI command runs as a **separate process** — connection IDs from `connect` do NOT persist across calls.
You MUST use `--session` on `connect` and pass `--session-id` to all subsequent commands.

## Workflow
1. Install (once): `robomotion install dropbox`
2. Connect with session:
   ```
   robomotion dropbox connect --session --output json
   # → {"outClientId":"<client-id>","session_id":"<session-id>"}
   ```
3. Use the returned `client-id` and `session-id` in all subsequent commands:
   ```
   robomotion dropbox upload_file --client-id "<client-id>" --file-path <local> --dropbox-path <remote> --session-id "<session-id>" --output json
   ```
4. Disconnect when done:
   ```
   robomotion dropbox disconnect --client-id "<client-id>" --session-id "<session-id>" --output json
   ```

**Always** append `--output json` to get structured JSON results.

## Commands Reference
- `robomotion dropbox connect --session --output json`
  Connect to Dropbox using an access token and return a client ID for subsequent operations
- `robomotion dropbox copy_file --client-id --source-path --destination-path --session-id "<session-id>" --output json`
  Copy a file or folder from one location to another in Dropbox
- `robomotion dropbox create_folder --client-id --dropbox-path --session-id "<session-id>" --output json`
  Create a new folder at the specified path in Dropbox
- `robomotion dropbox delete_file --client-id --dropbox-path --session-id "<session-id>" --output json`
  Delete a file or folder at the specified path in Dropbox
- `robomotion dropbox disconnect --client-id --session-id "<session-id>" --output json`
  Disconnect from Dropbox and release the client connection
- `robomotion dropbox download_file --client-id --dropbox-path --local-path --session-id "<session-id>" --output json`
  Download a file from Dropbox to the local filesystem
- `robomotion dropbox get_shareable_link --client-id --dropbox-path --session-id "<session-id>" --output json`
  Create a shareable link for a file or folder in Dropbox
- `robomotion dropbox move_file --client-id --source-path --destination-path --session-id "<session-id>" --output json`
  Move a file or folder from one location to another in Dropbox
- `robomotion dropbox file_stat --client-id --dropbox-path --session-id "<session-id>" --output json`
  Get metadata and statistics for a file or folder in Dropbox
- `robomotion dropbox list_files --client-id --dropbox-path --session-id "<session-id>" --output json`
  List all files and folders in a Dropbox directory
- `robomotion dropbox search --client-id --query --path --session-id "<session-id>" --output json`
  Search for files and folders in Dropbox by name or content
- `robomotion dropbox upload_file --client-id --dropbox-path --file-path --session-id "<session-id>" --output json`
  Upload a file from the local filesystem to Dropbox

## Environment
- ROBOMOTION_API_TOKEN (if vault credentials are needed)
