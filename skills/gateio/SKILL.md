---
name: "gateio"
description: "Gate.io cryptocurrency exchange — trade crypto, check prices, view orderbooks, and manage account balances. Supports market/limit orders, ticker data, and trading pair listing via `robomotion gateio`. Do NOT use for Binance, Coinbase, or other crypto exchanges."
---

# Gate.io

The `robomotion gateio` CLI connects to the Gate.io exchange for cryptocurrency trading and market data. It supports checking spot prices and 24h tickers, viewing orderbooks, placing market and limit orders, and managing account balances.

## When to use
- Get current prices and 24h ticker statistics for trading pairs
- View orderbook depth for any trading pair
- Place limit or market buy/sell orders on Gate.io
- Check account balances and list available trading pairs

## Prerequisites
- `robomotion` CLI installed
- Package installed: `robomotion install gateio`
- Gate.io API key and secret configured via Robomotion vault

## IMPORTANT: Session Mode Required for Multi-Step Operations
Each CLI command runs as a **separate process** — connection IDs from `connect` do NOT persist across calls.
You MUST use `--session` on `connect` and pass `--session-id` to all subsequent commands.

## Workflow
1. Install (once): `robomotion install gateio`
2. Connect with session:
   ```
   robomotion gateio gateio_connect --session --output json
   # → {"outClientId":"<client-id>","session_id":"<session-id>"}
   ```
3. Use the returned `client-id` and `session-id` in all subsequent commands:
   ```
   robomotion gateio gateio_get_spot_price --client-id "<client-id>" --btc_usdt --session-id "<session-id>" --output json
   ```
4. Disconnect when done:
   ```
   robomotion gateio gateio_disconnect --client-id "<client-id>" --session-id "<session-id>" --output json
   ```

**Always** append `--output json` to get structured JSON results.

## Commands Reference
- `robomotion gateio gateio_buy_order --client-id --currency-pair --order-amount --order-price --base-url --session-id "<session-id>" --output json`
  Place a buy order on Gate.io exchange
- `robomotion gateio gateio_cancel_order --client-id --order-id --currency-pair --base-url --session-id "<session-id>" --output json`
  Cancel an existing order on Gate.io
- `robomotion gateio gateio_connect --base-url --session --output json`
  Connect to Gate.io exchange using API credentials
- `robomotion gateio gateio_disconnect --client-id --session-id "<session-id>" --output json`
  Disconnect from Gate.io and release resources
- `robomotion gateio gateio_get_balance --client-id --currency --base-url --session-id "<session-id>" --output json`
  Get account balance for a specific currency on Gate.io
- `robomotion gateio gateio_get_price --client-id --btc-usdt --base-url --session-id "<session-id>" --output json`
  Get current price for a currency pair on Gate.io
- `robomotion gateio gateio_list_my_orders --client-id --base-url --session-id "<session-id>" --output json`
  List all open orders on Gate.io
- `robomotion gateio gateio_list_orders --btc-usdt --10 [--order-type] --output json`
  List order book (buy/sell orders) for a currency pair
- `robomotion gateio gateio_list_pairs --output json`
  List all available currency pairs on Gate.io
- `robomotion gateio gateio_sell_order --client-id --currency-pair --order-amount --order-price --base-url --session-id "<session-id>" --output json`
  Place a sell order on Gate.io exchange
- `robomotion gateio gateio_get_fee --client-id --btc-usdt --base-url --session-id "<session-id>" --output json`
  Get trading fee for a currency pair on Gate.io
- `robomotion gateio gateio_get_order --client-id --order-id --currency-pair --base-url --session-id "<session-id>" --output json`
  Get details of a specific order on Gate.io
- `robomotion gateio gateio_get_deposit_address --client-id --usdt --base-url --session-id "<session-id>" --output json`
  Get deposit address for a specific currency on Gate.io

## Environment
- ROBOMOTION_API_TOKEN (if vault credentials are needed)
