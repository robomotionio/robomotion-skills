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

## Workflow
1. Install: `robomotion install travisci`
2. Connect: `robomotion travisci travisci_connect` → returns a `client-id`
3. List builds: `robomotion travisci travisci_list_builds --client-id <id> --repo <repo>`
4. Trigger build: `robomotion travisci travisci_trigger_build --client-id <id> --repo <repo>`
5. Disconnect: `robomotion travisci travisci_disconnect --client-id <id>`

## Commands Reference
- `robomotion travisci travisci_connect`
  Connects to Travis CI API and returns a client ID
- `robomotion travisci travisci_disconnect --client-id`
  Closes the Travis CI connection and releases resources
- `robomotion travisci travisci_trigger_build --client-id --repository-slug --branch [--message] [--merge-mode]`
  Triggers a new build for a Travis CI repository
- `robomotion travisci travisci_get_build --client-id --build-id [--include]`
  Gets details of a specific Travis CI build
- `robomotion travisci travisci_list_builds --client-id --repository-slug [--25] [--sort-by] [--order] [--state-filter] [--event-type]`
  Lists builds for a repository or the current user
- `robomotion travisci travisci_cancel_build --client-id --build-id`
  Cancels a running Travis CI build
- `robomotion travisci travisci_restart_build --client-id --build-id`
  Restarts a completed or canceled Travis CI build
- `robomotion travisci travisci_get_repo --client-id --repository-slug [--include]`
  Gets details of a Travis CI repository
- `robomotion travisci travisci_list_repos --client-id --owner [--25] [--sort-by]`
  Lists Travis CI repositories for the current user or a specific owner
- `robomotion travisci travisci_get_job_log --client-id --job-id`
  Gets the log output of a Travis CI job

## Environment
- ROBOMOTION_API_TOKEN (if vault credentials are needed)
