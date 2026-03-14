---
name: "google-docs"
description: "Use when the user wants to call the Robomotion Google Docs package to create, read, or update Google Docs via the `robomotion googledocs` CLI. Do NOT use for local documents, Google Sheets, or Google Slides."
---

# Google Docs Skill

## When to use
- Create or update Google Docs documents
- Read content from Google Docs
- Insert text, tables, or images into Google Docs

## Prerequisites
- `robomotion` CLI installed
- Package installed: `robomotion install googledocs`
- Credentials configured via Robomotion vault or environment variables

## Workflow
1. Install the package: `robomotion install googledocs`
2. Run commands: `robomotion googledocs <command> [flags]`

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
