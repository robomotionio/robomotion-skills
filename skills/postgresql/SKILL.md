---
name: "postgresql"
description: "PostgreSQL database — execute SQL queries, manage transactions, and perform CRUD operations. Supports SELECT, INSERT, UPDATE, DELETE, batch transactions, and stored procedures via `robomotion postgresql`. Do NOT use for MySQL, MongoDB, SQLite, or other databases."
---

# PostgreSQL

The `robomotion postgresql` CLI connects to PostgreSQL databases for SQL operations. It executes queries and non-query statements, manages batch transactions for atomicity, and handles the full range of PostgreSQL SQL operations.

## When to use
- Execute SQL SELECT queries against PostgreSQL tables
- Run INSERT, UPDATE, DELETE, and DDL statements
- Use batch transactions for atomic multi-statement operations

## Prerequisites
- `robomotion` CLI installed
- Package installed: `robomotion install postgresql`
- PostgreSQL connection credentials configured via Robomotion vault

## IMPORTANT: Session Mode Required for Multi-Step Operations
Each CLI command runs as a **separate process** — connection IDs from `connect` do NOT persist across calls.
You MUST use `--session` on `connect` and pass `--session-id` to all subsequent commands.

## Workflow
1. Install (once): `robomotion install postgresql`
2. Connect with session:
   ```
   robomotion postgresql connect --session --output json
   # → {"outConnectionId":"<conn-id>","session_id":"<session-id>"}
   ```
3. Use the returned `conn-id` and `session-id` in all subsequent commands:
   ```
   robomotion postgresql execute_query --conn-id "<conn-id>" --session-id "<session-id>" --output json
   ```
4. Disconnect when done:
   ```
   robomotion postgresql disconnect --conn-id "<conn-id>" --session-id "<session-id>" --output json
   ```

**Always** append `--output json` to get structured JSON results.

## Environment
- ROBOMOTION_API_TOKEN (if vault credentials are needed)
