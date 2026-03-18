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

## Workflow
1. Install: `robomotion install googlespeech`
2. Connect: `robomotion googlespeech connect` → returns a `client-id`
3. Transcribe: `robomotion googlespeech speech_to_text --client-id <id> --audio-file <path>`
4. Disconnect: `robomotion googlespeech disconnect --client-id <id>`

## Commands Reference
- `robomotion googlespeech speech_to_text --gcs-uri [--sample-rate] [--language-code] [--model]`
  Convert speech audio from Google Cloud Storage to text using Google Cloud Speech-to-Text API
- `robomotion googlespeech text_to_speech --text --input-path [--audio-encoding] [--language-code] [--voice-name] [--sample-rate]`
  Convert text to speech audio using Google Cloud Text-to-Speech API

## Environment
- ROBOMOTION_API_TOKEN (if vault credentials are needed)
