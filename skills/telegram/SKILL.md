---
name: "telegram"
description: "Use when the user wants to call the Robomotion Telegram Bot package to send messages or interact with Telegram chats via the `robomotion telegrambot` CLI. Do NOT use for WhatsApp, Slack, or other messaging platforms."
---

# Telegram Skill

## When to use
- Send messages via a Telegram bot
- Send photos or files via Telegram
- Read messages from Telegram chats

## Prerequisites
- `robomotion` CLI installed
- Package installed: `robomotion install telegrambot`
- Credentials configured via Robomotion vault or environment variables

## Workflow
1. Install the package: `robomotion install telegrambot`
2. Run commands: `robomotion telegrambot <command> [flags]`

## Commands Reference
- `robomotion telegrambot connect`
  Connect to Telegram using a bot token
- `robomotion telegrambot get_bot_info --client-id`
  Get information about the connected Telegram bot
- `robomotion telegrambot download_file --client-id --file-id --save-path`
  Download a file from Telegram to local storage
- `robomotion telegrambot get_file_path --client-id --file-id`
  Get the file path for a Telegram file
- `robomotion telegrambot create_invite_link --client-id --0`
  Create an invite link for a Telegram chat
- `robomotion telegrambot send_message --client-id --chat-id --message-text [--0] [--parse-mode]`
  Send a text message to a Telegram chat
- `robomotion telegrambot receive_message [--0] [--0]`
  Receive and process incoming messages from a Telegram bot
- `robomotion telegrambot forward_message --client-id --from-chat-id --to-chat-id --message-id`
  Forward a message from one Telegram chat to another
- `robomotion telegrambot disconnect --client-id`
  Disconnect from Telegram and cleanup resources
- `robomotion telegrambot send_photo --client-id --chat-id --photo-url-or-path [--0] [--caption]`
  Send a photo to a Telegram chat
- `robomotion telegrambot send_audio --client-id --chat-id --audio-url-or-path [--0] [--caption] [--file-name] [--mime-type]`
  Send an audio file to a Telegram chat
- `robomotion telegrambot send_document --client-id --chat-id --document-path [--0] [--caption] [--file-name] [--mime-type]`
  Send a document to a Telegram chat

## Environment
- ROBOMOTION_API_TOKEN (if vault credentials are needed)
