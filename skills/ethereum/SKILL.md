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

## Workflow
1. Install: `robomotion install ethereum`
2. Connect: `robomotion ethereum eth_connect` → returns a `client-id`
3. Get balance: `robomotion ethereum eth_get_balance --client-id <id> --address <addr>`
4. Send TX: `robomotion ethereum eth_send_transaction --client-id <id> --to <addr> --value <wei>`
5. Disconnect: `robomotion ethereum eth_disconnect --client-id <id>`

## Commands Reference
- `robomotion ethereum ethereum_abi_method --abi --abi-method --args`
  Encode a smart contract method call using ABI
- `robomotion ethereum ethereum_get_balance --client-id --wallet [--4]`
  Get the balance of a wallet address on the blockchain
- `robomotion ethereum ethereum_call --client-id --trx-id --wallet --contract`
  Call a smart contract method without sending a transaction (read-only)
- `robomotion ethereum ethereum_cancel_transaction --client-id --hash --gas-price --gas`
  Cancel a pending transaction by sending a replacement with zero value
- `robomotion ethereum ethereum_create_client --rpc-url --chain-id`
  Create a Ethereum client connection to a blockchain RPC endpoint
- `robomotion ethereum ethereum_decode --abi --abi-method --data [--input/output]`
  Decode transaction input or output data using ABI
- `robomotion ethereum ethereum_estimate_gas --client-id --trx-id --wallet --to --value`
  Estimate the gas required for a transaction
- `robomotion ethereum ethereum_estimate_gas_price --client-id`
  Get the current gas price from the blockchain network
- `robomotion ethereum ethereum_export_wallet --keystore-file`
  Export a wallet to a keystore file
- `robomotion ethereum ethereum_from_wei --amount [--unit] [--4]`
  Convert amount from WEI or GWEI to ETH
- `robomotion ethereum ethereum_generate_wallet`
  Generate a new cryptocurrency wallet with encrypted private key
- `robomotion ethereum ethereum_get_transaction --client-id --hash`
  Get transaction details by hash
- `robomotion ethereum ethereum_get_wallet_address`
  Get wallet address from encrypted private key
- `robomotion ethereum ethereum_import_wallet --keystore-file`
  Import a wallet from a keystore file
- `robomotion ethereum ethereum_increase_gas --client-id --hash --gas-price --gas`
  Increase gas price of a pending transaction to speed it up
- `robomotion ethereum ethereum_parse_abi --abi-file`
  Parse a smart contract ABI file for use with other Ethereum nodes
- `robomotion ethereum ethereum_pending_transactions --client-id --new-pending-transactions [--abi] [--methods] [--to] [--http-provider-url]`
  Subscribe to pending transactions on the blockchain
- `robomotion ethereum ethereum_send_transaction --client-id --trx-id --to --gas-price --gas --value --nonce`
  Sign and send a transaction to the blockchain
- `robomotion ethereum ethereum_subscribe --client-id --contract --abi --event-name --params`
  Subscribe to blockchain events from a smart contract
- `robomotion ethereum ethereum_to_wei --amount [--unit]`
  Convert amount from ETH to WEI or GWEI
- `robomotion ethereum ethereum_transaction_receipt --client-id --hash`
  Get transaction receipt by hash
- `robomotion ethereum ethereum_transfer --wallet --to --amount`
  Create a transfer transaction to send cryptocurrency to another address

## Environment
- ROBOMOTION_API_TOKEN (if vault credentials are needed)
