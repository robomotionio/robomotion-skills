---
name: "splunk"
description: "Splunk — search logs, submit events, manage indexes, and run saved searches. Supports SPL queries, event ingestion, and search job management via `robomotion splunk`. Do NOT use for Datadog, Sentry, ELK Stack, or other log platforms."
---

# Splunk

The `robomotion splunk` CLI connects to Splunk for log management and search. It submits events to indexes, runs SPL search queries, manages search jobs, accesses saved searches, and handles index management.

## When to use
- Search logs and events using SPL (Search Processing Language)
- Submit events to Splunk indexes for ingestion
- Manage search jobs and retrieve results
- List and manage indexes and saved searches

## Prerequisites
- `robomotion` CLI installed
- Package installed: `robomotion install splunk`
- Splunk instance URL and API credentials configured via Robomotion vault

## Workflow
1. Install: `robomotion install splunk`
2. Connect: `robomotion splunk splunk_connect` → returns a `client-id`
3. Search: `robomotion splunk splunk_search --client-id <id> --query <spl>`
4. Submit event: `robomotion splunk splunk_submit_event --client-id <id> --index <idx> --event <json>`
5. Disconnect: `robomotion splunk splunk_disconnect --client-id <id>`

## Commands Reference
- `robomotion splunk splunk_connect --base-url --skip-tls-verification`
  Connects to Splunk instance and returns a client ID for subsequent operations
- `robomotion splunk splunk_disconnect --client-id`
  Disconnects from Splunk and releases the client
- `robomotion splunk splunk_search --client-id --search-query [--https://localhost:8089] [--earliest-time] [--latest-time] [--100] [--120] [--execution-mode]`
  Runs an SPL search query in Splunk and returns results
- `robomotion splunk splunk_get_search_results --client-id --sid [--https://localhost:8089] [--100] [--0]`
  Retrieves results from a completed Splunk search job
- `robomotion splunk splunk_send_event --hec-url --event-data [--index] [--source] [--sourcetype] [--host] [--30]`
  Sends an event to Splunk via HTTP Event Collector (HEC)
- `robomotion splunk splunk_list_indexes --client-id [--https://localhost:8089]`
  Lists all available indexes in Splunk
- `robomotion splunk splunk_list_saved_searches --client-id [--https://localhost:8089] [--50]`
  Lists all saved searches (reports) in Splunk
- `robomotion splunk splunk_run_saved_search --client-id --saved-search-name [--https://localhost:8089] [--100] [--120]`
  Dispatches a saved search and returns results
- `robomotion splunk splunk_get_server_info --client-id [--https://localhost:8089]`
  Gets Splunk server information including version، OS، and health status

## Environment
- ROBOMOTION_API_TOKEN (if vault credentials are needed)
