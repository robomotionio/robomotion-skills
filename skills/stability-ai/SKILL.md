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

## Workflow
1. Install: `robomotion install stabilityai`
2. Connect: `robomotion stabilityai stabilityai_connect` → returns a `client-id`
3. Generate: `robomotion stabilityai stabilityai_generate --client-id <id> --prompt <text>`
4. Disconnect: `robomotion stabilityai stabilityai_disconnect --client-id <id>`

## Commands Reference
- `robomotion stabilityai connect`
  Establishes a connection to Stability AI using API credentials
- `robomotion stabilityai disconnect --connection_id`
  Closes an existing Stability AI connection and releases resources
- `robomotion stabilityai get_engines_list --connection_id`
  Retrieves the list of available Stability AI engines for image generation
- `robomotion stabilityai get_user_account --connection_id`
  Retrieves the current user's Stability AI account information
- `robomotion stabilityai get_user_credit --connection_id`
  Retrieves the current user's Stability AI credit balance
- `robomotion stabilityai image_to_image --connection_id --in-image-path --in-prompt --in-init-image-path [--opt-engine-id] [--opt-neg-prompt] [--7] [--opt-clip-guidance-preset] [--opt-sampler] [--1] [--0] [--50] [--opt-style-preset] [--opt-init-image-mode] [--0.35] [--0.65] [--opt-step-schedule-end]`
  Generates new images based on an input image and text prompt using Stability AI
- `robomotion stabilityai masking --connection_id --in-image-path --in-init-image-path --in-engine-id --in-prompt [--7] [--opt-clip-guidance-preset] [--opt-sampler] [--1] [--0] [--50] [--opt-style-preset] [--opt-mask-source] [--opt-mask-image-path]`
  Generates images with masked inpainting using Stability AI
- `robomotion stabilityai text_to_image --connection_id --in-image-path --in-prompt [--opt-engine-id] [--opt-neg-prompt] [--opt-height] [--opt-width] [--7] [--opt-clip-guidance-preset] [--opt-sampler] [--1] [--0] [--50] [--opt-style-preset]`
  Generates images from text prompts using Stability AI
- `robomotion stabilityai upscale --connection_id --in-image-path --in-init-image-path [--opt-engine-id] [--opt-height] [--opt-width] [--opt-prompt] [--0] [--50] [--7]`
  Upscales an image to higher resolution using Stability AI

## Environment
- ROBOMOTION_API_TOKEN (if vault credentials are needed)
