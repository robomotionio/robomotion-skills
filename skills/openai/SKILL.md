---
name: "openai"
description: "OpenAI API — generate text, images, speech, transcriptions, and embeddings using GPT, DALL-E, Whisper, and TTS models. Supports chat completions, vision, function calling, and file management via `robomotion openai`. Do NOT use for Claude, Gemini, or direct LLM conversation."
---

# OpenAI

The `robomotion openai` CLI calls the OpenAI API for AI operations. It generates text with GPT models (including vision and function calling), creates images with DALL-E/GPT-Image, synthesizes and transcribes audio, generates embeddings, moderates content, and manages files.

## When to use
- Generate text or chat completions with GPT models (including tool use)
- Create or edit images with DALL-E and GPT-Image models
- Convert text to speech or transcribe/translate audio with Whisper
- Generate embeddings, moderate content, and manage uploaded files

## Prerequisites
- `robomotion` CLI installed
- Package installed: `robomotion install openai`
- OpenAI API key configured via Robomotion vault

## IMPORTANT: Session Mode Required for Multi-Step Operations
Each CLI command runs as a **separate process** — connection IDs from `connect` do NOT persist across calls.
You MUST use `--session` on `connect` and pass `--session-id` to all subsequent commands.

## Workflow
1. Install (once): `robomotion install openai`
2. Connect with session:
   ```
   robomotion openai connect_openai --session --output json
   # → {"outConnectionId":"<connection-id>","session_id":"<session-id>"}
   ```
3. Use the returned `connection-id` and `session-id` in all subsequent commands:
   ```
   robomotion openai generate_text --connection-id "<connection-id>" --user-prompt <prompt> --session-id "<session-id>" --output json
   ```
4. Disconnect when done:
   ```
   robomotion openai disconnect_openai --connection-id "<connection-id>" --session-id "<session-id>" --output json
   ```

**Always** append `--output json` to get structured JSON results.

## Commands Reference
- `robomotion openai connect_openai --session --output json`
  Connect to OpenAI API and create a client session for AI operations
- `robomotion openai disconnect_openai --connection-id --session-id "<session-id>" --output json`
  Disconnect from OpenAI API and release the client session
- `robomotion openai generate_text --connection-id --you-are-a-helpful-assistant- --user-prompt --history --tool-message --image-url --images [--model] [--custom-model] [--number-of-generations] [--temperature] [--top-p] [--max-tokens] [--frequency-penalty] [--presence-penalty] [--stop-sequences] [--reasoning-effort] [--image-detail] [--functions] [--tools-choice] [--seed] [--user] [--120] --session-id "<session-id>" --output json`
  Generate text completions using OpenAI language models with optional vision and tool calling
- `robomotion openai generate_image --connection-id --prompt [--model] [--number-of-images] [--size] [--quality] [--style] [--background] [--output-format] [--user] [--120] --session-id "<session-id>" --output json`
  Generate images using OpenAI DALL-E and GPT-Image models
- `robomotion openai edit_image --connection-id --image-path --mask-path --prompt [--model] [--number-of-images] [--size] [--user] [--120] --session-id "<session-id>" --output json`
  Edit an existing image based on a text prompt using DALL-E or GPT-Image models
- `robomotion openai create_image_variation --connection-id --image-path [--model] [--number-of-images] [--size] [--user] [--120] --session-id "<session-id>" --output json`
  Create variations of an existing image using DALL-E 2
- `robomotion openai generate_speech --connection-id --text [--model] [--voice] [--format] [--1-0] [--instructions] [--120] --session-id "<session-id>" --output json`
  Convert text to speech using OpenAI TTS models
- `robomotion openai transcribe_audio --connection-id --audio-file [--model] [--language] [--prompt] [--0] [--120] --session-id "<session-id>" --output json`
  Transcribe audio to text using OpenAI Whisper and GPT-4o transcription models
- `robomotion openai translate_audio --connection-id --audio-file [--model] [--prompt] [--0] [--120] --session-id "<session-id>" --output json`
  Translate audio to English text using OpenAI Whisper model
- `robomotion openai generate_embedding --connection-id --text [--model] [--custom-model] [--dimensions] [--user] --session-id "<session-id>" --output json`
  Generate vector embeddings from text using OpenAI embedding models
- `robomotion openai generate_batch_embeddings --connection-id --texts [--model] [--custom-model] [--dimensions] [--user] --session-id "<session-id>" --output json`
  Generate vector embeddings for multiple texts in a single batch request
- `robomotion openai similarity --connection-id --search-embeddings-csv --content-embeddings-csv [--5] --session-id "<session-id>" --output json`
  Calculate cosine similarity between embeddings to find most relevant content
- `robomotion openai moderate --connection-id --text [--model] --session-id "<session-id>" --output json`
  Check text content for policy violations using OpenAI moderation models
- `robomotion openai list_models --connection-id --session-id "<session-id>" --output json`
  List available OpenAI models with their details
- `robomotion openai retrieve_model --connection-id --gpt-5-mini --session-id "<session-id>" --output json`
  Retrieve detailed information about a specific OpenAI model
- `robomotion openai upload_file --connection-id --file-path [--purpose] --session-id "<session-id>" --output json`
  Upload a file to OpenAI file storage for use with assistants or fine-tuning
- `robomotion openai list_files --connection-id [--purpose-filter] --session-id "<session-id>" --output json`
  List all files uploaded to OpenAI file storage
- `robomotion openai retrieve_file_metadata --connection-id --file-id --session-id "<session-id>" --output json`
  Retrieve metadata about a file in OpenAI file storage
- `robomotion openai download_file --connection-id --file-id --session-id "<session-id>" --output json`
  Download a file from OpenAI file storage to local filesystem
- `robomotion openai delete_file --connection-id --file-id --session-id "<session-id>" --output json`
  Delete a file from OpenAI file storage

## Environment
- ROBOMOTION_API_TOKEN (if vault credentials are needed)
