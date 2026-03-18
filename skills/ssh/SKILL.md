---
name: "ssh"
description: "SSH — execute remote commands and transfer files via SSH/SCP/SFTP. Supports command execution, file upload/download, and tunneling via `robomotion ssh`. Do NOT use for local shell commands, Ansible, or Terraform."
---

# SSH

The `robomotion ssh` CLI connects to remote servers via SSH for command execution and file transfer. It runs commands on remote hosts, uploads and downloads files via SCP/SFTP, and manages SSH connections.

## When to use
- Execute commands on remote servers via SSH
- Upload or download files using SCP/SFTP
- Manage SSH connections to multiple hosts

## Prerequisites
- `robomotion` CLI installed
- Package installed: `robomotion install ssh`
- SSH host, username, and key/password configured via Robomotion vault

## IMPORTANT: Session Mode Required for Multi-Step Operations
Each CLI command runs as a **separate process** — connection IDs from `connect` do NOT persist across calls.
You MUST use `--session` on `connect` and pass `--session-id` to all subsequent commands.

## Workflow
1. Install (once): `robomotion install ssh`
2. Connect with session:
   ```
   robomotion ssh ssh_connect --session --output json
   # → {"outClientId":"<client-id>","session_id":"<session-id>"}
   ```
3. Use the returned `client-id` and `session-id` in all subsequent commands:
   ```
   robomotion ssh ssh_execute --client-id "<client-id>" --command <cmd> --session-id "<session-id>" --output json
   ```
4. Disconnect when done:
   ```
   robomotion ssh ssh_disconnect --client-id "<client-id>" --session-id "<session-id>" --output json
   ```

**Always** append `--output json` to get structured JSON results.

## Commands Reference
- `robomotion ssh connect --host --22 --private-key-path [--30] --session --output json`
  Connect to a remote SSH server using password or private key authentication
- `robomotion ssh run_command --client-id --command [--host] [--22] [--private-key-path] [--30] --session-id "<session-id>" --output json`
  Execute a shell command on the remote SSH server
- `robomotion ssh upload_file --client-id --local-path --remote-path [--host] [--22] [--private-key-path] [--30] --session-id "<session-id>" --output json`
  Upload a local file to the remote SSH server via SFTP
- `robomotion ssh download_file --client-id --remote-path --local-path [--host] [--22] [--private-key-path] [--30] --session-id "<session-id>" --output json`
  Download a file from the remote SSH server via SFTP
- `robomotion ssh disconnect --client-id --session-id "<session-id>" --output json`
  Disconnect from an SSH server and close the session

## Environment
- ROBOMOTION_API_TOKEN (if vault credentials are needed)
