---
name: "telegram"
description: "Telegram Bot — send messages, photos, documents, manage chats, and handle updates. Supports inline keyboards, chat management, and file operations via `robomotion telegrambot`. Do NOT use for WhatsApp, Slack, Discord, or other messaging platforms."
---

# Telegram Bot

The `robomotion telegrambot` CLI operates a Telegram bot for messaging and chat interaction. It sends text messages, photos, and documents; manages chats and members; handles inline keyboards; and processes incoming updates.

## When to use
- Send text messages, photos, or documents to Telegram chats
- Manage chats, members, and chat settings
- Create inline keyboards for interactive bot responses
- Listen for and process incoming messages/updates

## Prerequisites
- `robomotion` CLI installed
- Package installed: `robomotion install telegrambot`
- Telegram bot token configured via Robomotion vault

## Workflow
1. Install: `robomotion install telegrambot`
2. Connect: `robomotion telegrambot connect` → returns a `client-id`
3. Send message: `robomotion telegrambot send_message --client-id <id> --chat-id <chat> --text <text>`
4. Disconnect: `robomotion telegrambot disconnect --client-id <id>`

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
