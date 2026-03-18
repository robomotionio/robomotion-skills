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

## IMPORTANT: Session Mode Required for Multi-Step Operations
Each CLI command runs as a **separate process** — connection IDs from `connect` do NOT persist across calls.
You MUST use `--session` on `connect` and pass `--session-id` to all subsequent commands.

## Workflow
1. Install (once): `robomotion install googlevision`
2. Connect with session:
   ```
   robomotion googlevision connect --session --output json
   # → {"outClientId":"<client-id>","session_id":"<session-id>"}
   ```
3. Use the returned `client-id` and `session-id` in all subsequent commands:
   ```
   robomotion googlevision detect_text --client-id "<client-id>" --image-path <file> --session-id "<session-id>" --output json
   ```
4. Disconnect when done:
   ```
   robomotion googlevision disconnect --client-id "<client-id>" --session-id "<session-id>" --output json
   ```

**Always** append `--output json` to get structured JSON results.

## Commands Reference
- `robomotion googlevision pdf_to_text --vision-client-id --gcs-source-uri --gcs-destination-uri --output json`
  Extract text from a PDF file stored in Google Cloud Storage
- `robomotion googlevision connect_vision --session --output json`
  Connect to Google Cloud Vision API and create a client session
- `robomotion googlevision image_to_text --vision-client-id --image-path --output json`
  Extract text from an image using OCR (Optical Character Recognition)
- `robomotion googlevision extract_image_labels --vision-client-id --image-path --output json`
  Extract labels and descriptions from an image using Google Cloud Vision API
- `robomotion googlevision check_image_safety --vision-client-id --image-path --output json`
  Detect explicit content and unsafe categories in an image
- `robomotion googledocumentai extract_text --file-path --mime-type [--project-id] [--location] [--processor-id] --output json`
  Extracts text content from documents using Google Document AI OCR and text recognition
- `robomotion googledocumentai extract_tables --file-path --mime-type [--project-id] [--location] [--processor-id] --output json`
  Extracts table data from documents using Google Document AI with column headers and row values
- `robomotion googledocumentai extract_key_values --file-path --mime-type [--project-id] [--location] [--processor-id] --output json`
  Extracts key-value pairs from forms and documents using Google Document AI form parsing

## Environment
- ROBOMOTION_API_TOKEN (if vault credentials are needed)
