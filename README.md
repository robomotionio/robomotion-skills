# Robomotion Skills

Curated skills for Robomotion LLM Agents following the [agentskills.io](https://agentskills.io) specification. Each skill wraps one or more Robomotion Go packages as a CLI-callable tool.

## Structure

```
skills-index.json          # Manifest listing all skills
skills/
  # AI/LLM
  claude-ai/               # AI/LLM — Anthropic Claude
  elevenlabs-ai/           # AI/LLM — ElevenLabs speech & voice cloning
  falai/                   # AI/LLM — Fal.ai model runner
  gemini-ai/               # AI/LLM — Google Gemini
  leonardo-ai/             # AI/LLM — Leonardo AI image generation
  ollama/                  # AI/LLM — Ollama local AI models
  openai/                  # AI/LLM — OpenAI GPT, DALL-E, Whisper
  openrouter/              # AI/LLM — OpenRouter unified AI gateway
  perplexity/              # AI/LLM — Perplexity AI search
  replicate-ai/            # AI/LLM — Replicate AI predictions
  stability-ai/            # AI/LLM — Stability AI image generation

  # Document & Signatures
  docusign/                # Document — DocuSign eSignature
  google-docs/             # Document — Google Docs
  ocr-extraction/          # Document — OCR via Google Vision + Document AI
  pdf/                     # Document — PDF processing

  # Spreadsheets
  excel365/                # Spreadsheets — Microsoft Excel 365
  google-sheets/           # Spreadsheets — Google Sheets

  # Presentations
  google-slides/           # Presentations — Google Slides
  powerpoint365/           # Presentations — Microsoft PowerPoint 365

  # Cloud Storage
  dropbox/                 # Cloud Storage — Dropbox
  google-drive/            # Cloud Storage — Google Drive
  google-storage/          # Cloud Storage — Google Cloud Storage
  nextcloud/               # Cloud Storage — NextCloud
  onedrive365/             # Cloud Storage — Microsoft OneDrive 365
  pcloud/                  # Cloud Storage — pCloud
  s3-storage/              # Cloud Storage — Amazon S3

  # Database
  clickhouse/              # Database — ClickHouse
  mongodb/                 # Database — MongoDB
  mssql/                   # Database — Microsoft SQL Server
  mysql/                   # Database — MySQL
  oracle/                  # Database — Oracle
  postgresql/              # Database — PostgreSQL
  questdb/                 # Database — QuestDB time-series
  redis/                   # Database — Redis
  sqlite/                  # Database — SQLite
  supabase/                # Database — Supabase
  tidbcloud/               # Database — TiDB Cloud
  timescaledb/             # Database — TimescaleDB time-series

  # No-Code Database
  airtable/                # No-Code Database — Airtable
  baserow/                 # No-Code Database — Baserow
  nocodb/                  # No-Code Database — NocoDB
  seatable/                # No-Code Database — SeaTable

  # Vector Database
  pinecone/                # Vector Database — Pinecone
  qdrant/                  # Vector Database — Qdrant

  # Communication
  discord-bot/             # Communication — Discord
  gmail/                   # Communication — Gmail
  outlook365/              # Communication — Microsoft Outlook 365
  pushover/                # Communication — Pushover notifications
  resend/                  # Communication — Resend email API
  slack/                   # Communication — Slack
  teams365/                # Communication — Microsoft Teams 365
  telegram/                # Communication — Telegram Bot
  twilio/                  # Communication — Twilio SMS & voice
  whatsapp/                # Communication — WhatsApp Business
  zoom/                    # Communication — Zoom meetings

  # CRM & Marketing
  apollo/                  # CRM — Apollo.io
  dropcontact/             # Marketing — Dropcontact enrichment
  hubspot-crm/             # CRM — HubSpot
  instantly/               # Marketing — Instantly cold email
  lemlist/                 # Marketing — Lemlist outreach
  mautic/                  # Marketing — Mautic automation
  millionverifier/         # Marketing — MillionVerifier email verification
  phantombuster/           # Marketing — Phantombuster automation

  # Project Management
  clickup/                 # Project Management — ClickUp
  jira/                    # Project Management — Jira
  trello/                  # Project Management — Trello
  vikunja/                 # Project Management — Vikunja

  # Productivity & Notes
  fibery/                  # Productivity — Fibery
  notion/                  # Productivity — Notion
  onenote365/              # Productivity — Microsoft OneNote 365

  # Scheduling
  calcom/                  # Scheduling — Cal.com
  calendly/                # Scheduling — Calendly
  google-calendar/         # Scheduling — Google Calendar

  # Forms & Surveys
  google-forms/            # Forms — Google Forms
  typeform/                # Forms — Typeform

  # Web & Search
  apify/                   # Automation — Apify actors
  searchapi/               # Web Search — SearchAPI
  serper/                  # Web Search — Serper Google Search
  tavily/                  # Web Search — Tavily AI search
  web-scraper/             # Web — DOM parsing & scraping
  wikipedia/               # Web — Wikipedia

  # E-commerce
  shopify/                 # E-commerce — Shopify
  woocommerce/             # E-commerce — WooCommerce

  # Payments
  stripe-payments/         # Payments — Stripe

  # CMS
  ghost/                   # CMS — Ghost
  wordpress/               # CMS — WordPress

  # DevOps & Monitoring
  cloudflare/              # DevOps — Cloudflare DNS & Workers
  datadog/                 # Monitoring — Datadog
  monitoring/              # Monitoring — Uptime monitoring
  rundeck/                 # DevOps — Rundeck automation
  sentry/                  # Monitoring — Sentry error tracking
  splunk/                  # Monitoring — Splunk logs
  ssh/                     # DevOps — SSH remote commands
  travisci/                # CI/CD — Travis CI

  # Google Services
  google-maps/             # Maps — Google Maps
  google-speech/           # Speech — Google Speech-to-Text & TTS
  google-translate/        # Translation — Google Translate

  # Microsoft 365
  microsoft-ad/            # Identity — Microsoft Active Directory
  sharepoint365/           # Collaboration — Microsoft SharePoint 365

  # Crypto & Finance
  binance/                 # Crypto — Binance exchange
  ethereum/                # Crypto — Ethereum blockchain
  gateio/                  # Crypto — Gate.io exchange
  polymarket/              # Finance — Polymarket predictions

  # ERP & Backend
  odoo/                    # ERP — Odoo
  xano/                    # Backend — Xano

  # IoT
  homeassistant/           # IoT — Home Assistant

  # Education
  canvas/                  # Education — Canvas LMS

  # Message Broker
  rabbitmq/                # Message Broker — RabbitMQ

scripts/
  run_eval.py              # Eval runner for trigger precision & output quality
  USAGE.md                 # Eval tool usage guide
  docs/                    # Eval concepts, skill anatomy, best practices
```

## Adding a Skill

1. Create a folder under `skills/` with your skill name
2. Add a `SKILL.md` with YAML frontmatter (`name`, `description`) and markdown body
3. Add an `eval-set.json` with trigger and quality test cases
4. Add the skill entry to `skills-index.json`
5. Run evals: `python3 scripts/run_eval.py skills/<name>/ --type trigger`

## Running Evals

```bash
# All evals for a skill
python3 scripts/run_eval.py skills/claude-ai/

# Trigger evals only (fast, no tool execution)
python3 scripts/run_eval.py skills/claude-ai/ --type trigger

# Quality evals only
python3 scripts/run_eval.py skills/claude-ai/ --type quality

# Single case
python3 scripts/run_eval.py skills/claude-ai/ --case trigger-pos-1
```

See `scripts/USAGE.md` for full documentation.

## License

Apache-2.0
