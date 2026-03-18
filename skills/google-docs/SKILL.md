---
name: "google-docs"
description: "Google Docs — create, read, and update documents in Google Docs. Supports document creation, content reading, and text operations via `robomotion googledocs`. Do NOT use for Microsoft Word, local files, or PDF processing."
---

# Google Docs

The `robomotion googledocs` CLI connects to Google Docs API for document management. It creates new documents, reads document content, and updates existing documents in Google Drive.

## When to use
- Create new Google Docs documents
- Read content from existing Google Docs
- Update and modify document content

## Prerequisites
- `robomotion` CLI installed
- Package installed: `robomotion install googledocs`
- Google Docs OAuth2 or Service Account credentials configured via Robomotion vault

## IMPORTANT: Session Mode Required for Multi-Step Operations
Each CLI command runs as a **separate process** — connection IDs from `connect` do NOT persist across calls.
You MUST use `--session` on `connect` and pass `--session-id` to all subsequent commands.

## Workflow
1. Install (once): `robomotion install googledocs`
2. Connect with session:
   ```
   robomotion googledocs connect --session --output json
   # → {"outClientId":"<client-id>","session_id":"<session-id>"}
   ```
3. Use the returned `client-id` and `session-id` in all subsequent commands:
   ```
   robomotion googledocs create_document --client-id "<client-id>" --title <title> --session-id "<session-id>" --output json
   ```
4. Disconnect when done:
   ```
   robomotion googledocs disconnect --client-id "<client-id>" --session-id "<session-id>" --output json
   ```

**Always** append `--output json` to get structured JSON results.

## Commands Reference
- `robomotion googledocs create_document --title [--sharewith] --output json`
  Creates a new Google Doc with the specified title and optional sharing settings
- `robomotion googledocs open_document --url --output json`
  Opens an existing Google Doc by its URL for reading and editing
- `robomotion googledocs delete_range --document-id --start-index --end-index --output json`
  Deletes content in a Google Doc between specified start and end indices
- `robomotion googledocs insert_text --document-id --text --font-size --times-new-roman [--align] --output json`
  Inserts text at the end of a Google Doc with formatting options
- `robomotion googledocs read_document --document-id --output json`
  Reads the full text content of a Google Doc
- `robomotion googledocs insert_link --document-id --link --link-text --font-size --times-new-roman [--align] [--0-067] [--0-333] [--0-800] --output json`
  Inserts a clickable hyperlink at the end of a Google Doc with customizable text and styling
- `robomotion googledocs replace_text --document-id --text-to-replace --replacement [--replacement-type] --output json`
  Replaces all occurrences of a text string in a Google Doc with new text or a link
- `robomotion googledocs add_image --document-id --image-url [--height] [--width] --output json`
  Inserts an image from a URL into a Google Doc with optional size settings
- `robomotion googledocs add_header --document-id --text --font-size --times-new-roman [--align] --output json`
  Adds or replaces the header text in a Google Doc with formatting options
- `robomotion googledocs add_footer --document-id --text --font-size --times-new-roman [--align] --output json`
  Adds or replaces the footer text in a Google Doc with formatting options
- `robomotion googledocs add_heading --document-id --text --font-size --times-new-roman [--heading] [--align] --output json`
  Adds a styled heading (title٫ subtitle٫ or H1-H6) to a Google Doc
- `robomotion googledocs pdf_export --document-id --file-path --output json`
  Exports a Google Doc as a PDF file to the local filesystem

## Environment
- ROBOMOTION_API_TOKEN (if vault credentials are needed)
