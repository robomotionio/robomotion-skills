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

## Workflow
1. Install: `robomotion install gateio`
2. Connect: `robomotion gateio gateio_connect` → returns a `client-id`
3. Get price: `robomotion gateio gateio_get_spot_price --client-id <id> --btc_usdt`
4. Place order: `robomotion gateio gateio_buy_limit_order --client-id <id> --btc_usdt --amount <amt> --price <price>`
5. Disconnect: `robomotion gateio gateio_disconnect --client-id <id>`

## Commands Reference
- `robomotion gateio gateio_buy_order --client-id --currency-pair --order-amount --order-price --base-url`
  Place a buy order on Gate.io exchange
- `robomotion gateio gateio_cancel_order --client-id --order-id --currency-pair --base-url`
  Cancel an existing order on Gate.io
- `robomotion gateio gateio_connect --base-url`
  Connect to Gate.io exchange using API credentials
- `robomotion gateio gateio_disconnect --client-id`
  Disconnect from Gate.io and release resources
- `robomotion gateio gateio_get_balance --client-id --currency --base-url`
  Get account balance for a specific currency on Gate.io
- `robomotion gateio gateio_get_price --client-id --btc-usdt --base-url`
  Get current price for a currency pair on Gate.io
- `robomotion gateio gateio_list_my_orders --client-id --base-url`
  List all open orders on Gate.io
- `robomotion gateio gateio_list_orders --btc-usdt --10 [--order-type]`
  List order book (buy/sell orders) for a currency pair
- `robomotion gateio gateio_list_pairs`
  List all available currency pairs on Gate.io
- `robomotion gateio gateio_sell_order --client-id --currency-pair --order-amount --order-price --base-url`
  Place a sell order on Gate.io exchange
- `robomotion gateio gateio_get_fee --client-id --btc-usdt --base-url`
  Get trading fee for a currency pair on Gate.io
- `robomotion gateio gateio_get_order --client-id --order-id --currency-pair --base-url`
  Get details of a specific order on Gate.io
- `robomotion gateio gateio_get_deposit_address --client-id --usdt --base-url`
  Get deposit address for a specific currency on Gate.io

## Environment
- ROBOMOTION_API_TOKEN (if vault credentials are needed)
