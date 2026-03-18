---
name: "supabase"
description: "Supabase — query tables, manage storage, and call remote procedures on Supabase projects. Supports database CRUD, file storage, and RPC calls via `robomotion supabase`. Do NOT use for Firebase, direct PostgreSQL, or other BaaS platforms."
---

# Supabase

The `robomotion supabase` CLI connects to Supabase projects for database and storage operations. It queries and modifies table data with filters, manages files in Supabase storage buckets, and calls server-side remote procedure calls (RPCs).

## When to use
- Select, insert, update, or delete rows in Supabase tables with filters
- Upload, download, and manage files in Supabase storage
- Call remote procedure calls (RPCs) on Supabase
- Manage Supabase project connections

## Prerequisites
- `robomotion` CLI installed
- Package installed: `robomotion install supabase`
- Supabase project URL and API key configured via Robomotion vault

## Workflow
1. Install: `robomotion install supabase`
2. Connect: `robomotion supabase supabase_connect` → returns a `client-id`
3. Select: `robomotion supabase supabase_select --client-id <id> --table <table> --columns <cols>`
4. Insert: `robomotion supabase supabase_insert --client-id <id> --table <table> --data <json>`
5. Disconnect: `robomotion supabase supabase_disconnect --client-id <id>`

## Commands Reference
- `robomotion supabase supabase_connect --project-url`
  Connects to Supabase and returns a client ID for subsequent operations
- `robomotion supabase supabase_disconnect --client-id`
  Disconnects from Supabase and releases the client
- `robomotion supabase supabase_insert --client-id --table --data [--project-url]`
  Inserts a new row into a Supabase table
- `robomotion supabase supabase_select --client-id --table [--project-url] [--columns] [--filter] [--order-by] [--limit] [--offset]`
  Queries rows from a Supabase table
- `robomotion supabase supabase_update --client-id --table --filter --data [--project-url]`
  Updates rows in a Supabase table
- `robomotion supabase supabase_delete --client-id --table --filter [--project-url]`
  Deletes rows from a Supabase table
- `robomotion supabase supabase_upsert --client-id --table --data [--project-url] [--on-conflict]`
  Inserts a row or updates it if it already exists (based on primary key or unique constraint)
- `robomotion supabase supabase_storage_upload --client-id --bucket --path --local-file-path --base-64-data [--project-url] [--content-type]`
  Uploads a file to Supabase Storage
- `robomotion supabase supabase_storage_download --client-id --bucket --path --save-to-path [--project-url]`
  Downloads a file from Supabase Storage and saves it to disk
- `robomotion supabase supabase_storage_list --client-id --bucket [--project-url] [--prefix] [--limit] [--offset]`
  Lists files in a Supabase Storage bucket
- `robomotion supabase supabase_storage_delete --client-id --bucket --file-paths [--project-url]`
  Deletes one or more files from Supabase Storage
- `robomotion supabase supabase_rpc --client-id --function-name --parameters [--project-url]`
  Calls a PostgreSQL function (stored procedure) in Supabase

## Environment
- ROBOMOTION_API_TOKEN (if vault credentials are needed)
