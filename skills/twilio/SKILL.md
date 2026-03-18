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

## Workflow
1. Install: `robomotion install twilio`
2. Connect: `robomotion twilio twilio_connect` → returns a `client-id`
3. Send SMS: `robomotion twilio twilio_send_sms --client-id <id> --to <phone> --body <text>`
4. Disconnect: `robomotion twilio twilio_disconnect --client-id <id>`

## Commands Reference
- `robomotion twilio connect`
  Connect to Twilio API using account credentials
- `robomotion twilio disconnect --connection-id`
  Closes the Twilio connection and releases resources
- `robomotion twilio receive_whatsapp_message --port`
  Receive incoming WhatsApp messages via Twilio webhook
- `robomotion twilio send_whatsapp_message --connection-id --from-number --to-number --message`
  Send a WhatsApp message via Twilio
- `robomotion twilio send_sms --connection-id --from-number --to-number --message`
  Send an SMS message via Twilio
- `robomotion twilio voice_call --connection-id --from-number --to-number --xml-url --message [--woman] [--en-gb]`
  Make a voice call using Twilio
- `robomotion twilio send_verification_code --connection-id --to-number [--channel]`
  Send a verification code via Twilio Verify
- `robomotion twilio check_verification_code --connection-id --to-number --verification-code`
  Check a verification code sent via Twilio Verify

## Environment
- ROBOMOTION_API_TOKEN (if vault credentials are needed)
