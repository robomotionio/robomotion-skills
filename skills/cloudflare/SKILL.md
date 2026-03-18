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

## Workflow
1. Install: `robomotion install cloudflare`
2. Connect: `robomotion cloudflare cloudflare_connect` → returns a `client-id`
3. List DNS: `robomotion cloudflare cloudflare_list_dns_records --client-id <id> --zone-id <zone>`
4. Create record: `robomotion cloudflare cloudflare_create_dns_record --client-id <id> --zone-id <zone> --type A --name <host> --content <ip>`
5. Disconnect: `robomotion cloudflare cloudflare_disconnect --client-id <id>`

## Commands Reference
- `robomotion cloudflare cloudflare_connect`
  Connects to Cloudflare API and returns a client ID for use by other nodes
- `robomotion cloudflare cloudflare_disconnect --client-id`
  Closes the Cloudflare connection and releases resources
- `robomotion cloudflare cloudflare_list_zones --client-id [--domain-name] [--status] [--50]`
  Lists all zones (domains) in the Cloudflare account
- `robomotion cloudflare cloudflare_get_zone --client-id --zone-id`
  Gets detailed information about a specific Cloudflare zone
- `robomotion cloudflare cloudflare_create_zone --client-id --domain-name --account-id [--zone-type]`
  Adds a new domain (zone) to the Cloudflare account
- `robomotion cloudflare cloudflare_delete_zone --client-id --zone-id`
  Removes a zone (domain) from the Cloudflare account
- `robomotion cloudflare cloudflare_list_dns_records --client-id --zone-id [--record-type] [--record-name] [--search]`
  Lists DNS records for a Cloudflare zone
- `robomotion cloudflare cloudflare_create_dns_record --client-id --zone-id --record-name --content [--record-type] [--1] [--comment]`
  Creates a new DNS record in a Cloudflare zone
- `robomotion cloudflare cloudflare_update_dns_record --client-id --zone-id --record-id --record-name --content [--record-type] [--1] [--comment]`
  Updates an existing DNS record in a Cloudflare zone
- `robomotion cloudflare cloudflare_delete_dns_record --client-id --zone-id --record-id`
  Deletes a DNS record from a Cloudflare zone
- `robomotion cloudflare cloudflare_purge_cache --client-id --zone-id [--purge-type] [--files-(ur-ls)] [--cache-tags] [--hostnames] [--url-prefixes]`
  Purges cached content from a Cloudflare zone
- `robomotion cloudflare cloudflare_get_zone_setting --client-id --zone-id [--setting]`
  Retrieves a specific setting for a Cloudflare zone
- `robomotion cloudflare cloudflare_update_zone_setting --client-id --zone-id [--setting] [--value]`
  Updates a specific setting for a Cloudflare zone

## Environment
- ROBOMOTION_API_TOKEN (if vault credentials are needed)
