---
name: "google-slides"
description: "Google Slides — create presentations, add/manage/duplicate slides, replace text and images, and export to PDF. Supports template-based workflows via `robomotion googleslides`. Do NOT use for PowerPoint, Keynote, or other presentation tools."
---

# Google Slides

The `robomotion googleslides` CLI connects to Google Slides API for presentation management. It creates presentations, adds and duplicates slides, replaces text and images for template-based generation, and exports to PDF.

## When to use
- Create new presentations or work from templates
- Add, duplicate, or delete slides
- Replace text and images in slide templates for automated generation
- Export presentations to PDF

## Prerequisites
- `robomotion` CLI installed
- Package installed: `robomotion install googleslides`
- Google Slides OAuth2 or Service Account credentials configured via Robomotion vault

## Workflow
1. Install: `robomotion install googleslides`
2. Connect: `robomotion googleslides google_slides_connect` → returns a `client-id`
3. Create: `robomotion googleslides google_slides_create --client-id <id> --title <title>`
4. Replace text: `robomotion googleslides google_slides_replace_text --client-id <id> --presentation-id <id> --find <old> --replace <new>`
5. Disconnect: `robomotion googleslides google_slides_disconnect --client-id <id>`

## Commands Reference
- `robomotion googleslides create_presentation --title [--sharewith]`
  Creates a new Google Slides presentation with optional sharing
- `robomotion googleslides open_presentation --url`
  Opens an existing Google Slides presentation by URL
- `robomotion googleslides get_presentation --presentation-id [--page-object-id]`
  Retrieves presentation metadata or page element IDs
- `robomotion googleslides copy_presentation --presentation-id --title [--sharewith]`
  Creates a copy of an existing Google Slides presentation
- `robomotion googleslides replace_text --presentation-id --text-to-replace --replacement [--page-object-ids]`
  Finds and replaces text across all slides or specific pages
- `robomotion googleslides replace_image_by_id --presentation-id --image-object-id --replacement-image-url [--image-replace-method]`
  Replaces an existing image in a presentation by its object ID
- `robomotion googleslides replace_shapes_with_image --presentation-id --text-to-replace --replacement-image-url [--image-replace-method] [--page-object-ids]`
  Replaces shapes containing specific text with an image
- `robomotion googleslides add_image --presentation-id --image-object-id --image-url --0 [--0-0] [--0-0] [--0-0] [--0-0] [--1-0] [--1-0]`
  Adds an image to a slide at a specified position and size
- `robomotion googleslides pdf_export --presentation-id --file-path`
  Exports a Google Slides presentation to PDF format

## Environment
- ROBOMOTION_API_TOKEN (if vault credentials are needed)
