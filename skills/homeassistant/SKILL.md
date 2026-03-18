---
name: "homeassistant"
description: "Home Assistant — control smart home devices, call services, read states, manage automations, and monitor events. Supports device control, scene activation, and history queries via `robomotion homeassistant`. Do NOT use for AWS IoT, Google Home API, or other IoT platforms."
---

# Home Assistant

The `robomotion homeassistant` CLI connects to Home Assistant for smart home control and automation. It reads device states and sensor values, calls services (turn on/off, set temperature, etc.), activates scenes, fires events, and queries state history.

## When to use
- Control smart home devices — turn on/off lights, switches, etc.
- Read device states and sensor readings
- Call Home Assistant services and activate scenes
- Query state history and fire custom events

## Prerequisites
- `robomotion` CLI installed
- Package installed: `robomotion install homeassistant`
- Home Assistant URL and long-lived access token configured via Robomotion vault

## IMPORTANT: Session Mode Required for Multi-Step Operations
Each CLI command runs as a **separate process** — connection IDs from `connect` do NOT persist across calls.
You MUST use `--session` on `connect` and pass `--session-id` to all subsequent commands.

## Workflow
1. Install (once): `robomotion install homeassistant`
2. Connect with session:
   ```
   robomotion homeassistant ha_connect --session --output json
   # → {"outClientId":"<client-id>","session_id":"<session-id>"}
   ```
3. Use the returned `client-id` and `session-id` in all subsequent commands:
   ```
   robomotion homeassistant ha_get_state --client-id "<client-id>" --entity-id <entity> --session-id "<session-id>" --output json
   ```
4. Disconnect when done:
   ```
   robomotion homeassistant ha_disconnect --client-id "<client-id>" --session-id "<session-id>" --output json
   ```

**Always** append `--output json` to get structured JSON results.

## Commands Reference
- `robomotion homeassistant homeassistant_connect --http://localhost:8123 --session --output json`
  Connects to Home Assistant and returns a client ID
- `robomotion homeassistant homeassistant_disconnect --client-id --session-id "<session-id>" --output json`
  Closes the Home Assistant connection and releases resources
- `robomotion homeassistant homeassistant_get_state --client-id --entity-id [--base-url] --session-id "<session-id>" --output json`
  Gets the current state of an entity in Home Assistant
- `robomotion homeassistant homeassistant_get_states --client-id [--base-url] --session-id "<session-id>" --output json`
  Gets all entity states from Home Assistant
- `robomotion homeassistant homeassistant_set_state --client-id --entity-id --state --attributes [--base-url] --session-id "<session-id>" --output json`
  Creates or updates the state of an entity in Home Assistant
- `robomotion homeassistant homeassistant_call_service --client-id --domain --service --entity-id --service-data [--base-url] --session-id "<session-id>" --output json`
  Calls a service in Home Assistant (e.g. light.turn_on，switch.toggle)
- `robomotion homeassistant homeassistant_get_services --client-id [--base-url] --session-id "<session-id>" --output json`
  Lists all available services in Home Assistant
- `robomotion homeassistant homeassistant_fire_event --client-id --event-type --event-data [--base-url] --session-id "<session-id>" --output json`
  Fires a custom event in Home Assistant
- `robomotion homeassistant homeassistant_get_config --client-id [--base-url] --session-id "<session-id>" --output json`
  Gets the Home Assistant configuration
- `robomotion homeassistant homeassistant_render_template --client-id --template [--base-url] --session-id "<session-id>" --output json`
  Renders a Jinja2 template in Home Assistant
- `robomotion homeassistant homeassistant_get_error_log --client-id [--base-url] --session-id "<session-id>" --output json`
  Gets the Home Assistant error log

## Environment
- ROBOMOTION_API_TOKEN (if vault credentials are needed)
