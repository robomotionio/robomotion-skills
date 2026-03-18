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

## IMPORTANT: Session Mode Required for Multi-Step Operations
Each CLI command runs as a **separate process** — connection IDs from `connect` do NOT persist across calls.
You MUST use `--session` on `connect` and pass `--session-id` to all subsequent commands.

## Workflow
1. Install (once): `robomotion install questdb`
2. Connect with session:
   ```
   robomotion questdb questdb_connect --session --output json
   # → {"outConnectionId":"<conn-id>","session_id":"<session-id>"}
   ```
3. Use the returned `conn-id` and `session-id` in all subsequent commands:
   ```
   robomotion questdb questdb_execute_query --conn-id "<conn-id>" --session-id "<session-id>" --output json
   ```
4. Disconnect when done:
   ```
   robomotion questdb questdb_disconnect --conn-id "<conn-id>" --session-id "<session-id>" --output json
   ```

**Always** append `--output json` to get structured JSON results.

## Commands Reference
- `robomotion questdb questdb_connect --session --output json`
  Connects to QuestDB database and returns a client ID for subsequent operations
- `robomotion questdb questdb_disconnect --client-id --session-id "<session-id>" --output json`
  Closes the QuestDB connection and releases resources
- `robomotion questdb questdb_execute_query --client-id --query --parameters [--60] --session-id "<session-id>" --output json`
  Executes a custom SQL query on QuestDB
- `robomotion questdb questdb_select --client-id --table --columns --where-clause --order-by --limit [--60] --session-id "<session-id>" --output json`
  Selects rows from a QuestDB table with optional filtering
- `robomotion questdb questdb_insert --client-id --table --columns --values [--60] --session-id "<session-id>" --output json`
  Inserts rows into a QuestDB table

## Environment
- ROBOMOTION_API_TOKEN (if vault credentials are needed)
