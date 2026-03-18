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

## IMPORTANT: Session Mode Required for Multi-Step Operations
Each CLI command runs as a **separate process** — connection IDs from `connect` do NOT persist across calls.
You MUST use `--session` on `connect` and pass `--session-id` to all subsequent commands.

## Workflow
1. Install (once): `robomotion install wikipedia`
2. Connect with session:
   ```
   robomotion wikipedia wikipedia_connect --session --output json
   # → {"outClientId":"<client-id>","session_id":"<session-id>"}
   ```
3. Use the returned `client-id` and `session-id` in all subsequent commands:
   ```
   robomotion wikipedia wikipedia_search --client-id "<client-id>" --query <text> --session-id "<session-id>" --output json
   ```
4. Disconnect when done:
   ```
   robomotion wikipedia wikipedia_disconnect --client-id "<client-id>" --session-id "<session-id>" --output json
   ```

**Always** append `--output json` to get structured JSON results.

## Commands Reference
- `robomotion wikipedia wikipedia_connect [--en] [--base-url] --session --output json`
  Connects to Wikipedia API and returns a client ID
- `robomotion wikipedia wikipedia_disconnect --client-id --session-id "<session-id>" --output json`
  Closes the Wikipedia connection and releases resources
- `robomotion wikipedia wikipedia_search --client-id --query [--10] [--en] --session-id "<session-id>" --output json`
  Searches Wikipedia pages by keyword
- `robomotion wikipedia wikipedia_summary --client-id --page-title [--en] --session-id "<session-id>" --output json`
  Gets a summary and metadata for a Wikipedia page
- `robomotion wikipedia wikipedia_content --client-id --page-title [--en] --session-id "<session-id>" --output json`
  Gets the full HTML content of a Wikipedia page
- `robomotion wikipedia wikipedia_random --client-id [--en] --session-id "<session-id>" --output json`
  Gets a random Wikipedia page with its summary

## Environment
- ROBOMOTION_API_TOKEN (if vault credentials are needed)
