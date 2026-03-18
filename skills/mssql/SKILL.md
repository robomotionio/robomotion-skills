---
name: "mssql"
description: "Microsoft SQL Server — execute queries, stored procedures, and manage transactions on MSSQL databases. Supports SELECT, INSERT, UPDATE, DELETE, and batch operations via `robomotion mssql`. Do NOT use for PostgreSQL, MySQL, Oracle, or other databases."
---

# Microsoft SQL Server

The `robomotion mssql` CLI connects to Microsoft SQL Server for database operations. It executes SQL queries and non-query statements, manages transactions with batch support, and handles stored procedure execution.

## When to use
- Execute SQL SELECT queries and retrieve result sets
- Run INSERT, UPDATE, DELETE, and DDL statements
- Execute stored procedures with parameters
- Use batch transactions for atomic multi-statement operations

## Prerequisites
- `robomotion` CLI installed
- Package installed: `robomotion install mssql`
- SQL Server connection credentials configured via Robomotion vault

## IMPORTANT: Session Mode Required for Multi-Step Operations
Each CLI command runs as a **separate process** — connection IDs from `connect` do NOT persist across calls.
You MUST use `--session` on `connect` and pass `--session-id` to all subsequent commands.

## Workflow
1. Install (once): `robomotion install mssql`
2. Connect with session:
   ```
   robomotion mssql connect --session --output json
   # → {"outConnectionId":"<conn-id>","session_id":"<session-id>"}
   ```
3. Use the returned `conn-id` and `session-id` in all subsequent commands:
   ```
   robomotion mssql execute_query --conn-id "<conn-id>" --session-id "<session-id>" --output json
   ```
4. Disconnect when done:
   ```
   robomotion mssql disconnect --conn-id "<conn-id>" --session-id "<session-id>" --output json
   ```

**Always** append `--output json` to get structured JSON results.

## Commands Reference
- `robomotion mssql commit_transaction --in-transaction-id --output json`
  Commits a database transaction to make all changes permanent
- `robomotion mssql connect --session --output json`
  Connects to a Microsoft SQL Server database
- `robomotion mssql disconnect --in-connection-id --session-id "<session-id>" --output json`
  Closes an existing SQL Server database connection
- `robomotion mssql insert_table --in-connection-id --in-transaction-id --in-database-table --in-table --session-id "<session-id>" --output json`
  Inserts table data into a SQL Server database table
- `robomotion mssql execute_non_query --in-connection-id --in-transaction-id --func [--opt-command-timeout] --session-id "<session-id>" --output json`
  Executes a SQL command that does not return data (INSERT, UPDATE, DELETE, etc.)
- `robomotion mssql execute_query --in-connection-id --in-transaction-id --func [--opt-command-timeout] --session-id "<session-id>" --output json`
  Executes a SQL SELECT query and returns the results as a table
- `robomotion mssql start_transaction --in-connection-id --session-id "<session-id>" --output json`
  Starts a new database transaction for atomic operations
- `robomotion mssql wait_column --in-connection-id --in-table --session-id "<session-id>" --output json`
  Waits until a new column is added to a specified table
- `robomotion mssql wait_row --in-connection-id --in-table --in-sort-by --session-id "<session-id>" --output json`
  Waits until a new row is inserted into a specified table
- `robomotion mssql wait_table --in-connection-id --in-table --session-id "<session-id>" --output json`
  Waits until a new table matching the pattern is created in the database

## Environment
- ROBOMOTION_API_TOKEN (if vault credentials are needed)
