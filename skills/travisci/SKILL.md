---
name: "travisci"
description: "Travis CI — manage builds, repositories, jobs, and build logs. Supports build triggering, status monitoring, and repository management via `robomotion travisci`. Do NOT use for GitHub Actions, Jenkins, CircleCI, or other CI/CD platforms."
---

# Travis CI

The `robomotion travisci` CLI connects to Travis CI for build management and CI/CD operations. It lists and triggers builds, manages repositories, monitors job status, views build logs, and handles build lifecycle operations.

## When to use
- List and trigger builds for repositories
- Monitor build and job status in real-time
- View build logs and job details
- Manage repository settings and activation

## Prerequisites
- `robomotion` CLI installed
- Package installed: `robomotion install travisci`
- Travis CI API token configured via Robomotion vault

## IMPORTANT: Session Mode Required for Multi-Step Operations
Each CLI command runs as a **separate process** — connection IDs from `connect` do NOT persist across calls.
You MUST use `--session` on `connect` and pass `--session-id` to all subsequent commands.

## Workflow
1. Install (once): `robomotion install travisci`
2. Connect with session:
   ```
   robomotion travisci travisci_connect --session --output json
   # → {"outClientId":"<client-id>","session_id":"<session-id>"}
   ```
3. Use the returned `client-id` and `session-id` in all subsequent commands:
   ```
   robomotion travisci travisci_list_builds --client-id "<client-id>" --repo <repo> --session-id "<session-id>" --output json
   ```
4. Disconnect when done:
   ```
   robomotion travisci travisci_disconnect --client-id "<client-id>" --session-id "<session-id>" --output json
   ```

**Always** append `--output json` to get structured JSON results.

## Commands Reference
- `robomotion travisci travisci_connect --session --output json`
  Connects to Travis CI API and returns a client ID
- `robomotion travisci travisci_disconnect --client-id --session-id "<session-id>" --output json`
  Closes the Travis CI connection and releases resources
- `robomotion travisci travisci_trigger_build --client-id --repository-slug --branch [--message] [--merge-mode] --session-id "<session-id>" --output json`
  Triggers a new build for a Travis CI repository
- `robomotion travisci travisci_get_build --client-id --build-id [--include] --session-id "<session-id>" --output json`
  Gets details of a specific Travis CI build
- `robomotion travisci travisci_list_builds --client-id --repository-slug [--25] [--sort-by] [--order] [--state-filter] [--event-type] --session-id "<session-id>" --output json`
  Lists builds for a repository or the current user
- `robomotion travisci travisci_cancel_build --client-id --build-id --session-id "<session-id>" --output json`
  Cancels a running Travis CI build
- `robomotion travisci travisci_restart_build --client-id --build-id --session-id "<session-id>" --output json`
  Restarts a completed or canceled Travis CI build
- `robomotion travisci travisci_get_repo --client-id --repository-slug [--include] --session-id "<session-id>" --output json`
  Gets details of a Travis CI repository
- `robomotion travisci travisci_list_repos --client-id --owner [--25] [--sort-by] --session-id "<session-id>" --output json`
  Lists Travis CI repositories for the current user or a specific owner
- `robomotion travisci travisci_get_job_log --client-id --job-id --session-id "<session-id>" --output json`
  Gets the log output of a Travis CI job

## Environment
- ROBOMOTION_API_TOKEN (if vault credentials are needed)
