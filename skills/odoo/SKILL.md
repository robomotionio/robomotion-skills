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

## Workflow
1. Install: `robomotion install odoo`
2. Connect: `robomotion odoo odoo_connect` → returns a `client-id`
3. Search: `robomotion odoo odoo_search_read --client-id <id> --model <model> --domain <filter>`
4. Create: `robomotion odoo odoo_create --client-id <id> --model <model> --values <json>`
5. Disconnect: `robomotion odoo odoo_disconnect --client-id <id>`

## Commands Reference
- `robomotion odoo odoo_connect`
  Connects to an Odoo instance via XML-RPC and returns a client ID
- `robomotion odoo odoo_disconnect --client-id`
  Closes the Odoo connection and releases resources
- `robomotion odoo odoo_search_read --client-id --model --domain-filter --fields [--100] [--0]`
  Searches and reads records from any Odoo model using domain filters
- `robomotion odoo odoo_create_record --client-id --model --values`
  Creates a new record in any Odoo model
- `robomotion odoo odoo_update_record --client-id --model --record-i-ds --values`
  Updates one or more existing records in any Odoo model
- `robomotion odoo odoo_delete_record --client-id --model --record-i-ds`
  Deletes one or more records from any Odoo model
- `robomotion odoo odoo_get_fields --client-id --model --attributes`
  Retrieves field metadata for any Odoo model
- `robomotion odoo odoo_execute --client-id --model --method --arguments --keyword-arguments`
  Executes any method on any Odoo model via execute_kw

## Environment
- ROBOMOTION_API_TOKEN (if vault credentials are needed)
