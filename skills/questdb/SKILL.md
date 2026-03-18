---
name: "questdb"
description: "QuestDB time-series database — execute SQL queries and insert time-series data. Supports high-performance ingestion and time-based analytics via `robomotion questdb`. Do NOT use for TimescaleDB, InfluxDB, or other time-series databases."
---

# QuestDB

The `robomotion questdb` CLI connects to QuestDB for time-series database operations. It executes SQL queries optimized for time-series data, inserts records with timestamps, and manages connections to QuestDB instances.

## When to use
- Execute time-series SQL queries with time-based aggregations
- Insert time-series data points into QuestDB tables
- Query sensor, metrics, or event data with time filters

## Prerequisites
- `robomotion` CLI installed
- Package installed: `robomotion install questdb`
- QuestDB connection credentials configured via Robomotion vault

## Workflow
1. Install: `robomotion install questdb`
2. Connect: `robomotion questdb questdb_connect` → returns a `conn-id`
3. Query: `robomotion questdb questdb_execute_query --conn-id <id>` (with SQL in context)
4. Disconnect: `robomotion questdb questdb_disconnect --conn-id <id>`

## Commands Reference
- `robomotion questdb questdb_connect`
  Connects to QuestDB database and returns a client ID for subsequent operations
- `robomotion questdb questdb_disconnect --client-id`
  Closes the QuestDB connection and releases resources
- `robomotion questdb questdb_execute_query --client-id --query --parameters [--60]`
  Executes a custom SQL query on QuestDB
- `robomotion questdb questdb_select --client-id --table --columns --where-clause --order-by --limit [--60]`
  Selects rows from a QuestDB table with optional filtering
- `robomotion questdb questdb_insert --client-id --table --columns --values [--60]`
  Inserts rows into a QuestDB table

## Environment
- ROBOMOTION_API_TOKEN (if vault credentials are needed)
