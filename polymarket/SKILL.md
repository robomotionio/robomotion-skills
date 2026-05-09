---
name: polymarket
summary: Query Polymarket prediction markets — events, prices, orderbooks, history. Read-only, no auth.
---

# Polymarket

Query prediction-market data from Polymarket using their public REST APIs. All endpoints are read-only and require zero authentication.

The skill ships `scripts/polymarket.py`, a stdlib-only CLI that wraps the three public APIs (Gamma for discovery, CLOB for prices/orderbooks/history, Data for trades) and prints clean Markdown.

## Capabilities

- Search events / markets by keyword
- List trending markets
- Fetch full event or market details
- Real-time price + orderbook for a market token
- Price history at configurable granularity
- Recent trade history (per-market or global)

## Usage

```sh
python3 ${SKILL_DIR}/scripts/polymarket.py search "bitcoin"
python3 ${SKILL_DIR}/scripts/polymarket.py trending --limit 10
python3 ${SKILL_DIR}/scripts/polymarket.py market "<market-slug>"
python3 ${SKILL_DIR}/scripts/polymarket.py event "<event-slug>"
python3 ${SKILL_DIR}/scripts/polymarket.py price "<token-id>"
python3 ${SKILL_DIR}/scripts/polymarket.py book "<token-id>"
python3 ${SKILL_DIR}/scripts/polymarket.py history "<condition-id>" --interval all --fidelity 50
python3 ${SKILL_DIR}/scripts/polymarket.py trades --limit 10 --market "<condition-id>"
```

Full endpoint reference (curl examples for fields the CLI doesn't surface) lives in `references/api-endpoints.md` — `cat` it when you need a query the CLI doesn't wrap.

## When to use

- "What are the odds of X happening, according to Polymarket?"
- "Show me trending political prediction markets"
- "Price history of the BTC-100k market over the last month"
- "Recent trades on the election market"

## When NOT to use

- For placing trades — this is read-only. Polymarket trading requires a Web3 wallet + on-chain signing, out of scope for this skill.
- For non-Polymarket markets (Kalshi, Manifold, PredictIt — use those platforms' own APIs)
- As a probability oracle — market prices reflect market sentiment, not ground-truth probability. Surface them as such.

## Operating notes

- **Events vs. markets:** events contain one or more markets (1:many). For "Will X win the election?" the event has markets per candidate; each market is a binary Yes/No.
- **Prices ARE probabilities:** a market price of 0.65 means the market thinks 65% likely. Always between 0.00 and 1.00.
- `outcomePrices` is a JSON-encoded array like `["0.80", "0.20"]` (Yes, No).
- `clobTokenIds` is a JSON-encoded array of two token IDs `[Yes, No]` for price/book queries.
- `conditionId` is a hex string used for price-history queries.
- Volume is denominated in USDC (US dollars).
- The Gamma API can return hundreds of events for a broad search; use `--limit` aggressively or filter by `closed=false` to focus on active markets.

## Attribution

The bundled `polymarket.py` and `references/api-endpoints.md` are adapted from the [Nous Hermes Agent](https://github.com/NousResearch/hermes-agent) skill of the same name (MIT).
