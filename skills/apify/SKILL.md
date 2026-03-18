---
name: "apify"
description: "Apify web scraping platform — run Apify actors for large-scale crawling and data extraction. Supports actor execution, run monitoring, and dataset retrieval via `robomotion apify`. Do NOT use for simple HTML parsing or non-Apify scraping tools."
---

# Apify

The `robomotion apify` CLI runs actors on the Apify platform for web scraping, crawling, and data extraction at scale. It handles actor execution with configurable timeouts, run status monitoring, and paginated dataset retrieval.

## When to use
- Run pre-built or custom Apify actors for web scraping
- Monitor actor run status and retrieve results
- Extract paginated datasets from completed actor runs

## Prerequisites
- `robomotion` CLI installed
- Package installed: `robomotion install apify`
- Apify API token configured via Robomotion vault

## Workflow
1. Install: `robomotion install apify`
2. Connect: `robomotion apify apify_connect` → returns a `client-id`
3. Run actor: `robomotion apify run_actor --client-id <id> --actor-id <actor> --input <json>`
4. Get results: `robomotion apify get_dataset_items --client-id <id> --dataset-id <ds>`
5. Disconnect: `robomotion apify apify_disconnect --client-id <id>`

## Commands Reference
- `robomotion apify apify_connect`
  Connects to Apify and returns a client ID for subsequent operations
- `robomotion apify apify_disconnect --client-id`
  Closes the Apify connection and releases resources
- `robomotion apify run_actor --client-id --actor-id --input [--300]`
  Runs an Apify Actor and optionally waits for completion
- `robomotion apify get_run --client-id --run-id`
  Gets details of an Actor run including status，dataset ID，and usage statistics
- `robomotion apify get_dataset_items --client-id --dataset-id [--100] [--0] [--format]`
  Retrieves items from an Apify dataset with optional pagination

## Environment
- ROBOMOTION_API_TOKEN (if vault credentials are needed)
