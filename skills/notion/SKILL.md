---
name: "notion"
description: "Notion — create, read, update, and search pages and databases. Supports rich content blocks, database queries, and page management via `robomotion notion`. Do NOT use for Fibery, Confluence, Google Docs, or other wiki/productivity tools."
---

# Notion

The `robomotion notion` CLI connects to Notion for page and database management. It creates and updates pages with rich content blocks, queries databases with filters and sorts, and searches across the workspace.

## When to use
- Create, read, or update Notion pages with content blocks
- Query and filter Notion databases
- Search pages and databases across the workspace

## Prerequisites
- `robomotion` CLI installed
- Package installed: `robomotion install notion`
- Notion integration token configured via Robomotion vault

## IMPORTANT: Session Mode Required for Multi-Step Operations
Each CLI command runs as a **separate process** — connection IDs from `connect` do NOT persist across calls.
You MUST use `--session` on `connect` and pass `--session-id` to all subsequent commands.

## Workflow
1. Install (once): `robomotion install notion`
2. Connect with session:
   ```
   robomotion notion connect --session --output json
   # → {"outClientId":"<client-id>","session_id":"<session-id>"}
   ```
3. Use the returned `client-id` and `session-id` in all subsequent commands:
   ```
   robomotion notion search --client-id "<client-id>" --query <text> --session-id "<session-id>" --output json
   ```
4. Disconnect when done:
   ```
   robomotion notion disconnect --client-id "<client-id>" --session-id "<session-id>" --output json
   ```

**Always** append `--output json` to get structured JSON results.

## Commands Reference
- `robomotion notion notion_connect --session --output json`
  Connects to Notion API and returns a client ID for subsequent operations
- `robomotion notion notion_disconnect --client-id --session-id "<session-id>" --output json`
  Closes the Notion connection and releases resources
- `robomotion notion notion_create_page --client-id --parent-id --title --content [--icon-emoji] [--parent-type] --session-id "<session-id>" --output json`
  Creates a new page in Notion under a parent page or database
- `robomotion notion notion_get_page --client-id --page-id --session-id "<session-id>" --output json`
  Retrieves a page from Notion by its ID
- `robomotion notion notion_update_page --client-id --page-id --new-title --properties --icon-emoji --session-id "<session-id>" --output json`
  Updates a page's properties in Notion
- `robomotion notion notion_archive_page --client-id --page-id --session-id "<session-id>" --output json`
  Archives (soft deletes) a page in Notion. Can also restore archived pages.
- `robomotion notion notion_get_database --client-id --database-id --session-id "<session-id>" --output json`
  Retrieves a database schema from Notion by its ID
- `robomotion notion notion_query_database --client-id --database-id --filter --sorts [--100] [--start-cursor] --session-id "<session-id>" --output json`
  Queries a Notion database with optional filters and sorting
- `robomotion notion notion_append_blocks --client-id --parent-block/page-id --content --session-id "<session-id>" --output json`
  Appends content blocks to a page or existing block in Notion
- `robomotion notion notion_get_block_children --client-id --block/page-id [--100] [--start-cursor] --session-id "<session-id>" --output json`
  Retrieves child blocks of a page or block in Notion
- `robomotion notion notion_search --client-id --query [--search-type] [--sort-direction] [--sort-by] [--100] [--start-cursor] --session-id "<session-id>" --output json`
  Searches for pages and databases in Notion by title

## Environment
- ROBOMOTION_API_TOKEN (if vault credentials are needed)
