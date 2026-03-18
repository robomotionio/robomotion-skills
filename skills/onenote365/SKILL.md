---
name: "onenote365"
description: "Microsoft OneNote 365 — manage notebooks, sections, section groups, and pages via Microsoft Graph API. Supports page creation, content reading, and notebook organization via `robomotion onenote365`. Do NOT use for Notion, Evernote, Google Keep, or other note apps."
---

# Microsoft OneNote 365

The `robomotion onenote365` CLI connects to Microsoft OneNote via the Graph API for notebook management. It lists and manages notebooks, section groups, and sections; creates and reads pages with HTML content; and organizes note hierarchies.

## When to use
- Create pages with HTML content in OneNote sections
- List notebooks, section groups, and sections
- Read page content and manage notebook structure

## Prerequisites
- `robomotion` CLI installed
- Package installed: `robomotion install onenote365`
- Microsoft 365 OAuth2 credentials configured via Robomotion vault

## IMPORTANT: Session Mode Required for Multi-Step Operations
Each CLI command runs as a **separate process** — connection IDs from `connect` do NOT persist across calls.
You MUST use `--session` on `connect` and pass `--session-id` to all subsequent commands.

## Workflow
1. Install (once): `robomotion install onenote365`
2. Connect with session:
   ```
   robomotion onenote365 onenote_connect --session --output json
   # → {"outClientId":"<client-id>","session_id":"<session-id>"}
   ```
3. Use the returned `client-id` and `session-id` in all subsequent commands:
   ```
   robomotion onenote365 onenote_list_notebooks --client-id "<client-id>" --session-id "<session-id>" --output json
   ```
4. Disconnect when done:
   ```
   robomotion onenote365 onenote_disconnect --client-id "<client-id>" --session-id "<session-id>" --output json
   ```

**Always** append `--output json` to get structured JSON results.

## Commands Reference
- `robomotion onenote365 list_notebooks --output json`
  Lists all OneNote notebooks for the authenticated user
- `robomotion onenote365 get_notebook --notebook-id --output json`
  Gets a specific OneNote notebook by ID
- `robomotion onenote365 create_notebook --display-name --output json`
  Creates a new OneNote notebook
- `robomotion onenote365 list_sections --notebook-id --output json`
  Lists all sections in a OneNote notebook
- `robomotion onenote365 get_section --section-id --output json`
  Gets a specific OneNote section by ID
- `robomotion onenote365 create_section --notebook-id --display-name --output json`
  Creates a new section in a OneNote notebook
- `robomotion onenote365 list_section_groups --notebook-id --output json`
  Lists all section groups in a OneNote notebook
- `robomotion onenote365 get_section_group --section-group-id --output json`
  Gets a specific OneNote section group by ID
- `robomotion onenote365 create_section_group --notebook-id --display-name --output json`
  Creates a new section group in a OneNote notebook
- `robomotion onenote365 list_pages --section-id --output json`
  Lists all pages in a OneNote section
- `robomotion onenote365 get_page --page-id --output json`
  Gets a specific OneNote page by ID، optionally including its HTML content
- `robomotion onenote365 create_page --section-id --title --html-content --output json`
  Creates a new page in a OneNote section
- `robomotion onenote365 update_page --page-id --html-content [--action] --output json`
  Updates the content of a OneNote page by appending or replacing content
- `robomotion onenote365 delete_page --page-id --output json`
  Deletes a OneNote page
- `robomotion onenote365 search_pages --notebook-id --query --output json`
  Searches for OneNote pages by title

## Environment
- ROBOMOTION_API_TOKEN (if vault credentials are needed)
