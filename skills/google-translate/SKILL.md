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

## Workflow
1. Install: `robomotion install googletranslate`
2. Connect: `robomotion googletranslate connect` → returns a `client-id`
3. Translate: `robomotion googletranslate translate --client-id <id> --text <text> --target-language <lang>`
4. Disconnect: `robomotion googletranslate disconnect --client-id <id>`

## Commands Reference
- `robomotion googletranslate text_translate --text [--target-language]`
  Translate text from one language to another using Google Cloud Translation API

## Environment
- ROBOMOTION_API_TOKEN (if vault credentials are needed)
