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

## Workflow
1. Install: `robomotion install powerpoint365`
2. Connect: `robomotion powerpoint365 pptx_connect` → returns a `client-id`
3. Create from template: `robomotion powerpoint365 pptx_create_from_template --client-id <id> --template-path <tmpl>`
4. Replace text: `robomotion powerpoint365 pptx_replace_text --client-id <id> --presentation-id <id> --find <old> --replace <new>`
5. Disconnect: `robomotion powerpoint365 pptx_disconnect --client-id <id>`

## Commands Reference
- `robomotion powerpoint365 open_presentation --file-path`
  Opens a PowerPoint 365 presentation and returns a presentation ID for use in other nodes
- `robomotion powerpoint365 close_presentation --presentation-id`
  Closes an open PowerPoint presentation and releases resources
- `robomotion powerpoint365 save_presentation --presentation-id`
  Saves all changes made to the presentation back to OneDrive/SharePoint
- `robomotion powerpoint365 list_presentations --folder-path`
  Lists PowerPoint presentations in a specified folder
- `robomotion powerpoint365 create_presentation --file-path`
  Creates a new PowerPoint presentation at the specified path
- `robomotion powerpoint365 delete_presentation --file-path`
  Deletes a PowerPoint presentation (moves to recycle bin)
- `robomotion powerpoint365 copy_presentation --source-path --destination-path`
  Copies a PowerPoint presentation from source path to destination path
- `robomotion powerpoint365 download_presentation --remote-file-path --local-file-path [--format]`
  Downloads a PowerPoint presentation to local disk in PPTX or PDF format
- `robomotion powerpoint365 upload_presentation --local-file-path --remote-file-path`
  Uploads a local presentation file to OneDrive
- `robomotion powerpoint365 replace_text --presentation-id --replacements`
  Replaces text placeholders across all slides from a key-value map
- `robomotion powerpoint365 replace_image --presentation-id --placeholder-name --new-image`
  Replaces an image in the presentation by its placeholder name or alt text. The new image inherits the original's size and position

## Environment
- ROBOMOTION_API_TOKEN (if vault credentials are needed)
