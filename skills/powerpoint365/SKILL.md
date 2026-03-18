---
name: "powerpoint365"
description: "Microsoft PowerPoint 365 — create presentations from templates, replace text/images, duplicate slides, and export to PDF. Supports AI-powered presentation generation workflows via `robomotion powerpoint365`. Do NOT use for Google Slides, Keynote, or local PowerPoint files."
---

# Microsoft PowerPoint 365

The `robomotion powerpoint365` CLI connects to Microsoft PowerPoint 365 via the Graph API for presentation management. It creates presentations from templates, replaces text and images in slides, duplicates slides, manages slide content, and exports to PDF — ideal for automated presentation generation.

## When to use
- Create presentations from templates in OneDrive/SharePoint
- Replace text and images in slides for automated generation
- Duplicate slides and manage presentation structure
- Export presentations to PDF

## Prerequisites
- `robomotion` CLI installed
- Package installed: `robomotion install powerpoint365`
- Microsoft 365 OAuth2 credentials configured via Robomotion vault

## IMPORTANT: Session Mode Required for Multi-Step Operations
Each CLI command runs as a **separate process** — connection IDs from `connect` do NOT persist across calls.
You MUST use `--session` on `connect` and pass `--session-id` to all subsequent commands.

## Workflow
1. Install (once): `robomotion install powerpoint365`
2. Connect with session:
   ```
   robomotion powerpoint365 pptx_connect --session --output json
   # → {"outClientId":"<client-id>","session_id":"<session-id>"}
   ```
3. Use the returned `client-id` and `session-id` in all subsequent commands:
   ```
   robomotion powerpoint365 pptx_create_from_template --client-id "<client-id>" --template-path <tmpl> --session-id "<session-id>" --output json
   ```
4. Disconnect when done:
   ```
   robomotion powerpoint365 pptx_disconnect --client-id "<client-id>" --session-id "<session-id>" --output json
   ```

**Always** append `--output json` to get structured JSON results.

## Commands Reference
- `robomotion powerpoint365 open_presentation --file-path --output json`
  Opens a PowerPoint 365 presentation and returns a presentation ID for use in other nodes
- `robomotion powerpoint365 close_presentation --presentation-id --output json`
  Closes an open PowerPoint presentation and releases resources
- `robomotion powerpoint365 save_presentation --presentation-id --output json`
  Saves all changes made to the presentation back to OneDrive/SharePoint
- `robomotion powerpoint365 list_presentations --folder-path --output json`
  Lists PowerPoint presentations in a specified folder
- `robomotion powerpoint365 create_presentation --file-path --output json`
  Creates a new PowerPoint presentation at the specified path
- `robomotion powerpoint365 delete_presentation --file-path --output json`
  Deletes a PowerPoint presentation (moves to recycle bin)
- `robomotion powerpoint365 copy_presentation --source-path --destination-path --output json`
  Copies a PowerPoint presentation from source path to destination path
- `robomotion powerpoint365 download_presentation --remote-file-path --local-file-path [--format] --output json`
  Downloads a PowerPoint presentation to local disk in PPTX or PDF format
- `robomotion powerpoint365 upload_presentation --local-file-path --remote-file-path --output json`
  Uploads a local presentation file to OneDrive
- `robomotion powerpoint365 replace_text --presentation-id --replacements --output json`
  Replaces text placeholders across all slides from a key-value map
- `robomotion powerpoint365 replace_image --presentation-id --placeholder-name --new-image --output json`
  Replaces an image in the presentation by its placeholder name or alt text. The new image inherits the original's size and position

## Environment
- ROBOMOTION_API_TOKEN (if vault credentials are needed)
