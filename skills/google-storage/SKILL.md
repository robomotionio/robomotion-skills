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

## Workflow
1. Install: `robomotion install googlestorage`
2. Connect: `robomotion googlestorage google_storage_connect` → returns a `client-id`
3. Upload: `robomotion googlestorage google_storage_upload_object --client-id <id> --bucket-name <bucket> --file-path <local>`
4. List: `robomotion googlestorage google_storage_list_objects --client-id <id> --bucket-name <bucket>`
5. Disconnect: `robomotion googlestorage google_storage_disconnect --client-id <id>`

## Commands Reference
- `robomotion googlestorage connect_storage`
  Connect to Google Cloud Storage and create a client session
- `robomotion googlestorage read_object --gcs-id --bucket-name --object-name`
  Read the contents of an object from a Google Cloud Storage bucket
- `robomotion googlestorage upload_file --gcs-id --bucket-name --file-path [--file-name] [--30]`
  Upload a file to a Google Cloud Storage bucket
- `robomotion googlestorage delete_object --gcs-id --bucket-name --object-name`
  Delete an object from a Google Cloud Storage bucket
- `robomotion googlestorage list_bucket_objects --gcs-id --bucket-name`
  List all objects in a Google Cloud Storage bucket
- `robomotion googlestorage create_bucket --gcs-id --project-id --bucket-name [--labels] [--access-control-type] [--storage-class]`
  Create a new bucket in Google Cloud Storage
- `robomotion googlestorage delete_bucket --gcs-id --bucket-name`
  Delete a bucket from Google Cloud Storage
- `robomotion googlestorage update_bucket --gcs-id --bucket-name --label-name --label-value [--storage-class] [--enable-versioning]`
  Update attributes of a Google Cloud Storage bucket
- `robomotion googlestorage list_buckets --gcs-id --project-id`
  List all buckets in a Google Cloud project
- `robomotion googlestorage get_bucket --gcs-id --bucket-name`
  Get details and attributes of a Google Cloud Storage bucket

## Environment
- ROBOMOTION_API_TOKEN (if vault credentials are needed)
