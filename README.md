# Robomotion Skills

Curated skills for Robomotion LLM Agents following the [agentskills.io](https://agentskills.io) specification. Each skill wraps one or more Robomotion Go packages as a CLI-callable tool.

## Structure

```
skills-index.json          # Manifest listing all skills
skills/
  claude-ai/               # AI/LLM — Anthropic Claude
  openai/                  # AI/LLM — OpenAI GPT, DALL-E, Whisper
  gemini-ai/               # AI/LLM — Google Gemini
  pdf/                     # Document — PDF processing
  google-docs/             # Document — Google Docs
  ocr-extraction/          # Document — OCR via Google Vision + Document AI
  s3-storage/              # Cloud Storage — Amazon S3
  google-drive/            # Cloud Storage — Google Drive
  postgresql/              # Database — PostgreSQL
  mongodb/                 # Database — MongoDB
  clickhouse/              # Database — ClickHouse
  gmail/                   # Communication — Gmail
  slack/                   # Communication — Slack
  discord-bot/             # Communication — Discord
  telegram/                # Communication — Telegram Bot
  hubspot-crm/             # CRM — HubSpot
  apollo/                  # CRM — Apollo.io
  jira/                    # Project Management — Jira
  notion/                  # Productivity — Notion
  web-scraper/             # Web — DOM parsing & scraping
  apify/                   # Automation — Apify actors
  google-sheets/           # Spreadsheets — Google Sheets
  stripe-payments/         # Payments — Stripe
  cloudflare/              # DevOps — Cloudflare DNS & Workers
  whatsapp/                # Communication — WhatsApp Business
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
