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

## Workflow
1. Install: `robomotion install leonardoai`
2. Connect: `robomotion leonardoai leonardoai_connect` → returns a `client-id`
3. Generate: `robomotion leonardoai leonardoai_generate_image --client-id <id> --prompt <text>`
4. Get result: `robomotion leonardoai leonardoai_get_generation --client-id <id> --generation-id <gen>`
5. Disconnect: `robomotion leonardoai leonardoai_disconnect --client-id <id>`

## Commands Reference
- `robomotion leonardoai connect`
  Connect to Leonardo AI API using an API key
- `robomotion leonardoai create_generation --connection_id --in-prompt [--opt-neg-prompt] [--1] [--opt-width] [--opt-height] [--7] [--generation_id] [--image_id] [--0.5] [--30] [--opt-custom-model-id] [--opt-model-id] [--opt-control-net] [--opt-control-net-type] [--opt-preset-style] [--opt-prompt-magic] [--opt-public] [--opt-scheduler] [--opt-sd-version] [--opt-tiling]`
  Generate images from a text prompt using Leonardo AI
- `robomotion leonardoai create_upscale --connection_id --generation_id`
  Create an upscaled version of a generated image
- `robomotion leonardoai delete_generation --connection_id --generation_id`
  Delete a generation by its ID
- `robomotion leonardoai disconnect --connection_id`
  Disconnect from Leonardo AI API and clean up the connection
- `robomotion leonardoai get_generation --connection_id --generation_id`
  Get details of a generation by its ID
- `robomotion leonardoai get_user_details --connection_id`
  Get details of the authenticated Leonardo AI user
- `robomotion leonardoai get_variation --connection_id --variation_id`
  Get details of a variation by its ID
- `robomotion leonardoai delete_image --connection_id --image_id`
  Delete an uploaded image by its ID
- `robomotion leonardoai get_image --connection_id --image_id`
  Get details of an uploaded image by its ID
- `robomotion leonardoai list_generations --connection_id --user_id [--0] [--10]`
  List all generations for a specific user
- `robomotion leonardoai upload_image --connection_id --in-image-path [--opt-image-type]`
  Upload an image from local file for use as init image

## Environment
- ROBOMOTION_API_TOKEN (if vault credentials are needed)
