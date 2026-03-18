---
name: "polymarket"
description: "Polymarket prediction markets — access market data, event details, pricing, orderbooks, positions, and trading analytics. Supports market research and position tracking via `robomotion polymarket`. Do NOT use for Binance, stock trading, or other financial platforms."
---

# Polymarket

The `robomotion polymarket` CLI connects to Polymarket for prediction market data and analytics. It retrieves market listings, event details, current pricing/probabilities, orderbook depth, positions, trades, and spread analytics.

## When to use
- Browse prediction markets and get current pricing/probabilities
- View orderbook depth and market spread analytics
- Track positions and trade history
- Search for events and market outcomes

## Prerequisites
- `robomotion` CLI installed
- Package installed: `robomotion install polymarket`
- Polymarket API access configured via Robomotion vault

## Workflow
1. Install: `robomotion install polymarket`
2. Connect: `robomotion polymarket polymarket_connect` → returns a `client-id`
3. List markets: `robomotion polymarket polymarket_get_markets --client-id <id>`
4. Get price: `robomotion polymarket polymarket_get_price --client-id <id> --token-id <token>`
5. Disconnect: `robomotion polymarket polymarket_disconnect --client-id <id>`

## Commands Reference
- `robomotion polymarket polymarket_connect`
  Connects to Polymarket APIs and returns a client ID
- `robomotion polymarket polymarket_disconnect --client-id`
  Closes the Polymarket connection and releases resources
- `robomotion polymarket polymarket_get_markets --client-id --tag-id [--25] [--0] [--30] [--active] [--closed] [--sort-by] [--sort-direction]`
  Retrieves a list of Polymarket prediction markets with filtering and pagination
- `robomotion polymarket polymarket_get_market --client-id --market-id --slug [--30]`
  Retrieves details for a specific Polymarket market by ID or slug
- `robomotion polymarket polymarket_get_events --client-id --tag-id [--25] [--0] [--30] [--active] [--closed] [--sort-direction]`
  Retrieves a list of Polymarket events with filtering and pagination
- `robomotion polymarket polymarket_get_event --client-id --event-id [--30]`
  Retrieves details for a specific Polymarket event by ID
- `robomotion polymarket polymarket_search --client-id --query [--30]`
  Full-text search across Polymarket events and markets
- `robomotion polymarket polymarket_get_orderbook --client-id --token-id [--30]`
  Retrieves the order book (bid/ask data) for a specific token
- `robomotion polymarket polymarket_get_price --client-id --token-id [--side] [--30]`
  Retrieves the current best price for a token on a specific side (buy/sell)
- `robomotion polymarket polymarket_get_midpoint --client-id --token-id [--30]`
  Retrieves the midpoint price (average of best bid and ask) for a token
- `robomotion polymarket polymarket_get_spread --client-id --token-id [--30]`
  Retrieves the bid-ask spread for a token
- `robomotion polymarket polymarket_get_price_history --client-id --token-id --start-timestamp --end-timestamp [--interval] [--60] [--30]`
  Retrieves historical price data for a token with configurable time intervals
- `robomotion polymarket polymarket_get_positions --client-id --wallet-address [--25] [--0] [--30]`
  Retrieves current positions for a wallet address
- `robomotion polymarket polymarket_get_trades --client-id --wallet-address [--25] [--0] [--30]`
  Retrieves trade history for a wallet address
- `robomotion polymarket polymarket_get_leaderboard --client-id [--time-period] [--25] [--0] [--30]`
  Retrieves the Polymarket trader leaderboard ranked by PnL or volume

## Environment
- ROBOMOTION_API_TOKEN (if vault credentials are needed)
