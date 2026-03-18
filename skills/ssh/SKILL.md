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

## Workflow
1. Install: `robomotion install ssh`
2. Connect: `robomotion ssh ssh_connect` → returns a `client-id`
3. Execute: `robomotion ssh ssh_execute --client-id <id> --command <cmd>`
4. Upload: `robomotion ssh ssh_upload --client-id <id> --local-path <file> --remote-path <dest>`
5. Disconnect: `robomotion ssh ssh_disconnect --client-id <id>`

## Commands Reference
- `robomotion ssh connect --host --22 --private-key-path [--30]`
  Connect to a remote SSH server using password or private key authentication
- `robomotion ssh run_command --client-id --command [--host] [--22] [--private-key-path] [--30]`
  Execute a shell command on the remote SSH server
- `robomotion ssh upload_file --client-id --local-path --remote-path [--host] [--22] [--private-key-path] [--30]`
  Upload a local file to the remote SSH server via SFTP
- `robomotion ssh download_file --client-id --remote-path --local-path [--host] [--22] [--private-key-path] [--30]`
  Download a file from the remote SSH server via SFTP
- `robomotion ssh disconnect --client-id`
  Disconnect from an SSH server and close the session

## Environment
- ROBOMOTION_API_TOKEN (if vault credentials are needed)
