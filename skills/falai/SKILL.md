---
name: "falai"
description: "Fal.ai AI model runner — generate images, videos, and audio using cloud-hosted ML models. Supports synchronous and async (queue-based) inference via `robomotion falai`. Do NOT use for OpenAI, Stability AI, Replicate, or other AI inference platforms."
---

# Fal AI

The `robomotion falai` CLI runs AI models hosted on Fal.ai for image generation, video generation, text-to-speech, and other ML tasks. It supports both synchronous execution (wait for result) and async queue-based workflows (submit, poll status, retrieve result).

## When to use
- Generate images (Flux, SDXL, etc.) via Fal.ai
- Run video or audio generation models
- Submit long-running AI jobs to a queue and poll for results
- Cancel or check status of queued inference requests

## Prerequisites
- `robomotion` CLI installed
- Package installed: `robomotion install falai`
- Fal.ai API key configured via Robomotion vault

## Workflow
1. Install: `robomotion install falai`
2. Connect: `robomotion falai falai_connect` → returns a `client-id`
3. Run a model: `robomotion falai falai_run_model --client-id <id> --model-id <model> --input <json>`
4. Or submit async: `robomotion falai falai_submit_request --client-id <id> --model-id <model> --input <json>`
5. Disconnect: `robomotion falai falai_disconnect --client-id <id>`

## Commands Reference
- `robomotion falai falai_connect`
  Connects to Fal.ai API and returns a client ID for subsequent nodes
- `robomotion falai falai_disconnect --client-id`
  Closes the Fal.ai connection and releases resources
- `robomotion falai falai_run_model --client-id --model-id --input [--300] [--mode]`
  Runs an AI model on Fal.ai and waits for the result. Supports any model (image generation，video generation，TTS，etc.)
- `robomotion falai falai_submit_request --client-id --model-id --input [--webhook-url]`
  Submits a request to the Fal.ai queue and returns immediately with a request ID for async tracking
- `robomotion falai falai_get_status --client-id --model-id --request-id`
  Checks the status of a queued Fal.ai request
- `robomotion falai falai_get_result --client-id --model-id --request-id`
  Retrieves the result of a completed Fal.ai request
- `robomotion falai falai_cancel_request --client-id --model-id --request-id`
  Cancels a queued Fal.ai request

## Environment
- ROBOMOTION_API_TOKEN (if vault credentials are needed)
