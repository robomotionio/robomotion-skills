---
name: "sqlite"
description: "SQLite — execute queries and manage embedded SQLite database files. Supports SELECT, INSERT, UPDATE, DELETE, batch transactions, and local database operations via `robomotion sqlite`. Do NOT use for PostgreSQL, MySQL, or server-based databases."
---

# SQLite

The `robomotion sqlite` CLI works with local SQLite database files for embedded SQL operations. It executes queries and non-query statements, manages batch transactions, and handles schema operations on `.db` files without requiring a database server.

## When to use
- Execute SQL SELECT queries on local SQLite databases
- Run INSERT, UPDATE, DELETE, and DDL statements
- Use batch transactions for atomic operations
- Create and manage local SQLite database files

## Prerequisites
- `robomotion` CLI installed
- Package installed: `robomotion install sqlite`
- No external credentials needed — works with local `.db` files

## Workflow
1. Install: `robomotion install sqlite`
2. Connect: `robomotion sqlite connect` → returns a `conn-id` (provide database file path)
3. Query: `robomotion sqlite execute_query --conn-id <id>` (with SQL in context)
4. Disconnect: `robomotion sqlite disconnect --conn-id <id>`

## Commands Reference
- `robomotion sqlite commit_transaction --in-transaction-id`
  Commits a database transaction, making all changes permanent
- `robomotion sqlite connect [--opt-connection-string]`
  Connects to a SQLite database file
- `robomotion sqlite create_database --in-path`
  Creates a new SQLite database file at the specified path
- `robomotion sqlite disconnect --in-connection-id`
  Closes a SQLite database connection
- `robomotion sqlite export_query --in-connection-id --in-transaction-id --in-export-path --func [--separator] [--opt-connection-string]`
  Executes a SQL query and exports the results to a CSV file
- `robomotion sqlite insert_table --in-connection-id --in-transaction-id --in-database-table --in-table [--opt-connection-string]`
  Inserts rows from a table data structure into a database table
- `robomotion sqlite execute_non_query --in-connection-id --in-transaction-id --func [--opt-connection-string]`
  Executes an INSERT, UPDATE, or DELETE SQL statement
- `robomotion sqlite execute_query --in-connection-id --in-transaction-id --func [--opt-connection-string]`
  Executes a SELECT SQL query and returns the results as a table
- `robomotion sqlite start_transaction --in-connection-id`
  Starts a new database transaction for atomic operations

## Environment
- ROBOMOTION_API_TOKEN (if vault credentials are needed)
