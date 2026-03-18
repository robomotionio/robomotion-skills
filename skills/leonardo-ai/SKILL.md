---
name: "leonardo-ai"
description: "Leonardo AI image generation — create images, upscale, remove backgrounds, and manage generation jobs. Supports multiple AI models and style presets via `robomotion leonardoai`. Do NOT use for DALL-E, Stability AI, Midjourney, or other image generation services."
---

# Leonardo AI

The `robomotion leonardoai` CLI connects to Leonardo AI for AI-powered image generation and editing. It generates images from text prompts, upscales images, removes backgrounds, manages generation jobs, and supports various AI models and style presets.

## When to use
- Generate images from text prompts using Leonardo AI models
- Upscale images or remove backgrounds
- Track and retrieve generation job results
- List available models and manage image workflows

## Prerequisites
- `robomotion` CLI installed
- Package installed: `robomotion install leonardoai`
- Leonardo AI API key configured via Robomotion vault

## IMPORTANT: Session Mode Required for Multi-Step Operations
Each CLI command runs as a **separate process** — connection IDs from `connect` do NOT persist across calls.
You MUST use `--session` on `connect` and pass `--session-id` to all subsequent commands.

## Workflow
1. Install (once): `robomotion install leonardoai`
2. Connect with session:
   ```
   robomotion leonardoai leonardoai_connect --session --output json
   # → {"outClientId":"<client-id>","session_id":"<session-id>"}
   ```
3. Use the returned `client-id` and `session-id` in all subsequent commands:
   ```
   robomotion leonardoai leonardoai_generate_image --client-id "<client-id>" --prompt <text> --session-id "<session-id>" --output json
   ```
4. Disconnect when done:
   ```
   robomotion leonardoai leonardoai_disconnect --client-id "<client-id>" --session-id "<session-id>" --output json
   ```

**Always** append `--output json` to get structured JSON results.

## Commands Reference
- `robomotion leonardoai connect --session --output json`
  Connect to Leonardo AI API using an API key
- `robomotion leonardoai create_generation --connection_id --in-prompt [--opt-neg-prompt] [--1] [--opt-width] [--opt-height] [--7] [--generation_id] [--image_id] [--0.5] [--30] [--opt-custom-model-id] [--opt-model-id] [--opt-control-net] [--opt-control-net-type] [--opt-preset-style] [--opt-prompt-magic] [--opt-public] [--opt-scheduler] [--opt-sd-version] [--opt-tiling] --session-id "<session-id>" --output json`
  Generate images from a text prompt using Leonardo AI
- `robomotion leonardoai create_upscale --connection_id --generation_id --session-id "<session-id>" --output json`
  Create an upscaled version of a generated image
- `robomotion leonardoai delete_generation --connection_id --generation_id --session-id "<session-id>" --output json`
  Delete a generation by its ID
- `robomotion leonardoai disconnect --connection_id --session-id "<session-id>" --output json`
  Disconnect from Leonardo AI API and clean up the connection
- `robomotion leonardoai get_generation --connection_id --generation_id --session-id "<session-id>" --output json`
  Get details of a generation by its ID
- `robomotion leonardoai get_user_details --connection_id --session-id "<session-id>" --output json`
  Get details of the authenticated Leonardo AI user
- `robomotion leonardoai get_variation --connection_id --variation_id --session-id "<session-id>" --output json`
  Get details of a variation by its ID
- `robomotion leonardoai delete_image --connection_id --image_id --session-id "<session-id>" --output json`
  Delete an uploaded image by its ID
- `robomotion leonardoai get_image --connection_id --image_id --session-id "<session-id>" --output json`
  Get details of an uploaded image by its ID
- `robomotion leonardoai list_generations --connection_id --user_id [--0] [--10] --session-id "<session-id>" --output json`
  List all generations for a specific user
- `robomotion leonardoai upload_image --connection_id --in-image-path [--opt-image-type] --session-id "<session-id>" --output json`
  Upload an image from local file for use as init image

## Environment
- ROBOMOTION_API_TOKEN (if vault credentials are needed)
