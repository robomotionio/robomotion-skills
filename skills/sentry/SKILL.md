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

## Workflow
1. Install: `robomotion install sentry`
2. Connect: `robomotion sentry sentry_connect` → returns a `client-id`
3. Capture event: `robomotion sentry sentry_capture_event --client-id <id> --message <text>`
4. Disconnect: `robomotion sentry sentry_disconnect --client-id <id>`

## Commands Reference
- `robomotion sentry sentry_capture --message [--type]`
  Captures and sends a message or exception to Sentry for error monitoring

## Environment
- ROBOMOTION_API_TOKEN (if vault credentials are needed)
