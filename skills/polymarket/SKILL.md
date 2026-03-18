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

## IMPORTANT: Session Mode Required for Multi-Step Operations
Each CLI command runs as a **separate process** — connection IDs from `connect` do NOT persist across calls.
You MUST use `--session` on `connect` and pass `--session-id` to all subsequent commands.

## Workflow
1. Install (once): `robomotion install polymarket`
2. Connect with session:
   ```
   robomotion polymarket polymarket_connect --session --output json
   # → {"outClientId":"<client-id>","session_id":"<session-id>"}
   ```
3. Use the returned `client-id` and `session-id` in all subsequent commands:
   ```
   robomotion polymarket polymarket_get_markets --client-id "<client-id>" --session-id "<session-id>" --output json
   ```
4. Disconnect when done:
   ```
   robomotion polymarket polymarket_disconnect --client-id "<client-id>" --session-id "<session-id>" --output json
   ```

**Always** append `--output json` to get structured JSON results.

## Commands Reference
- `robomotion polymarket polymarket_connect --session --output json`
  Connects to Polymarket APIs and returns a client ID
- `robomotion polymarket polymarket_disconnect --client-id --session-id "<session-id>" --output json`
  Closes the Polymarket connection and releases resources
- `robomotion polymarket polymarket_get_markets --client-id --tag-id [--25] [--0] [--30] [--active] [--closed] [--sort-by] [--sort-direction] --session-id "<session-id>" --output json`
  Retrieves a list of Polymarket prediction markets with filtering and pagination
- `robomotion polymarket polymarket_get_market --client-id --market-id --slug [--30] --session-id "<session-id>" --output json`
  Retrieves details for a specific Polymarket market by ID or slug
- `robomotion polymarket polymarket_get_events --client-id --tag-id [--25] [--0] [--30] [--active] [--closed] [--sort-direction] --session-id "<session-id>" --output json`
  Retrieves a list of Polymarket events with filtering and pagination
- `robomotion polymarket polymarket_get_event --client-id --event-id [--30] --session-id "<session-id>" --output json`
  Retrieves details for a specific Polymarket event by ID
- `robomotion polymarket polymarket_search --client-id --query [--30] --session-id "<session-id>" --output json`
  Full-text search across Polymarket events and markets
- `robomotion polymarket polymarket_get_orderbook --client-id --token-id [--30] --session-id "<session-id>" --output json`
  Retrieves the order book (bid/ask data) for a specific token
- `robomotion polymarket polymarket_get_price --client-id --token-id [--side] [--30] --session-id "<session-id>" --output json`
  Retrieves the current best price for a token on a specific side (buy/sell)
- `robomotion polymarket polymarket_get_midpoint --client-id --token-id [--30] --session-id "<session-id>" --output json`
  Retrieves the midpoint price (average of best bid and ask) for a token
- `robomotion polymarket polymarket_get_spread --client-id --token-id [--30] --session-id "<session-id>" --output json`
  Retrieves the bid-ask spread for a token
- `robomotion polymarket polymarket_get_price_history --client-id --token-id --start-timestamp --end-timestamp [--interval] [--60] [--30] --session-id "<session-id>" --output json`
  Retrieves historical price data for a token with configurable time intervals
- `robomotion polymarket polymarket_get_positions --client-id --wallet-address [--25] [--0] [--30] --session-id "<session-id>" --output json`
  Retrieves current positions for a wallet address
- `robomotion polymarket polymarket_get_trades --client-id --wallet-address [--25] [--0] [--30] --session-id "<session-id>" --output json`
  Retrieves trade history for a wallet address
- `robomotion polymarket polymarket_get_leaderboard --client-id [--time-period] [--25] [--0] [--30] --session-id "<session-id>" --output json`
  Retrieves the Polymarket trader leaderboard ranked by PnL or volume

## Environment
- ROBOMOTION_API_TOKEN (if vault credentials are needed)
