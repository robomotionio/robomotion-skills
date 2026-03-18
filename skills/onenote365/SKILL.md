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

## Workflow
1. Install: `robomotion install onenote365`
2. Connect: `robomotion onenote365 onenote_connect` → returns a `client-id`
3. List notebooks: `robomotion onenote365 onenote_list_notebooks --client-id <id>`
4. Create page: `robomotion onenote365 onenote_create_page --client-id <id> --section-id <section> --title <title> --content <html>`
5. Disconnect: `robomotion onenote365 onenote_disconnect --client-id <id>`

## Commands Reference
- `robomotion onenote365 list_notebooks`
  Lists all OneNote notebooks for the authenticated user
- `robomotion onenote365 get_notebook --notebook-id`
  Gets a specific OneNote notebook by ID
- `robomotion onenote365 create_notebook --display-name`
  Creates a new OneNote notebook
- `robomotion onenote365 list_sections --notebook-id`
  Lists all sections in a OneNote notebook
- `robomotion onenote365 get_section --section-id`
  Gets a specific OneNote section by ID
- `robomotion onenote365 create_section --notebook-id --display-name`
  Creates a new section in a OneNote notebook
- `robomotion onenote365 list_section_groups --notebook-id`
  Lists all section groups in a OneNote notebook
- `robomotion onenote365 get_section_group --section-group-id`
  Gets a specific OneNote section group by ID
- `robomotion onenote365 create_section_group --notebook-id --display-name`
  Creates a new section group in a OneNote notebook
- `robomotion onenote365 list_pages --section-id`
  Lists all pages in a OneNote section
- `robomotion onenote365 get_page --page-id`
  Gets a specific OneNote page by ID، optionally including its HTML content
- `robomotion onenote365 create_page --section-id --title --html-content`
  Creates a new page in a OneNote section
- `robomotion onenote365 update_page --page-id --html-content [--action]`
  Updates the content of a OneNote page by appending or replacing content
- `robomotion onenote365 delete_page --page-id`
  Deletes a OneNote page
- `robomotion onenote365 search_pages --notebook-id --query`
  Searches for OneNote pages by title

## Environment
- ROBOMOTION_API_TOKEN (if vault credentials are needed)
