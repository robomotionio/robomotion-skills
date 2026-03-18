---
name: "oracle"
description: "Oracle Database — execute SQL queries, manage transactions, and perform CRUD operations. Supports SELECT, INSERT, UPDATE, DELETE, stored procedures, and batch transactions via `robomotion oracle`. Do NOT use for PostgreSQL, MySQL, MSSQL, or other databases."
---

# Oracle Database

The `robomotion oracle` CLI connects to Oracle databases for SQL operations. It executes queries and non-query statements, manages batch transactions, and handles the full range of Oracle SQL operations.

## When to use
- Execute SQL SELECT queries against Oracle tables
- Run INSERT, UPDATE, DELETE, and DDL statements
- Use batch transactions for atomic multi-statement operations

## Prerequisites
- `robomotion` CLI installed
- Package installed: `robomotion install oracle`
- Oracle database connection credentials configured via Robomotion vault

## IMPORTANT: Session Mode Required for Multi-Step Operations
Each CLI command runs as a **separate process** — connection IDs from `connect` do NOT persist across calls.
You MUST use `--session` on `connect` and pass `--session-id` to all subsequent commands.

## Workflow
1. Install (once): `robomotion install oracle`
2. Connect with session:
   ```
   robomotion oracle connect --session --output json
   # → {"outConnectionId":"<conn-id>","session_id":"<session-id>"}
   ```
3. Use the returned `conn-id` and `session-id` in all subsequent commands:
   ```
   robomotion oracle execute_query --conn-id "<conn-id>" --session-id "<session-id>" --output json
   ```
4. Disconnect when done:
   ```
   robomotion oracle disconnect --conn-id "<conn-id>" --session-id "<session-id>" --output json
   ```

**Always** append `--output json` to get structured JSON results.

## Commands Reference
- `robomotion oracle commit_transaction --in-transaction-id --output json`
  Commits a database transaction, making all changes permanent
- `robomotion oracle connect --session --output json`
  Connects to an Oracle database server using SID or Service Name
- `robomotion oracle disconnect --in-connection-id --session-id "<session-id>" --output json`
  Closes an Oracle database connection
- `robomotion oracle insert_table --in-connection-id --in-transaction-id --in-database-table --in-table --session-id "<session-id>" --output json`
  Inserts rows from a table data structure into a database table
- `robomotion oracle execute_non_query --in-connection-id --in-transaction-id --func --session-id "<session-id>" --output json`
  Executes an INSERT, UPDATE, or DELETE SQL statement
- `robomotion oracle execute_query --in-connection-id --in-transaction-id --func --session-id "<session-id>" --output json`
  Executes a SELECT SQL query and returns the results as a table
- `robomotion oracle start_transaction --in-connection-id --session-id "<session-id>" --output json`
  Starts a new database transaction for atomic operations

## Environment
- ROBOMOTION_API_TOKEN (if vault credentials are needed)
