---
name: "datadog"
description: "Datadog monitoring platform — submit metrics, query logs, manage monitors/alerts, and schedule downtimes. Supports infrastructure monitoring and incident response via `robomotion datadog`. Do NOT use for Sentry, Splunk, Prometheus, or other monitoring tools."
---

# Datadog

The `robomotion datadog` CLI connects to Datadog for infrastructure monitoring and alerting. It submits custom metrics, queries logs and events, creates and manages monitors with alert conditions, schedules downtimes, and handles incidents.

## When to use
- Submit custom metrics or gauge values to Datadog
- Query logs, search events, and analyze time-series data
- Create, update, or mute Datadog monitors and alerts
- Schedule maintenance downtimes and manage incidents

## Prerequisites
- `robomotion` CLI installed
- Package installed: `robomotion install datadog`
- Datadog API and application keys configured via Robomotion vault

## IMPORTANT: Session Mode Required for Multi-Step Operations
Each CLI command runs as a **separate process** — connection IDs from `connect` do NOT persist across calls.
You MUST use `--session` on `connect` and pass `--session-id` to all subsequent commands.

## Workflow
1. Install (once): `robomotion install datadog`
2. Connect with session:
   ```
   robomotion datadog datadog_connect --session --output json
   # → {"outClientId":"<client-id>","session_id":"<session-id>"}
   ```
3. Use the returned `client-id` and `session-id` in all subsequent commands:
   ```
   robomotion datadog datadog_submit_metric --client-id "<client-id>" --metric-name <name> --value <val> --session-id "<session-id>" --output json
   ```
4. Disconnect when done:
   ```
   robomotion datadog datadog_disconnect --client-id "<client-id>" --session-id "<session-id>" --output json
   ```

**Always** append `--output json` to get structured JSON results.

## Commands Reference
- `robomotion datadog datadog_connect [--site] --session --output json`
  Connects to Datadog API and returns a client ID
- `robomotion datadog datadog_disconnect --client-id --session-id "<session-id>" --output json`
  Closes the Datadog connection and releases resources
- `robomotion datadog datadog_submit_metrics --client-id --series [--site] [--60] --session-id "<session-id>" --output json`
  Submit custom metrics to Datadog for tracking performance، business metrics، or custom monitoring
- `robomotion datadog datadog_query_timeseries --client-id --query --from-(unix-timestamp) --to-(unix-timestamp) [--site] [--60] --session-id "<session-id>" --output json`
  Query metric timeseries data from Datadog for analyzing trends and retrieving metric values
- `robomotion datadog datadog_create_event --client-id --title --text [--site] [--alert-type] [--priority] [--host] [--tags] --session-id "<session-id>" --output json`
  Post an event to the Datadog event stream for deployment notifications، alerts، or significant occurrences
- `robomotion datadog datadog_create_monitor --client-id --name --query [--site] [--monitor-type] [--message] [--tags] [--0] [--options-(json)] --session-id "<session-id>" --output json`
  Create a new monitor/alert in Datadog to track metrics، service checks، events، and more
- `robomotion datadog datadog_get_monitor --client-id --monitor-id [--site] [--group-states] [--with-downtimes] --session-id "<session-id>" --output json`
  Retrieve details of a specific monitor by ID
- `robomotion datadog datadog_list_monitors --client-id [--site] [--name-filter] [--tags] [--monitor-tags] [--group-states] [--with-downtimes] [--0] [--100] --session-id "<session-id>" --output json`
  List all monitors in Datadog with optional filtering by name، tags، or state
- `robomotion datadog datadog_mute_monitor --client-id --monitor-id [--site] [--scope] [--0] --session-id "<session-id>" --output json`
  Mute a monitor to temporarily suppress notifications
- `robomotion datadog datadog_query_logs --client-id --query --from --to [--site] [--50] [--sort] [--indexes] --session-id "<session-id>" --output json`
  Search and retrieve logs from Datadog for troubleshooting and analysis
- `robomotion datadog datadog_send_logs --client-id --logs [--site] [--60] --session-id "<session-id>" --output json`
  Send log entries to Datadog for centralized logging and analysis
- `robomotion datadog datadog_create_downtime --client-id --scope [--site] [--message] [--0] [--0] [--timezone] [--monitor-id] [--monitor-tags] [--mute-first-recovery] --session-id "<session-id>" --output json`
  Schedule a downtime to suppress monitor notifications during maintenance windows
- `robomotion datadog datadog_list_downtimes --client-id [--site] [--current-only] [--monitor-id] --session-id "<session-id>" --output json`
  List all scheduled downtimes in Datadog
- `robomotion datadog datadog_cancel_downtime --client-id --downtime-id [--site] --session-id "<session-id>" --output json`
  Cancel a scheduled downtime in Datadog

## Environment
- ROBOMOTION_API_TOKEN (if vault credentials are needed)
