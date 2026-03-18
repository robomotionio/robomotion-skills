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

## Workflow
1. Install: `robomotion install oracle`
2. Connect: `robomotion oracle connect` → returns a `conn-id`
3. Query: `robomotion oracle execute_query --conn-id <id>` (with SQL in context)
4. Disconnect: `robomotion oracle disconnect --conn-id <id>`

## Commands Reference
- `robomotion oracle commit_transaction --in-transaction-id`
  Commits a database transaction, making all changes permanent
- `robomotion oracle connect`
  Connects to an Oracle database server using SID or Service Name
- `robomotion oracle disconnect --in-connection-id`
  Closes an Oracle database connection
- `robomotion oracle insert_table --in-connection-id --in-transaction-id --in-database-table --in-table`
  Inserts rows from a table data structure into a database table
- `robomotion oracle execute_non_query --in-connection-id --in-transaction-id --func`
  Executes an INSERT, UPDATE, or DELETE SQL statement
- `robomotion oracle execute_query --in-connection-id --in-transaction-id --func`
  Executes a SELECT SQL query and returns the results as a table
- `robomotion oracle start_transaction --in-connection-id`
  Starts a new database transaction for atomic operations

## Environment
- ROBOMOTION_API_TOKEN (if vault credentials are needed)
