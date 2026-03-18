# Skill Description Rewrite — TODO

## Goal
Rewrite every SKILL.md so the description and body describe the CLI as a **self-sufficient tool**, not "Use when the user wants to call the Robomotion X package".

Each skill must:
1. **Description (frontmatter)**: One-liner that says what the tool *is* and *does*. Format: `"<Service> <noun> — <what it does>. Supports <key capabilities> via \`robomotion <cli>\`. Do NOT use for <exclusions>."`
2. **Title**: Clean service name (not "X Skill")
3. **Intro paragraph**: 1-2 sentences explaining the CLI as a standalone tool
4. **When to use**: Specific use cases mentioning real features/models/APIs
5. **Prerequisites**: Service-specific (API key name, not generic "credentials configured")
6. **Workflow**: Real command flow with actual command names, not generic placeholders

## Example (falai — DONE)

```markdown
---
name: "falai"
description: "Fal.ai AI model runner — generate images, videos, and audio using cloud-hosted ML models. Supports synchronous and async (queue-based) inference via `robomotion falai`. Do NOT use for OpenAI, Stability AI, Replicate, or other AI inference platforms."
---

# Fal AI

The `robomotion falai` CLI runs AI models hosted on Fal.ai for image generation, video generation, text-to-speech, and other ML tasks. It supports both synchronous execution (wait for result) and async queue-based workflows (submit, poll status, retrieve result).

## When to use
- Generate images (Flux, SDXL, etc.) via Fal.ai
- Run video or audio generation models
- Submit long-running AI jobs to a queue and poll for results
- Cancel or check status of queued inference requests

## Prerequisites
- `robomotion` CLI installed
- Package installed: `robomotion install falai`
- Fal.ai API key configured via Robomotion vault

## Workflow
1. Install: `robomotion install falai`
2. Connect: `robomotion falai falai_connect` → returns a `client-id`
3. Run a model: `robomotion falai falai_run_model --client-id <id> --model-id <model> --input <json>`
4. Or submit async: `robomotion falai falai_submit_request --client-id <id> --model-id <model> --input <json>`
5. Disconnect: `robomotion falai falai_disconnect --client-id <id>`
```

## Progress — ALL DONE (109/109)

- [x] airtable
- [x]apify
- [x]apollo
- [x]baserow
- [x]binance
- [x]calcom
- [x]calendly
- [x]canvas
- [x]claude-ai
- [x]clickhouse
- [x]clickup
- [x]cloudflare
- [x]datadog
- [x]discord-bot
- [x]docusign
- [x]dropbox
- [x]dropcontact
- [x]elevenlabs-ai
- [x]ethereum
- [x]excel365
- [x]fibery
- [x]gateio
- [x]gemini-ai
- [x]ghost
- [x]gmail
- [x]google-calendar
- [x]google-docs
- [x]google-drive
- [x]google-forms
- [x]google-maps
- [x]google-sheets
- [x]google-slides
- [x]google-speech
- [x]google-storage
- [x]google-translate
- [x]homeassistant
- [x]hubspot-crm
- [x]instantly
- [x]jira
- [x]lemlist
- [x]leonardo-ai
- [x]mautic
- [x]microsoft-ad
- [x]millionverifier
- [x]mongodb
- [x]monitoring
- [x]mssql
- [x]mysql
- [x]nextcloud
- [x]nocodb
- [x]notion
- [x]ocr-extraction
- [x]odoo
- [x]ollama
- [x]onedrive365
- [x]onenote365
- [x]openai
- [x]openrouter
- [x]openweather
- [x]oracle
- [x]outlook365
- [x]pcloud
- [x]pdf
- [x]perplexity
- [x]phantombuster
- [x]pinecone
- [x]polymarket
- [x]postgresql
- [x]powerpoint365
- [x]pushover
- [x]qdrant
- [x]questdb
- [x]rabbitmq
- [x]redis
- [x]replicate-ai
- [x]resend
- [x]rundeck
- [x]s3-storage
- [x]searchapi
- [x]seatable
- [x]sentry
- [x]serper
- [x]sharepoint365
- [x]shopify
- [x]slack
- [x]splunk
- [x]sqlite
- [x]ssh
- [x]stability-ai
- [x]stripe-payments
- [x]supabase
- [x]tavily
- [x]teams365
- [x]telegram
- [x]tidbcloud
- [x]timescaledb
- [x]travisci
- [x]trello
- [x]twilio
- [x]typeform
- [x]vikunja
- [x]web-scraper
- [x]whatsapp
- [x]wikipedia
- [x]woocommerce
- [x]wordpress
- [x]xano
- [x]zoom
