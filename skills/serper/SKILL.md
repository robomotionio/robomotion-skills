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

## Workflow
1. Install: `robomotion install serper`
2. Connect: `robomotion serper serper_connect` → returns a `client-id`
3. Search web: `robomotion serper serper_search --client-id <id> --query <text>`
4. Search images: `robomotion serper serper_images --client-id <id> --query <text>`
5. Disconnect: `robomotion serper serper_disconnect --client-id <id>`

## Commands Reference
- `robomotion serper serper_connect`
  Connects to Serper API and returns a client ID for subsequent nodes
- `robomotion serper serper_disconnect --client-id`
  Closes the Serper connection and releases resources
- `robomotion serper serper_web_search --client-id --query [--country] [--language] [--location] [--10] [--1] [--time-period] [--30]`
  Performs a Google web search via Serper API and returns organic results，knowledge graph，answer box，and related searches
- `robomotion serper serper_image_search --client-id --query [--country] [--language] [--10] [--1] [--30]`
  Searches Google Images via Serper API and returns image URLs，dimensions，and sources
- `robomotion serper serper_video_search --client-id --query [--country] [--language] [--10] [--1] [--30]`
  Searches Google Videos via Serper API and returns video links，durations，and thumbnails
- `robomotion serper serper_news_search --client-id --query [--country] [--language] [--location] [--10] [--1] [--time-period] [--30]`
  Searches Google News via Serper API and returns news articles with titles，sources，and dates
- `robomotion serper serper_shopping_search --client-id --query [--country] [--language] [--location] [--10] [--1] [--30]`
  Searches Google Shopping via Serper API and returns products with prices，ratings，and links
- `robomotion serper serper_places_search --client-id --query [--country] [--language] [--location] [--30]`
  Searches Google Places via Serper API and returns locations with addresses，ratings，and coordinates
- `robomotion serper serper_scholar_search --client-id --query [--country] [--language] [--10] [--1] [--30]`
  Searches Google Scholar via Serper API and returns academic papers with citations，authors，and publication info
- `robomotion serper serper_autocomplete --client-id --query [--country] [--language] [--30]`
  Gets Google Autocomplete suggestions via Serper API for a given query prefix
- `robomotion serper serper_maps_search --client-id --query [--country] [--language] [--coordinates] [--30]`
  Searches Google Maps via Serper API and returns locations with GPS coordinates，ratings，and addresses
- `robomotion serper serper_patents_search --client-id --query [--10] [--1] [--30]`
  Searches Google Patents via Serper API and returns patent documents with titles，numbers，and snippets
- `robomotion serper serper_lens_search --client-id --image-url [--country] [--language] [--60]`
  Performs a Google Lens visual search via Serper API using an image URL
- `robomotion serper serper_scrape --client-id --url [--60]`
  Scrapes a webpage via Serper API and returns the page content as text and optionally markdown

## Environment
- ROBOMOTION_API_TOKEN (if vault credentials are needed)
