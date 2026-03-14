---
name: "s3-storage"
description: "Use when the user wants to call the Robomotion Amazon S3 package to upload, download, list, or manage files in S3 buckets via the `robomotion amazons3` CLI. Do NOT use for Google Drive, Dropbox, or local file operations."
---

# S3 Storage Skill

## When to use
- Upload files to S3 buckets
- Download files from S3
- List objects in an S3 bucket
- Delete or manage S3 objects

## Prerequisites
- `robomotion` CLI installed
- Package installed: `robomotion install amazons3`
- Credentials configured via Robomotion vault or environment variables

## Workflow
1. Install the package: `robomotion install amazons3`
2. Run commands: `robomotion amazons3 <command> [flags]`

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
