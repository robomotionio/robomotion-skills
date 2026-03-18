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

## Workflow
1. Install: `robomotion install googledocs`
2. Connect: `robomotion googledocs connect` → returns a `client-id`
3. Create doc: `robomotion googledocs create_document --client-id <id> --title <title>`
4. Read doc: `robomotion googledocs get_document --client-id <id> --document-id <doc>`
5. Disconnect: `robomotion googledocs disconnect --client-id <id>`

## Commands Reference
- `robomotion googledocs create_document --title [--sharewith]`
  Creates a new Google Doc with the specified title and optional sharing settings
- `robomotion googledocs open_document --url`
  Opens an existing Google Doc by its URL for reading and editing
- `robomotion googledocs delete_range --document-id --start-index --end-index`
  Deletes content in a Google Doc between specified start and end indices
- `robomotion googledocs insert_text --document-id --text --font-size --times-new-roman [--align]`
  Inserts text at the end of a Google Doc with formatting options
- `robomotion googledocs read_document --document-id`
  Reads the full text content of a Google Doc
- `robomotion googledocs insert_link --document-id --link --link-text --font-size --times-new-roman [--align] [--0-067] [--0-333] [--0-800]`
  Inserts a clickable hyperlink at the end of a Google Doc with customizable text and styling
- `robomotion googledocs replace_text --document-id --text-to-replace --replacement [--replacement-type]`
  Replaces all occurrences of a text string in a Google Doc with new text or a link
- `robomotion googledocs add_image --document-id --image-url [--height] [--width]`
  Inserts an image from a URL into a Google Doc with optional size settings
- `robomotion googledocs add_header --document-id --text --font-size --times-new-roman [--align]`
  Adds or replaces the header text in a Google Doc with formatting options
- `robomotion googledocs add_footer --document-id --text --font-size --times-new-roman [--align]`
  Adds or replaces the footer text in a Google Doc with formatting options
- `robomotion googledocs add_heading --document-id --text --font-size --times-new-roman [--heading] [--align]`
  Adds a styled heading (title٫ subtitle٫ or H1-H6) to a Google Doc
- `robomotion googledocs pdf_export --document-id --file-path`
  Exports a Google Doc as a PDF file to the local filesystem

## Environment
- ROBOMOTION_API_TOKEN (if vault credentials are needed)
