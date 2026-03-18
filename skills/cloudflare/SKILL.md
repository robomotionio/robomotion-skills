---
name: "cloudflare"
description: "Cloudflare platform — manage DNS records, zones, Workers, KV storage, and R2 buckets. Supports DNS CRUD, Worker deployment, and edge storage operations via `robomotion cloudflare`. Do NOT use for AWS Route53, Azure DNS, or other DNS/CDN providers."
---

# Cloudflare

The `robomotion cloudflare` CLI manages Cloudflare services including DNS records, zones, Workers (deploy/delete), KV namespaces, and R2 object storage. It covers the full lifecycle of DNS management, serverless deployment, and edge storage.

## When to use
- Create, update, list, or delete DNS records in Cloudflare zones
- Deploy, list, or delete Cloudflare Workers
- Manage KV namespaces and key-value pairs
- Upload, download, list, or delete objects in R2 buckets

## Prerequisites
- `robomotion` CLI installed
- Package installed: `robomotion install cloudflare`
- Cloudflare API token configured via Robomotion vault

## IMPORTANT: Session Mode Required for Multi-Step Operations
Each CLI command runs as a **separate process** — connection IDs from `connect` do NOT persist across calls.
You MUST use `--session` on `connect` and pass `--session-id` to all subsequent commands.

## Workflow
1. Install (once): `robomotion install cloudflare`
2. Connect with session:
   ```
   robomotion cloudflare cloudflare_connect --session --output json
   # → {"outClientId":"<client-id>","session_id":"<session-id>"}
   ```
3. Use the returned `client-id` and `session-id` in all subsequent commands:
   ```
   robomotion cloudflare cloudflare_list_dns_records --client-id "<client-id>" --zone-id <zone> --session-id "<session-id>" --output json
   ```
4. Disconnect when done:
   ```
   robomotion cloudflare cloudflare_disconnect --client-id "<client-id>" --session-id "<session-id>" --output json
   ```

**Always** append `--output json` to get structured JSON results.

## Commands Reference
- `robomotion cloudflare cloudflare_connect --session --output json`
  Connects to Cloudflare API and returns a client ID for use by other nodes
- `robomotion cloudflare cloudflare_disconnect --client-id --session-id "<session-id>" --output json`
  Closes the Cloudflare connection and releases resources
- `robomotion cloudflare cloudflare_list_zones --client-id [--domain-name] [--status] [--50] --session-id "<session-id>" --output json`
  Lists all zones (domains) in the Cloudflare account
- `robomotion cloudflare cloudflare_get_zone --client-id --zone-id --session-id "<session-id>" --output json`
  Gets detailed information about a specific Cloudflare zone
- `robomotion cloudflare cloudflare_create_zone --client-id --domain-name --account-id [--zone-type] --session-id "<session-id>" --output json`
  Adds a new domain (zone) to the Cloudflare account
- `robomotion cloudflare cloudflare_delete_zone --client-id --zone-id --session-id "<session-id>" --output json`
  Removes a zone (domain) from the Cloudflare account
- `robomotion cloudflare cloudflare_list_dns_records --client-id --zone-id [--record-type] [--record-name] [--search] --session-id "<session-id>" --output json`
  Lists DNS records for a Cloudflare zone
- `robomotion cloudflare cloudflare_create_dns_record --client-id --zone-id --record-name --content [--record-type] [--1] [--comment] --session-id "<session-id>" --output json`
  Creates a new DNS record in a Cloudflare zone
- `robomotion cloudflare cloudflare_update_dns_record --client-id --zone-id --record-id --record-name --content [--record-type] [--1] [--comment] --session-id "<session-id>" --output json`
  Updates an existing DNS record in a Cloudflare zone
- `robomotion cloudflare cloudflare_delete_dns_record --client-id --zone-id --record-id --session-id "<session-id>" --output json`
  Deletes a DNS record from a Cloudflare zone
- `robomotion cloudflare cloudflare_purge_cache --client-id --zone-id [--purge-type] [--files-(ur-ls)] [--cache-tags] [--hostnames] [--url-prefixes] --session-id "<session-id>" --output json`
  Purges cached content from a Cloudflare zone
- `robomotion cloudflare cloudflare_get_zone_setting --client-id --zone-id [--setting] --session-id "<session-id>" --output json`
  Retrieves a specific setting for a Cloudflare zone
- `robomotion cloudflare cloudflare_update_zone_setting --client-id --zone-id [--setting] [--value] --session-id "<session-id>" --output json`
  Updates a specific setting for a Cloudflare zone

## Environment
- ROBOMOTION_API_TOKEN (if vault credentials are needed)
