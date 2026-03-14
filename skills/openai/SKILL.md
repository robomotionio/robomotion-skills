---
name: "openai"
description: "Use when the user wants to call the Robomotion OpenAI package to generate text, images, embeddings, or audio via the `robomotion openai` CLI. Use only when the task involves running robomotion commands for OpenAI API calls. Do NOT use for Claude, Gemini, or direct LLM conversation."
---

# Openai Skill

## When to use
- Generate text or chat completions using GPT models
- Create images with DALL-E
- Transcribe audio with Whisper
- Generate embeddings for semantic search

## Prerequisites
- `robomotion` CLI installed
- Package installed: `robomotion install openai`
- Credentials configured via Robomotion vault or environment variables

## Workflow
1. Install the package: `robomotion install openai`
2. Run commands: `robomotion openai <command> [flags]`

## Commands Reference
- `robomotion openai connect_openai`
  Connect to OpenAI API and create a client session for AI operations
- `robomotion openai disconnect_openai --connection-id`
  Disconnect from OpenAI API and release the client session
- `robomotion openai generate_text --connection-id --you-are-a-helpful-assistant- --user-prompt --history --tool-message --image-url --images [--model] [--custom-model] [--number-of-generations] [--temperature] [--top-p] [--max-tokens] [--frequency-penalty] [--presence-penalty] [--stop-sequences] [--reasoning-effort] [--image-detail] [--functions] [--tools-choice] [--seed] [--user] [--120]`
  Generate text completions using OpenAI language models with optional vision and tool calling
- `robomotion openai generate_image --connection-id --prompt [--model] [--number-of-images] [--size] [--quality] [--style] [--background] [--output-format] [--user] [--120]`
  Generate images using OpenAI DALL-E and GPT-Image models
- `robomotion openai edit_image --connection-id --image-path --mask-path --prompt [--model] [--number-of-images] [--size] [--user] [--120]`
  Edit an existing image based on a text prompt using DALL-E or GPT-Image models
- `robomotion openai create_image_variation --connection-id --image-path [--model] [--number-of-images] [--size] [--user] [--120]`
  Create variations of an existing image using DALL-E 2
- `robomotion openai generate_speech --connection-id --text [--model] [--voice] [--format] [--1-0] [--instructions] [--120]`
  Convert text to speech using OpenAI TTS models
- `robomotion openai transcribe_audio --connection-id --audio-file [--model] [--language] [--prompt] [--0] [--120]`
  Transcribe audio to text using OpenAI Whisper and GPT-4o transcription models
- `robomotion openai translate_audio --connection-id --audio-file [--model] [--prompt] [--0] [--120]`
  Translate audio to English text using OpenAI Whisper model
- `robomotion openai generate_embedding --connection-id --text [--model] [--custom-model] [--dimensions] [--user]`
  Generate vector embeddings from text using OpenAI embedding models
- `robomotion openai generate_batch_embeddings --connection-id --texts [--model] [--custom-model] [--dimensions] [--user]`
  Generate vector embeddings for multiple texts in a single batch request
- `robomotion openai similarity --connection-id --search-embeddings-csv --content-embeddings-csv [--5]`
  Calculate cosine similarity between embeddings to find most relevant content
- `robomotion openai moderate --connection-id --text [--model]`
  Check text content for policy violations using OpenAI moderation models
- `robomotion openai list_models --connection-id`
  List available OpenAI models with their details
- `robomotion openai retrieve_model --connection-id --gpt-5-mini`
  Retrieve detailed information about a specific OpenAI model
- `robomotion openai upload_file --connection-id --file-path [--purpose]`
  Upload a file to OpenAI file storage for use with assistants or fine-tuning
- `robomotion openai list_files --connection-id [--purpose-filter]`
  List all files uploaded to OpenAI file storage
- `robomotion openai retrieve_file_metadata --connection-id --file-id`
  Retrieve metadata about a file in OpenAI file storage
- `robomotion openai download_file --connection-id --file-id`
  Download a file from OpenAI file storage to local filesystem
- `robomotion openai delete_file --connection-id --file-id`
  Delete a file from OpenAI file storage

## Environment
- ROBOMOTION_API_TOKEN (if vault credentials are needed)
