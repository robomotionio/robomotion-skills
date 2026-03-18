---
name: "google-translate"
description: "Google Translate — translate text between languages using Google Cloud Translation API. Supports language detection and 100+ languages via `robomotion googletranslate`. Do NOT use for OpenAI, Claude, DeepL, or other translation services."
---

# Google Translate

The `robomotion googletranslate` CLI connects to Google Cloud Translation API for text translation between 100+ languages with automatic language detection.

## When to use
- Translate text from one language to another
- Auto-detect source language
- Batch translate multiple texts

## Prerequisites
- `robomotion` CLI installed
- Package installed: `robomotion install googletranslate`
- Google Cloud Translation API credentials configured via Robomotion vault

## IMPORTANT: Session Mode Required for Multi-Step Operations
Each CLI command runs as a **separate process** — connection IDs from `connect` do NOT persist across calls.
You MUST use `--session` on `connect` and pass `--session-id` to all subsequent commands.

## Workflow
1. Install (once): `robomotion install googletranslate`
2. Connect with session:
   ```
   robomotion googletranslate connect --session --output json
   # → {"outClientId":"<client-id>","session_id":"<session-id>"}
   ```
3. Use the returned `client-id` and `session-id` in all subsequent commands:
   ```
   robomotion googletranslate translate --client-id "<client-id>" --text <text> --target-language <lang> --session-id "<session-id>" --output json
   ```
4. Disconnect when done:
   ```
   robomotion googletranslate disconnect --client-id "<client-id>" --session-id "<session-id>" --output json
   ```

**Always** append `--output json` to get structured JSON results.

## Commands Reference
- `robomotion googletranslate text_translate --text [--target-language] --output json`
  Translate text from one language to another using Google Cloud Translation API

## Environment
- ROBOMOTION_API_TOKEN (if vault credentials are needed)
