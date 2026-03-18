---
name: "shopify"
description: "Shopify — manage products, orders, customers, inventory, collections, and fulfillments. Supports full ecommerce operations including order processing and inventory tracking via `robomotion shopify`. Do NOT use for WooCommerce, Magento, or other ecommerce platforms."
---

# Shopify

The `robomotion shopify` CLI connects to Shopify for ecommerce management. It handles products (CRUD with variants), orders (create/fulfill/cancel), customers, inventory levels, collections, and fulfillment tracking — covering the full online store workflow.

## When to use
- Create, update, list, or delete products and variants
- Manage orders — create, fulfill, cancel, and track
- Search and manage customer records
- Track inventory levels and manage collections

## Prerequisites
- `robomotion` CLI installed
- Package installed: `robomotion install shopify`
- Shopify store URL and API access token configured via Robomotion vault

## IMPORTANT: Session Mode Required for Multi-Step Operations
Each CLI command runs as a **separate process** — connection IDs from `connect` do NOT persist across calls.
You MUST use `--session` on `connect` and pass `--session-id` to all subsequent commands.

## Workflow
1. Install (once): `robomotion install shopify`
2. Connect with session:
   ```
   robomotion shopify shopify_connect --session --output json
   # → {"outClientId":"<client-id>","session_id":"<session-id>"}
   ```
3. Use the returned `client-id` and `session-id` in all subsequent commands:
   ```
   robomotion shopify shopify_list_products --client-id "<client-id>" --session-id "<session-id>" --output json
   ```
4. Disconnect when done:
   ```
   robomotion shopify shopify_disconnect --client-id "<client-id>" --session-id "<session-id>" --output json
   ```

**Always** append `--output json` to get structured JSON results.

## Commands Reference
- `robomotion shopify shopify_connect --session --output json`
  Connects to Shopify Admin API and returns a client ID
- `robomotion shopify shopify_disconnect --client-id --session-id "<session-id>" --output json`
  Closes the Shopify connection and releases resources
- `robomotion shopify shopify_create_product --client-id --title [--description-html] [--vendor] [--product-type] [--tags] [--status] --session-id "<session-id>" --output json`
  Creates a new product in Shopify
- `robomotion shopify shopify_get_product --client-id --product-id --session-id "<session-id>" --output json`
  Retrieves a single product by ID from Shopify
- `robomotion shopify shopify_list_products --client-id [--50] [--title-filter] [--vendor-filter] [--product-type-filter] [--status-filter] [--since-id] --session-id "<session-id>" --output json`
  Lists products from Shopify with optional filtering
- `robomotion shopify shopify_update_product --client-id --product-id [--title] [--description-html] [--vendor] [--product-type] [--tags] [--status] --session-id "<session-id>" --output json`
  Updates an existing product in Shopify
- `robomotion shopify shopify_delete_product --client-id --product-id --session-id "<session-id>" --output json`
  Deletes a product from Shopify
- `robomotion shopify shopify_get_order --client-id --order-id --session-id "<session-id>" --output json`
  Retrieves a single order by ID from Shopify
- `robomotion shopify shopify_list_orders --client-id [--50] [--status] [--financial-status] [--fulfillment-status] [--since-id] --session-id "<session-id>" --output json`
  Lists orders from Shopify with optional filtering
- `robomotion shopify shopify_update_order --client-id --order-id [--note] [--tags] [--email] --session-id "<session-id>" --output json`
  Updates an existing order in Shopify (note، tags، email)
- `robomotion shopify shopify_cancel_order --client-id --order-id [--reason] --session-id "<session-id>" --output json`
  Cancels an existing order in Shopify
- `robomotion shopify shopify_create_customer --client-id [--email] [--first-name] [--last-name] [--phone] [--note] [--tags] --session-id "<session-id>" --output json`
  Creates a new customer in Shopify
- `robomotion shopify shopify_get_customer --client-id --customer-id --session-id "<session-id>" --output json`
  Retrieves a single customer by ID from Shopify
- `robomotion shopify shopify_list_customers --client-id [--50] [--since-id] --session-id "<session-id>" --output json`
  Lists customers from Shopify with optional filtering
- `robomotion shopify shopify_update_customer --client-id --customer-id [--email] [--first-name] [--last-name] [--phone] [--note] [--tags] --session-id "<session-id>" --output json`
  Updates an existing customer in Shopify
- `robomotion shopify shopify_delete_customer --client-id --customer-id --session-id "<session-id>" --output json`
  Deletes a customer from Shopify
- `robomotion shopify shopify_list_inventory_items --client-id --item-i-ds [--50] --session-id "<session-id>" --output json`
  Lists inventory items from Shopify
- `robomotion shopify shopify_get_inventory_level --client-id --inventory-item-id --location-id --session-id "<session-id>" --output json`
  Gets inventory levels for items at specific locations
- `robomotion shopify shopify_adjust_inventory --client-id --inventory-item-id --location-id --delta --session-id "<session-id>" --output json`
  Adjusts inventory quantity at a specific location
- `robomotion shopify shopify_list_locations --client-id --session-id "<session-id>" --output json`
  Lists all store locations for inventory operations
- `robomotion shopify shopify_create_fulfillment --client-id --order-id --location-id [--tracking-number] [--tracking-company] [--tracking-url] --session-id "<session-id>" --output json`
  Creates a fulfillment for an order (marks items as shipped)
- `robomotion shopify shopify_list_collections --client-id [--50] [--collection-type] [--since-id] --session-id "<session-id>" --output json`
  Lists product collections from Shopify
- `robomotion shopify shopify_get_collection --client-id --collection-id [--collection-type] [--50] --session-id "<session-id>" --output json`
  Retrieves a collection and its products from Shopify

## Environment
- ROBOMOTION_API_TOKEN (if vault credentials are needed)
