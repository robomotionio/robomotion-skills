#!/bin/sh
# PyMuPDF for text + table extraction. ~25MB. Handles text-based PDFs;
# scanned PDFs need a heavier OCR backend (out of scope for this skill).
set -eu

pip3 install --no-cache-dir --break-system-packages pymupdf
