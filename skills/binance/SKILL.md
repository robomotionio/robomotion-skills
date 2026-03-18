---
name: "binance"
description: "Binance cryptocurrency exchange — trade crypto, check prices, view balances, and access market data. Supports limit/market/stop orders, price history, deposits, and withdrawals via `robomotion binance`. Do NOT use for Gate.io, Coinbase, or other crypto exchanges."
---

# Binance

The `robomotion binance` CLI connects to the Binance exchange for cryptocurrency trading and market data. It supports placing limit, market, and stop-loss orders; checking balances and prices; downloading price history as CSV; and viewing deposits, withdrawals, and recent trades.

## When to use
- Get current prices, 24h stats, or historical candlestick data for trading pairs
- Place limit, market, or stop-loss orders on Binance
- Check account balances, open orders, deposits, and withdrawals
- List all trading pairs or recent trades for a symbol

## Prerequisites
- `robomotion` CLI installed
- Package installed: `robomotion install binance`
- Binance API key and secret configured via Robomotion vault

## IMPORTANT: Session Mode Required for Multi-Step Operations
Each CLI command runs as a **separate process** — connection IDs from `connect` do NOT persist across calls.
You MUST use `--session` on `connect` and pass `--session-id` to all subsequent commands.

## Workflow
1. Install (once): `robomotion install binance`
2. Connect with session:
   ```
   robomotion binance binance_connect --session --output json
   # → {"outClientId":"<client-id>","session_id":"<session-id>"}
   ```
3. Use the returned `client-id` and `session-id` in all subsequent commands:
   ```
   robomotion binance binance_get_price --client-id "<client-id>" --bnbusdt --session-id "<session-id>" --output json
   ```
4. Disconnect when done:
   ```
   robomotion binance binance_disconnect --client-id "<client-id>" --session-id "<session-id>" --output json
   ```

**Always** append `--output json` to get structured JSON results.

## Commands Reference
- `robomotion binance binance_buy_order --client-id --bnbusdt --order-quantity --order-price --session-id "<session-id>" --output json`
  Place a limit buy order on Binance
- `robomotion binance binance_cancel_order --client-id --order-id --bnbusdt --session-id "<session-id>" --output json`
  Cancel an open order on Binance
- `robomotion binance binance_connect --session --output json`
  Connect to Binance exchange using API credentials
- `robomotion binance binance_disconnect --client-id --session-id "<session-id>" --output json`
  Disconnect from Binance exchange
- `robomotion binance binance_get_balance --client-id --currency [--wallet-type] --session-id "<session-id>" --output json`
  Get account balance for a specific currency or all currencies
- `robomotion binance binance_get_coin_detail --client-id --bnb --session-id "<session-id>" --output json`
  Get detailed information about a cryptocurrency
- `robomotion binance binance_get_deposit_address --client-id --usdt --bsc --session-id "<session-id>" --output json`
  Get deposit address for a cryptocurrency on a specific network
- `robomotion binance binance_get_order --client-id --order-id --bnbusdt --session-id "<session-id>" --output json`
  Get details of a specific order on Binance
- `robomotion binance binance_get_price --client-id --bnbusdt --session-id "<session-id>" --output json`
  Get current average price for a trading pair
- `robomotion binance binance_get_price_change_info --client-id --btcusdt --session-id "<session-id>" --output json`
  Get 24-hour price change statistics for a trading pair
- `robomotion binance binance_get_price_history --client-id --bnbusdt --10 --start-date --end-date --save-path --0-5 --custom-interval [--interval] --session-id "<session-id>" --output json`
  Get historical price data (klines/candlesticks) for a trading pair and save to CSV
- `robomotion binance binance_list_deposits --client-id --5 --session-id "<session-id>" --output json`
  List recent deposit history for the account
- `robomotion binance binance_list_my_orders --client-id --session-id "<session-id>" --output json`
  List all open orders for the account
- `robomotion binance binance_list_orders --client-id --bnbusdt --10 [--order-type] --session-id "<session-id>" --output json`
  List current order book (bids or asks) for a trading pair
- `robomotion binance binance_sell_order --client-id --currency-pair --order-quantity --order-price --session-id "<session-id>" --output json`
  Place a limit sell order on Binance
- `robomotion binance binance_stop_order --client-id --bnbusdt --order-quantity --stop-price --price --session-id "<session-id>" --output json`
  Place a stop-loss limit order on Binance
- `robomotion binance binance_list_withdraws --client-id --5 --session-id "<session-id>" --output json`
  List recent withdrawal history for the account
- `robomotion binance binance_list_recent_trades --client-id --bnbusdt --5 --session-id "<session-id>" --output json`
  List recent trades for a trading pair
- `robomotion binance binance_market_order --client-id --bnbusdt --order-amount [--unit-type] [--order-type] --session-id "<session-id>" --output json`
  Place a market order (buy or sell) at current market price
- `robomotion binance binance_list_all_pairs --client-id --session-id "<session-id>" --output json`
  List all available trading pairs on Binance

## Environment
- ROBOMOTION_API_TOKEN (if vault credentials are needed)
