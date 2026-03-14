---
name: "clickhouse"
description: "Use when the user wants to call the Robomotion ClickHouse package to query or insert data into ClickHouse via the `robomotion clickhouse` CLI. Do NOT use for PostgreSQL, MySQL, or MongoDB."
---

# Clickhouse Skill

## When to use
- Run analytical queries on ClickHouse
- Insert data into ClickHouse tables
- Query time-series or event data in ClickHouse

## Prerequisites
- `robomotion` CLI installed
- Package installed: `robomotion install clickhouse`
- Credentials configured via Robomotion vault or environment variables

## Workflow
1. Install the package: `robomotion install clickhouse`
2. Run commands: `robomotion clickhouse <command> [flags]`

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
