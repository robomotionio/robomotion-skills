---
name: "gemini-ai"
description: "Google Gemini AI — generate text, analyze images, and create embeddings using Gemini models. Supports chat with history, vision, and content generation via `robomotion googlegemini`. Do NOT use for OpenAI, Claude, or other AI models."
---

# Google Gemini AI

The `robomotion googlegemini` CLI calls Google's Gemini API for text generation, image analysis, and embeddings. It supports single-turn generation, multi-turn chat with history, vision (image + text), and embedding generation.

## When to use
- Generate text responses using Gemini models
- Analyze images with text prompts (vision)
- Run multi-turn chat conversations with history
- Generate text embeddings for semantic search

## Prerequisites
- `robomotion` CLI installed
- Package installed: `robomotion install googlegemini`
- Google Gemini API key configured via Robomotion vault

## IMPORTANT: Session Mode Required for Multi-Step Operations
Each CLI command runs as a **separate process** — connection IDs from `connect` do NOT persist across calls.
You MUST use `--session` on `connect` and pass `--session-id` to all subsequent commands.

## Workflow
1. Install (once): `robomotion install googlegemini`
2. Connect with session:
   ```
   robomotion googlegemini connect_gemini --session --output json
   # → {"outConnectionId":"<connection-id>","session_id":"<session-id>"}
   ```
3. Use the returned `connection-id` and `session-id` in all subsequent commands:
   ```
   robomotion googlegemini generate_text --connection-id "<connection-id>" --prompt <text> --session-id "<session-id>" --output json
   ```
4. Disconnect when done:
   ```
   robomotion googlegemini disconnect_gemini --connection-id "<connection-id>" --session-id "<session-id>" --output json
   ```

**Always** append `--output json` to get structured JSON results.

## Commands Reference
- `robomotion googlegemini connect --session --output json`
  Establishes a connection to Google Gemini API using API key or Robomotion credits
- `robomotion googlegemini generate_text --connection-id --system-prompt --user-prompt --local-file-paths --file-paths --uploaded-files [--model] [--custom-model] [--number-of-generations] [--temperature] [--top-p] [--top-k] [--max-output-tokens] [--thinking-mode] [--thinking-budget] [--safety-settings-harassment] [--safety-settings-hate-speech] [--safety-settings-sexually-explicit] [--safety-settings-dangerous-content] [--safety-settings-civic-integrity] [--response-mime-type] [--response-schema] [--presence-penalty] [--frequency-penalty] [--stop-sequences] [--60] --session-id "<session-id>" --output json`
  Generates text using Google Gemini models with optional file inputs
- `robomotion googlegemini send_chat_message --connection-id --user-prompt --history --local-file-paths --file-paths --uploaded-files [--model] [--custom-model] [--temperature] [--top-p] [--top-k] [--max-output-tokens] [--safety-settings-harassment] [--safety-settings-hate-speech] [--safety-settings-sexually-explicit] [--safety-settings-dangerous-content] [--safety-settings-civic-integrity] [--response-mime-type] [--presence-penalty] [--frequency-penalty] [--60] --session-id "<session-id>" --output json`
  Sends a message in a multi-turn chat conversation with Gemini
- `robomotion googlegemini upload_file --connection-id --file-display-name --file-local-path --session-id "<session-id>" --output json`
  Uploads a local file to Google Gemini for use in prompts
- `robomotion googlegemini list_files --connection-id [--page-size] [--page-token] [--max-results] --session-id "<session-id>" --output json`
  Lists all uploaded files in your Google Gemini account
- `robomotion googlegemini get_file --connection-id --file-uri --session-id "<session-id>" --output json`
  Retrieves metadata for an uploaded file from Google Gemini
- `robomotion googlegemini delete_file --connection-id --file-uri --session-id "<session-id>" --output json`
  Deletes an uploaded file from Google Gemini
- `robomotion googlegemini list_models --connection-id [--page-size] [--page-token] [--filter] [--max-results] --session-id "<session-id>" --output json`
  Lists available Gemini models with their capabilities and token limits
- `robomotion googlegemini embeddings --connection-id --content --compare-text [--title] [--task-type] [--embedding-model] [--output-dimensionality] --session-id "<session-id>" --output json`
  Generates text embeddings for semantic search٫ classification٫ and similarity tasks
- `robomotion googlegemini batch_embeddings --connection-id --contents [--task-type] [--embedding-model] [--title] [--output-dimensionality] --session-id "<session-id>" --output json`
  Generates embeddings for multiple texts in a single batch operation
- `robomotion googlegemini compare_embeddings --connection-id --source-text --comparison-texts --source-embedding-file --target-embeddings-file --comparison-texts-file [--embedding-model] [--custom-model] [--similarity-metric] [--similarity-threshold] [--max-results] [--sort-order] [--60] --session-id "<session-id>" --output json`
  Compares semantic similarity between a source text and multiple target texts
- `robomotion googlegemini generate_image --connection-id --prompt --reference-images --reference-images [--model] [--custom-model] [--number-of-images] [--aspect-ratio] [--image-size] [--person-generation] [--output-format] [--120] --session-id "<session-id>" --output json`
  Generates images using Google Gemini image generation models
- `robomotion googlegemini edit_image --connection-id --edit-prompt --base-image-path --mask-image-path [--model] [--custom-model] [--number-of-images] [--negative-prompt] [--output-format] [--output-quality] [--120] --session-id "<session-id>" --output json`
  Edits an existing image using Gemini with mask-based inpainting
- `robomotion googlegemini generate_video --connection-id --video-prompt --negative-prompt --first-frame-image --last-frame-image [--model] [--custom-model] [--aspect-ratio] [--resolution] [--duration] [--generate-audio] [--person-generation] [--600] --session-id "<session-id>" --output json`
  Generates videos using Google Veo models with optional audio and frame control
- `robomotion googlegemini disconnect --connection-id --session-id "<session-id>" --output json`
  Closes an existing Google Gemini API connection

## Environment
- ROBOMOTION_API_TOKEN (if vault credentials are needed)
