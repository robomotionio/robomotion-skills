---
name: "google-speech"
description: "Google Speech — transcribe audio to text (speech-to-text) and convert text to speech (TTS). Supports multiple languages and audio formats via `robomotion googlespeech`. Do NOT use for OpenAI Whisper, ElevenLabs, or other speech services."
---

# Google Speech

The `robomotion googlespeech` CLI connects to Google Cloud Speech APIs for audio transcription and speech synthesis. It transcribes audio files to text and converts text to speech audio files.

## When to use
- Transcribe audio files to text in multiple languages
- Convert text to speech audio files

## Prerequisites
- `robomotion` CLI installed
- Package installed: `robomotion install googlespeech`
- Google Cloud Speech API credentials configured via Robomotion vault

## IMPORTANT: Session Mode Required for Multi-Step Operations
Each CLI command runs as a **separate process** — connection IDs from `connect` do NOT persist across calls.
You MUST use `--session` on `connect` and pass `--session-id` to all subsequent commands.

## Workflow
1. Install (once): `robomotion install googlespeech`
2. Connect with session:
   ```
   robomotion googlespeech connect --session --output json
   # → {"outClientId":"<client-id>","session_id":"<session-id>"}
   ```
3. Use the returned `client-id` and `session-id` in all subsequent commands:
   ```
   robomotion googlespeech speech_to_text --client-id "<client-id>" --audio-file <path> --session-id "<session-id>" --output json
   ```
4. Disconnect when done:
   ```
   robomotion googlespeech disconnect --client-id "<client-id>" --session-id "<session-id>" --output json
   ```

**Always** append `--output json` to get structured JSON results.

## Commands Reference
- `robomotion googlespeech speech_to_text --gcs-uri [--sample-rate] [--language-code] [--model] --output json`
  Convert speech audio from Google Cloud Storage to text using Google Cloud Speech-to-Text API
- `robomotion googlespeech text_to_speech --text --input-path [--audio-encoding] [--language-code] [--voice-name] [--sample-rate] --output json`
  Convert text to speech audio using Google Cloud Text-to-Speech API

## Environment
- ROBOMOTION_API_TOKEN (if vault credentials are needed)
