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

## IMPORTANT: Session Mode Required for Multi-Step Operations
Each CLI command runs as a **separate process** — connection IDs from `connect` do NOT persist across calls.
You MUST use `--session` on `connect` and pass `--session-id` to all subsequent commands.

## Workflow
1. Install (once): `robomotion install tidbcloud`
2. Connect with session:
   ```
   robomotion tidbcloud tidbcloud_connect --session --output json
   # → {"outConnectionId":"<conn-id>","session_id":"<session-id>"}
   ```
3. Use the returned `conn-id` and `session-id` in all subsequent commands:
   ```
   robomotion tidbcloud tidbcloud_execute_query --conn-id "<conn-id>" --session-id "<session-id>" --output json
   ```
4. Disconnect when done:
   ```
   robomotion tidbcloud tidbcloud_disconnect --conn-id "<conn-id>" --session-id "<session-id>" --output json
   ```

**Always** append `--output json` to get structured JSON results.

## Commands Reference
- `robomotion tidbcloud tidbcloud_connect --session --output json`
  Connects to TiDB Cloud database and returns a client ID for subsequent operations
- `robomotion tidbcloud tidbcloud_disconnect --client-id --session-id "<session-id>" --output json`
  Closes the TiDB Cloud connection and releases resources
- `robomotion tidbcloud tidbcloud_execute_query --client-id --query [--60] --session-id "<session-id>" --output json`
  Executes a custom SQL query on TiDB Cloud
- `robomotion tidbcloud tidbcloud_select --client-id --table --columns --where-clause --order-by --limit [--60] --session-id "<session-id>" --output json`
  Selects rows from a TiDB Cloud table with optional filtering
- `robomotion tidbcloud tidbcloud_insert --client-id --table --columns --values [--60] --session-id "<session-id>" --output json`
  Inserts rows into a TiDB Cloud table
- `robomotion tidbcloud tidbcloud_update --client-id --table --columns --values --where-clause [--60] --session-id "<session-id>" --output json`
  Updates rows in a TiDB Cloud table
- `robomotion tidbcloud tidbcloud_delete --client-id --table --where-clause [--60] --session-id "<session-id>" --output json`
  Deletes rows from a TiDB Cloud table

## Environment
- ROBOMOTION_API_TOKEN (if vault credentials are needed)
