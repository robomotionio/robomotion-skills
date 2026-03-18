---
name: "elevenlabs-ai"
description: "ElevenLabs AI speech platform — text-to-speech, speech-to-text, voice cloning, sound effects, and audio isolation. Supports 30+ languages, voice management, and pronunciation dictionaries via `robomotion elevenlabsai`. Do NOT use for OpenAI TTS, Google Speech, Amazon Polly, or other speech services."
---

# ElevenLabs AI

The `robomotion elevenlabsai` CLI connects to ElevenLabs for AI speech synthesis and processing. It generates natural-sounding speech from text in 30+ languages, transcribes audio, clones voices, creates sound effects, isolates audio, and manages voice libraries and pronunciation dictionaries.

## When to use
- Convert text to natural-sounding speech with selectable voices
- Transcribe audio files to text (speech-to-text)
- Clone voices or generate sound effects from descriptions
- Manage voice library, pronunciation dictionaries, and models

## Prerequisites
- `robomotion` CLI installed
- Package installed: `robomotion install elevenlabsai`
- ElevenLabs API key configured via Robomotion vault

## IMPORTANT: Session Mode Required for Multi-Step Operations
Each CLI command runs as a **separate process** — connection IDs from `connect` do NOT persist across calls.
You MUST use `--session` on `connect` and pass `--session-id` to all subsequent commands.

## Workflow
1. Install (once): `robomotion install elevenlabsai`
2. Connect with session:
   ```
   robomotion elevenlabsai elevenlabs_connect --session --output json
   # → {"outClientId":"<client-id>","session_id":"<session-id>"}
   ```
3. Use the returned `client-id` and `session-id` in all subsequent commands:
   ```
   robomotion elevenlabsai text_to_speech --client-id "<client-id>" --text <text> --voice-id <voice> --session-id "<session-id>" --output json
   ```
4. Disconnect when done:
   ```
   robomotion elevenlabsai elevenlabs_disconnect --client-id "<client-id>" --session-id "<session-id>" --output json
   ```

**Always** append `--output json` to get structured JSON results.

## Commands Reference
- `robomotion elevenlabsai add_voice --connection_id --in-name --files [--opt-description] [--opt-labels] --session-id "<session-id>" --output json`
  Adds a new voice to ElevenLabs using audio samples
- `robomotion elevenlabsai clone_voice --connection_id --in-name --files [--opt-description] --session-id "<session-id>" --output json`
  Creates a clone of a voice using audio samples
- `robomotion elevenlabsai connect --session --output json`
  Establishes a connection to ElevenLabs AI using API credentials
- `robomotion elevenlabsai delete_history_item --connection_id --in-history-item-id --session-id "<session-id>" --output json`
  Deletes a history item from ElevenLabs
- `robomotion elevenlabsai delete_voice --connection_id --in-voice-id --session-id "<session-id>" --output json`
  Deletes a voice from ElevenLabs by ID
- `robomotion elevenlabsai disconnect --connection_id --session-id "<session-id>" --output json`
  Closes an existing ElevenLabs AI connection and releases resources
- `robomotion elevenlabsai edit_voice --connection_id --in-voice-id --in-name --files [--opt-description] [--opt-labels] --session-id "<session-id>" --output json`
  Edits an existing voice's properties in ElevenLabs
- `robomotion elevenlabsai edit_voice_settings --connection_id --in-voice-id --0.5 --0.75 --session-id "<session-id>" --output json`
  Updates the settings for a specific voice
- `robomotion elevenlabsai get_audio_from_history_item --connection_id --in-history-item-id --in-path --session-id "<session-id>" --output json`
  Downloads the audio file from a history item
- `robomotion elevenlabsai get_history --connection_id --100 [--opt-last-history-item-id] --session-id "<session-id>" --output json`
  Retrieves the generation history from ElevenLabs
- `robomotion elevenlabsai get_history_item --connection_id --in-history-item-id --session-id "<session-id>" --output json`
  Retrieves a specific history item by ID
- `robomotion elevenlabsai get_models --connection_id --session-id "<session-id>" --output json`
  Retrieves the list of available ElevenLabs AI models
- `robomotion elevenlabsai get_user_info --connection_id --session-id "<session-id>" --output json`
  Retrieves the current user's ElevenLabs account information
- `robomotion elevenlabsai get_user_subscription_info --connection_id --session-id "<session-id>" --output json`
  Retrieves the current user's ElevenLabs subscription information
- `robomotion elevenlabsai get_voice --connection_id --in-voice-id --session-id "<session-id>" --output json`
  Retrieves details for a specific voice by ID
- `robomotion elevenlabsai get_voice_settings --connection_id --in-voice-id --session-id "<session-id>" --output json`
  Retrieves the settings for a specific voice by ID
- `robomotion elevenlabsai get_voices --connection_id --session-id "<session-id>" --output json`
  Retrieves all available voices from ElevenLabs AI
- `robomotion elevenlabsai speech_to_speech --connection_id --in-source-audio-path --in-output-path --in-voice-id [--0.5] [--0.75] --session-id "<session-id>" --output json`
  Converts speech from one voice to another using ElevenLabs AI
- `robomotion elevenlabsai speech_to_text --connection_id --in-audio-path [--opt-model] [--opt-language] [--opt-prompt] [--0] --session-id "<session-id>" --output json`
  Transcribes audio to text using ElevenLabs AI
- `robomotion elevenlabsai text_to_speech --connection_id --in-path --in-voice-id --in-text [--0.5] [--0.75] [--opt-model] --session-id "<session-id>" --output json`
  Converts text to speech audio using ElevenLabs AI

## Environment
- ROBOMOTION_API_TOKEN (if vault credentials are needed)
