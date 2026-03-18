---
name: "pcloud"
description: "pCloud — upload, download, list, create, delete, and manage files and folders in pCloud storage. Supports file operations and folder management via `robomotion pcloud`. Do NOT use for Dropbox, Google Drive, OneDrive, or other cloud storage."
---

# pCloud

The `robomotion pcloud` CLI connects to pCloud for cloud file storage management. It uploads, downloads, lists, and deletes files; creates and manages folders; and handles file operations on pCloud storage.

## When to use
- Upload or download files between local filesystem and pCloud
- List files and create/delete folders
- Manage files and folder structure in pCloud

## Prerequisites
- `robomotion` CLI installed
- Package installed: `robomotion install pcloud`
- pCloud access token configured via Robomotion vault

## IMPORTANT: Session Mode Required for Multi-Step Operations
Each CLI command runs as a **separate process** — connection IDs from `connect` do NOT persist across calls.
You MUST use `--session` on `connect` and pass `--session-id` to all subsequent commands.

## Workflow
1. Install (once): `robomotion install pcloud`
2. Connect with session:
   ```
   robomotion pcloud pcloud_connect --session --output json
   # → {"outClientId":"<client-id>","session_id":"<session-id>"}
   ```
3. Use the returned `client-id` and `session-id` in all subsequent commands:
   ```
   robomotion pcloud pcloud_upload_file --client-id "<client-id>" --file-path <local> --folder-id <folder> --session-id "<session-id>" --output json
   ```
4. Disconnect when done:
   ```
   robomotion pcloud pcloud_disconnect --client-id "<client-id>" --session-id "<session-id>" --output json
   ```

**Always** append `--output json` to get structured JSON results.

## Commands Reference
- `robomotion pcloud copy_file --client-id --source-path --target-path --session-id "<session-id>" --output json`
  Copy a file from one location to another in pCloud
- `robomotion pcloud create_folder --client-id --path --session-id "<session-id>" --output json`
  Create a new folder at the specified path in pCloud
- `robomotion pcloud delete_file --client-id --path --session-id "<session-id>" --output json`
  Delete a file at the specified path in pCloud
- `robomotion pcloud delete_folder --client-id --path --session-id "<session-id>" --output json`
  Delete a folder and all its contents recursively in pCloud
- `robomotion pcloud login [--region] --output json`
  Login to pCloud using username and password credentials
- `robomotion pcloud rename_file --client-id --source-path --target-path --session-id "<session-id>" --output json`
  Rename or move a file to a new path in pCloud
- `robomotion pcloud rename_folder --client-id --source-path --target-path --session-id "<session-id>" --output json`
  Rename or move a folder to a new path in pCloud
- `robomotion pcloud upload_file --client-id --file-path --folder-id --remote-file-name --session-id "<session-id>" --output json`
  Upload a file from local filesystem to pCloud
- `robomotion pcloud get_public_link --client-id --path [--type] --session-id "<session-id>" --output json`
  Generate a public sharing link for a file or folder in pCloud

## Environment
- ROBOMOTION_API_TOKEN (if vault credentials are needed)
