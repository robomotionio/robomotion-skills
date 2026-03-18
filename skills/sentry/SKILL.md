---
name: "sentry"
description: "Sentry error tracking — monitor application errors and capture events. Supports error reporting, issue listing, and event tracking via `robomotion sentry`. Do NOT use for Datadog, Splunk, New Relic, or other APM platforms."
---

# Sentry

The `robomotion sentry` CLI connects to Sentry for application error tracking. It captures and reports events, monitors errors, and manages issue tracking.

## When to use
- Capture and report error events to Sentry
- Monitor application errors and exceptions
- Track issues and event history

## Prerequisites
- `robomotion` CLI installed
- Package installed: `robomotion install sentry`
- Sentry DSN or API token configured via Robomotion vault

## IMPORTANT: Session Mode Required for Multi-Step Operations
Each CLI command runs as a **separate process** — connection IDs from `connect` do NOT persist across calls.
You MUST use `--session` on `connect` and pass `--session-id` to all subsequent commands.

## Workflow
1. Install (once): `robomotion install sentry`
2. Connect with session:
   ```
   robomotion sentry sentry_connect --session --output json
   # → {"outClientId":"<client-id>","session_id":"<session-id>"}
   ```
3. Use the returned `client-id` and `session-id` in all subsequent commands:
   ```
   robomotion sentry sentry_capture_event --client-id "<client-id>" --message <text> --session-id "<session-id>" --output json
   ```
4. Disconnect when done:
   ```
   robomotion sentry sentry_disconnect --client-id "<client-id>" --session-id "<session-id>" --output json
   ```

**Always** append `--output json` to get structured JSON results.

## Commands Reference
- `robomotion sentry sentry_capture --message [--type] --output json`
  Captures and sends a message or exception to Sentry for error monitoring

## Environment
- ROBOMOTION_API_TOKEN (if vault credentials are needed)
