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

## Workflow
1. Install: `robomotion install tavily`
2. Connect: `robomotion tavily tavily_connect` → returns a `client-id`
3. Search: `robomotion tavily tavily_search --client-id <id> --search-query <query>`
4. Extract: `robomotion tavily tavily_extract --client-id <id> --ur-ls <urls>`
5. Disconnect: `robomotion tavily tavily_disconnect --client-id <id>`

## Commands Reference
- `robomotion tavily tavily_connect`
  Connects to Tavily API and returns a client ID
- `robomotion tavily tavily_disconnect --client-id`
  Closes the Tavily connection and releases resources
- `robomotion tavily tavily_search --client-id --search-query [--search-depth] [--topic] [--include-answer] [--time-range] [--5] [--include-raw-content] [--include-images] [--include-domains] [--exclude-domains] [--60]`
  Searches the web using Tavily AI-powered search
- `robomotion tavily tavily_extract --client-id --ur-ls [--extract-depth] [--format] [--include-images] [--60]`
  Extracts content from one or more URLs using Tavily
- `robomotion tavily tavily_crawl --client-id --url [--extract-depth] [--format] [--1] [--20] [--50] [--allow-external] [--150]`
  Crawls a website starting from a root URL and extracts content from discovered pages
- `robomotion tavily tavily_map --client-id --url [--1] [--20] [--50] [--allow-external] [--150]`
  Maps a website to discover all URLs starting from a root URL

## Environment
- ROBOMOTION_API_TOKEN (if vault credentials are needed)
