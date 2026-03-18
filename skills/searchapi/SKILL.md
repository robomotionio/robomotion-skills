---
name: "searchapi"
description: "SearchAPI — search Google, Bing, YouTube, Google Maps, News, Scholar, Shopping, and more through a unified API. Supports multiple search engines and result types via `robomotion searchapi`. Do NOT use for Serper, Tavily, or direct Google API."
---

# SearchAPI

The `robomotion searchapi` CLI connects to SearchAPI.io for multi-engine web search. It searches Google, Bing, YouTube, Google Maps, News, Scholar, Shopping, and more through a unified interface with configurable result limits and search parameters.

## When to use
- Search Google, Bing, or YouTube for web results
- Get Google Maps, News, Scholar, or Shopping results
- Search for images or videos across engines
- Access multiple search engines through one API

## Prerequisites
- `robomotion` CLI installed
- Package installed: `robomotion install searchapi`
- SearchAPI.io API key configured via Robomotion vault

## Workflow
1. Install: `robomotion install searchapi`
2. Connect: `robomotion searchapi searchapi_connect` → returns a `client-id`
3. Search Google: `robomotion searchapi searchapi_google --client-id <id> --query <text>`
4. Search YouTube: `robomotion searchapi searchapi_youtube --client-id <id> --query <text>`
5. Disconnect: `robomotion searchapi searchapi_disconnect --client-id <id>`

## Commands Reference
- `robomotion searchapi searchapi_connect`
  Connects to SearchAPI.io and returns a client ID
- `robomotion searchapi searchapi_disconnect --client-id`
  Closes the SearchAPI.io connection and releases resources
- `robomotion searchapi google_search --client-id --query [--60] [--device] [--location] [--country] [--language] [--time-period] [--1] [--10] [--safe-search]`
  Searches Google and returns organic results，ads，knowledge graph，and more
- `robomotion searchapi google_images --client-id --query [--60] [--device] [--location] [--country] [--language] [--image-size] [--color] [--image-type] [--time-period] [--1]`
  Searches Google Images and returns image results with thumbnails，dimensions，and sources
- `robomotion searchapi google_news --client-id --query [--60] [--location] [--country] [--language] [--time-period] [--sort-by] [--1]`
  Searches Google News and returns news articles with titles，sources，and timestamps
- `robomotion searchapi google_videos --client-id --query [--60] [--device] [--location] [--country] [--language] [--duration] [--time-period] [--1]`
  Searches Google Videos and returns video results with duration，source，and thumbnails
- `robomotion searchapi google_maps --client-id --query [--60] [--coordinates] [--language] [--country] [--1]`
  Searches Google Maps for local businesses and places with ratings，reviews，and coordinates
- `robomotion searchapi google_shopping --client-id --query [--60] [--device] [--location] [--country] [--language] [--sort-by] [--condition] [--min-price] [--max-price] [--1]`
  Searches Google Shopping for products with prices，ratings，and seller info
- `robomotion searchapi google_scholar --client-id --query [--60] [--language] [--year-from] [--year-to] [--10] [--1]`
  Searches Google Scholar for academic papers，articles，and citations
- `robomotion searchapi google_jobs --client-id --query [--60] [--location] [--country] [--language] [--next-page-token]`
  Searches Google Jobs for job listings with titles，companies，and descriptions
- `robomotion searchapi google_trends --client-id --query [--60] [--data-type] [--region] [--time-range] [--category] [--search-type]`
  Gets Google Trends data including interest over time，by region，related queries，and topics
- `robomotion searchapi google_autocomplete --client-id --query [--60] [--country] [--language] [--client-type]`
  Gets Google autocomplete suggestions for keyword research and SEO
- `robomotion searchapi youtube_search --client-id --query [--60] [--country] [--language]`
  Searches YouTube for videos，channels，and playlists
- `robomotion searchapi bing_search --client-id --query [--60] [--device] [--location] [--market-code] [--safe-search] [--10] [--1]`
  Searches Bing and returns web results，related searches，and more

## Environment
- ROBOMOTION_API_TOKEN (if vault credentials are needed)
