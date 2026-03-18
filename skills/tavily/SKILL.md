---
name: "tavily"
description: "Tavily — AI-powered web search, content extraction, site crawling, and URL mapping. Supports search depth control, domain filtering, and structured content extraction via `robomotion tavily`. Do NOT use for Google Search, Serper, SearchAPI, or Perplexity."
---

# Tavily

The `robomotion tavily` CLI connects to Tavily for AI-powered web search and content extraction. It searches the web with relevance scoring, extracts content from URLs, crawls websites to discover pages, and maps site structure — all with configurable depth and domain filtering.

## When to use
- Search the web with AI-powered relevance scoring and topic filtering
- Extract clean content from one or more URLs
- Crawl websites starting from a root URL
- Map site structure to discover all URLs

## Prerequisites
- `robomotion` CLI installed
- Package installed: `robomotion install tavily`
- Tavily API key configured via Robomotion vault

## IMPORTANT: Session Mode Required for Multi-Step Operations
Each CLI command runs as a **separate process** — connection IDs from `connect` do NOT persist across calls.
You MUST use `--session` on `connect` and pass `--session-id` to all subsequent commands.

## Workflow
1. Install (once): `robomotion install tavily`
2. Connect with session:
   ```
   robomotion tavily tavily_connect --session --output json
   # → {"outClientId":"<client-id>","session_id":"<session-id>"}
   ```
3. Use the returned `client-id` and `session-id` in all subsequent commands:
   ```
   robomotion tavily tavily_search --client-id "<client-id>" --search-query <query> --session-id "<session-id>" --output json
   ```
4. Disconnect when done:
   ```
   robomotion tavily tavily_disconnect --client-id "<client-id>" --session-id "<session-id>" --output json
   ```

**Always** append `--output json` to get structured JSON results.

## Commands Reference
- `robomotion tavily tavily_connect --session --output json`
  Connects to Tavily API and returns a client ID
- `robomotion tavily tavily_disconnect --client-id --session-id "<session-id>" --output json`
  Closes the Tavily connection and releases resources
- `robomotion tavily tavily_search --client-id --search-query [--search-depth] [--topic] [--include-answer] [--time-range] [--5] [--include-raw-content] [--include-images] [--include-domains] [--exclude-domains] [--60] --session-id "<session-id>" --output json`
  Searches the web using Tavily AI-powered search
- `robomotion tavily tavily_extract --client-id --ur-ls [--extract-depth] [--format] [--include-images] [--60] --session-id "<session-id>" --output json`
  Extracts content from one or more URLs using Tavily
- `robomotion tavily tavily_crawl --client-id --url [--extract-depth] [--format] [--1] [--20] [--50] [--allow-external] [--150] --session-id "<session-id>" --output json`
  Crawls a website starting from a root URL and extracts content from discovered pages
- `robomotion tavily tavily_map --client-id --url [--1] [--20] [--50] [--allow-external] [--150] --session-id "<session-id>" --output json`
  Maps a website to discover all URLs starting from a root URL

## Environment
- ROBOMOTION_API_TOKEN (if vault credentials are needed)
