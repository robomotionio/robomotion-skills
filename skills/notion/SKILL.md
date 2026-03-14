---
name: "notion"
description: "Use when the user wants to call the Robomotion Notion package to create, read, or search Notion pages and databases via the `robomotion notion` CLI. Do NOT use for Google Docs, Confluence, or local files."
---

# Notion Skill

## When to use
- Create or update Notion pages
- Query Notion databases
- Search Notion workspace content
- Add blocks or content to Notion pages

## Prerequisites
- `robomotion` CLI installed
- Package installed: `robomotion install notion`
- Credentials configured via Robomotion vault or environment variables

## Workflow
1. Install the package: `robomotion install notion`
2. Run commands: `robomotion notion <command> [flags]`

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
