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

## Workflow
1. Install: `robomotion install datadog`
2. Connect: `robomotion datadog datadog_connect` → returns a `client-id`
3. Submit metric: `robomotion datadog datadog_submit_metric --client-id <id> --metric-name <name> --value <val>`
4. Query logs: `robomotion datadog datadog_query_logs --client-id <id> --query <query>`
5. Disconnect: `robomotion datadog datadog_disconnect --client-id <id>`

## Commands Reference
- `robomotion datadog datadog_connect [--site]`
  Connects to Datadog API and returns a client ID
- `robomotion datadog datadog_disconnect --client-id`
  Closes the Datadog connection and releases resources
- `robomotion datadog datadog_submit_metrics --client-id --series [--site] [--60]`
  Submit custom metrics to Datadog for tracking performance، business metrics، or custom monitoring
- `robomotion datadog datadog_query_timeseries --client-id --query --from-(unix-timestamp) --to-(unix-timestamp) [--site] [--60]`
  Query metric timeseries data from Datadog for analyzing trends and retrieving metric values
- `robomotion datadog datadog_create_event --client-id --title --text [--site] [--alert-type] [--priority] [--host] [--tags]`
  Post an event to the Datadog event stream for deployment notifications، alerts، or significant occurrences
- `robomotion datadog datadog_create_monitor --client-id --name --query [--site] [--monitor-type] [--message] [--tags] [--0] [--options-(json)]`
  Create a new monitor/alert in Datadog to track metrics، service checks، events، and more
- `robomotion datadog datadog_get_monitor --client-id --monitor-id [--site] [--group-states] [--with-downtimes]`
  Retrieve details of a specific monitor by ID
- `robomotion datadog datadog_list_monitors --client-id [--site] [--name-filter] [--tags] [--monitor-tags] [--group-states] [--with-downtimes] [--0] [--100]`
  List all monitors in Datadog with optional filtering by name، tags، or state
- `robomotion datadog datadog_mute_monitor --client-id --monitor-id [--site] [--scope] [--0]`
  Mute a monitor to temporarily suppress notifications
- `robomotion datadog datadog_query_logs --client-id --query --from --to [--site] [--50] [--sort] [--indexes]`
  Search and retrieve logs from Datadog for troubleshooting and analysis
- `robomotion datadog datadog_send_logs --client-id --logs [--site] [--60]`
  Send log entries to Datadog for centralized logging and analysis
- `robomotion datadog datadog_create_downtime --client-id --scope [--site] [--message] [--0] [--0] [--timezone] [--monitor-id] [--monitor-tags] [--mute-first-recovery]`
  Schedule a downtime to suppress monitor notifications during maintenance windows
- `robomotion datadog datadog_list_downtimes --client-id [--site] [--current-only] [--monitor-id]`
  List all scheduled downtimes in Datadog
- `robomotion datadog datadog_cancel_downtime --client-id --downtime-id [--site]`
  Cancel a scheduled downtime in Datadog

## Environment
- ROBOMOTION_API_TOKEN (if vault credentials are needed)
