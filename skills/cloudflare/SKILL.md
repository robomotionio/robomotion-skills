---
name: "cloudflare"
description: "Use when the user wants to call the Robomotion Cloudflare package to manage DNS records, zones, or Workers via the `robomotion cloudflare` CLI. Do NOT use for AWS Route53, Google Cloud DNS, or other providers."
---

# Cloudflare Skill

## When to use
- Manage Cloudflare DNS records
- Configure Cloudflare zones and settings
- Deploy or manage Cloudflare Workers
- Manage Cloudflare security rules

## Prerequisites
- `robomotion` CLI installed
- Package installed: `robomotion install cloudflare`
- Credentials configured via Robomotion vault or environment variables

## Workflow
1. Install the package: `robomotion install cloudflare`
2. Run commands: `robomotion cloudflare <command> [flags]`

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
