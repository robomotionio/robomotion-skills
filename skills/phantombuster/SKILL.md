---
name: "phantombuster"
description: "Phantombuster — run web scraping and automation Phantoms for data extraction from social media and websites. Supports Phantom management, execution, and result retrieval via `robomotion phantombuster`. Do NOT use for Apify, direct scraping, or dom parser."
---

# Phantombuster

The `robomotion phantombuster` CLI connects to Phantombuster for automated web scraping and data extraction. It launches and manages Phantoms (pre-built automation scripts), tracks execution status, retrieves results, and manages Phantom configuration.

## When to use
- Launch Phantombuster Phantoms for LinkedIn, Twitter, and web scraping
- Monitor Phantom execution status and retrieve output data
- Manage Phantom configurations and schedules

## Prerequisites
- `robomotion` CLI installed
- Package installed: `robomotion install phantombuster`
- Phantombuster API key configured via Robomotion vault

## Workflow
1. Install: `robomotion install phantombuster`
2. Connect: `robomotion phantombuster phantombuster_connect` → returns a `client-id`
3. Launch: `robomotion phantombuster phantombuster_launch --client-id <id> --phantom-id <phantom>`
4. Get output: `robomotion phantombuster phantombuster_get_output --client-id <id> --container-id <container>`
5. Disconnect: `robomotion phantombuster phantombuster_disconnect --client-id <id>`

## Commands Reference
- `robomotion phantombuster phantombuster_connect`
  Connects to Phantombuster API and returns a client ID
- `robomotion phantombuster phantombuster_disconnect --client-id`
  Closes the Phantombuster connection and releases resources
- `robomotion phantombuster launch_agent --client-id --agent-id --argument [--60]`
  Adds a Phantombuster agent (Phantom) to the launch queue
- `robomotion phantombuster get_agent --client-id --agent-id`
  Gets a Phantombuster agent (Phantom) by ID
- `robomotion phantombuster list_agents --client-id [--0]`
  Lists all Phantombuster agents (Phantoms) in your organization
- `robomotion phantombuster get_output --client-id --agent-id [--previous-container-id]`
  Gets the output of the most recent container of a Phantombuster agent
- `robomotion phantombuster stop_agent --client-id --agent-id`
  Stops a running Phantombuster agent
- `robomotion phantombuster delete_agent --client-id --agent-id`
  Deletes a Phantombuster agent by ID
- `robomotion phantombuster get_container_result --client-id --container-id`
  Gets the result object of a Phantombuster container

## Environment
- ROBOMOTION_API_TOKEN (if vault credentials are needed)
