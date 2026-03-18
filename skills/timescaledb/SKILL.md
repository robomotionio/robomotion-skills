---
name: "timescaledb"
description: "TimescaleDB — manage time-series data with hypertables, time-bucket queries, compression, and continuous aggregates. Supports high-performance time-series analytics via `robomotion timescaledb`. Do NOT use for QuestDB, InfluxDB, or plain PostgreSQL."
---

# TimescaleDB

The `robomotion timescaledb` CLI connects to TimescaleDB for time-series database operations. It manages hypertables, runs time-bucket aggregation queries, handles data insertion with timestamps, configures compression policies, and manages continuous aggregates.

## When to use
- Create hypertables and insert time-series data
- Run time-bucket queries for time-based aggregations
- Configure compression policies and continuous aggregates
- Execute standard SQL queries on TimescaleDB

## Prerequisites
- `robomotion` CLI installed
- Package installed: `robomotion install timescaledb`
- TimescaleDB connection credentials configured via Robomotion vault

## IMPORTANT: Session Mode Required for Multi-Step Operations
Each CLI command runs as a **separate process** — connection IDs from `connect` do NOT persist across calls.
You MUST use `--session` on `connect` and pass `--session-id` to all subsequent commands.

## Workflow
1. Install (once): `robomotion install timescaledb`
2. Connect with session:
   ```
   robomotion timescaledb timescaledb_connect --session --output json
   # → {"outConnectionId":"<conn-id>","session_id":"<session-id>"}
   ```
3. Use the returned `conn-id` and `session-id` in all subsequent commands:
   ```
   robomotion timescaledb timescaledb_execute_query --conn-id "<conn-id>" --session-id "<session-id>" --output json
   ```
4. Disconnect when done:
   ```
   robomotion timescaledb timescaledb_disconnect --conn-id "<conn-id>" --session-id "<session-id>" --output json
   ```

**Always** append `--output json` to get structured JSON results.

## Commands Reference
- `robomotion timescaledb timescaledb_connect --session --output json`
  Connects to a TimescaleDB server and returns a client ID for subsequent operations
- `robomotion timescaledb timescaledb_disconnect --client-id --session-id "<session-id>" --output json`
  Closes the TimescaleDB connection and releases resources
- `robomotion timescaledb timescaledb_execute_query --client-id --sql-query --query-params [--60] --session-id "<session-id>" --output json`
  Executes a raw SQL query against TimescaleDB and returns the results
- `robomotion timescaledb timescaledb_insert_data --client-id --table-name --columns --values [--60] --session-id "<session-id>" --output json`
  Inserts one or more rows of time-series data into a TimescaleDB hypertable
- `robomotion timescaledb timescaledb_query_data --client-id --table-name --select-columns --time-column --where-clause [--time-bucket] [--order-by] [--1000] [--60] --session-id "<session-id>" --output json`
  Queries time-series data from a hypertable with optional time_bucket aggregation
- `robomotion timescaledb timescaledb_create_hypertable --client-id --table-name --time-column [--chunk-time-interval] [--60] --session-id "<session-id>" --output json`
  Converts an existing PostgreSQL table into a TimescaleDB hypertable for time-series data
- `robomotion timescaledb timescaledb_drop_chunks --client-id --table-name --older-than [--120] --session-id "<session-id>" --output json`
  Drops old data chunks from a hypertable based on a time threshold for data retention
- `robomotion timescaledb timescaledb_enable_compression --client-id --table-name --segment-by --order-by [--compress-after] [--60] --session-id "<session-id>" --output json`
  Enables compression on a hypertable and optionally adds a compression policy
- `robomotion timescaledb timescaledb_create_continuous_aggregate --client-id --view-name --aggregate-query [--refresh-interval] [--start-offset] [--end-offset] [--120] --session-id "<session-id>" --output json`
  Creates a continuous aggregate (materialized view with automatic refresh) for a hypertable
- `robomotion timescaledb timescaledb_refresh_continuous_aggregate --client-id --view-name --start-time --end-time [--300] --session-id "<session-id>" --output json`
  Manually refreshes a continuous aggregate for a specified time window

## Environment
- ROBOMOTION_API_TOKEN (if vault credentials are needed)
