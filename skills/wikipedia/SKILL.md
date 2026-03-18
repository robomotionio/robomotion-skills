---
name: "wikipedia"
description: "Wikipedia — search articles, retrieve page content, get summaries, and access Wikipedia data. Supports full-text search, page retrieval, and content extraction via `robomotion wikipedia`. Do NOT use for Google Search, web scraping, or other encyclopedias."
---

# Wikipedia

The `robomotion wikipedia` CLI connects to Wikipedia for article search and content retrieval. It searches for articles, retrieves full page content or summaries, and accesses structured Wikipedia data.

## When to use
- Search Wikipedia for articles by keyword
- Retrieve full article content or summaries
- Get page metadata and structured data

## Prerequisites
- `robomotion` CLI installed
- Package installed: `robomotion install wikipedia`
- No external credentials needed — Wikipedia API is public

## Workflow
1. Install: `robomotion install wikipedia`
2. Connect: `robomotion wikipedia wikipedia_connect` → returns a `client-id`
3. Search: `robomotion wikipedia wikipedia_search --client-id <id> --query <text>`
4. Get page: `robomotion wikipedia wikipedia_get_page --client-id <id> --title <title>`
5. Disconnect: `robomotion wikipedia wikipedia_disconnect --client-id <id>`

## Commands Reference
- `robomotion wikipedia wikipedia_connect [--en] [--base-url]`
  Connects to Wikipedia API and returns a client ID
- `robomotion wikipedia wikipedia_disconnect --client-id`
  Closes the Wikipedia connection and releases resources
- `robomotion wikipedia wikipedia_search --client-id --query [--10] [--en]`
  Searches Wikipedia pages by keyword
- `robomotion wikipedia wikipedia_summary --client-id --page-title [--en]`
  Gets a summary and metadata for a Wikipedia page
- `robomotion wikipedia wikipedia_content --client-id --page-title [--en]`
  Gets the full HTML content of a Wikipedia page
- `robomotion wikipedia wikipedia_random --client-id [--en]`
  Gets a random Wikipedia page with its summary

## Environment
- ROBOMOTION_API_TOKEN (if vault credentials are needed)
