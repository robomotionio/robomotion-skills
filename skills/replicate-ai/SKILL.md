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

## Workflow
1. Install: `robomotion install replicateai`
2. Connect: `robomotion replicateai replicateai_connect` → returns a `client-id`
3. Run model: `robomotion replicateai replicateai_run --client-id <id> --model <owner/model> --input <json>`
4. Disconnect: `robomotion replicateai replicateai_disconnect --client-id <id>`

## Commands Reference
- `robomotion replicateai connect`
  Connect to Replicate AI and create a client session for running machine learning models
- `robomotion replicateai disconnect --connection-id`
  Closes the Replicate AI connection and releases resources
- `robomotion replicateai run_model --connection-id --owner/model:version --input [--timeout-(seconds)]`
  Run a machine learning model on Replicate AI and wait for completion
- `robomotion replicateai get_prediction --connection-id --prediction-id [--timeout-(seconds)]`
  Get the status and output of a prediction by ID
- `robomotion replicateai create_prediction --connection-id --owner/model:version --input [--timeout-(seconds)]`
  Create a prediction without waiting for completion - use Get Prediction to check status
- `robomotion replicateai get_model --connection-id --model-owner --model-name [--timeout-(seconds)]`
  Get information about a model including description٫ run count٫ and URLs
- `robomotion replicateai create_training --connection-id --model-owner --model-name --version --destination --inputs`
  Create a training job to fine-tune a model on your own data
- `robomotion replicateai get_training --connection-id --training-id`
  Get the status and output of a training job by ID
- `robomotion replicateai list_predictions --connection-id`
  List recent predictions from your Replicate account
- `robomotion replicateai cancel_prediction --connection-id --prediction-id`
  Cancel a running prediction by ID

## Environment
- ROBOMOTION_API_TOKEN (if vault credentials are needed)
