---
name: "mysql"
description: "MySQL database — execute queries, manage transactions, and perform CRUD operations on MySQL databases. Supports SELECT, INSERT, UPDATE, DELETE, stored procedures, and batch transactions via `robomotion mysql`. Do NOT use for PostgreSQL, MSSQL, MongoDB, or other databases."
---

# MySQL

The `robomotion mysql` CLI connects to MySQL databases for SQL operations. It executes queries and non-query statements, manages transactions with batch support, runs stored procedures, and handles full CRUD workflows.

## When to use
- Execute SQL SELECT queries against MySQL tables
- Run INSERT, UPDATE, DELETE, and DDL statements
- Execute stored procedures with parameters
- Use batch transactions for atomic operations

## Prerequisites
- `robomotion` CLI installed
- Package installed: `robomotion install mysql`
- MySQL connection credentials configured via Robomotion vault

## Workflow
1. Install: `robomotion install mysql`
2. Connect: `robomotion mysql connect` → returns a `conn-id`
3. Query: `robomotion mysql execute_query --conn-id <id>` (with SQL in context)
4. Disconnect: `robomotion mysql disconnect --conn-id <id>`

## Commands Reference
- `robomotion mysql backup_database --connection-id --backup-file-path [--opt-parameters]`
  Creates a backup of the MySQL database to a file
- `robomotion mysql commit_transaction --transaction-id`
  Commits a database transaction to make all changes permanent
- `robomotion mysql connect [--opt-parameters]`
  Connects to a MySQL database server using Database credentials
- `robomotion mysql disconnect --connection-id`
  Closes an existing MySQL database connection
- `robomotion mysql insert_table --connection-id --transaction-id --database-table --table [--opt-parameters]`
  Inserts table data into a MySQL database table
- `robomotion mysql execute_non_query --connection-id --transaction-id --func [--opt-parameters]`
  Executes a SQL command that does not return data (INSERT, UPDATE, DELETE, etc.)
- `robomotion mysql execute_query --connection-id --transaction-id --func [--opt-parameters]`
  Executes a SQL SELECT query and returns the results as a table
- `robomotion mysql restore_database --connection-id --backup-file-path [--opt-parameters]`
  Restores a MySQL database from a backup file
- `robomotion mysql start_transaction --connection-id [--opt-parameters]`
  Starts a new database transaction for atomic operations
- `robomotion mysql wait_column --connection-id --table [--opt-parameters]`
  Waits until a new column is added to a specified table
- `robomotion mysql wait_row --connection-id --table --sort-by [--opt-parameters]`
  Waits until a new row is inserted into a specified table
- `robomotion mysql wait_table --connection-id --table [--opt-parameters]`
  Waits until a new table matching the pattern is created in the database

## Environment
- ROBOMOTION_API_TOKEN (if vault credentials are needed)
