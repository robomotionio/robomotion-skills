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

## Workflow
1. Install: `robomotion install ollama`
2. Connect: `robomotion ollama ollama_connect` → returns a `client-id`
3. Generate: `robomotion ollama ollama_generate --client-id <id> --model llama3 --prompt <text>`
4. Chat: `robomotion ollama ollama_chat --client-id <id> --model llama3 --messages <json>`
5. Disconnect: `robomotion ollama ollama_disconnect --client-id <id>`

## Commands Reference
- `robomotion ollama connect_ollama`
  Connect to Ollama server and create a client session for local LLM operations
- `robomotion ollama disconnect_ollama --client-id`
  Disconnect from Ollama server and release the client session
- `robomotion ollama generate_completion --client-id --model --prompt [--options] [--host-url]`
  Generate text completion using a local Ollama model
- `robomotion ollama generate_chat_completion --client-id --model --messages [--options] [--host-url]`
  Generate chat responses using a local Ollama model with conversation history
- `robomotion ollama list_models --client-id [--host-url]`
  List all locally available Ollama models
- `robomotion ollama show_model_info --client-id --model [--host-url]`
  Get detailed information about a local Ollama model
- `robomotion ollama delete_model --client-id --model [--host-url]`
  Delete a local Ollama model
- `robomotion ollama pull_model --client-id --model [--host-url]`
  Download a model from the Ollama library to local storage
- `robomotion ollama generate_embeddings --client-id --model --prompt [--host-url]`
  Generate vector embeddings for text using a local Ollama model

## Environment
- ROBOMOTION_API_TOKEN (if vault credentials are needed)
