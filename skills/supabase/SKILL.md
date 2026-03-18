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

## IMPORTANT: Session Mode Required for Multi-Step Operations
Each CLI command runs as a **separate process** — connection IDs from `connect` do NOT persist across calls.
You MUST use `--session` on `connect` and pass `--session-id` to all subsequent commands.

## Workflow
1. Install (once): `robomotion install supabase`
2. Connect with session:
   ```
   robomotion supabase supabase_connect --session --output json
   # → {"outClientId":"<client-id>","session_id":"<session-id>"}
   ```
3. Use the returned `client-id` and `session-id` in all subsequent commands:
   ```
   robomotion supabase supabase_select --client-id "<client-id>" --table <table> --columns <cols> --session-id "<session-id>" --output json
   ```
4. Disconnect when done:
   ```
   robomotion supabase supabase_disconnect --client-id "<client-id>" --session-id "<session-id>" --output json
   ```

**Always** append `--output json` to get structured JSON results.

## Commands Reference
- `robomotion supabase supabase_connect --project-url --session --output json`
  Connects to Supabase and returns a client ID for subsequent operations
- `robomotion supabase supabase_disconnect --client-id --session-id "<session-id>" --output json`
  Disconnects from Supabase and releases the client
- `robomotion supabase supabase_insert --client-id --table --data [--project-url] --session-id "<session-id>" --output json`
  Inserts a new row into a Supabase table
- `robomotion supabase supabase_select --client-id --table [--project-url] [--columns] [--filter] [--order-by] [--limit] [--offset] --session-id "<session-id>" --output json`
  Queries rows from a Supabase table
- `robomotion supabase supabase_update --client-id --table --filter --data [--project-url] --session-id "<session-id>" --output json`
  Updates rows in a Supabase table
- `robomotion supabase supabase_delete --client-id --table --filter [--project-url] --session-id "<session-id>" --output json`
  Deletes rows from a Supabase table
- `robomotion supabase supabase_upsert --client-id --table --data [--project-url] [--on-conflict] --session-id "<session-id>" --output json`
  Inserts a row or updates it if it already exists (based on primary key or unique constraint)
- `robomotion supabase supabase_storage_upload --client-id --bucket --path --local-file-path --base-64-data [--project-url] [--content-type] --session-id "<session-id>" --output json`
  Uploads a file to Supabase Storage
- `robomotion supabase supabase_storage_download --client-id --bucket --path --save-to-path [--project-url] --session-id "<session-id>" --output json`
  Downloads a file from Supabase Storage and saves it to disk
- `robomotion supabase supabase_storage_list --client-id --bucket [--project-url] [--prefix] [--limit] [--offset] --session-id "<session-id>" --output json`
  Lists files in a Supabase Storage bucket
- `robomotion supabase supabase_storage_delete --client-id --bucket --file-paths [--project-url] --session-id "<session-id>" --output json`
  Deletes one or more files from Supabase Storage
- `robomotion supabase supabase_rpc --client-id --function-name --parameters [--project-url] --session-id "<session-id>" --output json`
  Calls a PostgreSQL function (stored procedure) in Supabase

## Environment
- ROBOMOTION_API_TOKEN (if vault credentials are needed)
