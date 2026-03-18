---
name: "ollama"
description: "Ollama local AI — run LLM models locally for text generation, chat, and embeddings. Supports model management, streaming, and multi-turn conversations via `robomotion ollama`. Do NOT use for OpenAI, Claude, Gemini, or other cloud AI services."
---

# Ollama

The `robomotion ollama` CLI connects to a local Ollama instance for running LLMs on your own hardware. It supports text generation, chat completions with history, embedding generation, model listing, and model management (pull/delete).

## When to use
- Generate text using local models (Llama, Mistral, etc.)
- Run multi-turn chat conversations locally
- Generate text embeddings for semantic search
- List, pull, or delete Ollama models

## Prerequisites
- `robomotion` CLI installed
- Package installed: `robomotion install ollama`
- Ollama running locally or on an accessible server

## IMPORTANT: Session Mode Required for Multi-Step Operations
Each CLI command runs as a **separate process** — connection IDs from `connect` do NOT persist across calls.
You MUST use `--session` on `connect` and pass `--session-id` to all subsequent commands.

## Workflow
1. Install (once): `robomotion install ollama`
2. Connect with session:
   ```
   robomotion ollama ollama_connect --session --output json
   # → {"outClientId":"<client-id>","session_id":"<session-id>"}
   ```
3. Use the returned `client-id` and `session-id` in all subsequent commands:
   ```
   robomotion ollama ollama_generate --client-id "<client-id>" --model llama3 --prompt <text> --session-id "<session-id>" --output json
   ```
4. Disconnect when done:
   ```
   robomotion ollama ollama_disconnect --client-id "<client-id>" --session-id "<session-id>" --output json
   ```

**Always** append `--output json` to get structured JSON results.

## Commands Reference
- `robomotion ollama connect_ollama --session --output json`
  Connect to Ollama server and create a client session for local LLM operations
- `robomotion ollama disconnect_ollama --client-id --session-id "<session-id>" --output json`
  Disconnect from Ollama server and release the client session
- `robomotion ollama generate_completion --client-id --model --prompt [--options] [--host-url] --session-id "<session-id>" --output json`
  Generate text completion using a local Ollama model
- `robomotion ollama generate_chat_completion --client-id --model --messages [--options] [--host-url] --session-id "<session-id>" --output json`
  Generate chat responses using a local Ollama model with conversation history
- `robomotion ollama list_models --client-id [--host-url] --session-id "<session-id>" --output json`
  List all locally available Ollama models
- `robomotion ollama show_model_info --client-id --model [--host-url] --session-id "<session-id>" --output json`
  Get detailed information about a local Ollama model
- `robomotion ollama delete_model --client-id --model [--host-url] --session-id "<session-id>" --output json`
  Delete a local Ollama model
- `robomotion ollama pull_model --client-id --model [--host-url] --session-id "<session-id>" --output json`
  Download a model from the Ollama library to local storage
- `robomotion ollama generate_embeddings --client-id --model --prompt [--host-url] --session-id "<session-id>" --output json`
  Generate vector embeddings for text using a local Ollama model

## Environment
- ROBOMOTION_API_TOKEN (if vault credentials are needed)
