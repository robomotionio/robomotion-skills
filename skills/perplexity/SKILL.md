---
name: "perplexity"
description: "Perplexity AI — AI-powered search and chat with real-time web data and citations. Supports web-grounded responses and conversational search via `robomotion perplexity`. Do NOT use for OpenAI, Claude, Google Search, Tavily, or other AI/search services."
---

# Perplexity AI

The `robomotion perplexity` CLI connects to Perplexity AI for search-augmented AI responses. It provides chat completions grounded in real-time web data with source citations, combining LLM reasoning with live search results.

## When to use
- Search the web with AI-powered answers and citations
- Run chat completions with real-time web data grounding
- Get up-to-date factual responses backed by sources

## Prerequisites
- `robomotion` CLI installed
- Package installed: `robomotion install perplexity`
- Perplexity API key configured via Robomotion vault

## Workflow
1. Install: `robomotion install perplexity`
2. Connect: `robomotion perplexity perplexity_connect` → returns a `client-id`
3. Search: `robomotion perplexity perplexity_chat --client-id <id> --messages <json>`
4. Disconnect: `robomotion perplexity perplexity_disconnect --client-id <id>`

## Commands Reference
- `robomotion perplexity perplexity_connect`
  Connects to Perplexity AI and returns a client ID for subsequent operations
- `robomotion perplexity perplexity_disconnect --client-id`
  Closes the Perplexity connection and releases resources
- `robomotion perplexity perplexity_chat_completion --client-id --user-message --system-message --messages [--model] [--search-context-size] [--search-recency-filter] [--search-mode] [--search-domain-filter] [--max-tokens] [--temperature] [--120]`
  Generates an AI response with real-time web search using Perplexity Sonar models
- `robomotion perplexity perplexity_search --client-id --query [--10] [--search-recency-filter] [--search-domain-filter] [--language-filter] [--country] [--60]`
  Searches the web using Perplexity and returns ranked results with snippets

## Environment
- ROBOMOTION_API_TOKEN (if vault credentials are needed)
