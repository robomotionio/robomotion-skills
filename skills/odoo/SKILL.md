---
name: "odoo"
description: "Odoo ERP — manage contacts, sales orders, invoices, products, leads, and any model via XML-RPC. Supports full ERP operations across all Odoo modules via `robomotion odoo`. Do NOT use for SAP, NetSuite, Salesforce, or other ERP/CRM platforms."
---

# Odoo

The `robomotion odoo` CLI connects to Odoo ERP via XML-RPC for business management operations. It handles contacts, sales orders, invoices, products, leads, and any Odoo model — supporting create, read, update, delete, and search operations across all modules.

## When to use
- Create, update, or search contacts, leads, and sales orders
- Manage invoices and products in Odoo
- Query any Odoo model using domain filters via XML-RPC

## Prerequisites
- `robomotion` CLI installed
- Package installed: `robomotion install odoo`
- Odoo instance URL, database, and API credentials configured via Robomotion vault

## IMPORTANT: Session Mode Required for Multi-Step Operations
Each CLI command runs as a **separate process** — connection IDs from `connect` do NOT persist across calls.
You MUST use `--session` on `connect` and pass `--session-id` to all subsequent commands.

## Workflow
1. Install (once): `robomotion install odoo`
2. Connect with session:
   ```
   robomotion odoo odoo_connect --session --output json
   # → {"outClientId":"<client-id>","session_id":"<session-id>"}
   ```
3. Use the returned `client-id` and `session-id` in all subsequent commands:
   ```
   robomotion odoo odoo_search_read --client-id "<client-id>" --model <model> --domain <filter> --session-id "<session-id>" --output json
   ```
4. Disconnect when done:
   ```
   robomotion odoo odoo_disconnect --client-id "<client-id>" --session-id "<session-id>" --output json
   ```

**Always** append `--output json` to get structured JSON results.

## Commands Reference
- `robomotion odoo odoo_connect --session --output json`
  Connects to an Odoo instance via XML-RPC and returns a client ID
- `robomotion odoo odoo_disconnect --client-id --session-id "<session-id>" --output json`
  Closes the Odoo connection and releases resources
- `robomotion odoo odoo_search_read --client-id --model --domain-filter --fields [--100] [--0] --session-id "<session-id>" --output json`
  Searches and reads records from any Odoo model using domain filters
- `robomotion odoo odoo_create_record --client-id --model --values --session-id "<session-id>" --output json`
  Creates a new record in any Odoo model
- `robomotion odoo odoo_update_record --client-id --model --record-i-ds --values --session-id "<session-id>" --output json`
  Updates one or more existing records in any Odoo model
- `robomotion odoo odoo_delete_record --client-id --model --record-i-ds --session-id "<session-id>" --output json`
  Deletes one or more records from any Odoo model
- `robomotion odoo odoo_get_fields --client-id --model --attributes --session-id "<session-id>" --output json`
  Retrieves field metadata for any Odoo model
- `robomotion odoo odoo_execute --client-id --model --method --arguments --keyword-arguments --session-id "<session-id>" --output json`
  Executes any method on any Odoo model via execute_kw

## Environment
- ROBOMOTION_API_TOKEN (if vault credentials are needed)
