---
name: "postgresql"
description: "Use when the user wants to call the Robomotion PostgreSQL package to query or manage a PostgreSQL database via the `robomotion postgresql` CLI. Do NOT use for MySQL, MongoDB, or other database systems."
---

# Postgresql Skill

## When to use
- Execute SQL queries against PostgreSQL
- Insert or update records in PostgreSQL tables
- Manage PostgreSQL database connections

## Prerequisites
- `robomotion` CLI installed
- Package installed: `robomotion install postgresql`
- Credentials configured via Robomotion vault or environment variables

## Workflow
1. Install the package: `robomotion install postgresql`
2. Run commands: `robomotion postgresql <command> [flags]`

## Environment
- ROBOMOTION_API_TOKEN (if vault credentials are needed)
