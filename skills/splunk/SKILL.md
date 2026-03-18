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

## IMPORTANT: Session Mode Required for Multi-Step Operations
Each CLI command runs as a **separate process** — connection IDs from `connect` do NOT persist across calls.
You MUST use `--session` on `connect` and pass `--session-id` to all subsequent commands.

## Workflow
1. Install (once): `robomotion install splunk`
2. Connect with session:
   ```
   robomotion splunk splunk_connect --session --output json
   # → {"outClientId":"<client-id>","session_id":"<session-id>"}
   ```
3. Use the returned `client-id` and `session-id` in all subsequent commands:
   ```
   robomotion splunk splunk_search --client-id "<client-id>" --query <spl> --session-id "<session-id>" --output json
   ```
4. Disconnect when done:
   ```
   robomotion splunk splunk_disconnect --client-id "<client-id>" --session-id "<session-id>" --output json
   ```

**Always** append `--output json` to get structured JSON results.

## Commands Reference
- `robomotion splunk splunk_connect --base-url --skip-tls-verification --session --output json`
  Connects to Splunk instance and returns a client ID for subsequent operations
- `robomotion splunk splunk_disconnect --client-id --session-id "<session-id>" --output json`
  Disconnects from Splunk and releases the client
- `robomotion splunk splunk_search --client-id --search-query [--https://localhost:8089] [--earliest-time] [--latest-time] [--100] [--120] [--execution-mode] --session-id "<session-id>" --output json`
  Runs an SPL search query in Splunk and returns results
- `robomotion splunk splunk_get_search_results --client-id --sid [--https://localhost:8089] [--100] [--0] --session-id "<session-id>" --output json`
  Retrieves results from a completed Splunk search job
- `robomotion splunk splunk_send_event --hec-url --event-data [--index] [--source] [--sourcetype] [--host] [--30] --output json`
  Sends an event to Splunk via HTTP Event Collector (HEC)
- `robomotion splunk splunk_list_indexes --client-id [--https://localhost:8089] --session-id "<session-id>" --output json`
  Lists all available indexes in Splunk
- `robomotion splunk splunk_list_saved_searches --client-id [--https://localhost:8089] [--50] --session-id "<session-id>" --output json`
  Lists all saved searches (reports) in Splunk
- `robomotion splunk splunk_run_saved_search --client-id --saved-search-name [--https://localhost:8089] [--100] [--120] --session-id "<session-id>" --output json`
  Dispatches a saved search and returns results
- `robomotion splunk splunk_get_server_info --client-id [--https://localhost:8089] --session-id "<session-id>" --output json`
  Gets Splunk server information including version، OS، and health status

## Environment
- ROBOMOTION_API_TOKEN (if vault credentials are needed)
