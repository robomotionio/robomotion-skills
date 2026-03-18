---
name: "replicate-ai"
description: "Replicate AI — run ML model predictions for image, video, text, and audio generation. Supports model execution, async predictions, streaming, and model management via `robomotion replicateai`. Do NOT use for OpenAI, Fal.ai, Stability AI, or other AI platforms."
---

# Replicate AI

The `robomotion replicateai` CLI runs AI model predictions on Replicate's cloud infrastructure. It supports running models synchronously or asynchronously, streaming predictions, listing and searching models, and managing prediction lifecycle.

## When to use
- Run AI model predictions (image gen, LLMs, audio, video)
- Submit async predictions and retrieve results later
- Stream prediction outputs in real-time
- Search and discover Replicate models

## Prerequisites
- `robomotion` CLI installed
- Package installed: `robomotion install replicateai`
- Replicate API token configured via Robomotion vault

## IMPORTANT: Session Mode Required for Multi-Step Operations
Each CLI command runs as a **separate process** — connection IDs from `connect` do NOT persist across calls.
You MUST use `--session` on `connect` and pass `--session-id` to all subsequent commands.

## Workflow
1. Install (once): `robomotion install replicateai`
2. Connect with session:
   ```
   robomotion replicateai replicateai_connect --session --output json
   # → {"outClientId":"<client-id>","session_id":"<session-id>"}
   ```
3. Use the returned `client-id` and `session-id` in all subsequent commands:
   ```
   robomotion replicateai replicateai_run --client-id "<client-id>" --model <owner/model> --input <json> --session-id "<session-id>" --output json
   ```
4. Disconnect when done:
   ```
   robomotion replicateai replicateai_disconnect --client-id "<client-id>" --session-id "<session-id>" --output json
   ```

**Always** append `--output json` to get structured JSON results.

## Commands Reference
- `robomotion replicateai connect --session --output json`
  Connect to Replicate AI and create a client session for running machine learning models
- `robomotion replicateai disconnect --connection-id --session-id "<session-id>" --output json`
  Closes the Replicate AI connection and releases resources
- `robomotion replicateai run_model --connection-id --owner/model:version --input [--timeout-(seconds)] --session-id "<session-id>" --output json`
  Run a machine learning model on Replicate AI and wait for completion
- `robomotion replicateai get_prediction --connection-id --prediction-id [--timeout-(seconds)] --session-id "<session-id>" --output json`
  Get the status and output of a prediction by ID
- `robomotion replicateai create_prediction --connection-id --owner/model:version --input [--timeout-(seconds)] --session-id "<session-id>" --output json`
  Create a prediction without waiting for completion - use Get Prediction to check status
- `robomotion replicateai get_model --connection-id --model-owner --model-name [--timeout-(seconds)] --session-id "<session-id>" --output json`
  Get information about a model including description٫ run count٫ and URLs
- `robomotion replicateai create_training --connection-id --model-owner --model-name --version --destination --inputs --session-id "<session-id>" --output json`
  Create a training job to fine-tune a model on your own data
- `robomotion replicateai get_training --connection-id --training-id --session-id "<session-id>" --output json`
  Get the status and output of a training job by ID
- `robomotion replicateai list_predictions --connection-id --session-id "<session-id>" --output json`
  List recent predictions from your Replicate account
- `robomotion replicateai cancel_prediction --connection-id --prediction-id --session-id "<session-id>" --output json`
  Cancel a running prediction by ID

## Environment
- ROBOMOTION_API_TOKEN (if vault credentials are needed)
