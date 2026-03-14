---
name: "claude-ai"
description: "Use when the user wants to call the Robomotion Claude package to generate text, summarize, translate, or analyze content via the `robomotion claude` CLI. Use only when the task involves running robomotion commands for Claude/Anthropic API calls. Do NOT use for direct conversation with Claude or for OpenAI/Gemini tasks."
---

# Claude Ai Skill

## When to use
- Generate text, summaries, or translations using Claude
- Analyze or classify content with Claude AI
- Chat completions or conversational AI via Anthropic

## Prerequisites
- `robomotion` CLI installed
- Package installed: `robomotion install claude`
- Credentials configured via Robomotion vault or environment variables

## Workflow
1. Install the package: `robomotion install claude`
2. Run commands: `robomotion claude <command> [flags]`

## Commands Reference
- `robomotion claude connect_claude`
  Connect to Anthropic Claude API and create a client session
- `robomotion claude generate_text --connection-id --system-prompt --user-prompt --image-paths --image-paths [--model] [--custom-model] [--max-tokens] [--temperature] [--top-p] [--top-k] [--thinking-mode] [--thinking-budget] [--120]`
  Generate text responses from Claude AI with optional vision capabilities
- `robomotion claude generate_chat_text --connection-id --system-prompt --user-prompt --history [--model] [--custom-model] [--max-tokens] [--temperature] [--top-p] [--top-k] [--stop-sequences] [--thinking-mode] [--thinking-budget] [--120]`
  Generate chat responses from Claude AI with conversation history support
- `robomotion claude analyze_document --connection-id --system-prompt --user-prompt --file-paths --file-paths [--model] [--custom-model] [--max-tokens] [--temperature] [--top-p] [--top-k] [--thinking-mode] [--thinking-budget] [--300]`
  Analyze documents using Claude AI with Beta Files API support
- `robomotion claude call_tool --connection-id --prompt --tools --history [--model] [--custom-model] [--max-tokens] [--max-tool-rounds] [--120]`
  Call tools using Claude AI function calling capabilities
- `robomotion claude mcp_message --connection-id --prompt --mcp-servers [--model] [--custom-model] [--max-tokens] [--120]`
  Send messages using Claude AI with Model Context Protocol (MCP) integration
- `robomotion claude list_models --connection-id [--30]`
  List available Claude models from the Anthropic API
- `robomotion claude disconnect_claude --connection-id`
  Disconnect from Claude API and release the client session

## Environment
- ROBOMOTION_API_TOKEN (if vault credentials are needed)
