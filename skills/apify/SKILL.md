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

## IMPORTANT: Session Mode Required for Multi-Step Operations
Each CLI command runs as a **separate process** — connection IDs from `connect` do NOT persist across calls.
You MUST use `--session` on `connect` and pass `--session-id` to all subsequent commands.

## Workflow
1. Install (once): `robomotion install apify`
2. Connect with session:
   ```
   robomotion apify apify_connect --session --output json
   # → {"outClientId":"<client-id>","session_id":"<session-id>"}
   ```
3. Use the returned `client-id` and `session-id` in all subsequent commands:
   ```
   robomotion apify run_actor --client-id "<client-id>" --actor-id <actor> --input <json> --session-id "<session-id>" --output json
   ```
4. Disconnect when done:
   ```
   robomotion apify apify_disconnect --client-id "<client-id>" --session-id "<session-id>" --output json
   ```

**Always** append `--output json` to get structured JSON results.

## Commands Reference
- `robomotion apify apify_connect --session --output json`
  Connects to Apify and returns a client ID for subsequent operations
- `robomotion apify apify_disconnect --client-id --session-id "<session-id>" --output json`
  Closes the Apify connection and releases resources
- `robomotion apify run_actor --client-id --actor-id --input [--300] --session-id "<session-id>" --output json`
  Runs an Apify Actor and optionally waits for completion
- `robomotion apify get_run --client-id --run-id --session-id "<session-id>" --output json`
  Gets details of an Actor run including status，dataset ID，and usage statistics
- `robomotion apify get_dataset_items --client-id --dataset-id [--100] [--0] [--format] --session-id "<session-id>" --output json`
  Retrieves items from an Apify dataset with optional pagination

## Environment
- ROBOMOTION_API_TOKEN (if vault credentials are needed)
