---
name: "stability-ai"
description: "Stability AI — generate and edit images using Stable Diffusion models. Supports text-to-image, image-to-image, upscaling, and style control via `robomotion stabilityai`. Do NOT use for DALL-E, Leonardo AI, Midjourney, or other image generation services."
---

# Stability AI

The `robomotion stabilityai` CLI connects to Stability AI for image generation and editing. It generates images from text prompts using Stable Diffusion models, performs image-to-image transformation, upscales images, and supports various style and quality controls.

## When to use
- Generate images from text prompts (text-to-image)
- Transform existing images with text guidance (image-to-image)
- Upscale images to higher resolutions
- Control generation with style presets and parameters

## Prerequisites
- `robomotion` CLI installed
- Package installed: `robomotion install stabilityai`
- Stability AI API key configured via Robomotion vault

## IMPORTANT: Session Mode Required for Multi-Step Operations
Each CLI command runs as a **separate process** — connection IDs from `connect` do NOT persist across calls.
You MUST use `--session` on `connect` and pass `--session-id` to all subsequent commands.

## Workflow
1. Install (once): `robomotion install stabilityai`
2. Connect with session:
   ```
   robomotion stabilityai stabilityai_connect --session --output json
   # → {"outClientId":"<client-id>","session_id":"<session-id>"}
   ```
3. Use the returned `client-id` and `session-id` in all subsequent commands:
   ```
   robomotion stabilityai stabilityai_generate --client-id "<client-id>" --prompt <text> --session-id "<session-id>" --output json
   ```
4. Disconnect when done:
   ```
   robomotion stabilityai stabilityai_disconnect --client-id "<client-id>" --session-id "<session-id>" --output json
   ```

**Always** append `--output json` to get structured JSON results.

## Commands Reference
- `robomotion stabilityai connect --session --output json`
  Establishes a connection to Stability AI using API credentials
- `robomotion stabilityai disconnect --connection_id --session-id "<session-id>" --output json`
  Closes an existing Stability AI connection and releases resources
- `robomotion stabilityai get_engines_list --connection_id --session-id "<session-id>" --output json`
  Retrieves the list of available Stability AI engines for image generation
- `robomotion stabilityai get_user_account --connection_id --session-id "<session-id>" --output json`
  Retrieves the current user's Stability AI account information
- `robomotion stabilityai get_user_credit --connection_id --session-id "<session-id>" --output json`
  Retrieves the current user's Stability AI credit balance
- `robomotion stabilityai image_to_image --connection_id --in-image-path --in-prompt --in-init-image-path [--opt-engine-id] [--opt-neg-prompt] [--7] [--opt-clip-guidance-preset] [--opt-sampler] [--1] [--0] [--50] [--opt-style-preset] [--opt-init-image-mode] [--0.35] [--0.65] [--opt-step-schedule-end] --session-id "<session-id>" --output json`
  Generates new images based on an input image and text prompt using Stability AI
- `robomotion stabilityai masking --connection_id --in-image-path --in-init-image-path --in-engine-id --in-prompt [--7] [--opt-clip-guidance-preset] [--opt-sampler] [--1] [--0] [--50] [--opt-style-preset] [--opt-mask-source] [--opt-mask-image-path] --session-id "<session-id>" --output json`
  Generates images with masked inpainting using Stability AI
- `robomotion stabilityai text_to_image --connection_id --in-image-path --in-prompt [--opt-engine-id] [--opt-neg-prompt] [--opt-height] [--opt-width] [--7] [--opt-clip-guidance-preset] [--opt-sampler] [--1] [--0] [--50] [--opt-style-preset] --session-id "<session-id>" --output json`
  Generates images from text prompts using Stability AI
- `robomotion stabilityai upscale --connection_id --in-image-path --in-init-image-path [--opt-engine-id] [--opt-height] [--opt-width] [--opt-prompt] [--0] [--50] [--7] --session-id "<session-id>" --output json`
  Upscales an image to higher resolution using Stability AI

## Environment
- ROBOMOTION_API_TOKEN (if vault credentials are needed)
