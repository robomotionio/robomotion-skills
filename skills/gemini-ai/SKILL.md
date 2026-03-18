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

## Workflow
1. Install: `robomotion install googlegemini`
2. Connect: `robomotion googlegemini connect_gemini` → returns a `connection-id`
3. Generate text: `robomotion googlegemini generate_text --connection-id <id> --prompt <text>`
4. Disconnect: `robomotion googlegemini disconnect_gemini --connection-id <id>`

## Commands Reference
- `robomotion googlegemini connect`
  Establishes a connection to Google Gemini API using API key or Robomotion credits
- `robomotion googlegemini generate_text --connection-id --system-prompt --user-prompt --local-file-paths --file-paths --uploaded-files [--model] [--custom-model] [--number-of-generations] [--temperature] [--top-p] [--top-k] [--max-output-tokens] [--thinking-mode] [--thinking-budget] [--safety-settings-harassment] [--safety-settings-hate-speech] [--safety-settings-sexually-explicit] [--safety-settings-dangerous-content] [--safety-settings-civic-integrity] [--response-mime-type] [--response-schema] [--presence-penalty] [--frequency-penalty] [--stop-sequences] [--60]`
  Generates text using Google Gemini models with optional file inputs
- `robomotion googlegemini send_chat_message --connection-id --user-prompt --history --local-file-paths --file-paths --uploaded-files [--model] [--custom-model] [--temperature] [--top-p] [--top-k] [--max-output-tokens] [--safety-settings-harassment] [--safety-settings-hate-speech] [--safety-settings-sexually-explicit] [--safety-settings-dangerous-content] [--safety-settings-civic-integrity] [--response-mime-type] [--presence-penalty] [--frequency-penalty] [--60]`
  Sends a message in a multi-turn chat conversation with Gemini
- `robomotion googlegemini upload_file --connection-id --file-display-name --file-local-path`
  Uploads a local file to Google Gemini for use in prompts
- `robomotion googlegemini list_files --connection-id [--page-size] [--page-token] [--max-results]`
  Lists all uploaded files in your Google Gemini account
- `robomotion googlegemini get_file --connection-id --file-uri`
  Retrieves metadata for an uploaded file from Google Gemini
- `robomotion googlegemini delete_file --connection-id --file-uri`
  Deletes an uploaded file from Google Gemini
- `robomotion googlegemini list_models --connection-id [--page-size] [--page-token] [--filter] [--max-results]`
  Lists available Gemini models with their capabilities and token limits
- `robomotion googlegemini embeddings --connection-id --content --compare-text [--title] [--task-type] [--embedding-model] [--output-dimensionality]`
  Generates text embeddings for semantic search٫ classification٫ and similarity tasks
- `robomotion googlegemini batch_embeddings --connection-id --contents [--task-type] [--embedding-model] [--title] [--output-dimensionality]`
  Generates embeddings for multiple texts in a single batch operation
- `robomotion googlegemini compare_embeddings --connection-id --source-text --comparison-texts --source-embedding-file --target-embeddings-file --comparison-texts-file [--embedding-model] [--custom-model] [--similarity-metric] [--similarity-threshold] [--max-results] [--sort-order] [--60]`
  Compares semantic similarity between a source text and multiple target texts
- `robomotion googlegemini generate_image --connection-id --prompt --reference-images --reference-images [--model] [--custom-model] [--number-of-images] [--aspect-ratio] [--image-size] [--person-generation] [--output-format] [--120]`
  Generates images using Google Gemini image generation models
- `robomotion googlegemini edit_image --connection-id --edit-prompt --base-image-path --mask-image-path [--model] [--custom-model] [--number-of-images] [--negative-prompt] [--output-format] [--output-quality] [--120]`
  Edits an existing image using Gemini with mask-based inpainting
- `robomotion googlegemini generate_video --connection-id --video-prompt --negative-prompt --first-frame-image --last-frame-image [--model] [--custom-model] [--aspect-ratio] [--resolution] [--duration] [--generate-audio] [--person-generation] [--600]`
  Generates videos using Google Veo models with optional audio and frame control
- `robomotion googlegemini disconnect --connection-id`
  Closes an existing Google Gemini API connection

## Environment
- ROBOMOTION_API_TOKEN (if vault credentials are needed)
