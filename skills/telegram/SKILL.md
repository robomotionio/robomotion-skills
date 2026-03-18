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

## IMPORTANT: Session Mode Required for Multi-Step Operations
Each CLI command runs as a **separate process** — connection IDs from `connect` do NOT persist across calls.
You MUST use `--session` on `connect` and pass `--session-id` to all subsequent commands.

## Workflow
1. Install (once): `robomotion install telegrambot`
2. Connect with session:
   ```
   robomotion telegrambot connect --session --output json
   # → {"outClientId":"<client-id>","session_id":"<session-id>"}
   ```
3. Use the returned `client-id` and `session-id` in all subsequent commands:
   ```
   robomotion telegrambot send_message --client-id "<client-id>" --chat-id <chat> --text <text> --session-id "<session-id>" --output json
   ```
4. Disconnect when done:
   ```
   robomotion telegrambot disconnect --client-id "<client-id>" --session-id "<session-id>" --output json
   ```

**Always** append `--output json` to get structured JSON results.

## Commands Reference
- `robomotion telegrambot connect --session --output json`
  Connect to Telegram using a bot token
- `robomotion telegrambot get_bot_info --client-id --session-id "<session-id>" --output json`
  Get information about the connected Telegram bot
- `robomotion telegrambot download_file --client-id --file-id --save-path --session-id "<session-id>" --output json`
  Download a file from Telegram to local storage
- `robomotion telegrambot get_file_path --client-id --file-id --session-id "<session-id>" --output json`
  Get the file path for a Telegram file
- `robomotion telegrambot create_invite_link --client-id --0 --session-id "<session-id>" --output json`
  Create an invite link for a Telegram chat
- `robomotion telegrambot send_message --client-id --chat-id --message-text [--0] [--parse-mode] --session-id "<session-id>" --output json`
  Send a text message to a Telegram chat
- `robomotion telegrambot receive_message [--0] [--0] --output json`
  Receive and process incoming messages from a Telegram bot
- `robomotion telegrambot forward_message --client-id --from-chat-id --to-chat-id --message-id --session-id "<session-id>" --output json`
  Forward a message from one Telegram chat to another
- `robomotion telegrambot disconnect --client-id --session-id "<session-id>" --output json`
  Disconnect from Telegram and cleanup resources
- `robomotion telegrambot send_photo --client-id --chat-id --photo-url-or-path [--0] [--caption] --session-id "<session-id>" --output json`
  Send a photo to a Telegram chat
- `robomotion telegrambot send_audio --client-id --chat-id --audio-url-or-path [--0] [--caption] [--file-name] [--mime-type] --session-id "<session-id>" --output json`
  Send an audio file to a Telegram chat
- `robomotion telegrambot send_document --client-id --chat-id --document-path [--0] [--caption] [--file-name] [--mime-type] --session-id "<session-id>" --output json`
  Send a document to a Telegram chat

## Environment
- ROBOMOTION_API_TOKEN (if vault credentials are needed)
