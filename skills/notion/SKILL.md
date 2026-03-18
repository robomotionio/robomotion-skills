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

## Workflow
1. Install: `robomotion install notion`
2. Connect: `robomotion notion connect` → returns a `client-id`
3. Search: `robomotion notion search --client-id <id> --query <text>`
4. Create page: `robomotion notion create_page --client-id <id> --parent-id <id> --title <title>`
5. Disconnect: `robomotion notion disconnect --client-id <id>`

## Commands Reference
- `robomotion notion notion_connect`
  Connects to Notion API and returns a client ID for subsequent operations
- `robomotion notion notion_disconnect --client-id`
  Closes the Notion connection and releases resources
- `robomotion notion notion_create_page --client-id --parent-id --title --content [--icon-emoji] [--parent-type]`
  Creates a new page in Notion under a parent page or database
- `robomotion notion notion_get_page --client-id --page-id`
  Retrieves a page from Notion by its ID
- `robomotion notion notion_update_page --client-id --page-id --new-title --properties --icon-emoji`
  Updates a page's properties in Notion
- `robomotion notion notion_archive_page --client-id --page-id`
  Archives (soft deletes) a page in Notion. Can also restore archived pages.
- `robomotion notion notion_get_database --client-id --database-id`
  Retrieves a database schema from Notion by its ID
- `robomotion notion notion_query_database --client-id --database-id --filter --sorts [--100] [--start-cursor]`
  Queries a Notion database with optional filters and sorting
- `robomotion notion notion_append_blocks --client-id --parent-block/page-id --content`
  Appends content blocks to a page or existing block in Notion
- `robomotion notion notion_get_block_children --client-id --block/page-id [--100] [--start-cursor]`
  Retrieves child blocks of a page or block in Notion
- `robomotion notion notion_search --client-id --query [--search-type] [--sort-direction] [--sort-by] [--100] [--start-cursor]`
  Searches for pages and databases in Notion by title

## Environment
- ROBOMOTION_API_TOKEN (if vault credentials are needed)
