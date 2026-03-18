---
name: "tidbcloud"
description: "TiDB Cloud — execute SQL queries and manage data in distributed TiDB Cloud databases. Supports MySQL-compatible SQL operations via `robomotion tidbcloud`. Do NOT use for MySQL, PostgreSQL, CockroachDB, or other databases."
---

# TiDB Cloud

The `robomotion tidbcloud` CLI connects to TiDB Cloud (distributed MySQL-compatible database) for SQL operations. It executes queries, runs non-query statements, and manages transactions on TiDB Cloud instances.

## When to use
- Execute SQL SELECT queries on TiDB Cloud databases
- Run INSERT, UPDATE, DELETE, and DDL statements
- Use batch transactions for atomic operations

## Prerequisites
- `robomotion` CLI installed
- Package installed: `robomotion install tidbcloud`
- TiDB Cloud connection credentials configured via Robomotion vault

## Workflow
1. Install: `robomotion install tidbcloud`
2. Connect: `robomotion tidbcloud tidbcloud_connect` → returns a `conn-id`
3. Query: `robomotion tidbcloud tidbcloud_execute_query --conn-id <id>` (with SQL in context)
4. Disconnect: `robomotion tidbcloud tidbcloud_disconnect --conn-id <id>`

## Commands Reference
- `robomotion tidbcloud tidbcloud_connect`
  Connects to TiDB Cloud database and returns a client ID for subsequent operations
- `robomotion tidbcloud tidbcloud_disconnect --client-id`
  Closes the TiDB Cloud connection and releases resources
- `robomotion tidbcloud tidbcloud_execute_query --client-id --query [--60]`
  Executes a custom SQL query on TiDB Cloud
- `robomotion tidbcloud tidbcloud_select --client-id --table --columns --where-clause --order-by --limit [--60]`
  Selects rows from a TiDB Cloud table with optional filtering
- `robomotion tidbcloud tidbcloud_insert --client-id --table --columns --values [--60]`
  Inserts rows into a TiDB Cloud table
- `robomotion tidbcloud tidbcloud_update --client-id --table --columns --values --where-clause [--60]`
  Updates rows in a TiDB Cloud table
- `robomotion tidbcloud tidbcloud_delete --client-id --table --where-clause [--60]`
  Deletes rows from a TiDB Cloud table

## Environment
- ROBOMOTION_API_TOKEN (if vault credentials are needed)
