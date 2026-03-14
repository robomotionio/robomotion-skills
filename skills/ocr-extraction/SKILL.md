---
name: "ocr-extraction"
description: "Use when the user wants to call the Robomotion Google Vision or Document AI packages to extract text from images or scanned documents via the `robomotion googlevision` or `robomotion googledocumentai` CLI. Do NOT use for digital PDFs with selectable text."
---

# Ocr Extraction Skill

## When to use
- Extract text from images or screenshots
- Process scanned documents or receipts
- Extract structured data from invoices or forms using Document AI

## Prerequisites
- `robomotion` CLI installed
- Package installed: `robomotion install googlevision googledocumentai`
- Credentials configured via Robomotion vault or environment variables

## Workflow
1. Install the package: `robomotion install googlevision googledocumentai`
2. Run commands: `robomotion googlevision <command> [flags]`
3. Run commands: `robomotion googledocumentai <command> [flags]`

## Commands Reference
- `robomotion googlevision pdf_to_text --vision-client-id --gcs-source-uri --gcs-destination-uri`
  Extract text from a PDF file stored in Google Cloud Storage
- `robomotion googlevision connect_vision`
  Connect to Google Cloud Vision API and create a client session
- `robomotion googlevision image_to_text --vision-client-id --image-path`
  Extract text from an image using OCR (Optical Character Recognition)
- `robomotion googlevision extract_image_labels --vision-client-id --image-path`
  Extract labels and descriptions from an image using Google Cloud Vision API
- `robomotion googlevision check_image_safety --vision-client-id --image-path`
  Detect explicit content and unsafe categories in an image
- `robomotion googledocumentai extract_text --file-path --mime-type [--project-id] [--location] [--processor-id]`
  Extracts text content from documents using Google Document AI OCR and text recognition
- `robomotion googledocumentai extract_tables --file-path --mime-type [--project-id] [--location] [--processor-id]`
  Extracts table data from documents using Google Document AI with column headers and row values
- `robomotion googledocumentai extract_key_values --file-path --mime-type [--project-id] [--location] [--processor-id]`
  Extracts key-value pairs from forms and documents using Google Document AI form parsing

## Environment
- ROBOMOTION_API_TOKEN (if vault credentials are needed)
