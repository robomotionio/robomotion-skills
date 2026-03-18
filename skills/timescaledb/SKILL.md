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

## Workflow
1. Install: `robomotion install timescaledb`
2. Connect: `robomotion timescaledb timescaledb_connect` → returns a `conn-id`
3. Query: `robomotion timescaledb timescaledb_execute_query --conn-id <id>` (with SQL in context)
4. Disconnect: `robomotion timescaledb timescaledb_disconnect --conn-id <id>`

## Commands Reference
- `robomotion timescaledb timescaledb_connect`
  Connects to a TimescaleDB server and returns a client ID for subsequent operations
- `robomotion timescaledb timescaledb_disconnect --client-id`
  Closes the TimescaleDB connection and releases resources
- `robomotion timescaledb timescaledb_execute_query --client-id --sql-query --query-params [--60]`
  Executes a raw SQL query against TimescaleDB and returns the results
- `robomotion timescaledb timescaledb_insert_data --client-id --table-name --columns --values [--60]`
  Inserts one or more rows of time-series data into a TimescaleDB hypertable
- `robomotion timescaledb timescaledb_query_data --client-id --table-name --select-columns --time-column --where-clause [--time-bucket] [--order-by] [--1000] [--60]`
  Queries time-series data from a hypertable with optional time_bucket aggregation
- `robomotion timescaledb timescaledb_create_hypertable --client-id --table-name --time-column [--chunk-time-interval] [--60]`
  Converts an existing PostgreSQL table into a TimescaleDB hypertable for time-series data
- `robomotion timescaledb timescaledb_drop_chunks --client-id --table-name --older-than [--120]`
  Drops old data chunks from a hypertable based on a time threshold for data retention
- `robomotion timescaledb timescaledb_enable_compression --client-id --table-name --segment-by --order-by [--compress-after] [--60]`
  Enables compression on a hypertable and optionally adds a compression policy
- `robomotion timescaledb timescaledb_create_continuous_aggregate --client-id --view-name --aggregate-query [--refresh-interval] [--start-offset] [--end-offset] [--120]`
  Creates a continuous aggregate (materialized view with automatic refresh) for a hypertable
- `robomotion timescaledb timescaledb_refresh_continuous_aggregate --client-id --view-name --start-time --end-time [--300]`
  Manually refreshes a continuous aggregate for a specified time window

## Environment
- ROBOMOTION_API_TOKEN (if vault credentials are needed)
