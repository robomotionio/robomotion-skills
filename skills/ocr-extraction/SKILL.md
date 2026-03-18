---
name: "ocr-extraction"
description: "OCR text extraction — extract text from images and scanned documents using Google Vision and Document AI. Supports image OCR, document parsing, and structured data extraction via `robomotion googlevision` and `robomotion googledocumentai`. Do NOT use for Tesseract, ABBYY, or direct text processing."
---

# OCR Extraction (Google Vision / Document AI)

The `robomotion googlevision` and `robomotion googledocumentai` CLIs extract text from images and scanned documents using Google Cloud Vision OCR and Document AI. They support image text detection, document parsing, and structured content extraction.

## When to use
- Extract text from images using Google Vision OCR
- Parse scanned documents with Google Document AI
- Process invoices, receipts, and forms for structured data

## Prerequisites
- `robomotion` CLI installed
- Package installed: `robomotion install googlevision`
- Google Cloud Vision / Document AI credentials configured via Robomotion vault

## Workflow
1. Install: `robomotion install googlevision` or `robomotion install googledocumentai`
2. Connect: `robomotion googlevision connect` → returns a `client-id`
3. Extract text: `robomotion googlevision detect_text --client-id <id> --image-path <file>`
4. Disconnect: `robomotion googlevision disconnect --client-id <id>`

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
