---
name: "openrouter"
description: "OpenRouter unified AI API — access 480+ AI models (Claude, GPT, Gemini, Grok, DeepSeek, etc.) through a single API. Supports text generation, chat, image generation, streaming, and reasoning mode via `robomotion openrouter`. Do NOT use for direct OpenAI, Claude, or Gemini API calls."
---

# OpenRouter

The `robomotion openrouter` CLI connects to OpenRouter's unified API gateway providing access to 480+ AI models across providers. It supports text generation, chat completions with history, image generation, streaming responses, reasoning mode, and model listing.

## When to use
- Generate text or chat responses using any of 480+ AI models
- Access Claude, GPT, Gemini, Grok, DeepSeek through a single API
- Generate images or use reasoning mode for complex tasks
- Stream responses and manage model selection

## Prerequisites
- `robomotion` CLI installed
- Package installed: `robomotion install openrouter`
- OpenRouter API key configured via Robomotion vault

## IMPORTANT: Session Mode Required for Multi-Step Operations
Each CLI command runs as a **separate process** — connection IDs from `connect` do NOT persist across calls.
You MUST use `--session` on `connect` and pass `--session-id` to all subsequent commands.

## Workflow
1. Install (once): `robomotion install openrouter`
2. Connect with session:
   ```
   robomotion openrouter openrouter_connect --session --output json
   # → {"outClientId":"<client-id>","session_id":"<session-id>"}
   ```
3. Use the returned `client-id` and `session-id` in all subsequent commands:
   ```
   robomotion openrouter openrouter_generate_text --client-id "<client-id>" --model <model> --prompt <text> --session-id "<session-id>" --output json
   ```
4. Disconnect when done:
   ```
   robomotion openrouter openrouter_disconnect --client-id "<client-id>" --session-id "<session-id>" --output json
   ```

**Always** append `--output json` to get structured JSON results.

## Commands Reference
- `robomotion openrouter connect_openrouter --session --output json`
  Connect to OpenRouter API and create a client session for accessing 480+ AI models
- `robomotion openrouter generate_text --connection-id --you-are-a-helpful-assistant- --user-prompt [--model] [--custom-model] [--number-of-generations] [--temperature] [--top-p] [--max-tokens] [--stop-sequences] [--reasoning-mode] [--response-schema] [--seed] [--120] --session-id "<session-id>" --output json`
  Generate text using AI models through OpenRouter with support for reasoning mode and structured outputs
- `robomotion openrouter chat_completion --connection-id --you-are-a-helpful-assistant- --user-prompt --history [--model] [--custom-model] [--number-of-generations] [--temperature] [--top-p] [--max-tokens] [--stop-sequences] [--reasoning-mode] [--response-schema] [--seed] [--120] --session-id "<session-id>" --output json`
  Generate chat responses with conversation history support using AI models through OpenRouter
- `robomotion openrouter generate_image --connection-id --prompt --reference-images [--model] [--custom-model] [--number-of-images] [--aspect-ratio] [--120] --session-id "<session-id>" --output json`
  Generate images using AI models like Gemini or Flux through OpenRouter
- `robomotion openrouter get_generation --connection-id --generation-id --session-id "<session-id>" --output json`
  Retrieve generation metadata including cost and token usage from OpenRouter
- `robomotion openrouter get_credits --connection-id --session-id "<session-id>" --output json`
  Get OpenRouter account credits balance and usage information
- `robomotion openrouter get_current_api_key --connection-id --session-id "<session-id>" --output json`
  Get information about the currently authenticated API key
- `robomotion openrouter create_api_key --connection-id --name [--limit] [--include-byok-in-limit] --session-id "<session-id>" --output json`
  Create a new API key in OpenRouter (requires Provisioning API key)
- `robomotion openrouter get_api_key --connection-id --hash --session-id "<session-id>" --output json`
  Get API key information by hash from OpenRouter (requires Provisioning API key)
- `robomotion openrouter list_api_keys --connection-id [--offset] [--include-disabled] --session-id "<session-id>" --output json`
  List all API keys in OpenRouter account (requires Provisioning API key)
- `robomotion openrouter update_api_key --connection-id --hash [--name] [--disabled] [--limit] [--include-byok-in-limit] --session-id "<session-id>" --output json`
  Update an existing API key in OpenRouter (requires Provisioning API key)
- `robomotion openrouter delete_api_key --connection-id --hash --session-id "<session-id>" --output json`
  Delete an API key from OpenRouter (requires Provisioning API key)
- `robomotion openrouter list_models --connection-id [--category-filter] [--rss-format] [--rss-chat-links] --session-id "<session-id>" --output json`
  List available AI models from OpenRouter with optional category filtering
- `robomotion openrouter list_model_endpoints --connection-id --author --slug --session-id "<session-id>" --output json`
  List available provider endpoints for a specific AI model on OpenRouter
- `robomotion openrouter disconnect_openrouter --connection-id --session-id "<session-id>" --output json`
  Disconnect from OpenRouter API and release the client session

## Environment
- ROBOMOTION_API_TOKEN (if vault credentials are needed)
