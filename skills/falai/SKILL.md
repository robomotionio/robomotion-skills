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

## IMPORTANT: Session Mode Required for Multi-Step Operations
Each CLI command runs as a **separate process** — connection IDs from `connect` do NOT persist across calls.
You MUST use `--session` on `connect` and pass `--session-id` to all subsequent commands.

## Workflow
1. Install (once): `robomotion install falai`
2. Connect with session:
   ```
   robomotion falai falai_connect --session --output json
   # → {"outClientId":"<client-id>","session_id":"<session-id>"}
   ```
3. Use the returned `client-id` and `session-id` in all subsequent commands:
   ```
   robomotion falai falai_run_model --client-id "<client-id>" --model-id <model> --input <json> --session-id "<session-id>" --output json
   ```
4. Disconnect when done:
   ```
   robomotion falai falai_disconnect --client-id "<client-id>" --session-id "<session-id>" --output json
   ```

**Always** append `--output json` to get structured JSON results.

## Commands Reference
- `robomotion falai falai_connect --session --output json`
  Connects to Fal.ai API and returns a client ID for subsequent nodes
- `robomotion falai falai_disconnect --client-id --session-id "<session-id>" --output json`
  Closes the Fal.ai connection and releases resources
- `robomotion falai falai_run_model --client-id --model-id --input [--300] [--mode] --session-id "<session-id>" --output json`
  Runs an AI model on Fal.ai and waits for the result. Supports any model (image generation，video generation，TTS，etc.)
- `robomotion falai falai_submit_request --client-id --model-id --input [--webhook-url] --session-id "<session-id>" --output json`
  Submits a request to the Fal.ai queue and returns immediately with a request ID for async tracking
- `robomotion falai falai_get_status --client-id --model-id --request-id --session-id "<session-id>" --output json`
  Checks the status of a queued Fal.ai request
- `robomotion falai falai_get_result --client-id --model-id --request-id --session-id "<session-id>" --output json`
  Retrieves the result of a completed Fal.ai request
- `robomotion falai falai_cancel_request --client-id --model-id --request-id --session-id "<session-id>" --output json`
  Cancels a queued Fal.ai request

## Environment
- ROBOMOTION_API_TOKEN (if vault credentials are needed)
