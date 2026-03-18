---
name: "ethereum"
description: "Ethereum blockchain client — interact with smart contracts, send transactions, check balances, and monitor blocks/events. Supports ERC-20 tokens, ENS resolution, gas estimation, and event watching via `robomotion ethereum`. Do NOT use for Binance, centralized exchanges, or other blockchains."
---

# Ethereum

The `robomotion ethereum` CLI connects to the Ethereum blockchain for Web3 operations. It checks ETH and ERC-20 balances, sends transactions, deploys and calls smart contracts, resolves ENS names, estimates gas, watches events, and monitors blocks.

## When to use
- Check ETH or ERC-20 token balances for wallet addresses
- Send ETH transactions or call smart contract methods
- Deploy smart contracts and interact with existing ones
- Resolve ENS names, estimate gas, and watch blockchain events

## Prerequisites
- `robomotion` CLI installed
- Package installed: `robomotion install ethereum`
- Ethereum RPC endpoint (Infura, Alchemy, etc.) configured via Robomotion vault

## IMPORTANT: Session Mode Required for Multi-Step Operations
Each CLI command runs as a **separate process** — connection IDs from `connect` do NOT persist across calls.
You MUST use `--session` on `connect` and pass `--session-id` to all subsequent commands.

## Workflow
1. Install (once): `robomotion install ethereum`
2. Connect with session:
   ```
   robomotion ethereum eth_connect --session --output json
   # → {"outClientId":"<client-id>","session_id":"<session-id>"}
   ```
3. Use the returned `client-id` and `session-id` in all subsequent commands:
   ```
   robomotion ethereum eth_get_balance --client-id "<client-id>" --address <addr> --session-id "<session-id>" --output json
   ```
4. Disconnect when done:
   ```
   robomotion ethereum eth_disconnect --client-id "<client-id>" --session-id "<session-id>" --output json
   ```

**Always** append `--output json` to get structured JSON results.

## Commands Reference
- `robomotion ethereum ethereum_abi_method --abi --abi-method --args --output json`
  Encode a smart contract method call using ABI
- `robomotion ethereum ethereum_get_balance --client-id --wallet [--4] --session-id "<session-id>" --output json`
  Get the balance of a wallet address on the blockchain
- `robomotion ethereum ethereum_call --client-id --trx-id --wallet --contract --session-id "<session-id>" --output json`
  Call a smart contract method without sending a transaction (read-only)
- `robomotion ethereum ethereum_cancel_transaction --client-id --hash --gas-price --gas --session-id "<session-id>" --output json`
  Cancel a pending transaction by sending a replacement with zero value
- `robomotion ethereum ethereum_create_client --rpc-url --chain-id --output json`
  Create a Ethereum client connection to a blockchain RPC endpoint
- `robomotion ethereum ethereum_decode --abi --abi-method --data [--input/output] --output json`
  Decode transaction input or output data using ABI
- `robomotion ethereum ethereum_estimate_gas --client-id --trx-id --wallet --to --value --session-id "<session-id>" --output json`
  Estimate the gas required for a transaction
- `robomotion ethereum ethereum_estimate_gas_price --client-id --session-id "<session-id>" --output json`
  Get the current gas price from the blockchain network
- `robomotion ethereum ethereum_export_wallet --keystore-file --output json`
  Export a wallet to a keystore file
- `robomotion ethereum ethereum_from_wei --amount [--unit] [--4] --output json`
  Convert amount from WEI or GWEI to ETH
- `robomotion ethereum ethereum_generate_wallet --output json`
  Generate a new cryptocurrency wallet with encrypted private key
- `robomotion ethereum ethereum_get_transaction --client-id --hash --session-id "<session-id>" --output json`
  Get transaction details by hash
- `robomotion ethereum ethereum_get_wallet_address --output json`
  Get wallet address from encrypted private key
- `robomotion ethereum ethereum_import_wallet --keystore-file --output json`
  Import a wallet from a keystore file
- `robomotion ethereum ethereum_increase_gas --client-id --hash --gas-price --gas --session-id "<session-id>" --output json`
  Increase gas price of a pending transaction to speed it up
- `robomotion ethereum ethereum_parse_abi --abi-file --output json`
  Parse a smart contract ABI file for use with other Ethereum nodes
- `robomotion ethereum ethereum_pending_transactions --client-id --new-pending-transactions [--abi] [--methods] [--to] [--http-provider-url] --session-id "<session-id>" --output json`
  Subscribe to pending transactions on the blockchain
- `robomotion ethereum ethereum_send_transaction --client-id --trx-id --to --gas-price --gas --value --nonce --session-id "<session-id>" --output json`
  Sign and send a transaction to the blockchain
- `robomotion ethereum ethereum_subscribe --client-id --contract --abi --event-name --params --session-id "<session-id>" --output json`
  Subscribe to blockchain events from a smart contract
- `robomotion ethereum ethereum_to_wei --amount [--unit] --output json`
  Convert amount from ETH to WEI or GWEI
- `robomotion ethereum ethereum_transaction_receipt --client-id --hash --session-id "<session-id>" --output json`
  Get transaction receipt by hash
- `robomotion ethereum ethereum_transfer --wallet --to --amount --output json`
  Create a transfer transaction to send cryptocurrency to another address

## Environment
- ROBOMOTION_API_TOKEN (if vault credentials are needed)
