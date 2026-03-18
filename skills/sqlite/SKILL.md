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

## Two Usage Modes

### Mode A: Stateless (recommended for simple queries)
Pass `--opt-connection-string` directly to every command. No connect/disconnect needed.

Connection string format: `"Data Source=/path/to/file.db;Version=3;"`

```
robomotion sqlite execute_query --in-connection-id "" --func "SELECT * FROM users" --opt-connection-string "Data Source=/path/to/file.db;Version=3;" --output json
```

### Mode B: Stateful Session (for multiple operations)
Use `--session` on `connect` to start a background daemon that holds the connection. Then pass `--session-id` to all subsequent commands.

```
# 1. Connect with --session (starts daemon, returns session-id + connection-id)
robomotion sqlite connect --opt-connection-string "Data Source=/path/to/file.db;Version=3;" --session --output json
# → {"outConnectionId":"<conn-id>","session_id":"<session-id>"}

# 2. Query using session-id + connection-id
robomotion sqlite execute_query --in-connection-id "<conn-id>" --func "SELECT * FROM users" --session-id "<session-id>" --output json

# 3. Disconnect when done
robomotion sqlite disconnect --in-connection-id "<conn-id>" --session-id "<session-id>" --output json
```

**Always** append `--output json` to get structured JSON results.

## Workflow
1. Install (once): `robomotion install sqlite`
2. For quick queries: use Mode A (stateless) — pass `--opt-connection-string` and `--in-connection-id ""` to each command
3. For multiple operations on the same database: use Mode B (session) — `connect --session` first, then reuse `--session-id` and `--in-connection-id`

**IMPORTANT:** Without `--session`, each CLI invocation is a separate process. Connection IDs from `connect` will NOT persist. Either use `--session` or pass `--opt-connection-string` to every command.

## Commands Reference
- `robomotion sqlite execute_query --in-connection-id "" --func "<SQL>" --opt-connection-string "<conn-string>" --output json`
  Executes a SELECT SQL query and returns the results as JSON
- `robomotion sqlite execute_non_query --in-connection-id "" --func "<SQL>" --opt-connection-string "<conn-string>" --output json`
  Executes an INSERT, UPDATE, or DELETE SQL statement
- `robomotion sqlite connect --opt-connection-string "<conn-string>" --session --output json`
  Connects to a SQLite database file (use --session to start a daemon for subsequent calls)
- `robomotion sqlite disconnect --in-connection-id "<conn-id>" --session-id "<session-id>" --output json`
  Closes a SQLite database connection (session mode only)
- `robomotion sqlite create_database --in-path <path>`
  Creates a new SQLite database file at the specified path
- `robomotion sqlite export_query --in-connection-id "" --func "<SQL>" --in-export-path <path> --opt-connection-string "<conn-string>" --output json`
  Executes a SQL query and exports the results to a CSV file
- `robomotion sqlite insert_table --in-connection-id "" --in-database-table <table> --in-table <json> --opt-connection-string "<conn-string>" --output json`
  Inserts rows from a table data structure into a database table
- `robomotion sqlite start_transaction --in-connection-id "<conn-id>" --session-id "<session-id>" --output json`
  Starts a new database transaction for atomic operations (session mode only)
- `robomotion sqlite commit_transaction --in-transaction-id "<tx-id>" --session-id "<session-id>" --output json`
  Commits a database transaction (session mode only)

## Environment
- ROBOMOTION_API_TOKEN (if vault credentials are needed)
