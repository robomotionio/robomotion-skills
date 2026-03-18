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

## Workflow
1. Install: `robomotion install monitoring`
2. Connect: `robomotion monitoring monitoring_connect` → returns a `client-id`
3. Check: `robomotion monitoring monitoring_check --client-id <id> --url <url>`
4. Disconnect: `robomotion monitoring monitoring_disconnect --client-id <id>`

## Commands Reference
- `robomotion monitoring dns_check --domain [--record-type] [--30]`
  Checks DNS records for a domain including A⸴ MX⸴ TXT⸴ NS⸴ and CNAME records
- `robomotion monitoring keyword_check --url --keywords [--check-if-keywords] [--30]`
  Checks if specified keywords exist or do not exist on a webpage
- `robomotion monitoring ping_check --host [--4] [--30] [--1000]`
  Pings a host and returns latency and packet loss statistics
- `robomotion monitoring port_check --ip --port [--check-port] [--30]`
  Checks if a TCP port is open or closed on a given IP address
- `robomotion monitoring ssl_check --url --443 [--30]`
  Validates SSL certificate and returns expiry⸴ issuer⸴ and subject information
- `robomotion monitoring website_check --url [--30]`
  Checks if a website is alive and returns status code and response time

## Environment
- ROBOMOTION_API_TOKEN (if vault credentials are needed)
