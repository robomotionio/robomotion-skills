# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.4.0] - 2026-03-23

### Added

- **windows-vm** skill: Create, manage, and connect to a headless Windows 11 VM running in Docker with KVM acceleration and SSH access. Supports full lifecycle management (create, start, stop, restart, ssh, status) with automated OpenSSH, Node.js, and Claude Code setup.

## [0.3.0] - 2025-01-31

### Added

- **slack-messaging** skill: Send and read Slack messages from the command line using slackcli. Supports multiple workspaces with browser token authentication. Includes helper script for token extraction.

## [0.2.0] - 2025-01-11

### Added

- **finding-duplicate-functions** skill: Detect semantic code duplication in LLM-generated codebases using a two-phase approach (classical extraction + LLM-powered intent clustering). Includes shell scripts for function extraction, category splitting, and report generation.

## [0.1.0] - 2024-11-10

### Added

- Initial release with experimental skills
- **using-tmux-for-interactive-commands** skill: Control interactive CLI tools through tmux sessions
- **mcp-cli** skill: On-demand MCP server usage via the mcp CLI tool
