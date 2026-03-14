---
name: "stripe-payments"
description: "Use when the user wants to call the Robomotion Stripe package to manage payments, customers, or subscriptions via the `robomotion stripe` CLI. Do NOT use for PayPal, Square, or other payment processors."
---

# Stripe Payments Skill

## When to use
- Create or manage Stripe customers
- Process payments or charges via Stripe
- Manage Stripe subscriptions and invoices
- List or search Stripe transactions

## Prerequisites
- `robomotion` CLI installed
- Package installed: `robomotion install stripe`
- Credentials configured via Robomotion vault or environment variables

## Workflow
1. Install the package: `robomotion install stripe`
2. Run commands: `robomotion stripe <command> [flags]`

## Commands Reference
- `robomotion stripe stripe_connect`
  Connects to Stripe API and returns a client ID for subsequent operations
- `robomotion stripe stripe_disconnect --client-id`
  Closes the Stripe connection and releases resources
- `robomotion stripe stripe_create_customer --client-id --name --email [--phone] [--description] --metadata`
  Creates a new customer in Stripe
- `robomotion stripe stripe_get_customer --client-id --customer-id`
  Retrieves a customer by ID from Stripe
- `robomotion stripe stripe_update_customer --client-id --customer-id [--name] [--email] [--phone] [--description]`
  Updates an existing customer in Stripe
- `robomotion stripe stripe_delete_customer --client-id --customer-id`
  Permanently deletes a customer from Stripe
- `robomotion stripe stripe_list_customers --client-id [--100] [--filter-by-email]`
  Lists customers from Stripe with optional filtering
- `robomotion stripe stripe_search_customers --client-id --query [--100]`
  Searches customers using Stripe Search Query Language
- `robomotion stripe stripe_create_payment_intent --client-id --amount --currency [--customer-id] [--description] [--payment-method] [--receipt-email] --metadata`
  Creates a new payment intent in Stripe
- `robomotion stripe stripe_get_payment_intent --client-id --payment-intent-id`
  Retrieves a payment intent by ID from Stripe
- `robomotion stripe stripe_confirm_payment_intent --client-id --payment-intent-id [--payment-method]`
  Confirms a payment intent to initiate the payment
- `robomotion stripe stripe_list_payment_intents --client-id [--100] [--customer-id]`
  Lists payment intents from Stripe with optional filtering
- `robomotion stripe stripe_create_invoice --client-id --customer-id [--description] [--collection-method] --metadata`
  Creates a new draft invoice for a customer
- `robomotion stripe stripe_get_invoice --client-id --invoice-id`
  Retrieves an invoice by ID from Stripe
- `robomotion stripe stripe_finalize_invoice --client-id --invoice-id`
  Finalizes a draft invoice so it can be paid
- `robomotion stripe stripe_list_invoices --client-id [--100] [--customer-id] [--status]`
  Lists invoices from Stripe with optional filtering
- `robomotion stripe stripe_create_subscription --client-id --customer-id --price-id [--trial-period-days] --metadata`
  Creates a new subscription for a customer
- `robomotion stripe stripe_cancel_subscription --client-id --subscription-id`
  Cancels an existing subscription
- `robomotion stripe stripe_get_subscription --client-id --subscription-id`
  Retrieves a subscription by ID from Stripe
- `robomotion stripe stripe_list_subscriptions --client-id [--100] [--customer-id] [--status]`
  Lists subscriptions from Stripe with optional filtering
- `robomotion stripe stripe_create_product --client-id --name [--description] --metadata`
  Creates a new product in Stripe
- `robomotion stripe stripe_get_product --client-id --product-id`
  Retrieves a product by ID from Stripe
- `robomotion stripe stripe_list_products --client-id [--100] [--active]`
  Lists products from Stripe
- `robomotion stripe stripe_create_price --client-id --product-id --unit-amount --currency [--billing-interval] --metadata`
  Creates a new price for a product in Stripe
- `robomotion stripe stripe_list_prices --client-id [--100] [--product-id] [--active]`
  Lists prices from Stripe with optional filtering
- `robomotion stripe stripe_get_charge --client-id --charge-id`
  Retrieves a charge by ID from Stripe
- `robomotion stripe stripe_list_charges --client-id [--100] [--customer-id]`
  Lists charges from Stripe with optional filtering
- `robomotion stripe stripe_create_refund --client-id --payment-intent-id [--amount] [--reason] --metadata`
  Creates a refund for a charge or payment intent
- `robomotion stripe stripe_list_refunds --client-id [--100] [--payment-intent-id]`
  Lists refunds from Stripe with optional filtering
- `robomotion stripe stripe_get_balance --client-id`
  Retrieves the current account balance from Stripe

## Environment
- ROBOMOTION_API_TOKEN (if vault credentials are needed)
