---
name: "whatsapp"
description: "WhatsApp Business API — send text messages, media, templates, and interactive messages. Supports message sending, contact management, and template messaging via `robomotion whatsapp`. Do NOT use for Telegram, Twilio SMS, or other messaging services."
---

# WhatsApp Business

The `robomotion whatsapp` CLI connects to the WhatsApp Business API for messaging operations. It sends text messages, images, documents, and template messages; manages contacts; and handles interactive message types.

## When to use
- Send text, image, document, or video messages via WhatsApp
- Send template messages for notifications and alerts
- Manage contacts and conversation threads

## Prerequisites
- `robomotion` CLI installed
- Package installed: `robomotion install whatsapp`
- WhatsApp Business API credentials configured via Robomotion vault

## IMPORTANT: Session Mode Required for Multi-Step Operations
Each CLI command runs as a **separate process** — connection IDs from `connect` do NOT persist across calls.
You MUST use `--session` on `connect` and pass `--session-id` to all subsequent commands.

## Workflow
1. Install (once): `robomotion install whatsapp`
2. Connect with session:
   ```
   robomotion whatsapp connect --session --output json
   # → {"outClientId":"<client-id>","session_id":"<session-id>"}
   ```
3. Use the returned `client-id` and `session-id` in all subsequent commands:
   ```
   robomotion whatsapp send_message --client-id "<client-id>" --to <phone> --text <text> --session-id "<session-id>" --output json
   ```
4. Disconnect when done:
   ```
   robomotion whatsapp disconnect --client-id "<client-id>" --session-id "<session-id>" --output json
   ```

**Always** append `--output json` to get structured JSON results.

## Commands Reference
- `robomotion whatsapp receive_events --127-0-0-1 --3000 [--/webhook] [--verify-token] --output json`
  Receive incoming WhatsApp messages via webhook
- `robomotion whatsapp send_text_message --phone-number-id --to-phone-number --message-text [--21-0] --output json`
  Send a text message via WhatsApp Business Cloud API
- `robomotion whatsapp send_template_message --phone-number-id --to-phone-number --template-name --template-params [--21-0] [--en-us] [--none] [--header-value] [--button-params] --output json`
  Send an approved template message via WhatsApp Business Cloud API
- `robomotion whatsapp send_image_message --phone-number-id --to-phone-number --image-url [--21-0] [--caption] --output json`
  Send an image via WhatsApp Business Cloud API
- `robomotion whatsapp send_video_message --phone-number-id --to-phone-number --video-url [--21-0] [--caption] --output json`
  Send a video via WhatsApp Business Cloud API
- `robomotion whatsapp send_document_message --phone-number-id --to-phone-number --document-url [--21-0] [--caption] [--filename] --output json`
  Send a document via WhatsApp Business Cloud API
- `robomotion whatsapp send_audio_message --phone-number-id --to-phone-number --audio-url [--21-0] --output json`
  Send an audio file via WhatsApp Business Cloud API
- `robomotion whatsapp send_location_message --phone-number-id --to-phone-number --latitude --longitude [--21-0] [--location-name] [--address] --output json`
  Send a location via WhatsApp Business Cloud API
- `robomotion whatsapp send_contact_message --phone-number-id --to-phone-number --contacts [--21-0] --output json`
  Send contact information via WhatsApp Business Cloud API
- `robomotion whatsapp send_reply_buttons --phone-number-id --to-phone-number --body-text --buttons [--21-0] [--header-text] [--footer-text] --output json`
  Send interactive reply buttons via WhatsApp Business Cloud API
- `robomotion whatsapp send_list_message --phone-number-id --to-phone-number --body-text --button-text --sections [--21-0] [--header-text] [--footer-text] --output json`
  Send an interactive list message via WhatsApp Business Cloud API
- `robomotion whatsapp mark_as_read --phone-number-id --message-id [--21-0] --output json`
  Mark a WhatsApp message as read
- `robomotion whatsapp get_media_url --media-id [--21-0] --output json`
  Get the download URL for a WhatsApp media file
- `robomotion whatsapp upload_media --phone-number-id --file-path --mime-type [--21-0] --output json`
  Upload a media file to WhatsApp servers

## Environment
- ROBOMOTION_API_TOKEN (if vault credentials are needed)
