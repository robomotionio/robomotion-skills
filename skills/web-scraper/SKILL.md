---
name: "web-scraper"
description: "DOM Parser web scraper — extract data from HTML pages using CSS selectors and XPath queries. Supports structured data extraction, attribute reading, and HTML parsing via `robomotion domparser`. Do NOT use for Apify, Puppeteer, or browser automation."
---

# Web Scraper (DOM Parser)

The `robomotion domparser` CLI parses and extracts data from HTML web pages. It loads HTML content, queries elements using CSS selectors or XPath, extracts text and attributes, and outputs structured data from web pages.

## When to use
- Extract data from HTML pages using CSS selectors
- Query DOM elements with XPath expressions
- Parse HTML content and extract text or attributes

## Prerequisites
- `robomotion` CLI installed
- Package installed: `robomotion install domparser`
- No external credentials needed — works with HTML content/URLs

## Workflow
1. Install: `robomotion install domparser`
2. Load HTML: `robomotion domparser load --url <url>` or `--html <content>`
3. Extract: `robomotion domparser query --selector <css>` or `--xpath <xpath>`

## Commands Reference
- `robomotion domparser dom_find_element --html --css-selector [--contains-filter] [--exclude-filter] [--index] --output json`
  Find a single HTML element using CSS selector
- `robomotion domparser dom_find_all_elements --html --css-selector [--contains-filter] [--exclude-filter] [--limit] [--offset] --output json`
  Find all HTML elements matching a CSS selector
- `robomotion domparser dom_get_value --element --css-selector --attribute-name --output json`
  Extract text content or attribute value from an HTML element
- `robomotion domparser dom_get_values --elements --css-selector --attribute-name --output json`
  Extract text or attribute values from multiple HTML elements
- `robomotion domparser dom_extract_text --element [--separator] --output json`
  Extract all text content from an HTML element
- `robomotion domparser dom_extract_table --element [--header-row] [--skip-rows] --output json`
  Extract HTML table data as JSON with columns and rows
- `robomotion domparser dom_extract_images --element [--filter-extension] --output json`
  Extract all image URLs from an HTML element
- `robomotion domparser dom_count_words --text [--min-word-length] [--max-results] [--stop-words] --output json`
  Calculate word frequency statistics from text
- `robomotion domparser dom_unescape_html --unescape-string --output json`
  Unescape HTML entities in a string
- `robomotion domparser dom_escape_html --escape-string --output json`
  Escape special HTML characters in a string

## Environment
- ROBOMOTION_API_TOKEN (if vault credentials are needed)
