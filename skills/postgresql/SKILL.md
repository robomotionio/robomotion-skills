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

## Workflow
1. Install: `robomotion install postgresql`
2. Connect: `robomotion postgresql connect` → returns a `conn-id`
3. Query: `robomotion postgresql execute_query --conn-id <id>` (with SQL in context)
4. Disconnect: `robomotion postgresql disconnect --conn-id <id>`

## Environment
- ROBOMOTION_API_TOKEN (if vault credentials are needed)
