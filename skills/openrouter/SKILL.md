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

## Workflow
1. Install: `robomotion install openrouter`
2. Connect: `robomotion openrouter openrouter_connect` → returns a `client-id`
3. Generate: `robomotion openrouter openrouter_generate_text --client-id <id> --model <model> --prompt <text>`
4. Chat: `robomotion openrouter openrouter_generate_chat --client-id <id> --model <model> --messages <json>`
5. Disconnect: `robomotion openrouter openrouter_disconnect --client-id <id>`

## Commands Reference
- `robomotion openrouter connect_openrouter`
  Connect to OpenRouter API and create a client session for accessing 480+ AI models
- `robomotion openrouter generate_text --connection-id --you-are-a-helpful-assistant- --user-prompt [--model] [--custom-model] [--number-of-generations] [--temperature] [--top-p] [--max-tokens] [--stop-sequences] [--reasoning-mode] [--response-schema] [--seed] [--120]`
  Generate text using AI models through OpenRouter with support for reasoning mode and structured outputs
- `robomotion openrouter chat_completion --connection-id --you-are-a-helpful-assistant- --user-prompt --history [--model] [--custom-model] [--number-of-generations] [--temperature] [--top-p] [--max-tokens] [--stop-sequences] [--reasoning-mode] [--response-schema] [--seed] [--120]`
  Generate chat responses with conversation history support using AI models through OpenRouter
- `robomotion openrouter generate_image --connection-id --prompt --reference-images [--model] [--custom-model] [--number-of-images] [--aspect-ratio] [--120]`
  Generate images using AI models like Gemini or Flux through OpenRouter
- `robomotion openrouter get_generation --connection-id --generation-id`
  Retrieve generation metadata including cost and token usage from OpenRouter
- `robomotion openrouter get_credits --connection-id`
  Get OpenRouter account credits balance and usage information
- `robomotion openrouter get_current_api_key --connection-id`
  Get information about the currently authenticated API key
- `robomotion openrouter create_api_key --connection-id --name [--limit] [--include-byok-in-limit]`
  Create a new API key in OpenRouter (requires Provisioning API key)
- `robomotion openrouter get_api_key --connection-id --hash`
  Get API key information by hash from OpenRouter (requires Provisioning API key)
- `robomotion openrouter list_api_keys --connection-id [--offset] [--include-disabled]`
  List all API keys in OpenRouter account (requires Provisioning API key)
- `robomotion openrouter update_api_key --connection-id --hash [--name] [--disabled] [--limit] [--include-byok-in-limit]`
  Update an existing API key in OpenRouter (requires Provisioning API key)
- `robomotion openrouter delete_api_key --connection-id --hash`
  Delete an API key from OpenRouter (requires Provisioning API key)
- `robomotion openrouter list_models --connection-id [--category-filter] [--rss-format] [--rss-chat-links]`
  List available AI models from OpenRouter with optional category filtering
- `robomotion openrouter list_model_endpoints --connection-id --author --slug`
  List available provider endpoints for a specific AI model on OpenRouter
- `robomotion openrouter disconnect_openrouter --connection-id`
  Disconnect from OpenRouter API and release the client session

## Environment
- ROBOMOTION_API_TOKEN (if vault credentials are needed)
