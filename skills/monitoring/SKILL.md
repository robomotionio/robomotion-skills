---
name: "monitoring"
description: "Uptime monitoring — check website and API endpoint health, ping services, and monitor HTTP status. Supports health checks, response time measurement, and availability tracking via `robomotion monitoring`. Do NOT use for Sentry, Datadog, Splunk, or application-level monitoring."
---

# Monitoring

The `robomotion monitoring` CLI provides uptime and health monitoring for websites, APIs, and services. It pings endpoints, checks HTTP status codes, measures response times, and tracks service availability.

## When to use
- Check if a website or API endpoint is up and responding
- Monitor HTTP response codes and response times
- Ping services and track availability

## Prerequisites
- `robomotion` CLI installed
- Package installed: `robomotion install monitoring`
- No external credentials needed for basic HTTP monitoring

## IMPORTANT: Session Mode Required for Multi-Step Operations
Each CLI command runs as a **separate process** — connection IDs from `connect` do NOT persist across calls.
You MUST use `--session` on `connect` and pass `--session-id` to all subsequent commands.

## Workflow
1. Install (once): `robomotion install monitoring`
2. Connect with session:
   ```
   robomotion monitoring monitoring_connect --session --output json
   # → {"outClientId":"<client-id>","session_id":"<session-id>"}
   ```
3. Use the returned `client-id` and `session-id` in all subsequent commands:
   ```
   robomotion monitoring monitoring_check --client-id "<client-id>" --url <url> --session-id "<session-id>" --output json
   ```
4. Disconnect when done:
   ```
   robomotion monitoring monitoring_disconnect --client-id "<client-id>" --session-id "<session-id>" --output json
   ```

**Always** append `--output json` to get structured JSON results.

## Commands Reference
- `robomotion monitoring dns_check --domain [--record-type] [--30] --output json`
  Checks DNS records for a domain including A⸴ MX⸴ TXT⸴ NS⸴ and CNAME records
- `robomotion monitoring keyword_check --url --keywords [--check-if-keywords] [--30] --output json`
  Checks if specified keywords exist or do not exist on a webpage
- `robomotion monitoring ping_check --host [--4] [--30] [--1000] --output json`
  Pings a host and returns latency and packet loss statistics
- `robomotion monitoring port_check --ip --port [--check-port] [--30] --output json`
  Checks if a TCP port is open or closed on a given IP address
- `robomotion monitoring ssl_check --url --443 [--30] --output json`
  Validates SSL certificate and returns expiry⸴ issuer⸴ and subject information
- `robomotion monitoring website_check --url [--30] --output json`
  Checks if a website is alive and returns status code and response time

## Environment
- ROBOMOTION_API_TOKEN (if vault credentials are needed)
