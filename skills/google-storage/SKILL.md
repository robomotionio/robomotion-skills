---
name: "google-storage"
description: "Google Cloud Storage — upload, download, list, delete, copy, and move objects in GCS buckets. Supports bucket management, signed URLs, and metadata operations via `robomotion googlestorage`. Do NOT use for S3, Dropbox, Google Drive, or local filesystem."
---

# Google Cloud Storage

The `robomotion googlestorage` CLI connects to Google Cloud Storage for object and bucket management. It uploads, downloads, lists, deletes, copies, and moves objects; creates and manages buckets; generates signed URLs; and reads object metadata.

## When to use
- Upload or download files between local filesystem and GCS buckets
- List, copy, move, or delete objects in buckets
- Create or delete GCS buckets
- Generate signed URLs for temporary access

## Prerequisites
- `robomotion` CLI installed
- Package installed: `robomotion install googlestorage`
- Google Cloud service account credentials configured via Robomotion vault

## IMPORTANT: Session Mode Required for Multi-Step Operations
Each CLI command runs as a **separate process** — connection IDs from `connect` do NOT persist across calls.
You MUST use `--session` on `connect` and pass `--session-id` to all subsequent commands.

## Workflow
1. Install (once): `robomotion install googlestorage`
2. Connect with session:
   ```
   robomotion googlestorage google_storage_connect --session --output json
   # → {"outClientId":"<client-id>","session_id":"<session-id>"}
   ```
3. Use the returned `client-id` and `session-id` in all subsequent commands:
   ```
   robomotion googlestorage google_storage_upload_object --client-id "<client-id>" --bucket-name <bucket> --file-path <local> --session-id "<session-id>" --output json
   ```
4. Disconnect when done:
   ```
   robomotion googlestorage google_storage_disconnect --client-id "<client-id>" --session-id "<session-id>" --output json
   ```

**Always** append `--output json` to get structured JSON results.

## Commands Reference
- `robomotion googlestorage connect_storage --session --output json`
  Connect to Google Cloud Storage and create a client session
- `robomotion googlestorage read_object --gcs-id --bucket-name --object-name --output json`
  Read the contents of an object from a Google Cloud Storage bucket
- `robomotion googlestorage upload_file --gcs-id --bucket-name --file-path [--file-name] [--30] --output json`
  Upload a file to a Google Cloud Storage bucket
- `robomotion googlestorage delete_object --gcs-id --bucket-name --object-name --output json`
  Delete an object from a Google Cloud Storage bucket
- `robomotion googlestorage list_bucket_objects --gcs-id --bucket-name --output json`
  List all objects in a Google Cloud Storage bucket
- `robomotion googlestorage create_bucket --gcs-id --project-id --bucket-name [--labels] [--access-control-type] [--storage-class] --output json`
  Create a new bucket in Google Cloud Storage
- `robomotion googlestorage delete_bucket --gcs-id --bucket-name --output json`
  Delete a bucket from Google Cloud Storage
- `robomotion googlestorage update_bucket --gcs-id --bucket-name --label-name --label-value [--storage-class] [--enable-versioning] --output json`
  Update attributes of a Google Cloud Storage bucket
- `robomotion googlestorage list_buckets --gcs-id --project-id --output json`
  List all buckets in a Google Cloud project
- `robomotion googlestorage get_bucket --gcs-id --bucket-name --output json`
  Get details and attributes of a Google Cloud Storage bucket

## Environment
- ROBOMOTION_API_TOKEN (if vault credentials are needed)
