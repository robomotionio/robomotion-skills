---
name: "pdf"
description: "PDF processor — create, merge, split, extract text, convert, and manipulate PDF files. Supports page operations, text extraction, and format conversions via `robomotion pdfprocessor`. Do NOT use for Google Docs, Word documents, or image OCR."
---

# PDF Processor

The `robomotion pdfprocessor` CLI handles PDF file operations. It creates, merges, splits, extracts text from, and converts PDF files. It supports page-level operations, metadata handling, and various format conversions.

## When to use
- Extract text content from PDF files
- Merge multiple PDFs into one or split PDFs by pages
- Create new PDF files from content
- Convert between PDF and other formats

## Prerequisites
- `robomotion` CLI installed
- Package installed: `robomotion install pdfprocessor`
- No external credentials needed — works with local PDF files

## Workflow
1. Install: `robomotion install pdfprocessor`
2. Extract text: `robomotion pdfprocessor extract_text --file-path <pdf>`
3. Merge: `robomotion pdfprocessor merge --files <pdf1,pdf2> --output <out.pdf>`

## Commands Reference
- `robomotion pdfprocessor pdf_export_form_to_json --pdf-path --json-path-to-save --output json`
  Export PDF form fields and data to a JSON file
- `robomotion pdfprocessor pdf_fill_form_from_json --json-path --source-pdf-path --pdf-path-to-save --output json`
  Fill PDF form fields with data from a JSON file
- `robomotion pdfprocessor pdf_create_from_json --json-path [--in-pdf-path] [--out-pdf-path] --output json`
  Create a PDF document from a JSON definition file
- `robomotion pdfprocessor pdf_extract_images --pdf-path --directory-to-extract-images [--from-selected-pages] --output json`
  Extract images from a PDF file to a specified directory
- `robomotion pdfprocessor pdf_split --pdf-path --directory-to-save-pages --page-number(s)-to-split [--custom-pages] --output json`
  Split a PDF file into multiple files by page numbers
- `robomotion pdfprocessor pdf_merge --pdf-paths --custom-paths --pdf-path-to-save --output json`
  Merge multiple PDF files into a single PDF document
- `robomotion pdfprocessor pdf_optimize --pdf-path [--pdf-path-to-save] --output json`
  Optimize a PDF file to reduce its file size
- `robomotion pdfprocessor pdf_encrypt --pdf-path [--pdf-path-to-save] [--mode] [--key-length] --output json`
  Encrypt a PDF file with password protection
- `robomotion pdfprocessor pdf_decrypt --pdf-path [--pdf-path-to-save] [--mode] [--key-length] --output json`
  Decrypt a password-protected PDF file
- `robomotion pdfprocessor pdf_change_password --pdf-path [--pdf-path-to-save] [--mode] [--key-length] [--change-owner-or-user] --output json`
  Change the owner or user password of an encrypted PDF file

## Environment
- ROBOMOTION_API_TOKEN (if vault credentials are needed)
