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

## Workflow
1. Install: `robomotion install woocommerce`
2. Connect: `robomotion woocommerce woocommerce_connect` → returns a `client-id`
3. List products: `robomotion woocommerce woocommerce_list_products --client-id <id>`
4. Create order: `robomotion woocommerce woocommerce_create_order --client-id <id> --line-items <json>`
5. Disconnect: `robomotion woocommerce woocommerce_disconnect --client-id <id>`

## Commands Reference
- `robomotion woocommerce woocommerce_connect`
  Connects to a WooCommerce store and returns a client ID
- `robomotion woocommerce woocommerce_disconnect --client-id`
  Closes the WooCommerce connection and releases resources
- `robomotion woocommerce create_product --client-id --product-name --regular-price --data [--product-type] [--status] [--60]`
  Creates a new product in the WooCommerce store
- `robomotion woocommerce get_product --client-id --product-id [--60]`
  Retrieves a single product by ID from WooCommerce
- `robomotion woocommerce update_product --client-id --product-id --data [--60]`
  Updates an existing product in WooCommerce
- `robomotion woocommerce delete_product --client-id --product-id [--60]`
  Deletes a product from WooCommerce
- `robomotion woocommerce list_products --client-id [--search] [--status] [--category] [--10] [--1] [--order-by] [--order] [--60]`
  Lists products from the WooCommerce store
- `robomotion woocommerce create_order --client-id --data [--status] [--payment-method] [--60]`
  Creates a new order in WooCommerce
- `robomotion woocommerce get_order --client-id --order-id [--60]`
  Retrieves a single order by ID from WooCommerce
- `robomotion woocommerce update_order --client-id --order-id --data [--60]`
  Updates an existing order in WooCommerce
- `robomotion woocommerce delete_order --client-id --order-id [--60]`
  Deletes an order from WooCommerce
- `robomotion woocommerce list_orders --client-id [--status] [--search] [--10] [--1] [--order-by] [--order] [--60]`
  Lists orders from the WooCommerce store
- `robomotion woocommerce create_customer --client-id --email --first-name --last-name --data [--60]`
  Creates a new customer in WooCommerce
- `robomotion woocommerce get_customer --client-id --customer-id [--60]`
  Retrieves a single customer by ID from WooCommerce
- `robomotion woocommerce update_customer --client-id --customer-id --data [--60]`
  Updates an existing customer in WooCommerce
- `robomotion woocommerce delete_customer --client-id --customer-id [--60]`
  Deletes a customer from WooCommerce
- `robomotion woocommerce list_customers --client-id [--search] [--role] [--10] [--1] [--order-by] [--order] [--60]`
  Lists customers from the WooCommerce store
- `robomotion woocommerce create_coupon --client-id --coupon-code --amount --data [--discount-type] [--60]`
  Creates a new coupon in WooCommerce
- `robomotion woocommerce get_coupon --client-id --coupon-id [--60]`
  Retrieves a single coupon by ID from WooCommerce
- `robomotion woocommerce update_coupon --client-id --coupon-id --data [--60]`
  Updates an existing coupon in WooCommerce
- `robomotion woocommerce delete_coupon --client-id --coupon-id [--60]`
  Deletes a coupon from WooCommerce
- `robomotion woocommerce list_coupons --client-id [--search] [--10] [--1] [--order-by] [--order] [--60]`
  Lists coupons from the WooCommerce store

## Environment
- ROBOMOTION_API_TOKEN (if vault credentials are needed)
