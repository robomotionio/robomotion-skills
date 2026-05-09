---
name: pdf-extract
summary: Extract text, tables, and metadata from PDFs (text-based and digital-native). Uses PyMuPDF.
---

# PDF Extract

Extract text from PDF files for downstream summarization, search, or transformation. Uses PyMuPDF — fast, ~25MB install, handles text-based PDFs (most modern PDFs, papers, reports) plus basic table extraction.

For OCR on scanned/image-only PDFs, this skill is NOT enough — those need a heavier OCR backend (marker-pdf or tesseract). This skill flags scan-only PDFs and tells the user to use a different tool.

## Capabilities

- Per-page text extraction
- Table extraction (basic — works on grid-aligned tables)
- Metadata (title, author, page count, creation date)
- Page-range slicing
- JSON output for downstream processing

## Usage

```sh
SKILL=$(dirname "$(find /opt/robomotion/skills -name SKILL.md -path '*/pdf-extract/*' | head -1)")

# Save a PDF to /workspace first (e.g. via curl)
curl -L -o /workspace/paper.pdf https://arxiv.org/pdf/2401.12345

# Extract all text
python3 "$SKILL/scripts/extract.py" /workspace/paper.pdf

# Extract specific pages
python3 "$SKILL/scripts/extract.py" /workspace/paper.pdf --pages 1-3

# Output JSON (page-keyed) for further processing
python3 "$SKILL/scripts/extract.py" /workspace/paper.pdf --json > /workspace/paper.json
```

## When to use

- "Summarize this PDF the user uploaded"
- "Pull the abstract and conclusion from this paper"
- "Extract the table on page 5"
- "What's the metadata on this report?"

## When NOT to use

- Scanned PDFs (images of text) — pymupdf returns empty strings; the user needs OCR
- Forms with editable fields where field values matter — use a forms-specific tool
- PDFs with strict layout requirements (preserving exact formatting) — text extraction loses positional info

## Operating notes

- pymupdf is fast and lightweight — prefer it over `pdftotext` for programmatic use.
- For papers, the abstract is usually on page 1 and the conclusion is the last named section. The `--pages` flag scopes extraction to limit token use.
- Equations come out as Unicode text where possible, otherwise as garbled characters. For mathy PDFs, warn the user that equations may be lost.
- Tables: pymupdf's table detection works on grid-aligned tables (rows separated by lines). Free-form spreadsheet-like tables come out as flat text.
- If the script returns very little text but the PDF has many pages, it's probably a scan — surface that to the user with a clear "this PDF appears to be scanned; use an OCR-capable tool".

## Attribution

The bundled `extract.py` is adapted from the [Nous Hermes Agent](https://github.com/NousResearch/hermes-agent) `ocr-and-documents` skill (MIT).
