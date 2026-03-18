---
name: "nextcloud"
description: "NextCloud — manage files, folders, sharing, and users on self-hosted NextCloud instances. Supports upload, download, file sharing, and user administration via `robomotion nextcloud`. Do NOT use for Dropbox, Google Drive, OneDrive, or other cloud storage."
---

# NextCloud

The `robomotion nextcloud` CLI connects to NextCloud (self-hosted cloud storage) for file management, sharing, and administration. It uploads, downloads, lists, and deletes files; creates and manages shares with permissions; and administers users.

## When to use
- Upload or download files between local filesystem and NextCloud
- List files, create folders, and manage file operations
- Create, list, and manage file/folder shares with permissions
- Administer NextCloud users

## Prerequisites
- `robomotion` CLI installed
- Package installed: `robomotion install nextcloud`
- NextCloud instance URL and credentials configured via Robomotion vault

## Workflow
1. Install: `robomotion install nextcloud`
2. Connect: `robomotion nextcloud nextcloud_connect` → returns a `client-id`
3. Upload: `robomotion nextcloud nextcloud_upload --client-id <id> --local-path <file> --remote-path <dest>`
4. List: `robomotion nextcloud nextcloud_list_files --client-id <id> --path <folder>`
5. Disconnect: `robomotion nextcloud nextcloud_disconnect --client-id <id>`

## Commands Reference
- `robomotion nextcloud upload_file --client-id --local-file-path --remote-path [--120]`
  Uploads a local file to NextCloud
- `robomotion nextcloud download_file --client-id --remote-path --save-to-path [--120]`
  Downloads a file from NextCloud to local disk
- `robomotion nextcloud delete_file --client-id --remote-path`
  Deletes a file or folder from NextCloud
- `robomotion nextcloud copy_file --client-id --from-path --to-path [--overwrite]`
  Copies a file or folder to a new location on NextCloud
- `robomotion nextcloud move_file --client-id --from-path --to-path [--overwrite]`
  Moves or renames a file or folder on NextCloud
- `robomotion nextcloud list_files --client-id --folder-path`
  Lists files and folders in a NextCloud directory
- `robomotion nextcloud create_folder --client-id --folder-path`
  Creates a new folder on NextCloud
- `robomotion nextcloud create_share --client-id --path --share-with [--share-type] [--permissions] [--password]`
  Creates a share link for a file or folder on NextCloud
- `robomotion nextcloud list_shares --client-id --path`
  Lists shares for a path or all shares on NextCloud
- `robomotion nextcloud delete_share --client-id --share-id`
  Deletes a share by its ID on NextCloud
- `robomotion nextcloud create_user --client-id --user-id --password --email [--display-name]`
  Creates a new user on NextCloud
- `robomotion nextcloud get_user --client-id --user-id`
  Gets user details from NextCloud
- `robomotion nextcloud list_users --client-id [--search] [--50] [--0]`
  Lists users on NextCloud

## Environment
- ROBOMOTION_API_TOKEN (if vault credentials are needed)
