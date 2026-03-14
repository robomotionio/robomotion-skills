---
name: "web-scraper"
description: "Use when the user wants to call the Robomotion DOM Parser package to scrape or extract data from web pages via the `robomotion domparser` CLI. Do NOT use for API-based data retrieval or local file parsing."
---

# Web Scraper Skill

## When to use
- Scrape data from web pages
- Parse HTML to extract specific elements
- Extract tables, links, or text from web pages

## Prerequisites
- `robomotion` CLI installed
- Package installed: `robomotion install domparser`

## Workflow
1. Install the package: `robomotion install domparser`
2. Run commands: `robomotion domparser <command> [flags]`

## Commands Reference
- `robomotion domparser dom_find_element --html --css-selector [--contains-filter] [--exclude-filter] [--index]`
  Find a single HTML element using CSS selector
- `robomotion domparser dom_find_all_elements --html --css-selector [--contains-filter] [--exclude-filter] [--limit] [--offset]`
  Find all HTML elements matching a CSS selector
- `robomotion domparser dom_get_value --element --css-selector --attribute-name`
  Extract text content or attribute value from an HTML element
- `robomotion domparser dom_get_values --elements --css-selector --attribute-name`
  Extract text or attribute values from multiple HTML elements
- `robomotion domparser dom_extract_text --element [--separator]`
  Extract all text content from an HTML element
- `robomotion domparser dom_extract_table --element [--header-row] [--skip-rows]`
  Extract HTML table data as JSON with columns and rows
- `robomotion domparser dom_extract_images --element [--filter-extension]`
  Extract all image URLs from an HTML element
- `robomotion domparser dom_count_words --text [--min-word-length] [--max-results] [--stop-words]`
  Calculate word frequency statistics from text
- `robomotion domparser dom_unescape_html --unescape-string`
  Unescape HTML entities in a string
- `robomotion domparser dom_escape_html --escape-string`
  Escape special HTML characters in a string

## Environment
- ROBOMOTION_API_TOKEN (if vault credentials are needed)
