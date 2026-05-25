---
name: notion
version: 1.0.0
summary: Read and write Notion pages, databases (data sources), and blocks via the HTTP API and curl.
tags: ["notion", "notes", "database", "productivity"]
---

# Notion

Work with Notion pages, databases, and blocks through Notion's HTTP API using `curl`. One integration token authenticates every call. This port is HTTP-only — it works headlessly in the sandbox and on every platform.

## Capabilities

- Search pages and databases across the workspace
- Read a page's metadata, its Markdown rendering, or its raw block tree
- Create pages from Markdown or from typed database properties
- Patch page properties and append blocks
- Create and query databases (data sources)
- Upload files and attach them to pages

## Usage

Every call carries two headers: the auth token and the API version. `Notion-Version: 2025-09-03` is **required** — omit it and the API rejects the request.

```sh
# Search
curl -s -X POST "https://api.notion.com/v1/search" \
  -H "Authorization: Bearer $NOTION_API_KEY" \
  -H "Notion-Version: 2025-09-03" \
  -H "Content-Type: application/json" \
  -d '{"query": "roadmap"}' | python3 -m json.tool

# Read a page as Markdown (best for summarizing — feed straight to the model)
curl -s "https://api.notion.com/v1/pages/PAGE_ID/markdown" \
  -H "Authorization: Bearer $NOTION_API_KEY" \
  -H "Notion-Version: 2025-09-03"

# Read a page's block tree (when you need structure, not prose)
curl -s "https://api.notion.com/v1/blocks/PAGE_ID/children" \
  -H "Authorization: Bearer $NOTION_API_KEY" \
  -H "Notion-Version: 2025-09-03" | python3 -m json.tool

# Create a page from Markdown under a parent page
curl -s -X POST "https://api.notion.com/v1/pages" \
  -H "Authorization: Bearer $NOTION_API_KEY" \
  -H "Notion-Version: 2025-09-03" \
  -H "Content-Type: application/json" \
  -d '{
    "parent": {"page_id": "PARENT_PAGE_ID"},
    "properties": {"title": [{"text": {"content": "Meeting notes"}}]},
    "markdown": "# Agenda\n\n- Q3 roadmap\n- Hiring\n\n## Decisions\n- Ship MVP Friday"
  }' | python3 -m json.tool

# Create a row in a database (typed properties — see Property types below)
curl -s -X POST "https://api.notion.com/v1/pages" \
  -H "Authorization: Bearer $NOTION_API_KEY" \
  -H "Notion-Version: 2025-09-03" \
  -H "Content-Type: application/json" \
  -d '{
    "parent": {"database_id": "DATABASE_ID"},
    "properties": {
      "Name": {"title": [{"text": {"content": "New item"}}]},
      "Status": {"select": {"name": "Todo"}}
    }
  }' | python3 -m json.tool

# Query a database — note: query hits the DATA SOURCE id, not the database id
curl -s -X POST "https://api.notion.com/v1/data_sources/DATA_SOURCE_ID/query" \
  -H "Authorization: Bearer $NOTION_API_KEY" \
  -H "Notion-Version: 2025-09-03" \
  -H "Content-Type: application/json" \
  -d '{
    "filter": {"property": "Status", "select": {"equals": "Active"}},
    "sorts": [{"property": "Date", "direction": "descending"}]
  }' | python3 -m json.tool

# Update page properties
curl -s -X PATCH "https://api.notion.com/v1/pages/PAGE_ID" \
  -H "Authorization: Bearer $NOTION_API_KEY" \
  -H "Notion-Version: 2025-09-03" \
  -H "Content-Type: application/json" \
  -d '{"properties": {"Status": {"select": {"name": "Done"}}}}' | python3 -m json.tool

# Append blocks to a page
curl -s -X PATCH "https://api.notion.com/v1/blocks/PAGE_ID/children" \
  -H "Authorization: Bearer $NOTION_API_KEY" \
  -H "Notion-Version: 2025-09-03" \
  -H "Content-Type: application/json" \
  -d '{"children": [{"object": "block", "type": "paragraph", "paragraph": {"rich_text": [{"text": {"content": "Appended line"}}]}}]}'
```

File upload is a 3-step flow: `POST /v1/file_uploads` to get an `upload_url`, `PUT` the bytes to it, then reference the returned `file_upload_id` in a page/block payload.

For the full block-type catalog (headings, to-dos, callouts, code, images, and how to read text back out of each), see `${SKILL_DIR}/references/block-types.md`.

## Property types

Write shapes for the common database property types:

- **Title:** `{"title": [{"text": {"content": "..."}}]}`
- **Rich text:** `{"rich_text": [{"text": {"content": "..."}}]}`
- **Select:** `{"select": {"name": "Option"}}` · **Multi-select:** `{"multi_select": [{"name": "A"}, {"name": "B"}]}`
- **Date:** `{"date": {"start": "2026-01-15", "end": "2026-01-16"}}`
- **Checkbox:** `{"checkbox": true}` · **Number:** `{"number": 42}`
- **URL/Email:** `{"url": "https://..."}` / `{"email": "user@example.com"}`
- **Relation:** `{"relation": [{"id": "PAGE_ID"}]}`

## When to use

- "Summarize the contents of this Notion page"
- "Add a row to the Tasks database with status Todo"
- "Find every page mentioning 'Q3 planning' and list their titles"
- "Append a decision log entry to the meeting notes page"

## When NOT to use

- Setting database *view* filters/sorts — the API can't, that's UI-only
- Bulk migrations of thousands of pages — paginate and batch, expect rate limiting
- Anything outside Notion (use `linear`/`github-issues` for trackers, `airtable` for spreadsheet-style data)

## Operating notes

- **Share the target with the integration first.** A page the integration hasn't been connected to returns `404` even though it exists — in Notion, open the page menu → `Connect to` → the integration. This is the single most common failure.
- **Databases are "data sources" in API 2025-09-03.** A database has two IDs: use `database_id` when *creating* pages (`parent: {"database_id": ...}`) and `data_source_id` when *querying* (`POST /v1/data_sources/{id}/query`). Search returns databases as `"object": "data_source"`.
- **Always pass `-s` to curl** to suppress progress noise, and pipe through `python3 -m json.tool` (always present) or `jq` for readable output.
- IDs are UUIDs; dashes are optional.
- Rate limit is ~3 requests/second average — coalesce calls and paginate rather than re-fetching.
- This port covers the HTTP API only. Notion's `ntn` CLI and hosted Workers are out of scope here; everything above works without them.

## Attribution

Adapted from the [Nous Hermes Agent](https://github.com/NousResearch/hermes-agent) `notion` skill (MIT). The bundled `references/block-types.md` was contributed by [@dogiladeveloper](https://github.com/dogiladeveloper).
