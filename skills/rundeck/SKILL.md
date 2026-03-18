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

## Workflow
1. Install: `robomotion install rundeck`
2. Connect: `robomotion rundeck rundeck_connect` → returns a `client-id`
3. Run job: `robomotion rundeck rundeck_run_job --client-id <id> --job-id <job>`
4. Disconnect: `robomotion rundeck rundeck_disconnect --client-id <id>`

## Commands Reference
- `robomotion rundeck rundeck_connect`
  Connects to Rundeck server and returns a client ID
- `robomotion rundeck rundeck_disconnect --client-id`
  Closes the Rundeck connection and releases resources
- `robomotion rundeck rundeck_execute_job --client-id --job-id --options --node-filter [--30]`
  Executes a Rundeck job by ID with optional arguments and node filter
- `robomotion rundeck rundeck_get_job_info --client-id --job-id [--30]`
  Retrieves metadata about a Rundeck job

## Environment
- ROBOMOTION_API_TOKEN (if vault credentials are needed)
