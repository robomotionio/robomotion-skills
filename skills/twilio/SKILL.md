---
name: "twilio"
description: "Twilio — send SMS/MMS messages, make phone calls, and manage communication resources. Supports messaging, voice calls, and phone number lookup via `robomotion twilio`. Do NOT use for WhatsApp, Telegram, email, or other messaging platforms."
---

# Twilio

The `robomotion twilio` CLI connects to Twilio for cloud communications. It sends SMS and MMS messages, initiates phone calls, looks up phone number information, and manages Twilio messaging resources.

## When to use
- Send SMS or MMS messages to phone numbers
- Initiate and manage phone calls
- Look up phone number carrier and format information
- Manage messaging services and resources

## Prerequisites
- `robomotion` CLI installed
- Package installed: `robomotion install twilio`
- Twilio Account SID and Auth Token configured via Robomotion vault

## IMPORTANT: Session Mode Required for Multi-Step Operations
Each CLI command runs as a **separate process** — connection IDs from `connect` do NOT persist across calls.
You MUST use `--session` on `connect` and pass `--session-id` to all subsequent commands.

## Workflow
1. Install (once): `robomotion install twilio`
2. Connect with session:
   ```
   robomotion twilio twilio_connect --session --output json
   # → {"outClientId":"<client-id>","session_id":"<session-id>"}
   ```
3. Use the returned `client-id` and `session-id` in all subsequent commands:
   ```
   robomotion twilio twilio_send_sms --client-id "<client-id>" --to <phone> --body <text> --session-id "<session-id>" --output json
   ```
4. Disconnect when done:
   ```
   robomotion twilio twilio_disconnect --client-id "<client-id>" --session-id "<session-id>" --output json
   ```

**Always** append `--output json` to get structured JSON results.

## Commands Reference
- `robomotion twilio connect --session --output json`
  Connect to Twilio API using account credentials
- `robomotion twilio disconnect --connection-id --session-id "<session-id>" --output json`
  Closes the Twilio connection and releases resources
- `robomotion twilio receive_whatsapp_message --port --output json`
  Receive incoming WhatsApp messages via Twilio webhook
- `robomotion twilio send_whatsapp_message --connection-id --from-number --to-number --message --session-id "<session-id>" --output json`
  Send a WhatsApp message via Twilio
- `robomotion twilio send_sms --connection-id --from-number --to-number --message --session-id "<session-id>" --output json`
  Send an SMS message via Twilio
- `robomotion twilio voice_call --connection-id --from-number --to-number --xml-url --message [--woman] [--en-gb] --session-id "<session-id>" --output json`
  Make a voice call using Twilio
- `robomotion twilio send_verification_code --connection-id --to-number [--channel] --session-id "<session-id>" --output json`
  Send a verification code via Twilio Verify
- `robomotion twilio check_verification_code --connection-id --to-number --verification-code --session-id "<session-id>" --output json`
  Check a verification code sent via Twilio Verify

## Environment
- ROBOMOTION_API_TOKEN (if vault credentials are needed)
