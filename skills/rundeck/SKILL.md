---
name: "rundeck"
description: "Rundeck — execute automation jobs, manage projects, and monitor job executions. Supports runbook automation and job scheduling via `robomotion rundeck`. Do NOT use for Ansible, Jenkins, GitHub Actions, or other CI/CD tools."
---

# Rundeck

The `robomotion rundeck` CLI connects to Rundeck for runbook automation and job execution. It lists projects, executes jobs with parameters, and monitors execution status.

## When to use
- Execute Rundeck automation jobs with parameters
- List and manage Rundeck projects
- Monitor job execution status and results

## Prerequisites
- `robomotion` CLI installed
- Package installed: `robomotion install rundeck`
- Rundeck URL and API token configured via Robomotion vault

## IMPORTANT: Session Mode Required for Multi-Step Operations
Each CLI command runs as a **separate process** — connection IDs from `connect` do NOT persist across calls.
You MUST use `--session` on `connect` and pass `--session-id` to all subsequent commands.

## Workflow
1. Install (once): `robomotion install rundeck`
2. Connect with session:
   ```
   robomotion rundeck rundeck_connect --session --output json
   # → {"outClientId":"<client-id>","session_id":"<session-id>"}
   ```
3. Use the returned `client-id` and `session-id` in all subsequent commands:
   ```
   robomotion rundeck rundeck_run_job --client-id "<client-id>" --job-id <job> --session-id "<session-id>" --output json
   ```
4. Disconnect when done:
   ```
   robomotion rundeck rundeck_disconnect --client-id "<client-id>" --session-id "<session-id>" --output json
   ```

**Always** append `--output json` to get structured JSON results.

## Commands Reference
- `robomotion rundeck rundeck_connect --session --output json`
  Connects to Rundeck server and returns a client ID
- `robomotion rundeck rundeck_disconnect --client-id --session-id "<session-id>" --output json`
  Closes the Rundeck connection and releases resources
- `robomotion rundeck rundeck_execute_job --client-id --job-id --options --node-filter [--30] --session-id "<session-id>" --output json`
  Executes a Rundeck job by ID with optional arguments and node filter
- `robomotion rundeck rundeck_get_job_info --client-id --job-id [--30] --session-id "<session-id>" --output json`
  Retrieves metadata about a Rundeck job

## Environment
- ROBOMOTION_API_TOKEN (if vault credentials are needed)
