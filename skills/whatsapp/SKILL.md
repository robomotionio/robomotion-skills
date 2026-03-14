---
name: "whatsapp"
description: "Use when the user wants to call the Robomotion WhatsApp package to send messages or media via the WhatsApp Business API using the `robomotion whatsapp` CLI. Do NOT use for Telegram, SMS, or other messaging platforms."
---

# Whatsapp Skill

## When to use
- Send WhatsApp messages via the Business API
- Send media (images, documents) via WhatsApp
- Manage WhatsApp message templates

## Prerequisites
- `robomotion` CLI installed
- Package installed: `robomotion install whatsapp`
- Credentials configured via Robomotion vault or environment variables

## Workflow
1. Install the package: `robomotion install whatsapp`
2. Run commands: `robomotion whatsapp <command> [flags]`

## Commands Reference
- `robomotion whatsapp receive_events --127-0-0-1 --3000 [--/webhook] [--verify-token]`
  Receive incoming WhatsApp messages via webhook
- `robomotion whatsapp send_text_message --phone-number-id --to-phone-number --message-text [--21-0]`
  Send a text message via WhatsApp Business Cloud API
- `robomotion whatsapp send_template_message --phone-number-id --to-phone-number --template-name --template-params [--21-0] [--en-us] [--none] [--header-value] [--button-params]`
  Send an approved template message via WhatsApp Business Cloud API
- `robomotion whatsapp send_image_message --phone-number-id --to-phone-number --image-url [--21-0] [--caption]`
  Send an image via WhatsApp Business Cloud API
- `robomotion whatsapp send_video_message --phone-number-id --to-phone-number --video-url [--21-0] [--caption]`
  Send a video via WhatsApp Business Cloud API
- `robomotion whatsapp send_document_message --phone-number-id --to-phone-number --document-url [--21-0] [--caption] [--filename]`
  Send a document via WhatsApp Business Cloud API
- `robomotion whatsapp send_audio_message --phone-number-id --to-phone-number --audio-url [--21-0]`
  Send an audio file via WhatsApp Business Cloud API
- `robomotion whatsapp send_location_message --phone-number-id --to-phone-number --latitude --longitude [--21-0] [--location-name] [--address]`
  Send a location via WhatsApp Business Cloud API
- `robomotion whatsapp send_contact_message --phone-number-id --to-phone-number --contacts [--21-0]`
  Send contact information via WhatsApp Business Cloud API
- `robomotion whatsapp send_reply_buttons --phone-number-id --to-phone-number --body-text --buttons [--21-0] [--header-text] [--footer-text]`
  Send interactive reply buttons via WhatsApp Business Cloud API
- `robomotion whatsapp send_list_message --phone-number-id --to-phone-number --body-text --button-text --sections [--21-0] [--header-text] [--footer-text]`
  Send an interactive list message via WhatsApp Business Cloud API
- `robomotion whatsapp mark_as_read --phone-number-id --message-id [--21-0]`
  Mark a WhatsApp message as read
- `robomotion whatsapp get_media_url --media-id [--21-0]`
  Get the download URL for a WhatsApp media file
- `robomotion whatsapp upload_media --phone-number-id --file-path --mime-type [--21-0]`
  Upload a media file to WhatsApp servers

## Environment
- ROBOMOTION_API_TOKEN (if vault credentials are needed)
