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

## IMPORTANT: Session Mode Required for Multi-Step Operations
Each CLI command runs as a **separate process** — connection IDs from `connect` do NOT persist across calls.
You MUST use `--session` on `connect` and pass `--session-id` to all subsequent commands.

## Workflow
1. Install (once): `robomotion install phantombuster`
2. Connect with session:
   ```
   robomotion phantombuster phantombuster_connect --session --output json
   # → {"outClientId":"<client-id>","session_id":"<session-id>"}
   ```
3. Use the returned `client-id` and `session-id` in all subsequent commands:
   ```
   robomotion phantombuster phantombuster_launch --client-id "<client-id>" --phantom-id <phantom> --session-id "<session-id>" --output json
   ```
4. Disconnect when done:
   ```
   robomotion phantombuster phantombuster_disconnect --client-id "<client-id>" --session-id "<session-id>" --output json
   ```

**Always** append `--output json` to get structured JSON results.

## Commands Reference
- `robomotion phantombuster phantombuster_connect --session --output json`
  Connects to Phantombuster API and returns a client ID
- `robomotion phantombuster phantombuster_disconnect --client-id --session-id "<session-id>" --output json`
  Closes the Phantombuster connection and releases resources
- `robomotion phantombuster launch_agent --client-id --agent-id --argument [--60] --session-id "<session-id>" --output json`
  Adds a Phantombuster agent (Phantom) to the launch queue
- `robomotion phantombuster get_agent --client-id --agent-id --session-id "<session-id>" --output json`
  Gets a Phantombuster agent (Phantom) by ID
- `robomotion phantombuster list_agents --client-id [--0] --session-id "<session-id>" --output json`
  Lists all Phantombuster agents (Phantoms) in your organization
- `robomotion phantombuster get_output --client-id --agent-id [--previous-container-id] --session-id "<session-id>" --output json`
  Gets the output of the most recent container of a Phantombuster agent
- `robomotion phantombuster stop_agent --client-id --agent-id --session-id "<session-id>" --output json`
  Stops a running Phantombuster agent
- `robomotion phantombuster delete_agent --client-id --agent-id --session-id "<session-id>" --output json`
  Deletes a Phantombuster agent by ID
- `robomotion phantombuster get_container_result --client-id --container-id --session-id "<session-id>" --output json`
  Gets the result object of a Phantombuster container

## Environment
- ROBOMOTION_API_TOKEN (if vault credentials are needed)
