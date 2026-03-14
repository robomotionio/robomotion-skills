---
name: "pdf"
description: "Use when the user wants to call the Robomotion PDF package to create, merge, split, or extract text from PDF files via the `robomotion pdfprocessor` CLI. Do NOT use for viewing PDFs, non-PDF formats, or when the user wants to use Python PDF libraries directly."
---

# Pdf Skill

## When to use
- Extract text or metadata from PDF files
- Merge or split PDF documents
- Create PDF files programmatically
- Convert PDF pages to images

## Prerequisites
- `robomotion` CLI installed
- Package installed: `robomotion install pdfprocessor`

## Workflow
1. Install the package: `robomotion install pdfprocessor`
2. Run commands: `robomotion pdfprocessor <command> [flags]`

## Commands Reference
- `robomotion pdfprocessor pdf_export_form_to_json --pdf-path --json-path-to-save`
  Export PDF form fields and data to a JSON file
- `robomotion pdfprocessor pdf_fill_form_from_json --json-path --source-pdf-path --pdf-path-to-save`
  Fill PDF form fields with data from a JSON file
- `robomotion pdfprocessor pdf_create_from_json --json-path [--in-pdf-path] [--out-pdf-path]`
  Create a PDF document from a JSON definition file
- `robomotion pdfprocessor pdf_extract_images --pdf-path --directory-to-extract-images [--from-selected-pages]`
  Extract images from a PDF file to a specified directory
- `robomotion pdfprocessor pdf_split --pdf-path --directory-to-save-pages --page-number(s)-to-split [--custom-pages]`
  Split a PDF file into multiple files by page numbers
- `robomotion pdfprocessor pdf_merge --pdf-paths --custom-paths --pdf-path-to-save`
  Merge multiple PDF files into a single PDF document
- `robomotion pdfprocessor pdf_optimize --pdf-path [--pdf-path-to-save]`
  Optimize a PDF file to reduce its file size
- `robomotion pdfprocessor pdf_encrypt --pdf-path [--pdf-path-to-save] [--mode] [--key-length]`
  Encrypt a PDF file with password protection
- `robomotion pdfprocessor pdf_decrypt --pdf-path [--pdf-path-to-save] [--mode] [--key-length]`
  Decrypt a password-protected PDF file
- `robomotion pdfprocessor pdf_change_password --pdf-path [--pdf-path-to-save] [--mode] [--key-length] [--change-owner-or-user]`
  Change the owner or user password of an encrypted PDF file

## Environment
- ROBOMOTION_API_TOKEN (if vault credentials are needed)
