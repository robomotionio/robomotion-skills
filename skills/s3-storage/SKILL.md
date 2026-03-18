---
name: "s3-storage"
description: "Amazon S3 — upload, download, list, delete, and manage objects in S3 buckets. Supports bucket management, presigned URLs, and multi-part uploads via `robomotion amazons3`. Do NOT use for Google Cloud Storage, Dropbox, OneDrive, or other storage services."
---

# Amazon S3

The `robomotion amazons3` CLI connects to Amazon S3 for object storage operations. It uploads, downloads, lists, copies, and deletes objects; manages buckets; generates presigned URLs; and handles file operations across S3 buckets.

## When to use
- Upload or download files between local filesystem and S3
- List, copy, or delete objects in S3 buckets
- Create or manage S3 buckets
- Generate presigned URLs for temporary access

## Prerequisites
- `robomotion` CLI installed
- Package installed: `robomotion install amazons3`
- AWS access key and secret key configured via Robomotion vault

## Workflow
1. Install: `robomotion install amazons3`
2. Connect: `robomotion amazons3 connect` → returns a `client-id`
3. Upload: `robomotion amazons3 upload_file --client-id <id> --bucket <bucket> --key <key> --file-path <file>`
4. List: `robomotion amazons3 list_objects --client-id <id> --bucket <bucket>`
5. Disconnect: `robomotion amazons3 disconnect --client-id <id>`

## Commands Reference
- `robomotion amazons3 connect --end-point`
  Connect to Amazon S3 or S3-compatible storage using access credentials
- `robomotion amazons3 disconnect --client-id`
  Closes the S3 client connection and releases resources
- `robomotion amazons3 upload_object --client-id --file-path --bucket-name --object-name [--content-type] [--user-metadata] [--end-point]`
  Upload a local file to an S3 bucket
- `robomotion amazons3 download_object --client-id --bucket-name --object-name --file-path [--end-point]`
  Download an object from S3 to a local file
- `robomotion amazons3 get_object --client-id --bucket-name --object-name [--end-point]`
  Get metadata information about an S3 object
- `robomotion amazons3 delete_object --client-id --bucket-name --object-name [--version-id] [--end-point]`
  Delete an object from an S3 bucket
- `robomotion amazons3 list_objects --client-id --bucket-name [--end-point]`
  List all objects in an S3 bucket
- `robomotion amazons3 list_buckets --client-id [--end-point]`
  List all S3 buckets accessible with the current credentials
- `robomotion amazons3 delete_bucket --client-id --bucket-name [--end-point]`
  Delete an empty S3 bucket
- `robomotion amazons3 create_bucket --client-id --bucket-name [--region] [--end-point]`
  Create a new S3 bucket in the specified region
- `robomotion amazons3 download_presigned_url --client-id --bucket-name --object-name --expiration-second [--file-name] [--end-point]`
  Generate a presigned URL for downloading an S3 object

## Environment
- ROBOMOTION_API_TOKEN (if vault credentials are needed)
