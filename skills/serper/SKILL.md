---
name: "serper"
description: "Serper Google Search API — search Google for web, image, video, news, shopping, scholar, places, and autocomplete results. Supports multiple search types and result formats via `robomotion serper`. Do NOT use for SearchAPI, Tavily, or direct Google API."
---

# Serper

The `robomotion serper` CLI connects to Serper's Google Search API for fast, structured search results. It searches Google web, images, videos, news, shopping, scholar, places, and provides autocomplete and related searches.

## When to use
- Search Google for web results, images, videos, or news
- Get Google Shopping, Scholar, or Places results
- Use autocomplete and related searches
- Access structured search results in JSON format

## Prerequisites
- `robomotion` CLI installed
- Package installed: `robomotion install serper`
- Serper API key configured via Robomotion vault

## IMPORTANT: Session Mode Required for Multi-Step Operations
Each CLI command runs as a **separate process** — connection IDs from `connect` do NOT persist across calls.
You MUST use `--session` on `connect` and pass `--session-id` to all subsequent commands.

## Workflow
1. Install (once): `robomotion install serper`
2. Connect with session:
   ```
   robomotion serper serper_connect --session --output json
   # → {"outClientId":"<client-id>","session_id":"<session-id>"}
   ```
3. Use the returned `client-id` and `session-id` in all subsequent commands:
   ```
   robomotion serper serper_search --client-id "<client-id>" --query <text> --session-id "<session-id>" --output json
   ```
4. Disconnect when done:
   ```
   robomotion serper serper_disconnect --client-id "<client-id>" --session-id "<session-id>" --output json
   ```

**Always** append `--output json` to get structured JSON results.

## Commands Reference
- `robomotion serper serper_connect --session --output json`
  Connects to Serper API and returns a client ID for subsequent nodes
- `robomotion serper serper_disconnect --client-id --session-id "<session-id>" --output json`
  Closes the Serper connection and releases resources
- `robomotion serper serper_web_search --client-id --query [--country] [--language] [--location] [--10] [--1] [--time-period] [--30] --session-id "<session-id>" --output json`
  Performs a Google web search via Serper API and returns organic results，knowledge graph，answer box，and related searches
- `robomotion serper serper_image_search --client-id --query [--country] [--language] [--10] [--1] [--30] --session-id "<session-id>" --output json`
  Searches Google Images via Serper API and returns image URLs，dimensions，and sources
- `robomotion serper serper_video_search --client-id --query [--country] [--language] [--10] [--1] [--30] --session-id "<session-id>" --output json`
  Searches Google Videos via Serper API and returns video links，durations，and thumbnails
- `robomotion serper serper_news_search --client-id --query [--country] [--language] [--location] [--10] [--1] [--time-period] [--30] --session-id "<session-id>" --output json`
  Searches Google News via Serper API and returns news articles with titles，sources，and dates
- `robomotion serper serper_shopping_search --client-id --query [--country] [--language] [--location] [--10] [--1] [--30] --session-id "<session-id>" --output json`
  Searches Google Shopping via Serper API and returns products with prices，ratings，and links
- `robomotion serper serper_places_search --client-id --query [--country] [--language] [--location] [--30] --session-id "<session-id>" --output json`
  Searches Google Places via Serper API and returns locations with addresses，ratings，and coordinates
- `robomotion serper serper_scholar_search --client-id --query [--country] [--language] [--10] [--1] [--30] --session-id "<session-id>" --output json`
  Searches Google Scholar via Serper API and returns academic papers with citations，authors，and publication info
- `robomotion serper serper_autocomplete --client-id --query [--country] [--language] [--30] --session-id "<session-id>" --output json`
  Gets Google Autocomplete suggestions via Serper API for a given query prefix
- `robomotion serper serper_maps_search --client-id --query [--country] [--language] [--coordinates] [--30] --session-id "<session-id>" --output json`
  Searches Google Maps via Serper API and returns locations with GPS coordinates，ratings，and addresses
- `robomotion serper serper_patents_search --client-id --query [--10] [--1] [--30] --session-id "<session-id>" --output json`
  Searches Google Patents via Serper API and returns patent documents with titles，numbers，and snippets
- `robomotion serper serper_lens_search --client-id --image-url [--country] [--language] [--60] --session-id "<session-id>" --output json`
  Performs a Google Lens visual search via Serper API using an image URL
- `robomotion serper serper_scrape --client-id --url [--60] --session-id "<session-id>" --output json`
  Scrapes a webpage via Serper API and returns the page content as text and optionally markdown

## Environment
- ROBOMOTION_API_TOKEN (if vault credentials are needed)
