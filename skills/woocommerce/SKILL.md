---
name: "woocommerce"
description: "WooCommerce — manage products, orders, customers, coupons, and categories in WordPress-based online stores. Supports full ecommerce operations via `robomotion woocommerce`. Do NOT use for Shopify, Magento, or other ecommerce platforms."
---

# WooCommerce

The `robomotion woocommerce` CLI connects to WooCommerce stores for ecommerce management. It manages products with variations, handles orders and fulfillments, administers customers and coupons, and organizes product categories — covering the full WordPress-based store workflow.

## When to use
- Create, update, list, or delete products and variations
- Manage orders — create, update status, and track
- Search and manage customer records and coupons
- Organize product categories and tags

## Prerequisites
- `robomotion` CLI installed
- Package installed: `robomotion install woocommerce`
- WooCommerce store URL, consumer key, and consumer secret configured via Robomotion vault

## IMPORTANT: Session Mode Required for Multi-Step Operations
Each CLI command runs as a **separate process** — connection IDs from `connect` do NOT persist across calls.
You MUST use `--session` on `connect` and pass `--session-id` to all subsequent commands.

## Workflow
1. Install (once): `robomotion install woocommerce`
2. Connect with session:
   ```
   robomotion woocommerce woocommerce_connect --session --output json
   # → {"outClientId":"<client-id>","session_id":"<session-id>"}
   ```
3. Use the returned `client-id` and `session-id` in all subsequent commands:
   ```
   robomotion woocommerce woocommerce_list_products --client-id "<client-id>" --session-id "<session-id>" --output json
   ```
4. Disconnect when done:
   ```
   robomotion woocommerce woocommerce_disconnect --client-id "<client-id>" --session-id "<session-id>" --output json
   ```

**Always** append `--output json` to get structured JSON results.

## Commands Reference
- `robomotion woocommerce woocommerce_connect --session --output json`
  Connects to a WooCommerce store and returns a client ID
- `robomotion woocommerce woocommerce_disconnect --client-id --session-id "<session-id>" --output json`
  Closes the WooCommerce connection and releases resources
- `robomotion woocommerce create_product --client-id --product-name --regular-price --data [--product-type] [--status] [--60] --session-id "<session-id>" --output json`
  Creates a new product in the WooCommerce store
- `robomotion woocommerce get_product --client-id --product-id [--60] --session-id "<session-id>" --output json`
  Retrieves a single product by ID from WooCommerce
- `robomotion woocommerce update_product --client-id --product-id --data [--60] --session-id "<session-id>" --output json`
  Updates an existing product in WooCommerce
- `robomotion woocommerce delete_product --client-id --product-id [--60] --session-id "<session-id>" --output json`
  Deletes a product from WooCommerce
- `robomotion woocommerce list_products --client-id [--search] [--status] [--category] [--10] [--1] [--order-by] [--order] [--60] --session-id "<session-id>" --output json`
  Lists products from the WooCommerce store
- `robomotion woocommerce create_order --client-id --data [--status] [--payment-method] [--60] --session-id "<session-id>" --output json`
  Creates a new order in WooCommerce
- `robomotion woocommerce get_order --client-id --order-id [--60] --session-id "<session-id>" --output json`
  Retrieves a single order by ID from WooCommerce
- `robomotion woocommerce update_order --client-id --order-id --data [--60] --session-id "<session-id>" --output json`
  Updates an existing order in WooCommerce
- `robomotion woocommerce delete_order --client-id --order-id [--60] --session-id "<session-id>" --output json`
  Deletes an order from WooCommerce
- `robomotion woocommerce list_orders --client-id [--status] [--search] [--10] [--1] [--order-by] [--order] [--60] --session-id "<session-id>" --output json`
  Lists orders from the WooCommerce store
- `robomotion woocommerce create_customer --client-id --email --first-name --last-name --data [--60] --session-id "<session-id>" --output json`
  Creates a new customer in WooCommerce
- `robomotion woocommerce get_customer --client-id --customer-id [--60] --session-id "<session-id>" --output json`
  Retrieves a single customer by ID from WooCommerce
- `robomotion woocommerce update_customer --client-id --customer-id --data [--60] --session-id "<session-id>" --output json`
  Updates an existing customer in WooCommerce
- `robomotion woocommerce delete_customer --client-id --customer-id [--60] --session-id "<session-id>" --output json`
  Deletes a customer from WooCommerce
- `robomotion woocommerce list_customers --client-id [--search] [--role] [--10] [--1] [--order-by] [--order] [--60] --session-id "<session-id>" --output json`
  Lists customers from the WooCommerce store
- `robomotion woocommerce create_coupon --client-id --coupon-code --amount --data [--discount-type] [--60] --session-id "<session-id>" --output json`
  Creates a new coupon in WooCommerce
- `robomotion woocommerce get_coupon --client-id --coupon-id [--60] --session-id "<session-id>" --output json`
  Retrieves a single coupon by ID from WooCommerce
- `robomotion woocommerce update_coupon --client-id --coupon-id --data [--60] --session-id "<session-id>" --output json`
  Updates an existing coupon in WooCommerce
- `robomotion woocommerce delete_coupon --client-id --coupon-id [--60] --session-id "<session-id>" --output json`
  Deletes a coupon from WooCommerce
- `robomotion woocommerce list_coupons --client-id [--search] [--10] [--1] [--order-by] [--order] [--60] --session-id "<session-id>" --output json`
  Lists coupons from the WooCommerce store

## Environment
- ROBOMOTION_API_TOKEN (if vault credentials are needed)
