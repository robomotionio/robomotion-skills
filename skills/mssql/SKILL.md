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

## Workflow
1. Install: `robomotion install mssql`
2. Connect: `robomotion mssql connect` → returns a `conn-id`
3. Query: `robomotion mssql execute_query --conn-id <id>` (with SQL in context)
4. Disconnect: `robomotion mssql disconnect --conn-id <id>`

## Commands Reference
- `robomotion mssql commit_transaction --in-transaction-id`
  Commits a database transaction to make all changes permanent
- `robomotion mssql connect`
  Connects to a Microsoft SQL Server database
- `robomotion mssql disconnect --in-connection-id`
  Closes an existing SQL Server database connection
- `robomotion mssql insert_table --in-connection-id --in-transaction-id --in-database-table --in-table`
  Inserts table data into a SQL Server database table
- `robomotion mssql execute_non_query --in-connection-id --in-transaction-id --func [--opt-command-timeout]`
  Executes a SQL command that does not return data (INSERT, UPDATE, DELETE, etc.)
- `robomotion mssql execute_query --in-connection-id --in-transaction-id --func [--opt-command-timeout]`
  Executes a SQL SELECT query and returns the results as a table
- `robomotion mssql start_transaction --in-connection-id`
  Starts a new database transaction for atomic operations
- `robomotion mssql wait_column --in-connection-id --in-table`
  Waits until a new column is added to a specified table
- `robomotion mssql wait_row --in-connection-id --in-table --in-sort-by`
  Waits until a new row is inserted into a specified table
- `robomotion mssql wait_table --in-connection-id --in-table`
  Waits until a new table matching the pattern is created in the database

## Environment
- ROBOMOTION_API_TOKEN (if vault credentials are needed)
