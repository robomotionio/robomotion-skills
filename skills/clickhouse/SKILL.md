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

## Workflow
1. Install: `robomotion install clickhouse`
2. Connect: `robomotion clickhouse connect` → returns a `conn-id`
3. Query: `robomotion clickhouse execute_query --conn-id <id>`
4. Batch insert: `robomotion clickhouse create_batch --conn-id <id>` → add statements → `robomotion clickhouse send_batch --batch-id <id>`
5. Disconnect: `robomotion clickhouse disconnect --conn-id <id>`

## Commands Reference
- `robomotion clickhouse connect`
  Connect to a ClickHouse database server using credentials
- `robomotion clickhouse create_batch --conn-id`
  Create a new batch transaction for executing multiple SQL commands atomically
- `robomotion clickhouse disconnect --conn-id`
  Disconnect from a ClickHouse database server and release the connection
- `robomotion clickhouse execute_non_query --conn-id --batch-id`
  Execute a SQL command (INSERT٫ UPDATE٫ DELETE٫ etc.) that does not return results
- `robomotion clickhouse execute_query --conn-id --batch-id`
  Execute a SQL SELECT query on ClickHouse and return the results
- `robomotion clickhouse send_batch --batch-id`
  Commit a batch transaction and execute all queued SQL commands

## Environment
- ROBOMOTION_API_TOKEN (if vault credentials are needed)
