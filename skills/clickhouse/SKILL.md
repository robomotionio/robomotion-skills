---
name: "clickhouse"
description: "ClickHouse columnar database — execute analytical SQL queries and batch inserts on ClickHouse. Supports query execution, batch transactions, and non-query operations via `robomotion clickhouse`. Do NOT use for PostgreSQL, MySQL, MongoDB, or other databases."
---

# ClickHouse

The `robomotion clickhouse` CLI connects to ClickHouse for analytical SQL workloads. It supports executing SELECT queries, running INSERT/UPDATE/DELETE statements, and batch transactions for atomically executing multiple SQL commands.

## When to use
- Run analytical SQL queries on ClickHouse columnar tables
- Insert data using batch transactions for atomicity
- Execute DDL or non-query SQL statements

## Prerequisites
- `robomotion` CLI installed
- Package installed: `robomotion install clickhouse`
- ClickHouse connection credentials configured via Robomotion vault

## IMPORTANT: Session Mode Required for Multi-Step Operations
Each CLI command runs as a **separate process** — connection IDs from `connect` do NOT persist across calls.
You MUST use `--session` on `connect` and pass `--session-id` to all subsequent commands.

## Workflow
1. Install (once): `robomotion install clickhouse`
2. Connect with session:
   ```
   robomotion clickhouse connect --session --output json
   # → {"outConnectionId":"<conn-id>","session_id":"<session-id>"}
   ```
3. Use the returned `conn-id` and `session-id` in all subsequent commands:
   ```
   robomotion clickhouse execute_query --conn-id "<conn-id>" --session-id "<session-id>" --output json
   ```
4. Disconnect when done:
   ```
   robomotion clickhouse disconnect --conn-id "<conn-id>" --session-id "<session-id>" --output json
   ```

**Always** append `--output json` to get structured JSON results.

## Commands Reference
- `robomotion clickhouse connect --session --output json`
  Connect to a ClickHouse database server using credentials
- `robomotion clickhouse create_batch --conn-id --session-id "<session-id>" --output json`
  Create a new batch transaction for executing multiple SQL commands atomically
- `robomotion clickhouse disconnect --conn-id --session-id "<session-id>" --output json`
  Disconnect from a ClickHouse database server and release the connection
- `robomotion clickhouse execute_non_query --conn-id --batch-id --session-id "<session-id>" --output json`
  Execute a SQL command (INSERT٫ UPDATE٫ DELETE٫ etc.) that does not return results
- `robomotion clickhouse execute_query --conn-id --batch-id --session-id "<session-id>" --output json`
  Execute a SQL SELECT query on ClickHouse and return the results
- `robomotion clickhouse send_batch --batch-id --output json`
  Commit a batch transaction and execute all queued SQL commands

## Environment
- ROBOMOTION_API_TOKEN (if vault credentials are needed)
