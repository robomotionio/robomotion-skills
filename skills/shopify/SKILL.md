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

## Workflow
1. Install: `robomotion install shopify`
2. Connect: `robomotion shopify shopify_connect` → returns a `client-id`
3. List products: `robomotion shopify shopify_list_products --client-id <id>`
4. Create order: `robomotion shopify shopify_create_order --client-id <id> --line-items <json>`
5. Disconnect: `robomotion shopify shopify_disconnect --client-id <id>`

## Commands Reference
- `robomotion shopify shopify_connect`
  Connects to Shopify Admin API and returns a client ID
- `robomotion shopify shopify_disconnect --client-id`
  Closes the Shopify connection and releases resources
- `robomotion shopify shopify_create_product --client-id --title [--description-html] [--vendor] [--product-type] [--tags] [--status]`
  Creates a new product in Shopify
- `robomotion shopify shopify_get_product --client-id --product-id`
  Retrieves a single product by ID from Shopify
- `robomotion shopify shopify_list_products --client-id [--50] [--title-filter] [--vendor-filter] [--product-type-filter] [--status-filter] [--since-id]`
  Lists products from Shopify with optional filtering
- `robomotion shopify shopify_update_product --client-id --product-id [--title] [--description-html] [--vendor] [--product-type] [--tags] [--status]`
  Updates an existing product in Shopify
- `robomotion shopify shopify_delete_product --client-id --product-id`
  Deletes a product from Shopify
- `robomotion shopify shopify_get_order --client-id --order-id`
  Retrieves a single order by ID from Shopify
- `robomotion shopify shopify_list_orders --client-id [--50] [--status] [--financial-status] [--fulfillment-status] [--since-id]`
  Lists orders from Shopify with optional filtering
- `robomotion shopify shopify_update_order --client-id --order-id [--note] [--tags] [--email]`
  Updates an existing order in Shopify (note، tags، email)
- `robomotion shopify shopify_cancel_order --client-id --order-id [--reason]`
  Cancels an existing order in Shopify
- `robomotion shopify shopify_create_customer --client-id [--email] [--first-name] [--last-name] [--phone] [--note] [--tags]`
  Creates a new customer in Shopify
- `robomotion shopify shopify_get_customer --client-id --customer-id`
  Retrieves a single customer by ID from Shopify
- `robomotion shopify shopify_list_customers --client-id [--50] [--since-id]`
  Lists customers from Shopify with optional filtering
- `robomotion shopify shopify_update_customer --client-id --customer-id [--email] [--first-name] [--last-name] [--phone] [--note] [--tags]`
  Updates an existing customer in Shopify
- `robomotion shopify shopify_delete_customer --client-id --customer-id`
  Deletes a customer from Shopify
- `robomotion shopify shopify_list_inventory_items --client-id --item-i-ds [--50]`
  Lists inventory items from Shopify
- `robomotion shopify shopify_get_inventory_level --client-id --inventory-item-id --location-id`
  Gets inventory levels for items at specific locations
- `robomotion shopify shopify_adjust_inventory --client-id --inventory-item-id --location-id --delta`
  Adjusts inventory quantity at a specific location
- `robomotion shopify shopify_list_locations --client-id`
  Lists all store locations for inventory operations
- `robomotion shopify shopify_create_fulfillment --client-id --order-id --location-id [--tracking-number] [--tracking-company] [--tracking-url]`
  Creates a fulfillment for an order (marks items as shipped)
- `robomotion shopify shopify_list_collections --client-id [--50] [--collection-type] [--since-id]`
  Lists product collections from Shopify
- `robomotion shopify shopify_get_collection --client-id --collection-id [--collection-type] [--50]`
  Retrieves a collection and its products from Shopify

## Environment
- ROBOMOTION_API_TOKEN (if vault credentials are needed)
