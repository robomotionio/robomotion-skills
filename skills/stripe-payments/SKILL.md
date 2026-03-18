---
name: "stripe-payments"
description: "Stripe — manage payments, customers, subscriptions, invoices, and products. Supports charge creation, refunds, and billing lifecycle via `robomotion stripe`. Do NOT use for PayPal, Square, or other payment processors."
---

# Stripe Payments

The `robomotion stripe` CLI connects to Stripe for payment processing and billing management. It creates charges, manages customers and subscriptions, handles invoices and refunds, and manages products and pricing.

## When to use
- Create charges and process payments
- Manage customers, subscriptions, and billing
- Handle invoices and refunds
- Manage products and pricing plans

## Prerequisites
- `robomotion` CLI installed
- Package installed: `robomotion install stripe`
- Stripe API key configured via Robomotion vault

## IMPORTANT: Session Mode Required for Multi-Step Operations
Each CLI command runs as a **separate process** — connection IDs from `connect` do NOT persist across calls.
You MUST use `--session` on `connect` and pass `--session-id` to all subsequent commands.

## Workflow
1. Install (once): `robomotion install stripe`
2. Connect with session:
   ```
   robomotion stripe connect --session --output json
   # → {"outClientId":"<client-id>","session_id":"<session-id>"}
   ```
3. Use the returned `client-id` and `session-id` in all subsequent commands:
   ```
   robomotion stripe create_charge --client-id "<client-id>" --amount <amount> --currency <cur> --session-id "<session-id>" --output json
   ```
4. Disconnect when done:
   ```
   robomotion stripe disconnect --client-id "<client-id>" --session-id "<session-id>" --output json
   ```

**Always** append `--output json` to get structured JSON results.

## Commands Reference
- `robomotion stripe stripe_connect --session --output json`
  Connects to Stripe API and returns a client ID for subsequent operations
- `robomotion stripe stripe_disconnect --client-id --session-id "<session-id>" --output json`
  Closes the Stripe connection and releases resources
- `robomotion stripe stripe_create_customer --client-id --name --email [--phone] [--description] --metadata --session-id "<session-id>" --output json`
  Creates a new customer in Stripe
- `robomotion stripe stripe_get_customer --client-id --customer-id --session-id "<session-id>" --output json`
  Retrieves a customer by ID from Stripe
- `robomotion stripe stripe_update_customer --client-id --customer-id [--name] [--email] [--phone] [--description] --session-id "<session-id>" --output json`
  Updates an existing customer in Stripe
- `robomotion stripe stripe_delete_customer --client-id --customer-id --session-id "<session-id>" --output json`
  Permanently deletes a customer from Stripe
- `robomotion stripe stripe_list_customers --client-id [--100] [--filter-by-email] --session-id "<session-id>" --output json`
  Lists customers from Stripe with optional filtering
- `robomotion stripe stripe_search_customers --client-id --query [--100] --session-id "<session-id>" --output json`
  Searches customers using Stripe Search Query Language
- `robomotion stripe stripe_create_payment_intent --client-id --amount --currency [--customer-id] [--description] [--payment-method] [--receipt-email] --metadata --session-id "<session-id>" --output json`
  Creates a new payment intent in Stripe
- `robomotion stripe stripe_get_payment_intent --client-id --payment-intent-id --session-id "<session-id>" --output json`
  Retrieves a payment intent by ID from Stripe
- `robomotion stripe stripe_confirm_payment_intent --client-id --payment-intent-id [--payment-method] --session-id "<session-id>" --output json`
  Confirms a payment intent to initiate the payment
- `robomotion stripe stripe_list_payment_intents --client-id [--100] [--customer-id] --session-id "<session-id>" --output json`
  Lists payment intents from Stripe with optional filtering
- `robomotion stripe stripe_create_invoice --client-id --customer-id [--description] [--collection-method] --metadata --session-id "<session-id>" --output json`
  Creates a new draft invoice for a customer
- `robomotion stripe stripe_get_invoice --client-id --invoice-id --session-id "<session-id>" --output json`
  Retrieves an invoice by ID from Stripe
- `robomotion stripe stripe_finalize_invoice --client-id --invoice-id --session-id "<session-id>" --output json`
  Finalizes a draft invoice so it can be paid
- `robomotion stripe stripe_list_invoices --client-id [--100] [--customer-id] [--status] --session-id "<session-id>" --output json`
  Lists invoices from Stripe with optional filtering
- `robomotion stripe stripe_create_subscription --client-id --customer-id --price-id [--trial-period-days] --metadata --session-id "<session-id>" --output json`
  Creates a new subscription for a customer
- `robomotion stripe stripe_cancel_subscription --client-id --subscription-id --session-id "<session-id>" --output json`
  Cancels an existing subscription
- `robomotion stripe stripe_get_subscription --client-id --subscription-id --session-id "<session-id>" --output json`
  Retrieves a subscription by ID from Stripe
- `robomotion stripe stripe_list_subscriptions --client-id [--100] [--customer-id] [--status] --session-id "<session-id>" --output json`
  Lists subscriptions from Stripe with optional filtering
- `robomotion stripe stripe_create_product --client-id --name [--description] --metadata --session-id "<session-id>" --output json`
  Creates a new product in Stripe
- `robomotion stripe stripe_get_product --client-id --product-id --session-id "<session-id>" --output json`
  Retrieves a product by ID from Stripe
- `robomotion stripe stripe_list_products --client-id [--100] [--active] --session-id "<session-id>" --output json`
  Lists products from Stripe
- `robomotion stripe stripe_create_price --client-id --product-id --unit-amount --currency [--billing-interval] --metadata --session-id "<session-id>" --output json`
  Creates a new price for a product in Stripe
- `robomotion stripe stripe_list_prices --client-id [--100] [--product-id] [--active] --session-id "<session-id>" --output json`
  Lists prices from Stripe with optional filtering
- `robomotion stripe stripe_get_charge --client-id --charge-id --session-id "<session-id>" --output json`
  Retrieves a charge by ID from Stripe
- `robomotion stripe stripe_list_charges --client-id [--100] [--customer-id] --session-id "<session-id>" --output json`
  Lists charges from Stripe with optional filtering
- `robomotion stripe stripe_create_refund --client-id --payment-intent-id [--amount] [--reason] --metadata --session-id "<session-id>" --output json`
  Creates a refund for a charge or payment intent
- `robomotion stripe stripe_list_refunds --client-id [--100] [--payment-intent-id] --session-id "<session-id>" --output json`
  Lists refunds from Stripe with optional filtering
- `robomotion stripe stripe_get_balance --client-id --session-id "<session-id>" --output json`
  Retrieves the current account balance from Stripe

## Environment
- ROBOMOTION_API_TOKEN (if vault credentials are needed)
