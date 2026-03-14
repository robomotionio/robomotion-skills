---
name: "apify"
description: "Use when the user wants to call the Robomotion Apify package to run Apify actors for web scraping or data extraction via the `robomotion apify` CLI. Do NOT use for simple HTML parsing or non-Apify tools."
---

# Apify Skill

## When to use
- Run Apify actors for large-scale scraping
- Crawl websites using Apify crawlers
- Extract data using pre-built Apify actors

## Prerequisites
- `robomotion` CLI installed
- Package installed: `robomotion install apify`
- Credentials configured via Robomotion vault or environment variables

## Workflow
1. Install the package: `robomotion install apify`
2. Run commands: `robomotion apify <command> [flags]`

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
