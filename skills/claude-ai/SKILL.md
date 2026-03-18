---
name: "claude-ai"
description: "Anthropic Claude AI — generate text, analyze documents, chat with history, and call tools via Claude models. Supports vision, thinking mode, MCP integration, and function calling via `robomotion claude`. Do NOT use for OpenAI, Gemini, or direct conversation — this runs Claude API calls through the Robomotion CLI."
---

# Claude AI (Anthropic)

The `robomotion claude` CLI calls the Anthropic Claude API for text generation, document analysis, chat completions with history, and tool/function calling. It supports vision (image inputs), extended thinking mode, MCP server integration, and model listing.

## When to use
- Generate text or chat responses with Claude models (Opus, Sonnet, Haiku)
- Analyze documents (PDF, images) using Claude's vision and Files API
- Use function calling / tool use with Claude for structured workflows
- Integrate with MCP servers for extended capabilities

## Prerequisites
- `robomotion` CLI installed
- Package installed: `robomotion install claude`
- Anthropic API key configured via Robomotion vault

## Workflow
1. Install: `robomotion install claude`
2. Connect: `robomotion claude connect_claude` → returns a `connection-id`
3. Generate text: `robomotion claude generate_text --connection-id <id> --system-prompt <prompt> --user-prompt <prompt>`
4. Analyze doc: `robomotion claude analyze_document --connection-id <id> --file-paths <paths> --user-prompt <prompt>`
5. Disconnect: `robomotion claude disconnect_claude --connection-id <id>`

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
