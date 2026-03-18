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

## Workflow
1. Install: `robomotion install pcloud`
2. Connect: `robomotion pcloud pcloud_connect` → returns a `client-id`
3. Upload: `robomotion pcloud pcloud_upload_file --client-id <id> --file-path <local> --folder-id <folder>`
4. List: `robomotion pcloud pcloud_list_folder --client-id <id> --folder-id <folder>`
5. Disconnect: `robomotion pcloud pcloud_disconnect --client-id <id>`

## Commands Reference
- `robomotion pcloud copy_file --client-id --source-path --target-path`
  Copy a file from one location to another in pCloud
- `robomotion pcloud create_folder --client-id --path`
  Create a new folder at the specified path in pCloud
- `robomotion pcloud delete_file --client-id --path`
  Delete a file at the specified path in pCloud
- `robomotion pcloud delete_folder --client-id --path`
  Delete a folder and all its contents recursively in pCloud
- `robomotion pcloud login [--region]`
  Login to pCloud using username and password credentials
- `robomotion pcloud rename_file --client-id --source-path --target-path`
  Rename or move a file to a new path in pCloud
- `robomotion pcloud rename_folder --client-id --source-path --target-path`
  Rename or move a folder to a new path in pCloud
- `robomotion pcloud upload_file --client-id --file-path --folder-id --remote-file-name`
  Upload a file from local filesystem to pCloud
- `robomotion pcloud get_public_link --client-id --path [--type]`
  Generate a public sharing link for a file or folder in pCloud

## Environment
- ROBOMOTION_API_TOKEN (if vault credentials are needed)
