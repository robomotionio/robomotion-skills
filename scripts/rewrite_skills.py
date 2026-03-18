#!/usr/bin/env python3
"""
Rewrite all SKILL.md files with proper self-sufficient descriptions.
Keeps Commands Reference and Environment sections intact.
Updates skills-index.json descriptions to match.
"""

import json
import os
import re
import sys

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SKILLS_DIR = os.path.join(REPO_ROOT, "skills")
INDEX_PATH = os.path.join(REPO_ROOT, "skills-index.json")

# ─── Rewrite data for every skill ────────────────────────────────────────────
# Key: skill name (directory name)
# Values: description, title, intro, use_cases, prereq_note, workflow_steps

REWRITES = {
    "airtable": {
        "desc": "Airtable database client — manage records, tables, and bases in Airtable. Supports CRUD operations, formula-based search, bulk operations, and comments via `robomotion airtable`. Do NOT use for Google Sheets, Excel, Baserow, NocoDB, or other spreadsheet/database tools.",
        "title": "Airtable",
        "intro": "The `robomotion airtable` CLI connects to Airtable's API to manage bases, tables, and records. It supports listing, creating, updating, deleting records (including bulk operations), searching with formula filters, and managing record comments.",
        "use_cases": [
            "List, create, update, or delete records in Airtable tables",
            "Search records using Airtable formula filters",
            "Bulk create or delete up to 10 records at once",
            "List bases, get table schemas, and manage comments on records",
        ],
        "prereq": "Airtable API key configured via Robomotion vault",
        "workflow": [
            "Install: `robomotion install airtable`",
            "Connect: `robomotion airtable connect` → returns a `key-id`",
            "List records: `robomotion airtable list_records --key-id <id> --base-id <base> --table-name <table>`",
            "Create record: `robomotion airtable create_record --key-id <id> --base-id <base> --table-name <table> --record <json>`",
            "Disconnect: `robomotion airtable disconnect --key-id <id>`",
        ],
    },
    "apify": {
        "desc": "Apify web scraping platform — run Apify actors for large-scale crawling and data extraction. Supports actor execution, run monitoring, and dataset retrieval via `robomotion apify`. Do NOT use for simple HTML parsing or non-Apify scraping tools.",
        "title": "Apify",
        "intro": "The `robomotion apify` CLI runs actors on the Apify platform for web scraping, crawling, and data extraction at scale. It handles actor execution with configurable timeouts, run status monitoring, and paginated dataset retrieval.",
        "use_cases": [
            "Run pre-built or custom Apify actors for web scraping",
            "Monitor actor run status and retrieve results",
            "Extract paginated datasets from completed actor runs",
        ],
        "prereq": "Apify API token configured via Robomotion vault",
        "workflow": [
            "Install: `robomotion install apify`",
            "Connect: `robomotion apify apify_connect` → returns a `client-id`",
            "Run actor: `robomotion apify run_actor --client-id <id> --actor-id <actor> --input <json>`",
            "Get results: `robomotion apify get_dataset_items --client-id <id> --dataset-id <ds>`",
            "Disconnect: `robomotion apify apify_disconnect --client-id <id>`",
        ],
    },
    "apollo": {
        "desc": "Apollo.io sales intelligence — search 265M+ contacts, enrich leads, manage contacts/accounts/deals. Supports people search, organization enrichment, and CRM operations via `robomotion apollo`. Do NOT use for HubSpot, Salesforce, or other CRM systems.",
        "title": "Apollo.io",
        "intro": "The `robomotion apollo` CLI connects to Apollo.io's sales intelligence platform. It searches a 265M+ person database by job title, company, and location; enriches contacts and organizations; and manages contacts, accounts, and deals in your Apollo workspace.",
        "use_cases": [
            "Search Apollo's database for leads by job title, company, or location",
            "Enrich person or organization data by email, LinkedIn URL, or domain",
            "Create and manage contacts, accounts, and deals in Apollo CRM",
        ],
        "prereq": "Apollo.io API key configured via Robomotion vault",
        "workflow": [
            "Install: `robomotion install apollo`",
            "Connect: `robomotion apollo apollo_connect` → returns a `client-id`",
            "Search people: `robomotion apollo apollo_search_people --client-id <id> --job-titles <titles> --company-name <company>`",
            "Enrich: `robomotion apollo apollo_enrich_person --client-id <id> --email <email>`",
            "Disconnect: `robomotion apollo apollo_disconnect --client-id <id>`",
        ],
    },
    "baserow": {
        "desc": "Baserow open-source database — manage rows, tables, and fields in self-hosted or cloud Baserow instances. Supports CRUD, filtering, sorting, search, and field listing via `robomotion baserow`. Do NOT use for Airtable, NocoDB, Google Sheets, or other no-code databases.",
        "title": "Baserow",
        "intro": "The `robomotion baserow` CLI connects to Baserow (open-source Airtable alternative) for row and table management. It supports listing rows with filtering/sorting/search, single-row CRUD, and field schema inspection on any self-hosted or cloud Baserow instance.",
        "use_cases": [
            "List, create, update, or delete rows in Baserow tables",
            "Search and filter rows with custom queries",
            "Get table field definitions and schema",
        ],
        "prereq": "Baserow instance URL and API token configured via Robomotion vault",
        "workflow": [
            "Install: `robomotion install baserow`",
            "Connect: `robomotion baserow baserow_connect --https://api-baserow-io` → returns a `client-id`",
            "List rows: `robomotion baserow baserow_list_rows --client-id <id> --table-id <table>`",
            "Create row: `robomotion baserow baserow_create_row --client-id <id> --table-id <table> --row-data <json>`",
            "Disconnect: `robomotion baserow baserow_disconnect --client-id <id>`",
        ],
    },
    "binance": {
        "desc": "Binance cryptocurrency exchange — trade crypto, check prices, view balances, and access market data. Supports limit/market/stop orders, price history, deposits, and withdrawals via `robomotion binance`. Do NOT use for Gate.io, Coinbase, or other crypto exchanges.",
        "title": "Binance",
        "intro": "The `robomotion binance` CLI connects to the Binance exchange for cryptocurrency trading and market data. It supports placing limit, market, and stop-loss orders; checking balances and prices; downloading price history as CSV; and viewing deposits, withdrawals, and recent trades.",
        "use_cases": [
            "Get current prices, 24h stats, or historical candlestick data for trading pairs",
            "Place limit, market, or stop-loss orders on Binance",
            "Check account balances, open orders, deposits, and withdrawals",
            "List all trading pairs or recent trades for a symbol",
        ],
        "prereq": "Binance API key and secret configured via Robomotion vault",
        "workflow": [
            "Install: `robomotion install binance`",
            "Connect: `robomotion binance binance_connect` → returns a `client-id`",
            "Get price: `robomotion binance binance_get_price --client-id <id> --bnbusdt`",
            "Place order: `robomotion binance binance_market_order --client-id <id> --bnbusdt --order-amount 100`",
            "Disconnect: `robomotion binance binance_disconnect --client-id <id>`",
        ],
    },
    "calcom": {
        "desc": "Cal.com scheduling platform — manage bookings, event types, availability slots, and schedules. Supports creating, rescheduling, and canceling bookings via `robomotion calcom`. Do NOT use for Calendly, Google Calendar, Outlook Calendar, or other scheduling tools.",
        "title": "Cal.com",
        "intro": "The `robomotion calcom` CLI connects to Cal.com for scheduling management. It handles creating and managing bookings, event types with custom durations and buffers, availability schedules with timezone support, and available slot queries.",
        "use_cases": [
            "Create, reschedule, or cancel bookings on Cal.com",
            "List and manage event types with durations and buffer times",
            "Query available time slots for specific event types",
            "Manage availability schedules and overrides",
        ],
        "prereq": "Cal.com API key configured via Robomotion vault",
        "workflow": [
            "Install: `robomotion install calcom`",
            "Connect: `robomotion calcom calcom_connect` → returns a `client-id`",
            "List bookings: `robomotion calcom calcom_list_bookings --client-id <id>`",
            "Create booking: `robomotion calcom calcom_create_booking --client-id <id> --event-type-id <type> --start-time <time> --attendee-name <name> --attendee-email <email>`",
            "Disconnect: `robomotion calcom calcom_disconnect --client-id <id>`",
        ],
    },
    "calendly": {
        "desc": "Calendly scheduling — list events, manage event types, handle invitees, and configure webhooks. Supports event scheduling, cancellation, and scheduling link creation via `robomotion calendly`. Do NOT use for Cal.com, Google Calendar, Outlook Calendar, or other scheduling tools.",
        "title": "Calendly",
        "intro": "The `robomotion calendly` CLI connects to Calendly for scheduling management. It lists scheduled events and invitees, manages event types, creates single-use scheduling links, cancels meetings, and configures webhook subscriptions for real-time event notifications.",
        "use_cases": [
            "List scheduled events with date range and invitee filters",
            "Cancel scheduled events or view event details",
            "Create single-use scheduling links for event types",
            "Manage webhook subscriptions for event notifications",
        ],
        "prereq": "Calendly API token or OAuth2 credentials configured via Robomotion vault",
        "workflow": [
            "Install: `robomotion install calendly`",
            "Connect: `robomotion calendly connect` → returns a `client-id`",
            "List events: `robomotion calendly list_scheduled_events --client-id <id> --user-url <url>`",
            "Cancel event: `robomotion calendly cancel_scheduled_event --client-id <id> --event-url <url> --reason <text>`",
            "Disconnect: `robomotion calendly disconnect --client-id <id>`",
        ],
    },
    "canvas": {
        "desc": "Canvas LMS — manage courses, assignments, users, enrollments, submissions, pages, modules, and announcements. Supports grading, enrollment management, and course content creation via `robomotion canvas`. Do NOT use for Moodle, Google Classroom, Blackboard, or other LMS platforms.",
        "title": "Canvas LMS",
        "intro": "The `robomotion canvas` CLI connects to Canvas LMS for education management. It manages courses, assignments (create/update/delete/grade), user enrollments, wiki pages, modules, and announcements — covering the full lifecycle of course content and student interaction.",
        "use_cases": [
            "Create, update, or delete assignments and grade submissions",
            "Manage course enrollments — enroll or remove students",
            "Create wiki pages, modules, and announcements in courses",
            "List courses, users, assignments, and submissions with filters",
        ],
        "prereq": "Canvas LMS API access token configured via Robomotion vault",
        "workflow": [
            "Install: `robomotion install canvas`",
            "Connect: `robomotion canvas canvas_connect` → returns a `client-id`",
            "List courses: `robomotion canvas canvas_list_courses --client-id <id>`",
            "Create assignment: `robomotion canvas canvas_create_assignment --client-id <id> --course-id <course> --name <name>`",
            "Grade: `robomotion canvas canvas_grade_submission --client-id <id> --course-id <course> --assignment-id <asn> --user-id <user> --grade <grade>`",
            "Disconnect: `robomotion canvas canvas_disconnect --client-id <id>`",
        ],
    },
    "claude-ai": {
        "desc": "Anthropic Claude AI — generate text, analyze documents, chat with history, and call tools via Claude models. Supports vision, thinking mode, MCP integration, and function calling via `robomotion claude`. Do NOT use for OpenAI, Gemini, or direct conversation — this runs Claude API calls through the Robomotion CLI.",
        "title": "Claude AI (Anthropic)",
        "intro": "The `robomotion claude` CLI calls the Anthropic Claude API for text generation, document analysis, chat completions with history, and tool/function calling. It supports vision (image inputs), extended thinking mode, MCP server integration, and model listing.",
        "use_cases": [
            "Generate text or chat responses with Claude models (Opus, Sonnet, Haiku)",
            "Analyze documents (PDF, images) using Claude's vision and Files API",
            "Use function calling / tool use with Claude for structured workflows",
            "Integrate with MCP servers for extended capabilities",
        ],
        "prereq": "Anthropic API key configured via Robomotion vault",
        "workflow": [
            "Install: `robomotion install claude`",
            "Connect: `robomotion claude connect_claude` → returns a `connection-id`",
            "Generate text: `robomotion claude generate_text --connection-id <id> --system-prompt <prompt> --user-prompt <prompt>`",
            "Analyze doc: `robomotion claude analyze_document --connection-id <id> --file-paths <paths> --user-prompt <prompt>`",
            "Disconnect: `robomotion claude disconnect_claude --connection-id <id>`",
        ],
    },
    "clickhouse": {
        "desc": "ClickHouse columnar database — execute analytical SQL queries and batch inserts on ClickHouse. Supports query execution, batch transactions, and non-query operations via `robomotion clickhouse`. Do NOT use for PostgreSQL, MySQL, MongoDB, or other databases.",
        "title": "ClickHouse",
        "intro": "The `robomotion clickhouse` CLI connects to ClickHouse for analytical SQL workloads. It supports executing SELECT queries, running INSERT/UPDATE/DELETE statements, and batch transactions for atomically executing multiple SQL commands.",
        "use_cases": [
            "Run analytical SQL queries on ClickHouse columnar tables",
            "Insert data using batch transactions for atomicity",
            "Execute DDL or non-query SQL statements",
        ],
        "prereq": "ClickHouse connection credentials configured via Robomotion vault",
        "workflow": [
            "Install: `robomotion install clickhouse`",
            "Connect: `robomotion clickhouse connect` → returns a `conn-id`",
            "Query: `robomotion clickhouse execute_query --conn-id <id>`",
            "Batch insert: `robomotion clickhouse create_batch --conn-id <id>` → add statements → `robomotion clickhouse send_batch --batch-id <id>`",
            "Disconnect: `robomotion clickhouse disconnect --conn-id <id>`",
        ],
    },
    "clickup": {
        "desc": "ClickUp project management — manage workspaces, spaces, folders, lists, tasks, and comments. Supports full task lifecycle including creation, updates, assignments, and commenting via `robomotion clickup`. Do NOT use for Jira, Trello, Asana, or other PM tools.",
        "title": "ClickUp",
        "intro": "The `robomotion clickup` CLI connects to ClickUp for project and task management. It covers the full workspace hierarchy (teams → spaces → folders → lists → tasks) and supports task CRUD, comment management, member listing, and organizational operations.",
        "use_cases": [
            "Create, update, or delete tasks with assignees, due dates, and priorities",
            "List and manage workspaces, spaces, folders, and lists",
            "Add, update, or delete comments on tasks",
            "Browse team members and task details",
        ],
        "prereq": "ClickUp API token configured via Robomotion vault",
        "workflow": [
            "Install: `robomotion install clickup`",
            "Connect: `robomotion clickup clickup_connect` → returns a `client-id`",
            "List tasks: `robomotion clickup clickup_get_tasks --client-id <id> --list-id <list>`",
            "Create task: `robomotion clickup clickup_create_task --client-id <id> --list-id <list> --name <name>`",
            "Disconnect: `robomotion clickup clickup_disconnect --client-id <id>`",
        ],
    },
    "cloudflare": {
        "desc": "Cloudflare platform — manage DNS records, zones, Workers, KV storage, and R2 buckets. Supports DNS CRUD, Worker deployment, and edge storage operations via `robomotion cloudflare`. Do NOT use for AWS Route53, Azure DNS, or other DNS/CDN providers.",
        "title": "Cloudflare",
        "intro": "The `robomotion cloudflare` CLI manages Cloudflare services including DNS records, zones, Workers (deploy/delete), KV namespaces, and R2 object storage. It covers the full lifecycle of DNS management, serverless deployment, and edge storage.",
        "use_cases": [
            "Create, update, list, or delete DNS records in Cloudflare zones",
            "Deploy, list, or delete Cloudflare Workers",
            "Manage KV namespaces and key-value pairs",
            "Upload, download, list, or delete objects in R2 buckets",
        ],
        "prereq": "Cloudflare API token configured via Robomotion vault",
        "workflow": [
            "Install: `robomotion install cloudflare`",
            "Connect: `robomotion cloudflare cloudflare_connect` → returns a `client-id`",
            "List DNS: `robomotion cloudflare cloudflare_list_dns_records --client-id <id> --zone-id <zone>`",
            "Create record: `robomotion cloudflare cloudflare_create_dns_record --client-id <id> --zone-id <zone> --type A --name <host> --content <ip>`",
            "Disconnect: `robomotion cloudflare cloudflare_disconnect --client-id <id>`",
        ],
    },
    "datadog": {
        "desc": "Datadog monitoring platform — submit metrics, query logs, manage monitors/alerts, and schedule downtimes. Supports infrastructure monitoring and incident response via `robomotion datadog`. Do NOT use for Sentry, Splunk, Prometheus, or other monitoring tools.",
        "title": "Datadog",
        "intro": "The `robomotion datadog` CLI connects to Datadog for infrastructure monitoring and alerting. It submits custom metrics, queries logs and events, creates and manages monitors with alert conditions, schedules downtimes, and handles incidents.",
        "use_cases": [
            "Submit custom metrics or gauge values to Datadog",
            "Query logs, search events, and analyze time-series data",
            "Create, update, or mute Datadog monitors and alerts",
            "Schedule maintenance downtimes and manage incidents",
        ],
        "prereq": "Datadog API and application keys configured via Robomotion vault",
        "workflow": [
            "Install: `robomotion install datadog`",
            "Connect: `robomotion datadog datadog_connect` → returns a `client-id`",
            "Submit metric: `robomotion datadog datadog_submit_metric --client-id <id> --metric-name <name> --value <val>`",
            "Query logs: `robomotion datadog datadog_query_logs --client-id <id> --query <query>`",
            "Disconnect: `robomotion datadog datadog_disconnect --client-id <id>`",
        ],
    },
    "discord-bot": {
        "desc": "Discord bot — send messages, manage channels, handle roles, and interact with Discord servers. Supports message sending, channel management, and server administration via `robomotion discordbot`. Do NOT use for Slack, Teams, Telegram, or other messaging platforms.",
        "title": "Discord Bot",
        "intro": "The `robomotion discordbot` CLI operates a Discord bot to send messages, manage channels and roles, and interact with Discord servers. It supports posting messages, listing channels/members, and performing server administration tasks.",
        "use_cases": [
            "Send messages to Discord channels or users",
            "List channels, members, and roles in a Discord server",
            "Manage Discord channels and server settings",
        ],
        "prereq": "Discord bot token configured via Robomotion vault",
        "workflow": [
            "Install: `robomotion install discordbot`",
            "Connect: `robomotion discordbot connect` → returns a `client-id`",
            "Send message: `robomotion discordbot send_message --client-id <id> --channel-id <channel> --message <text>`",
            "List channels: `robomotion discordbot list_channels --client-id <id>`",
            "Disconnect: `robomotion discordbot disconnect --client-id <id>`",
        ],
    },
    "docusign": {
        "desc": "DocuSign eSignature — send documents for signing, manage envelopes and templates, track recipients. Supports envelope creation, status tracking, and document download via `robomotion docusign`. Do NOT use for Adobe Sign, HelloSign, PandaDoc, or other e-signature tools.",
        "title": "DocuSign",
        "intro": "The `robomotion docusign` CLI connects to DocuSign's eSignature API to send documents for electronic signing, manage envelopes and templates, track recipient status, and download completed documents.",
        "use_cases": [
            "Send documents for electronic signature via envelopes",
            "Create envelopes from templates with recipient data",
            "Track envelope and recipient signing status",
            "List templates and download completed documents",
        ],
        "prereq": "DocuSign API credentials (integration key, account ID) configured via Robomotion vault",
        "workflow": [
            "Install: `robomotion install docusign`",
            "Connect: `robomotion docusign docusign_connect` → returns a `client-id`",
            "Create envelope: `robomotion docusign docusign_create_envelope --client-id <id> --template-id <tmpl> --recipients <json>`",
            "Check status: `robomotion docusign docusign_get_envelope --client-id <id> --envelope-id <env>`",
            "Disconnect: `robomotion docusign docusign_disconnect --client-id <id>`",
        ],
    },
    "dropbox": {
        "desc": "Dropbox cloud storage — upload, download, copy, move, delete, search, and share files. Supports folder management, file metadata, and shareable link creation via `robomotion dropbox`. Do NOT use for Google Drive, S3, OneDrive, or local filesystem operations.",
        "title": "Dropbox",
        "intro": "The `robomotion dropbox` CLI manages files and folders in Dropbox. It supports uploading, downloading, copying, moving, deleting files; creating folders; searching by name/content; getting file metadata; and generating shareable links.",
        "use_cases": [
            "Upload or download files between local filesystem and Dropbox",
            "Copy, move, or delete files and folders in Dropbox",
            "Search for files by name or content",
            "Create shareable links and get file metadata/stats",
        ],
        "prereq": "Dropbox access token configured via Robomotion vault",
        "workflow": [
            "Install: `robomotion install dropbox`",
            "Connect: `robomotion dropbox connect` → returns a `client-id`",
            "Upload: `robomotion dropbox upload_file --client-id <id> --file-path <local> --dropbox-path <remote>`",
            "List: `robomotion dropbox list_files --client-id <id> --dropbox-path <folder>`",
            "Disconnect: `robomotion dropbox disconnect --client-id <id>`",
        ],
    },
    "dropcontact": {
        "desc": "Dropcontact data enrichment — enrich and verify contact information including emails, phone numbers, and company data. Supports single and batch enrichment via `robomotion dropcontact`. Do NOT use for Apollo, Clearbit, Hunter.io, or other enrichment services.",
        "title": "Dropcontact",
        "intro": "The `robomotion dropcontact` CLI connects to Dropcontact for contact data enrichment and verification. It enriches contacts with company information, verifies email deliverability, and finds professional email addresses.",
        "use_cases": [
            "Enrich contacts with company details, job titles, and social profiles",
            "Verify and clean email addresses",
            "Find professional email addresses from name and company",
        ],
        "prereq": "Dropcontact API key configured via Robomotion vault",
        "workflow": [
            "Install: `robomotion install dropcontact`",
            "Connect: `robomotion dropcontact dropcontact_connect` → returns a `client-id`",
            "Enrich: `robomotion dropcontact dropcontact_enrich --client-id <id> --email <email>`",
            "Disconnect: `robomotion dropcontact dropcontact_disconnect --client-id <id>`",
        ],
    },
    "elevenlabs-ai": {
        "desc": "ElevenLabs AI speech platform — text-to-speech, speech-to-text, voice cloning, sound effects, and audio isolation. Supports 30+ languages, voice management, and pronunciation dictionaries via `robomotion elevenlabsai`. Do NOT use for OpenAI TTS, Google Speech, Amazon Polly, or other speech services.",
        "title": "ElevenLabs AI",
        "intro": "The `robomotion elevenlabsai` CLI connects to ElevenLabs for AI speech synthesis and processing. It generates natural-sounding speech from text in 30+ languages, transcribes audio, clones voices, creates sound effects, isolates audio, and manages voice libraries and pronunciation dictionaries.",
        "use_cases": [
            "Convert text to natural-sounding speech with selectable voices",
            "Transcribe audio files to text (speech-to-text)",
            "Clone voices or generate sound effects from descriptions",
            "Manage voice library, pronunciation dictionaries, and models",
        ],
        "prereq": "ElevenLabs API key configured via Robomotion vault",
        "workflow": [
            "Install: `robomotion install elevenlabsai`",
            "Connect: `robomotion elevenlabsai elevenlabs_connect` → returns a `client-id`",
            "Generate speech: `robomotion elevenlabsai text_to_speech --client-id <id> --text <text> --voice-id <voice>`",
            "Transcribe: `robomotion elevenlabsai speech_to_text --client-id <id> --audio-file <path>`",
            "Disconnect: `robomotion elevenlabsai elevenlabs_disconnect --client-id <id>`",
        ],
    },
    "ethereum": {
        "desc": "Ethereum blockchain client — interact with smart contracts, send transactions, check balances, and monitor blocks/events. Supports ERC-20 tokens, ENS resolution, gas estimation, and event watching via `robomotion ethereum`. Do NOT use for Binance, centralized exchanges, or other blockchains.",
        "title": "Ethereum",
        "intro": "The `robomotion ethereum` CLI connects to the Ethereum blockchain for Web3 operations. It checks ETH and ERC-20 balances, sends transactions, deploys and calls smart contracts, resolves ENS names, estimates gas, watches events, and monitors blocks.",
        "use_cases": [
            "Check ETH or ERC-20 token balances for wallet addresses",
            "Send ETH transactions or call smart contract methods",
            "Deploy smart contracts and interact with existing ones",
            "Resolve ENS names, estimate gas, and watch blockchain events",
        ],
        "prereq": "Ethereum RPC endpoint (Infura, Alchemy, etc.) configured via Robomotion vault",
        "workflow": [
            "Install: `robomotion install ethereum`",
            "Connect: `robomotion ethereum eth_connect` → returns a `client-id`",
            "Get balance: `robomotion ethereum eth_get_balance --client-id <id> --address <addr>`",
            "Send TX: `robomotion ethereum eth_send_transaction --client-id <id> --to <addr> --value <wei>`",
            "Disconnect: `robomotion ethereum eth_disconnect --client-id <id>`",
        ],
    },
    "excel365": {
        "desc": "Microsoft Excel 365 — read, write, and manage workbooks, worksheets, tables, ranges, cells, rows, columns, and formulas in OneDrive/SharePoint. Full spreadsheet operations via `robomotion excel365`. Do NOT use for Google Sheets, local Excel files, or CSV processing.",
        "title": "Microsoft Excel 365",
        "intro": "The `robomotion excel365` CLI connects to Microsoft Excel 365 via the Graph API for full spreadsheet operations. It manages workbooks in OneDrive/SharePoint — reading and writing ranges, cells, rows, columns; managing worksheets and tables; handling formulas and hyperlinks; and supporting append, clear, and delete operations.",
        "use_cases": [
            "Read or write cell ranges, rows, and columns in Excel 365 workbooks",
            "Create workbooks and worksheets in OneDrive/SharePoint",
            "Manage Excel tables — get/set/append rows, create tables from ranges",
            "Get or set formulas and hyperlinks in cells",
        ],
        "prereq": "Microsoft 365 OAuth2 credentials configured via Robomotion vault",
        "workflow": [
            "Install: `robomotion install excel365`",
            "Open workbook: `robomotion excel365 open_workbook --file-path <path>` → returns a `workbook-id`",
            "Read range: `robomotion excel365 read_range --workbook-id <id> --sheet-1 --range-address A1:D10`",
            "Write cell: `robomotion excel365 set_cell --workbook-id <id> --sheet-1 --cell-address A1 --value <val>`",
            "Close: `robomotion excel365 close_workbook --workbook-id <id>`",
        ],
    },
    "fibery": {
        "desc": "Fibery workspace platform — manage entities, databases, documents, and spaces. Supports CRUD on any entity type with filtering and search via `robomotion fibery`. Do NOT use for Notion, ClickUp, Monday.com, or other productivity platforms.",
        "title": "Fibery",
        "intro": "The `robomotion fibery` CLI connects to Fibery for workspace and entity management. It creates, reads, updates, and deletes entities in any Fibery database, lists available types/spaces, and supports filtered queries.",
        "use_cases": [
            "Create, update, or delete entities in Fibery databases",
            "List and search entities with filters",
            "Browse available entity types and database schemas",
        ],
        "prereq": "Fibery API token and workspace URL configured via Robomotion vault",
        "workflow": [
            "Install: `robomotion install fibery`",
            "Connect: `robomotion fibery fibery_connect` → returns a `client-id`",
            "List entities: `robomotion fibery fibery_list_entities --client-id <id> --type <type>`",
            "Create entity: `robomotion fibery fibery_create_entity --client-id <id> --type <type> --fields <json>`",
            "Disconnect: `robomotion fibery fibery_disconnect --client-id <id>`",
        ],
    },
    "gateio": {
        "desc": "Gate.io cryptocurrency exchange — trade crypto, check prices, view orderbooks, and manage account balances. Supports market/limit orders, ticker data, and trading pair listing via `robomotion gateio`. Do NOT use for Binance, Coinbase, or other crypto exchanges.",
        "title": "Gate.io",
        "intro": "The `robomotion gateio` CLI connects to the Gate.io exchange for cryptocurrency trading and market data. It supports checking spot prices and 24h tickers, viewing orderbooks, placing market and limit orders, and managing account balances.",
        "use_cases": [
            "Get current prices and 24h ticker statistics for trading pairs",
            "View orderbook depth for any trading pair",
            "Place limit or market buy/sell orders on Gate.io",
            "Check account balances and list available trading pairs",
        ],
        "prereq": "Gate.io API key and secret configured via Robomotion vault",
        "workflow": [
            "Install: `robomotion install gateio`",
            "Connect: `robomotion gateio gateio_connect` → returns a `client-id`",
            "Get price: `robomotion gateio gateio_get_spot_price --client-id <id> --btc_usdt`",
            "Place order: `robomotion gateio gateio_buy_limit_order --client-id <id> --btc_usdt --amount <amt> --price <price>`",
            "Disconnect: `robomotion gateio gateio_disconnect --client-id <id>`",
        ],
    },
    "gemini-ai": {
        "desc": "Google Gemini AI — generate text, analyze images, and create embeddings using Gemini models. Supports chat with history, vision, and content generation via `robomotion googlegemini`. Do NOT use for OpenAI, Claude, or other AI models.",
        "title": "Google Gemini AI",
        "intro": "The `robomotion googlegemini` CLI calls Google's Gemini API for text generation, image analysis, and embeddings. It supports single-turn generation, multi-turn chat with history, vision (image + text), and embedding generation.",
        "use_cases": [
            "Generate text responses using Gemini models",
            "Analyze images with text prompts (vision)",
            "Run multi-turn chat conversations with history",
            "Generate text embeddings for semantic search",
        ],
        "prereq": "Google Gemini API key configured via Robomotion vault",
        "workflow": [
            "Install: `robomotion install googlegemini`",
            "Connect: `robomotion googlegemini connect_gemini` → returns a `connection-id`",
            "Generate text: `robomotion googlegemini generate_text --connection-id <id> --prompt <text>`",
            "Disconnect: `robomotion googlegemini disconnect_gemini --connection-id <id>`",
        ],
    },
    "ghost": {
        "desc": "Ghost CMS — manage posts, pages, tags, members, tiers, newsletters, and offers on Ghost-powered sites. Supports content publishing, membership management, and newsletter configuration via `robomotion ghost`. Do NOT use for WordPress, Medium, or other CMS platforms.",
        "title": "Ghost",
        "intro": "The `robomotion ghost` CLI connects to Ghost CMS for content and membership management. It handles creating/updating/deleting posts and pages, managing tags, administering members and tiers, configuring newsletters, and managing offers — covering both content publishing and subscription operations.",
        "use_cases": [
            "Create, update, publish, or delete blog posts and pages",
            "Manage tags, members, tiers, and subscription offers",
            "Configure and manage Ghost newsletters",
            "List and search content, members, and site resources",
        ],
        "prereq": "Ghost Admin API key configured via Robomotion vault",
        "workflow": [
            "Install: `robomotion install ghost`",
            "Connect: `robomotion ghost ghost_connect` → returns a `client-id`",
            "Create post: `robomotion ghost ghost_create_post --client-id <id> --title <title> --html <body> --status draft`",
            "List members: `robomotion ghost ghost_list_members --client-id <id>`",
            "Disconnect: `robomotion ghost ghost_disconnect --client-id <id>`",
        ],
    },
    "gmail": {
        "desc": "Gmail — send, read, search, label, archive, draft, and manage emails and threads. Supports attachments, labels, drafts, and thread operations via `robomotion gmail`. Do NOT use for Outlook, generic SMTP, or non-email messaging.",
        "title": "Gmail",
        "intro": "The `robomotion gmail` CLI connects to Gmail via the Google API for full email management. It sends, reads, replies to, and searches emails; manages labels and drafts; handles archiving, trash, and read/unread status; downloads attachments; and operates on email threads.",
        "use_cases": [
            "Send emails with To/CC/BCC recipients, or reply to existing messages",
            "Search and list emails with query filters and label filtering",
            "Manage labels — create, list, add/remove from messages",
            "Create, list, send, or delete email drafts",
            "Download attachments and manage email threads",
        ],
        "prereq": "Gmail OAuth2 or Service Account credentials configured via Robomotion vault",
        "workflow": [
            "Install: `robomotion install gmail`",
            "Connect: `robomotion gmail gmail_connect` → returns a `client-id`",
            "Send email: `robomotion gmail gmail_send_email --client-id <id> --to <email> --subject <subj> --body <body>`",
            "List emails: `robomotion gmail gmail_list_emails --client-id <id> --search-query <query>`",
            "Disconnect: `robomotion gmail gmail_disconnect --client-id <id>`",
        ],
    },
    "google-calendar": {
        "desc": "Google Calendar — create, read, update, delete, and search calendar events. Supports recurring events, attendees, and multi-calendar management via `robomotion googlecalendar`. Do NOT use for Outlook Calendar, Calendly, Cal.com, or other scheduling tools.",
        "title": "Google Calendar",
        "intro": "The `robomotion googlecalendar` CLI connects to Google Calendar API for event management. It creates, reads, updates, deletes, and searches events across calendars, with support for attendees, time zones, and calendar listing.",
        "use_cases": [
            "Create, update, or delete calendar events with attendees",
            "List upcoming events or search by keyword/date range",
            "Manage multiple calendars — list and select calendars",
        ],
        "prereq": "Google Calendar OAuth2 or Service Account credentials configured via Robomotion vault",
        "workflow": [
            "Install: `robomotion install googlecalendar`",
            "Connect: `robomotion googlecalendar google_calendar_connect` → returns a `client-id`",
            "Create event: `robomotion googlecalendar google_calendar_create_event --client-id <id> --summary <title> --start <time> --end <time>`",
            "List events: `robomotion googlecalendar google_calendar_list_events --client-id <id>`",
            "Disconnect: `robomotion googlecalendar google_calendar_disconnect --client-id <id>`",
        ],
    },
    "google-docs": {
        "desc": "Google Docs — create, read, and update documents in Google Docs. Supports document creation, content reading, and text operations via `robomotion googledocs`. Do NOT use for Microsoft Word, local files, or PDF processing.",
        "title": "Google Docs",
        "intro": "The `robomotion googledocs` CLI connects to Google Docs API for document management. It creates new documents, reads document content, and updates existing documents in Google Drive.",
        "use_cases": [
            "Create new Google Docs documents",
            "Read content from existing Google Docs",
            "Update and modify document content",
        ],
        "prereq": "Google Docs OAuth2 or Service Account credentials configured via Robomotion vault",
        "workflow": [
            "Install: `robomotion install googledocs`",
            "Connect: `robomotion googledocs connect` → returns a `client-id`",
            "Create doc: `robomotion googledocs create_document --client-id <id> --title <title>`",
            "Read doc: `robomotion googledocs get_document --client-id <id> --document-id <doc>`",
            "Disconnect: `robomotion googledocs disconnect --client-id <id>`",
        ],
    },
    "google-drive": {
        "desc": "Google Drive — upload, download, list, copy, move, delete, and share files and folders. Supports file search, permission management, and shared drive operations via `robomotion googledrive`. Do NOT use for Dropbox, S3, OneDrive, or local filesystem.",
        "title": "Google Drive",
        "intro": "The `robomotion googledrive` CLI connects to Google Drive API for file and folder management. It uploads, downloads, copies, moves, and deletes files; creates folders; searches by name/query; and manages sharing permissions.",
        "use_cases": [
            "Upload or download files between local filesystem and Google Drive",
            "List, search, copy, move, or delete files and folders",
            "Create folders and manage file sharing permissions",
        ],
        "prereq": "Google Drive OAuth2 or Service Account credentials configured via Robomotion vault",
        "workflow": [
            "Install: `robomotion install googledrive`",
            "Connect: `robomotion googledrive connect` → returns a `client-id`",
            "Upload: `robomotion googledrive upload_file --client-id <id> --file-path <local> --parent-id <folder>`",
            "List: `robomotion googledrive list_files --client-id <id>`",
            "Disconnect: `robomotion googledrive disconnect --client-id <id>`",
        ],
    },
    "google-forms": {
        "desc": "Google Forms — create forms, manage questions, and retrieve responses. Supports form creation, question management, and response collection via `robomotion googleforms`. Do NOT use for Typeform, SurveyMonkey, or other form builders.",
        "title": "Google Forms",
        "intro": "The `robomotion googleforms` CLI connects to Google Forms API for form and response management. It creates forms, adds and manages questions, retrieves form submissions, and lists available forms.",
        "use_cases": [
            "Create new Google Forms with custom questions",
            "Retrieve and list form responses/submissions",
            "Manage form questions and settings",
        ],
        "prereq": "Google Forms OAuth2 or Service Account credentials configured via Robomotion vault",
        "workflow": [
            "Install: `robomotion install googleforms`",
            "Connect: `robomotion googleforms googleforms_connect` → returns a `client-id`",
            "List responses: `robomotion googleforms googleforms_list_responses --client-id <id> --form-id <form>`",
            "Disconnect: `robomotion googleforms googleforms_disconnect --client-id <id>`",
        ],
    },
    "google-maps": {
        "desc": "Google Maps — geocode addresses, reverse geocode coordinates, search for places, and get directions. Supports location services via `robomotion googlemaps`. Do NOT use for OpenStreetMap, Mapbox, or other mapping services.",
        "title": "Google Maps",
        "intro": "The `robomotion googlemaps` CLI connects to Google Maps Platform for geocoding and location services. It converts addresses to coordinates (geocode), coordinates to addresses (reverse geocode), searches for places/businesses, and calculates directions between locations.",
        "use_cases": [
            "Geocode addresses to latitude/longitude coordinates",
            "Reverse geocode coordinates to human-readable addresses",
            "Search for places and businesses by query",
            "Get directions and distance between locations",
        ],
        "prereq": "Google Maps API key configured via Robomotion vault",
        "workflow": [
            "Install: `robomotion install googlemaps`",
            "Connect: `robomotion googlemaps googlemaps_connect` → returns a `client-id`",
            "Geocode: `robomotion googlemaps googlemaps_geocode --client-id <id> --address <address>`",
            "Disconnect: `robomotion googlemaps googlemaps_disconnect --client-id <id>`",
        ],
    },
    "google-sheets": {
        "desc": "Google Sheets — read, write, append, and manage spreadsheet data, sheets, and formatting. Supports cell operations, range reads/writes, and sheet management via `robomotion googlesheets`. Do NOT use for Excel 365, Airtable, or CSV files.",
        "title": "Google Sheets",
        "intro": "The `robomotion googlesheets` CLI connects to Google Sheets API for spreadsheet operations. It reads and writes cell ranges, appends rows, manages worksheets, and handles spreadsheet creation and formatting.",
        "use_cases": [
            "Read or write cell ranges and individual cells in Google Sheets",
            "Append rows to spreadsheets",
            "Create spreadsheets and manage worksheets",
        ],
        "prereq": "Google Sheets OAuth2 or Service Account credentials configured via Robomotion vault",
        "workflow": [
            "Install: `robomotion install googlesheets`",
            "Connect: `robomotion googlesheets connect` → returns a `client-id`",
            "Read range: `robomotion googlesheets get_range --client-id <id> --spreadsheet-id <id> --range <A1:D10>`",
            "Write: `robomotion googlesheets set_range --client-id <id> --spreadsheet-id <id> --range <A1> --values <data>`",
            "Disconnect: `robomotion googlesheets disconnect --client-id <id>`",
        ],
    },
    "google-slides": {
        "desc": "Google Slides — create presentations, add/manage/duplicate slides, replace text and images, and export to PDF. Supports template-based workflows via `robomotion googleslides`. Do NOT use for PowerPoint, Keynote, or other presentation tools.",
        "title": "Google Slides",
        "intro": "The `robomotion googleslides` CLI connects to Google Slides API for presentation management. It creates presentations, adds and duplicates slides, replaces text and images for template-based generation, and exports to PDF.",
        "use_cases": [
            "Create new presentations or work from templates",
            "Add, duplicate, or delete slides",
            "Replace text and images in slide templates for automated generation",
            "Export presentations to PDF",
        ],
        "prereq": "Google Slides OAuth2 or Service Account credentials configured via Robomotion vault",
        "workflow": [
            "Install: `robomotion install googleslides`",
            "Connect: `robomotion googleslides google_slides_connect` → returns a `client-id`",
            "Create: `robomotion googleslides google_slides_create --client-id <id> --title <title>`",
            "Replace text: `robomotion googleslides google_slides_replace_text --client-id <id> --presentation-id <id> --find <old> --replace <new>`",
            "Disconnect: `robomotion googleslides google_slides_disconnect --client-id <id>`",
        ],
    },
    "google-speech": {
        "desc": "Google Speech — transcribe audio to text (speech-to-text) and convert text to speech (TTS). Supports multiple languages and audio formats via `robomotion googlespeech`. Do NOT use for OpenAI Whisper, ElevenLabs, or other speech services.",
        "title": "Google Speech",
        "intro": "The `robomotion googlespeech` CLI connects to Google Cloud Speech APIs for audio transcription and speech synthesis. It transcribes audio files to text and converts text to speech audio files.",
        "use_cases": [
            "Transcribe audio files to text in multiple languages",
            "Convert text to speech audio files",
        ],
        "prereq": "Google Cloud Speech API credentials configured via Robomotion vault",
        "workflow": [
            "Install: `robomotion install googlespeech`",
            "Connect: `robomotion googlespeech connect` → returns a `client-id`",
            "Transcribe: `robomotion googlespeech speech_to_text --client-id <id> --audio-file <path>`",
            "Disconnect: `robomotion googlespeech disconnect --client-id <id>`",
        ],
    },
    "google-storage": {
        "desc": "Google Cloud Storage — upload, download, list, delete, copy, and move objects in GCS buckets. Supports bucket management, signed URLs, and metadata operations via `robomotion googlestorage`. Do NOT use for S3, Dropbox, Google Drive, or local filesystem.",
        "title": "Google Cloud Storage",
        "intro": "The `robomotion googlestorage` CLI connects to Google Cloud Storage for object and bucket management. It uploads, downloads, lists, deletes, copies, and moves objects; creates and manages buckets; generates signed URLs; and reads object metadata.",
        "use_cases": [
            "Upload or download files between local filesystem and GCS buckets",
            "List, copy, move, or delete objects in buckets",
            "Create or delete GCS buckets",
            "Generate signed URLs for temporary access",
        ],
        "prereq": "Google Cloud service account credentials configured via Robomotion vault",
        "workflow": [
            "Install: `robomotion install googlestorage`",
            "Connect: `robomotion googlestorage google_storage_connect` → returns a `client-id`",
            "Upload: `robomotion googlestorage google_storage_upload_object --client-id <id> --bucket-name <bucket> --file-path <local>`",
            "List: `robomotion googlestorage google_storage_list_objects --client-id <id> --bucket-name <bucket>`",
            "Disconnect: `robomotion googlestorage google_storage_disconnect --client-id <id>`",
        ],
    },
    "google-translate": {
        "desc": "Google Translate — translate text between languages using Google Cloud Translation API. Supports language detection and 100+ languages via `robomotion googletranslate`. Do NOT use for OpenAI, Claude, DeepL, or other translation services.",
        "title": "Google Translate",
        "intro": "The `robomotion googletranslate` CLI connects to Google Cloud Translation API for text translation between 100+ languages with automatic language detection.",
        "use_cases": [
            "Translate text from one language to another",
            "Auto-detect source language",
            "Batch translate multiple texts",
        ],
        "prereq": "Google Cloud Translation API credentials configured via Robomotion vault",
        "workflow": [
            "Install: `robomotion install googletranslate`",
            "Connect: `robomotion googletranslate connect` → returns a `client-id`",
            "Translate: `robomotion googletranslate translate --client-id <id> --text <text> --target-language <lang>`",
            "Disconnect: `robomotion googletranslate disconnect --client-id <id>`",
        ],
    },
    "homeassistant": {
        "desc": "Home Assistant — control smart home devices, call services, read states, manage automations, and monitor events. Supports device control, scene activation, and history queries via `robomotion homeassistant`. Do NOT use for AWS IoT, Google Home API, or other IoT platforms.",
        "title": "Home Assistant",
        "intro": "The `robomotion homeassistant` CLI connects to Home Assistant for smart home control and automation. It reads device states and sensor values, calls services (turn on/off, set temperature, etc.), activates scenes, fires events, and queries state history.",
        "use_cases": [
            "Control smart home devices — turn on/off lights, switches, etc.",
            "Read device states and sensor readings",
            "Call Home Assistant services and activate scenes",
            "Query state history and fire custom events",
        ],
        "prereq": "Home Assistant URL and long-lived access token configured via Robomotion vault",
        "workflow": [
            "Install: `robomotion install homeassistant`",
            "Connect: `robomotion homeassistant ha_connect` → returns a `client-id`",
            "Get state: `robomotion homeassistant ha_get_state --client-id <id> --entity-id <entity>`",
            "Call service: `robomotion homeassistant ha_call_service --client-id <id> --domain light --service turn_on --entity-id <entity>`",
            "Disconnect: `robomotion homeassistant ha_disconnect --client-id <id>`",
        ],
    },
    "hubspot-crm": {
        "desc": "HubSpot CRM — manage contacts, companies, deals, tickets, and products. Supports CRUD, search, associations, and pipeline management via `robomotion hubspot`. Do NOT use for Salesforce, Apollo, Pipedrive, or other CRM systems.",
        "title": "HubSpot CRM",
        "intro": "The `robomotion hubspot` CLI connects to HubSpot CRM for contact, company, deal, and ticket management. It supports creating, reading, updating, and searching CRM objects with property filtering and association management.",
        "use_cases": [
            "Create, update, or search contacts, companies, and deals",
            "Manage deal pipelines and ticket workflows",
            "Search CRM records with property filters",
        ],
        "prereq": "HubSpot API key or OAuth2 token configured via Robomotion vault",
        "workflow": [
            "Install: `robomotion install hubspot`",
            "Connect: `robomotion hubspot connect` → returns a `client-id`",
            "Search contacts: `robomotion hubspot search_contacts --client-id <id> --query <query>`",
            "Create deal: `robomotion hubspot create_deal --client-id <id> --properties <json>`",
            "Disconnect: `robomotion hubspot disconnect --client-id <id>`",
        ],
    },
    "instantly": {
        "desc": "Instantly cold email platform — manage campaigns, leads, email accounts, and track analytics. Supports lead import, campaign management, and deliverability monitoring via `robomotion instantly`. Do NOT use for Lemlist, Mailchimp, Gmail, or other email platforms.",
        "title": "Instantly",
        "intro": "The `robomotion instantly` CLI connects to Instantly for cold email outreach management. It manages campaigns (create/update/activate/pause), imports and manages leads, tracks email analytics and sending stats, and handles email account configuration.",
        "use_cases": [
            "Create, update, activate, or pause cold email campaigns",
            "Add, list, or manage leads in campaigns",
            "Track campaign analytics — open rates, replies, bounces",
            "Manage email sending accounts and warm-up settings",
        ],
        "prereq": "Instantly API key configured via Robomotion vault",
        "workflow": [
            "Install: `robomotion install instantly`",
            "Connect: `robomotion instantly instantly_connect` → returns a `client-id`",
            "List campaigns: `robomotion instantly instantly_list_campaigns --client-id <id>`",
            "Add lead: `robomotion instantly instantly_add_lead --client-id <id> --campaign-id <camp> --email <email>`",
            "Disconnect: `robomotion instantly instantly_disconnect --client-id <id>`",
        ],
    },
    "jira": {
        "desc": "Jira project management — create, update, search, transition, and comment on issues. Supports JQL search, issue lifecycle, and project management via `robomotion jira`. Do NOT use for Trello, ClickUp, Asana, or other PM tools.",
        "title": "Jira",
        "intro": "The `robomotion jira` CLI connects to Jira for issue and project management. It creates, reads, updates, and transitions issues; searches with JQL; adds comments; manages projects and issue types — covering the full issue lifecycle.",
        "use_cases": [
            "Create, update, or transition Jira issues through workflow states",
            "Search issues using JQL queries",
            "Add comments and manage issue details",
            "List projects and issue types",
        ],
        "prereq": "Jira URL and API token (or OAuth) configured via Robomotion vault",
        "workflow": [
            "Install: `robomotion install jira`",
            "Connect: `robomotion jira connect` → returns a `client-id`",
            "Create issue: `robomotion jira create_issue --client-id <id> --project <proj> --summary <text> --issue-type <type>`",
            "Search: `robomotion jira search_issues --client-id <id> --jql <query>`",
            "Disconnect: `robomotion jira disconnect --client-id <id>`",
        ],
    },
    "lemlist": {
        "desc": "Lemlist email outreach — manage campaigns, leads, and email sequences. Supports lead management and campaign operations via `robomotion lemlist`. Do NOT use for Instantly, Mailchimp, Gmail, or other email platforms.",
        "title": "Lemlist",
        "intro": "The `robomotion lemlist` CLI connects to Lemlist for email outreach management. It lists and manages campaigns, adds and removes leads from campaigns, and handles outreach sequence operations.",
        "use_cases": [
            "List campaigns and view campaign details",
            "Add or remove leads from email campaigns",
            "Manage lead data and outreach sequences",
        ],
        "prereq": "Lemlist API key configured via Robomotion vault",
        "workflow": [
            "Install: `robomotion install lemlist`",
            "Connect: `robomotion lemlist lemlist_connect` → returns a `client-id`",
            "List campaigns: `robomotion lemlist lemlist_list_campaigns --client-id <id>`",
            "Add lead: `robomotion lemlist lemlist_add_lead --client-id <id> --campaign-id <camp> --email <email>`",
            "Disconnect: `robomotion lemlist lemlist_disconnect --client-id <id>`",
        ],
    },
    "leonardo-ai": {
        "desc": "Leonardo AI image generation — create images, upscale, remove backgrounds, and manage generation jobs. Supports multiple AI models and style presets via `robomotion leonardoai`. Do NOT use for DALL-E, Stability AI, Midjourney, or other image generation services.",
        "title": "Leonardo AI",
        "intro": "The `robomotion leonardoai` CLI connects to Leonardo AI for AI-powered image generation and editing. It generates images from text prompts, upscales images, removes backgrounds, manages generation jobs, and supports various AI models and style presets.",
        "use_cases": [
            "Generate images from text prompts using Leonardo AI models",
            "Upscale images or remove backgrounds",
            "Track and retrieve generation job results",
            "List available models and manage image workflows",
        ],
        "prereq": "Leonardo AI API key configured via Robomotion vault",
        "workflow": [
            "Install: `robomotion install leonardoai`",
            "Connect: `robomotion leonardoai leonardoai_connect` → returns a `client-id`",
            "Generate: `robomotion leonardoai leonardoai_generate_image --client-id <id> --prompt <text>`",
            "Get result: `robomotion leonardoai leonardoai_get_generation --client-id <id> --generation-id <gen>`",
            "Disconnect: `robomotion leonardoai leonardoai_disconnect --client-id <id>`",
        ],
    },
    "mautic": {
        "desc": "Mautic marketing automation — manage contacts, companies, segments, campaigns, emails, and forms. Supports lead scoring, campaign automation, and email marketing via `robomotion mautic`. Do NOT use for HubSpot Marketing, Mailchimp, or other marketing platforms.",
        "title": "Mautic",
        "intro": "The `robomotion mautic` CLI connects to Mautic (open-source marketing automation) for contact and campaign management. It handles contacts, companies, segments, campaigns, email templates, forms, and notes — covering the full marketing automation workflow.",
        "use_cases": [
            "Create, update, search, or delete contacts and companies",
            "Manage segments and add/remove contacts from them",
            "List and manage marketing campaigns and email templates",
            "Handle forms and contact notes",
        ],
        "prereq": "Mautic instance URL and API credentials configured via Robomotion vault",
        "workflow": [
            "Install: `robomotion install mautic`",
            "Connect: `robomotion mautic mautic_connect` → returns a `client-id`",
            "Create contact: `robomotion mautic mautic_create_contact --client-id <id> --fields <json>`",
            "List segments: `robomotion mautic mautic_list_segments --client-id <id>`",
            "Disconnect: `robomotion mautic mautic_disconnect --client-id <id>`",
        ],
    },
    "microsoft-ad": {
        "desc": "Active Directory — manage users, groups, organizational units, and group memberships. Supports LDAP-based user/group CRUD and OU management via `robomotion activedirectory`. Do NOT use for Azure AD/Entra ID, Okta, Auth0, or other identity providers.",
        "title": "Active Directory",
        "intro": "The `robomotion activedirectory` CLI connects to on-premises Active Directory via LDAP for user and group management. It creates, reads, updates, and deletes users; manages groups and group memberships; and handles organizational unit operations.",
        "use_cases": [
            "Create, update, disable, or delete Active Directory user accounts",
            "Manage AD groups and add/remove members",
            "List and search users or groups in organizational units",
            "Manage organizational units (OUs)",
        ],
        "prereq": "Active Directory LDAP connection credentials configured via Robomotion vault",
        "workflow": [
            "Install: `robomotion install activedirectory`",
            "Connect: `robomotion activedirectory ad_connect` → returns a `client-id`",
            "List users: `robomotion activedirectory ad_list_users --client-id <id> --ou <ou-dn>`",
            "Create user: `robomotion activedirectory ad_create_user --client-id <id> --username <user> --password <pass>`",
            "Disconnect: `robomotion activedirectory ad_disconnect --client-id <id>`",
        ],
    },
    "millionverifier": {
        "desc": "MillionVerifier email verification — verify single emails and run bulk email list verification. Supports quality scoring, verdicts, bulk upload, and report download via `robomotion millionverifier`. Do NOT use for Dropcontact, ZeroBounce, or other verification services.",
        "title": "MillionVerifier",
        "intro": "The `robomotion millionverifier` CLI connects to MillionVerifier for email address verification. It verifies single emails with quality/verdict scores, uploads email lists for bulk verification, tracks processing status, downloads verification reports, and manages API credits.",
        "use_cases": [
            "Verify single email addresses with quality and verdict scoring",
            "Upload email lists for bulk verification",
            "Track bulk verification progress and download reports",
            "Check remaining API credits",
        ],
        "prereq": "MillionVerifier API key configured via Robomotion vault",
        "workflow": [
            "Install: `robomotion install millionverifier`",
            "Connect: `robomotion millionverifier millionverifier_connect` → returns a `client-id`",
            "Verify email: `robomotion millionverifier verify_email --client-id <id> --email <email>`",
            "Bulk upload: `robomotion millionverifier bulk_upload --client-id <id> --file-path <file>`",
            "Disconnect: `robomotion millionverifier millionverifier_disconnect --client-id <id>`",
        ],
    },
    "mongodb": {
        "desc": "MongoDB — query, insert, update, delete, and aggregate documents in MongoDB collections. Supports CRUD operations, aggregation pipelines, and collection management via `robomotion mongodb`. Do NOT use for PostgreSQL, MySQL, Redis, or other databases.",
        "title": "MongoDB",
        "intro": "The `robomotion mongodb` CLI connects to MongoDB for document database operations. It supports finding, inserting, updating, and deleting documents; running aggregation pipelines; and managing collections.",
        "use_cases": [
            "Query documents with filters and projections",
            "Insert, update, or delete documents in collections",
            "Run aggregation pipelines for data analysis",
            "Manage MongoDB connections and collections",
        ],
        "prereq": "MongoDB connection URI configured via Robomotion vault",
        "workflow": [
            "Install: `robomotion install mongodb`",
            "Connect: `robomotion mongodb connect` → returns a `conn-id`",
            "Find: `robomotion mongodb find --conn-id <id> --collection <col> --filter <json>`",
            "Insert: `robomotion mongodb insert_one --conn-id <id> --collection <col> --document <json>`",
            "Disconnect: `robomotion mongodb disconnect --conn-id <id>`",
        ],
    },
    "monitoring": {
        "desc": "Uptime monitoring — check website and API endpoint health, ping services, and monitor HTTP status. Supports health checks, response time measurement, and availability tracking via `robomotion monitoring`. Do NOT use for Sentry, Datadog, Splunk, or application-level monitoring.",
        "title": "Monitoring",
        "intro": "The `robomotion monitoring` CLI provides uptime and health monitoring for websites, APIs, and services. It pings endpoints, checks HTTP status codes, measures response times, and tracks service availability.",
        "use_cases": [
            "Check if a website or API endpoint is up and responding",
            "Monitor HTTP response codes and response times",
            "Ping services and track availability",
        ],
        "prereq": "No external credentials needed for basic HTTP monitoring",
        "workflow": [
            "Install: `robomotion install monitoring`",
            "Connect: `robomotion monitoring monitoring_connect` → returns a `client-id`",
            "Check: `robomotion monitoring monitoring_check --client-id <id> --url <url>`",
            "Disconnect: `robomotion monitoring monitoring_disconnect --client-id <id>`",
        ],
    },
    "mssql": {
        "desc": "Microsoft SQL Server — execute queries, stored procedures, and manage transactions on MSSQL databases. Supports SELECT, INSERT, UPDATE, DELETE, and batch operations via `robomotion mssql`. Do NOT use for PostgreSQL, MySQL, Oracle, or other databases.",
        "title": "Microsoft SQL Server",
        "intro": "The `robomotion mssql` CLI connects to Microsoft SQL Server for database operations. It executes SQL queries and non-query statements, manages transactions with batch support, and handles stored procedure execution.",
        "use_cases": [
            "Execute SQL SELECT queries and retrieve result sets",
            "Run INSERT, UPDATE, DELETE, and DDL statements",
            "Execute stored procedures with parameters",
            "Use batch transactions for atomic multi-statement operations",
        ],
        "prereq": "SQL Server connection credentials configured via Robomotion vault",
        "workflow": [
            "Install: `robomotion install mssql`",
            "Connect: `robomotion mssql connect` → returns a `conn-id`",
            "Query: `robomotion mssql execute_query --conn-id <id>` (with SQL in context)",
            "Disconnect: `robomotion mssql disconnect --conn-id <id>`",
        ],
    },
    "mysql": {
        "desc": "MySQL database — execute queries, manage transactions, and perform CRUD operations on MySQL databases. Supports SELECT, INSERT, UPDATE, DELETE, stored procedures, and batch transactions via `robomotion mysql`. Do NOT use for PostgreSQL, MSSQL, MongoDB, or other databases.",
        "title": "MySQL",
        "intro": "The `robomotion mysql` CLI connects to MySQL databases for SQL operations. It executes queries and non-query statements, manages transactions with batch support, runs stored procedures, and handles full CRUD workflows.",
        "use_cases": [
            "Execute SQL SELECT queries against MySQL tables",
            "Run INSERT, UPDATE, DELETE, and DDL statements",
            "Execute stored procedures with parameters",
            "Use batch transactions for atomic operations",
        ],
        "prereq": "MySQL connection credentials configured via Robomotion vault",
        "workflow": [
            "Install: `robomotion install mysql`",
            "Connect: `robomotion mysql connect` → returns a `conn-id`",
            "Query: `robomotion mysql execute_query --conn-id <id>` (with SQL in context)",
            "Disconnect: `robomotion mysql disconnect --conn-id <id>`",
        ],
    },
    "nextcloud": {
        "desc": "NextCloud — manage files, folders, sharing, and users on self-hosted NextCloud instances. Supports upload, download, file sharing, and user administration via `robomotion nextcloud`. Do NOT use for Dropbox, Google Drive, OneDrive, or other cloud storage.",
        "title": "NextCloud",
        "intro": "The `robomotion nextcloud` CLI connects to NextCloud (self-hosted cloud storage) for file management, sharing, and administration. It uploads, downloads, lists, and deletes files; creates and manages shares with permissions; and administers users.",
        "use_cases": [
            "Upload or download files between local filesystem and NextCloud",
            "List files, create folders, and manage file operations",
            "Create, list, and manage file/folder shares with permissions",
            "Administer NextCloud users",
        ],
        "prereq": "NextCloud instance URL and credentials configured via Robomotion vault",
        "workflow": [
            "Install: `robomotion install nextcloud`",
            "Connect: `robomotion nextcloud nextcloud_connect` → returns a `client-id`",
            "Upload: `robomotion nextcloud nextcloud_upload --client-id <id> --local-path <file> --remote-path <dest>`",
            "List: `robomotion nextcloud nextcloud_list_files --client-id <id> --path <folder>`",
            "Disconnect: `robomotion nextcloud nextcloud_disconnect --client-id <id>`",
        ],
    },
    "nocodb": {
        "desc": "NocoDB — manage tables, records, and databases in NocoDB (open-source Airtable alternative). Supports CRUD, filtering, sorting, and table management via `robomotion nocodb`. Do NOT use for Airtable, Baserow, Google Sheets, or other no-code databases.",
        "title": "NocoDB",
        "intro": "The `robomotion nocodb` CLI connects to NocoDB for database and record management. It supports listing, creating, updating, and deleting records in tables; filtering and sorting data; and managing table schemas.",
        "use_cases": [
            "List, create, update, or delete records in NocoDB tables",
            "Search and filter records with conditions",
            "Manage tables and view schemas",
        ],
        "prereq": "NocoDB instance URL and API token configured via Robomotion vault",
        "workflow": [
            "Install: `robomotion install nocodb`",
            "Connect: `robomotion nocodb nocodb_connect` → returns a `client-id`",
            "List records: `robomotion nocodb nocodb_list_records --client-id <id> --table-id <table>`",
            "Create record: `robomotion nocodb nocodb_create_record --client-id <id> --table-id <table> --fields <json>`",
            "Disconnect: `robomotion nocodb nocodb_disconnect --client-id <id>`",
        ],
    },
    "notion": {
        "desc": "Notion — create, read, update, and search pages and databases. Supports rich content blocks, database queries, and page management via `robomotion notion`. Do NOT use for Fibery, Confluence, Google Docs, or other wiki/productivity tools.",
        "title": "Notion",
        "intro": "The `robomotion notion` CLI connects to Notion for page and database management. It creates and updates pages with rich content blocks, queries databases with filters and sorts, and searches across the workspace.",
        "use_cases": [
            "Create, read, or update Notion pages with content blocks",
            "Query and filter Notion databases",
            "Search pages and databases across the workspace",
        ],
        "prereq": "Notion integration token configured via Robomotion vault",
        "workflow": [
            "Install: `robomotion install notion`",
            "Connect: `robomotion notion connect` → returns a `client-id`",
            "Search: `robomotion notion search --client-id <id> --query <text>`",
            "Create page: `robomotion notion create_page --client-id <id> --parent-id <id> --title <title>`",
            "Disconnect: `robomotion notion disconnect --client-id <id>`",
        ],
    },
    "ocr-extraction": {
        "desc": "OCR text extraction — extract text from images and scanned documents using Google Vision and Document AI. Supports image OCR, document parsing, and structured data extraction via `robomotion googlevision` and `robomotion googledocumentai`. Do NOT use for Tesseract, ABBYY, or direct text processing.",
        "title": "OCR Extraction (Google Vision / Document AI)",
        "intro": "The `robomotion googlevision` and `robomotion googledocumentai` CLIs extract text from images and scanned documents using Google Cloud Vision OCR and Document AI. They support image text detection, document parsing, and structured content extraction.",
        "use_cases": [
            "Extract text from images using Google Vision OCR",
            "Parse scanned documents with Google Document AI",
            "Process invoices, receipts, and forms for structured data",
        ],
        "prereq": "Google Cloud Vision / Document AI credentials configured via Robomotion vault",
        "workflow": [
            "Install: `robomotion install googlevision` or `robomotion install googledocumentai`",
            "Connect: `robomotion googlevision connect` → returns a `client-id`",
            "Extract text: `robomotion googlevision detect_text --client-id <id> --image-path <file>`",
            "Disconnect: `robomotion googlevision disconnect --client-id <id>`",
        ],
    },
    "odoo": {
        "desc": "Odoo ERP — manage contacts, sales orders, invoices, products, leads, and any model via XML-RPC. Supports full ERP operations across all Odoo modules via `robomotion odoo`. Do NOT use for SAP, NetSuite, Salesforce, or other ERP/CRM platforms.",
        "title": "Odoo",
        "intro": "The `robomotion odoo` CLI connects to Odoo ERP via XML-RPC for business management operations. It handles contacts, sales orders, invoices, products, leads, and any Odoo model — supporting create, read, update, delete, and search operations across all modules.",
        "use_cases": [
            "Create, update, or search contacts, leads, and sales orders",
            "Manage invoices and products in Odoo",
            "Query any Odoo model using domain filters via XML-RPC",
        ],
        "prereq": "Odoo instance URL, database, and API credentials configured via Robomotion vault",
        "workflow": [
            "Install: `robomotion install odoo`",
            "Connect: `robomotion odoo odoo_connect` → returns a `client-id`",
            "Search: `robomotion odoo odoo_search_read --client-id <id> --model <model> --domain <filter>`",
            "Create: `robomotion odoo odoo_create --client-id <id> --model <model> --values <json>`",
            "Disconnect: `robomotion odoo odoo_disconnect --client-id <id>`",
        ],
    },
    "ollama": {
        "desc": "Ollama local AI — run LLM models locally for text generation, chat, and embeddings. Supports model management, streaming, and multi-turn conversations via `robomotion ollama`. Do NOT use for OpenAI, Claude, Gemini, or other cloud AI services.",
        "title": "Ollama",
        "intro": "The `robomotion ollama` CLI connects to a local Ollama instance for running LLMs on your own hardware. It supports text generation, chat completions with history, embedding generation, model listing, and model management (pull/delete).",
        "use_cases": [
            "Generate text using local models (Llama, Mistral, etc.)",
            "Run multi-turn chat conversations locally",
            "Generate text embeddings for semantic search",
            "List, pull, or delete Ollama models",
        ],
        "prereq": "Ollama running locally or on an accessible server",
        "workflow": [
            "Install: `robomotion install ollama`",
            "Connect: `robomotion ollama ollama_connect` → returns a `client-id`",
            "Generate: `robomotion ollama ollama_generate --client-id <id> --model llama3 --prompt <text>`",
            "Chat: `robomotion ollama ollama_chat --client-id <id> --model llama3 --messages <json>`",
            "Disconnect: `robomotion ollama ollama_disconnect --client-id <id>`",
        ],
    },
    "onedrive365": {
        "desc": "Microsoft OneDrive 365 — upload, download, list, copy, move, delete, and share files via Microsoft Graph API. Supports folder management, sharing links, and permission control via `robomotion onedrive365`. Do NOT use for Google Drive, Dropbox, S3, or SharePoint document libraries.",
        "title": "Microsoft OneDrive 365",
        "intro": "The `robomotion onedrive365` CLI connects to Microsoft OneDrive via the Graph API for file management. It uploads, downloads, lists, copies, moves, and deletes files; creates folders; generates sharing links; and manages file permissions.",
        "use_cases": [
            "Upload or download files between local filesystem and OneDrive",
            "List, copy, move, or delete files and folders",
            "Create sharing links and manage file permissions",
            "Create folders and manage the file hierarchy",
        ],
        "prereq": "Microsoft 365 OAuth2 credentials configured via Robomotion vault",
        "workflow": [
            "Install: `robomotion install onedrive365`",
            "Connect: `robomotion onedrive365 onedrive_connect` → returns a `client-id`",
            "Upload: `robomotion onedrive365 onedrive_upload_file --client-id <id> --local-path <file> --remote-path <dest>`",
            "List: `robomotion onedrive365 onedrive_list_files --client-id <id> --path <folder>`",
            "Disconnect: `robomotion onedrive365 onedrive_disconnect --client-id <id>`",
        ],
    },
    "onenote365": {
        "desc": "Microsoft OneNote 365 — manage notebooks, sections, section groups, and pages via Microsoft Graph API. Supports page creation, content reading, and notebook organization via `robomotion onenote365`. Do NOT use for Notion, Evernote, Google Keep, or other note apps.",
        "title": "Microsoft OneNote 365",
        "intro": "The `robomotion onenote365` CLI connects to Microsoft OneNote via the Graph API for notebook management. It lists and manages notebooks, section groups, and sections; creates and reads pages with HTML content; and organizes note hierarchies.",
        "use_cases": [
            "Create pages with HTML content in OneNote sections",
            "List notebooks, section groups, and sections",
            "Read page content and manage notebook structure",
        ],
        "prereq": "Microsoft 365 OAuth2 credentials configured via Robomotion vault",
        "workflow": [
            "Install: `robomotion install onenote365`",
            "Connect: `robomotion onenote365 onenote_connect` → returns a `client-id`",
            "List notebooks: `robomotion onenote365 onenote_list_notebooks --client-id <id>`",
            "Create page: `robomotion onenote365 onenote_create_page --client-id <id> --section-id <section> --title <title> --content <html>`",
            "Disconnect: `robomotion onenote365 onenote_disconnect --client-id <id>`",
        ],
    },
    "openai": {
        "desc": "OpenAI API — generate text, images, speech, transcriptions, and embeddings using GPT, DALL-E, Whisper, and TTS models. Supports chat completions, vision, function calling, and file management via `robomotion openai`. Do NOT use for Claude, Gemini, or direct LLM conversation.",
        "title": "OpenAI",
        "intro": "The `robomotion openai` CLI calls the OpenAI API for AI operations. It generates text with GPT models (including vision and function calling), creates images with DALL-E/GPT-Image, synthesizes and transcribes audio, generates embeddings, moderates content, and manages files.",
        "use_cases": [
            "Generate text or chat completions with GPT models (including tool use)",
            "Create or edit images with DALL-E and GPT-Image models",
            "Convert text to speech or transcribe/translate audio with Whisper",
            "Generate embeddings, moderate content, and manage uploaded files",
        ],
        "prereq": "OpenAI API key configured via Robomotion vault",
        "workflow": [
            "Install: `robomotion install openai`",
            "Connect: `robomotion openai connect_openai` → returns a `connection-id`",
            "Generate text: `robomotion openai generate_text --connection-id <id> --user-prompt <prompt>`",
            "Generate image: `robomotion openai generate_image --connection-id <id> --prompt <text>`",
            "Disconnect: `robomotion openai disconnect_openai --connection-id <id>`",
        ],
    },
    "openrouter": {
        "desc": "OpenRouter unified AI API — access 480+ AI models (Claude, GPT, Gemini, Grok, DeepSeek, etc.) through a single API. Supports text generation, chat, image generation, streaming, and reasoning mode via `robomotion openrouter`. Do NOT use for direct OpenAI, Claude, or Gemini API calls.",
        "title": "OpenRouter",
        "intro": "The `robomotion openrouter` CLI connects to OpenRouter's unified API gateway providing access to 480+ AI models across providers. It supports text generation, chat completions with history, image generation, streaming responses, reasoning mode, and model listing.",
        "use_cases": [
            "Generate text or chat responses using any of 480+ AI models",
            "Access Claude, GPT, Gemini, Grok, DeepSeek through a single API",
            "Generate images or use reasoning mode for complex tasks",
            "Stream responses and manage model selection",
        ],
        "prereq": "OpenRouter API key configured via Robomotion vault",
        "workflow": [
            "Install: `robomotion install openrouter`",
            "Connect: `robomotion openrouter openrouter_connect` → returns a `client-id`",
            "Generate: `robomotion openrouter openrouter_generate_text --client-id <id> --model <model> --prompt <text>`",
            "Chat: `robomotion openrouter openrouter_generate_chat --client-id <id> --model <model> --messages <json>`",
            "Disconnect: `robomotion openrouter openrouter_disconnect --client-id <id>`",
        ],
    },
    "openweather": {
        "desc": "OpenWeatherMap — get current weather, forecasts, air quality, and historical weather data for any location. Supports geocoding and multiple weather data types via `robomotion openweather`. Do NOT use for AccuWeather or other weather services.",
        "title": "OpenWeather",
        "intro": "The `robomotion openweather` CLI connects to OpenWeatherMap API for weather data retrieval. It gets current weather conditions, multi-day forecasts, air quality data, and historical weather for any location by city name or coordinates.",
        "use_cases": [
            "Get current weather conditions for any city or coordinates",
            "Retrieve multi-day weather forecasts",
            "Check air quality index and pollutant levels",
            "Access historical weather data",
        ],
        "prereq": "OpenWeatherMap API key configured via Robomotion vault",
        "workflow": [
            "Install: `robomotion install openweather`",
            "Connect: `robomotion openweather openweather_connect` → returns a `client-id`",
            "Get weather: `robomotion openweather openweather_current --client-id <id> --city <city>`",
            "Disconnect: `robomotion openweather openweather_disconnect --client-id <id>`",
        ],
    },
    "oracle": {
        "desc": "Oracle Database — execute SQL queries, manage transactions, and perform CRUD operations. Supports SELECT, INSERT, UPDATE, DELETE, stored procedures, and batch transactions via `robomotion oracle`. Do NOT use for PostgreSQL, MySQL, MSSQL, or other databases.",
        "title": "Oracle Database",
        "intro": "The `robomotion oracle` CLI connects to Oracle databases for SQL operations. It executes queries and non-query statements, manages batch transactions, and handles the full range of Oracle SQL operations.",
        "use_cases": [
            "Execute SQL SELECT queries against Oracle tables",
            "Run INSERT, UPDATE, DELETE, and DDL statements",
            "Use batch transactions for atomic multi-statement operations",
        ],
        "prereq": "Oracle database connection credentials configured via Robomotion vault",
        "workflow": [
            "Install: `robomotion install oracle`",
            "Connect: `robomotion oracle connect` → returns a `conn-id`",
            "Query: `robomotion oracle execute_query --conn-id <id>` (with SQL in context)",
            "Disconnect: `robomotion oracle disconnect --conn-id <id>`",
        ],
    },
    "outlook365": {
        "desc": "Microsoft Outlook 365 — send, read, search, and manage emails, calendar events, and mail folders via Microsoft Graph API. Supports attachments, replies, and event scheduling via `robomotion outlook365`. Do NOT use for Gmail, generic SMTP, or non-Microsoft email.",
        "title": "Microsoft Outlook 365",
        "intro": "The `robomotion outlook365` CLI connects to Microsoft Outlook 365 via the Graph API for email and calendar management. It sends, reads, replies to, and searches emails; manages mail folders; handles attachments; and creates, lists, and manages calendar events.",
        "use_cases": [
            "Send emails with recipients, CC/BCC, and attachments",
            "Read, search, reply to, or delete emails",
            "Manage mail folders and email organization",
            "Create, list, and manage calendar events",
        ],
        "prereq": "Microsoft 365 OAuth2 credentials configured via Robomotion vault",
        "workflow": [
            "Install: `robomotion install outlook365`",
            "Connect: `robomotion outlook365 outlook_connect` → returns a `client-id`",
            "Send email: `robomotion outlook365 outlook_send_email --client-id <id> --to <email> --subject <subj> --body <body>`",
            "List emails: `robomotion outlook365 outlook_list_emails --client-id <id>`",
            "Disconnect: `robomotion outlook365 outlook_disconnect --client-id <id>`",
        ],
    },
    "pcloud": {
        "desc": "pCloud — upload, download, list, create, delete, and manage files and folders in pCloud storage. Supports file operations and folder management via `robomotion pcloud`. Do NOT use for Dropbox, Google Drive, OneDrive, or other cloud storage.",
        "title": "pCloud",
        "intro": "The `robomotion pcloud` CLI connects to pCloud for cloud file storage management. It uploads, downloads, lists, and deletes files; creates and manages folders; and handles file operations on pCloud storage.",
        "use_cases": [
            "Upload or download files between local filesystem and pCloud",
            "List files and create/delete folders",
            "Manage files and folder structure in pCloud",
        ],
        "prereq": "pCloud access token configured via Robomotion vault",
        "workflow": [
            "Install: `robomotion install pcloud`",
            "Connect: `robomotion pcloud pcloud_connect` → returns a `client-id`",
            "Upload: `robomotion pcloud pcloud_upload_file --client-id <id> --file-path <local> --folder-id <folder>`",
            "List: `robomotion pcloud pcloud_list_folder --client-id <id> --folder-id <folder>`",
            "Disconnect: `robomotion pcloud pcloud_disconnect --client-id <id>`",
        ],
    },
    "pdf": {
        "desc": "PDF processor — create, merge, split, extract text, convert, and manipulate PDF files. Supports page operations, text extraction, and format conversions via `robomotion pdfprocessor`. Do NOT use for Google Docs, Word documents, or image OCR.",
        "title": "PDF Processor",
        "intro": "The `robomotion pdfprocessor` CLI handles PDF file operations. It creates, merges, splits, extracts text from, and converts PDF files. It supports page-level operations, metadata handling, and various format conversions.",
        "use_cases": [
            "Extract text content from PDF files",
            "Merge multiple PDFs into one or split PDFs by pages",
            "Create new PDF files from content",
            "Convert between PDF and other formats",
        ],
        "prereq": "No external credentials needed — works with local PDF files",
        "workflow": [
            "Install: `robomotion install pdfprocessor`",
            "Extract text: `robomotion pdfprocessor extract_text --file-path <pdf>`",
            "Merge: `robomotion pdfprocessor merge --files <pdf1,pdf2> --output <out.pdf>`",
        ],
    },
    "perplexity": {
        "desc": "Perplexity AI — AI-powered search and chat with real-time web data and citations. Supports web-grounded responses and conversational search via `robomotion perplexity`. Do NOT use for OpenAI, Claude, Google Search, Tavily, or other AI/search services.",
        "title": "Perplexity AI",
        "intro": "The `robomotion perplexity` CLI connects to Perplexity AI for search-augmented AI responses. It provides chat completions grounded in real-time web data with source citations, combining LLM reasoning with live search results.",
        "use_cases": [
            "Search the web with AI-powered answers and citations",
            "Run chat completions with real-time web data grounding",
            "Get up-to-date factual responses backed by sources",
        ],
        "prereq": "Perplexity API key configured via Robomotion vault",
        "workflow": [
            "Install: `robomotion install perplexity`",
            "Connect: `robomotion perplexity perplexity_connect` → returns a `client-id`",
            "Search: `robomotion perplexity perplexity_chat --client-id <id> --messages <json>`",
            "Disconnect: `robomotion perplexity perplexity_disconnect --client-id <id>`",
        ],
    },
    "phantombuster": {
        "desc": "Phantombuster — run web scraping and automation Phantoms for data extraction from social media and websites. Supports Phantom management, execution, and result retrieval via `robomotion phantombuster`. Do NOT use for Apify, direct scraping, or dom parser.",
        "title": "Phantombuster",
        "intro": "The `robomotion phantombuster` CLI connects to Phantombuster for automated web scraping and data extraction. It launches and manages Phantoms (pre-built automation scripts), tracks execution status, retrieves results, and manages Phantom configuration.",
        "use_cases": [
            "Launch Phantombuster Phantoms for LinkedIn, Twitter, and web scraping",
            "Monitor Phantom execution status and retrieve output data",
            "Manage Phantom configurations and schedules",
        ],
        "prereq": "Phantombuster API key configured via Robomotion vault",
        "workflow": [
            "Install: `robomotion install phantombuster`",
            "Connect: `robomotion phantombuster phantombuster_connect` → returns a `client-id`",
            "Launch: `robomotion phantombuster phantombuster_launch --client-id <id> --phantom-id <phantom>`",
            "Get output: `robomotion phantombuster phantombuster_get_output --client-id <id> --container-id <container>`",
            "Disconnect: `robomotion phantombuster phantombuster_disconnect --client-id <id>`",
        ],
    },
    "pinecone": {
        "desc": "Pinecone vector database — upsert, query, and manage vector embeddings in Pinecone indexes. Supports similarity search, namespace management, and index operations via `robomotion pinecone`. Do NOT use for Qdrant, Weaviate, ChromaDB, or other vector databases.",
        "title": "Pinecone",
        "intro": "The `robomotion pinecone` CLI connects to Pinecone for vector database operations. It upserts, queries, fetches, and deletes vectors; manages indexes and namespaces; and performs similarity searches with metadata filtering.",
        "use_cases": [
            "Upsert vector embeddings into Pinecone indexes",
            "Query for similar vectors with top-K and metadata filtering",
            "Manage Pinecone indexes — create, describe, list, delete",
            "Fetch vectors by ID and manage namespaces",
        ],
        "prereq": "Pinecone API key configured via Robomotion vault",
        "workflow": [
            "Install: `robomotion install pinecone`",
            "Connect: `robomotion pinecone pinecone_connect` → returns a `client-id`",
            "Upsert: `robomotion pinecone pinecone_upsert --client-id <id> --index <idx> --vectors <json>`",
            "Query: `robomotion pinecone pinecone_query --client-id <id> --index <idx> --vector <vec> --top-k 10`",
            "Disconnect: `robomotion pinecone pinecone_disconnect --client-id <id>`",
        ],
    },
    "polymarket": {
        "desc": "Polymarket prediction markets — access market data, event details, pricing, orderbooks, positions, and trading analytics. Supports market research and position tracking via `robomotion polymarket`. Do NOT use for Binance, stock trading, or other financial platforms.",
        "title": "Polymarket",
        "intro": "The `robomotion polymarket` CLI connects to Polymarket for prediction market data and analytics. It retrieves market listings, event details, current pricing/probabilities, orderbook depth, positions, trades, and spread analytics.",
        "use_cases": [
            "Browse prediction markets and get current pricing/probabilities",
            "View orderbook depth and market spread analytics",
            "Track positions and trade history",
            "Search for events and market outcomes",
        ],
        "prereq": "Polymarket API access configured via Robomotion vault",
        "workflow": [
            "Install: `robomotion install polymarket`",
            "Connect: `robomotion polymarket polymarket_connect` → returns a `client-id`",
            "List markets: `robomotion polymarket polymarket_get_markets --client-id <id>`",
            "Get price: `robomotion polymarket polymarket_get_price --client-id <id> --token-id <token>`",
            "Disconnect: `robomotion polymarket polymarket_disconnect --client-id <id>`",
        ],
    },
    "postgresql": {
        "desc": "PostgreSQL database — execute SQL queries, manage transactions, and perform CRUD operations. Supports SELECT, INSERT, UPDATE, DELETE, batch transactions, and stored procedures via `robomotion postgresql`. Do NOT use for MySQL, MongoDB, SQLite, or other databases.",
        "title": "PostgreSQL",
        "intro": "The `robomotion postgresql` CLI connects to PostgreSQL databases for SQL operations. It executes queries and non-query statements, manages batch transactions for atomicity, and handles the full range of PostgreSQL SQL operations.",
        "use_cases": [
            "Execute SQL SELECT queries against PostgreSQL tables",
            "Run INSERT, UPDATE, DELETE, and DDL statements",
            "Use batch transactions for atomic multi-statement operations",
        ],
        "prereq": "PostgreSQL connection credentials configured via Robomotion vault",
        "workflow": [
            "Install: `robomotion install postgresql`",
            "Connect: `robomotion postgresql connect` → returns a `conn-id`",
            "Query: `robomotion postgresql execute_query --conn-id <id>` (with SQL in context)",
            "Disconnect: `robomotion postgresql disconnect --conn-id <id>`",
        ],
    },
    "powerpoint365": {
        "desc": "Microsoft PowerPoint 365 — create presentations from templates, replace text/images, duplicate slides, and export to PDF. Supports AI-powered presentation generation workflows via `robomotion powerpoint365`. Do NOT use for Google Slides, Keynote, or local PowerPoint files.",
        "title": "Microsoft PowerPoint 365",
        "intro": "The `robomotion powerpoint365` CLI connects to Microsoft PowerPoint 365 via the Graph API for presentation management. It creates presentations from templates, replaces text and images in slides, duplicates slides, manages slide content, and exports to PDF — ideal for automated presentation generation.",
        "use_cases": [
            "Create presentations from templates in OneDrive/SharePoint",
            "Replace text and images in slides for automated generation",
            "Duplicate slides and manage presentation structure",
            "Export presentations to PDF",
        ],
        "prereq": "Microsoft 365 OAuth2 credentials configured via Robomotion vault",
        "workflow": [
            "Install: `robomotion install powerpoint365`",
            "Connect: `robomotion powerpoint365 pptx_connect` → returns a `client-id`",
            "Create from template: `robomotion powerpoint365 pptx_create_from_template --client-id <id> --template-path <tmpl>`",
            "Replace text: `robomotion powerpoint365 pptx_replace_text --client-id <id> --presentation-id <id> --find <old> --replace <new>`",
            "Disconnect: `robomotion powerpoint365 pptx_disconnect --client-id <id>`",
        ],
    },
    "pushover": {
        "desc": "Pushover — send push notifications to Android, iOS, and desktop devices with priority levels, sounds, and attachments. Supports emergency alerts and delivery verification via `robomotion pushover`. Do NOT use for Slack, email, Twilio SMS, or other notification channels.",
        "title": "Pushover",
        "intro": "The `robomotion pushover` CLI sends push notifications via Pushover to mobile and desktop devices. It supports priority levels (including emergency with acknowledgment), custom sounds, URL attachments, and delivery receipt verification.",
        "use_cases": [
            "Send push notifications with custom priority, title, and message",
            "Send emergency notifications that require acknowledgment",
            "Attach URLs and custom sounds to notifications",
            "Verify delivery receipts for critical alerts",
        ],
        "prereq": "Pushover API token and user key configured via Robomotion vault",
        "workflow": [
            "Install: `robomotion install pushover`",
            "Connect: `robomotion pushover pushover_connect` → returns a `client-id`",
            "Send: `robomotion pushover pushover_send --client-id <id> --message <text> --title <title>`",
            "Disconnect: `robomotion pushover pushover_disconnect --client-id <id>`",
        ],
    },
    "qdrant": {
        "desc": "Qdrant vector database — upsert, search, and manage vector embeddings with payload filtering. Supports collection management, similarity search, batch operations, and scroll queries via `robomotion qdrant`. Do NOT use for Pinecone, Weaviate, ChromaDB, or other vector databases.",
        "title": "Qdrant",
        "intro": "The `robomotion qdrant` CLI connects to Qdrant for vector database operations. It upserts, searches, scrolls, and deletes points; manages collections with configurable distance metrics; supports batch operations; and performs filtered similarity searches with payload conditions.",
        "use_cases": [
            "Upsert vectors with payloads into Qdrant collections",
            "Search for similar vectors with filtering and scoring",
            "Manage collections — create, delete, get info",
            "Scroll through points and retrieve by ID",
        ],
        "prereq": "Qdrant instance URL and API key (if secured) configured via Robomotion vault",
        "workflow": [
            "Install: `robomotion install qdrant`",
            "Connect: `robomotion qdrant qdrant_connect` → returns a `client-id`",
            "Upsert: `robomotion qdrant qdrant_upsert_points --client-id <id> --collection <col> --points <json>`",
            "Search: `robomotion qdrant qdrant_search --client-id <id> --collection <col> --vector <vec> --limit 10`",
            "Disconnect: `robomotion qdrant qdrant_disconnect --client-id <id>`",
        ],
    },
    "questdb": {
        "desc": "QuestDB time-series database — execute SQL queries and insert time-series data. Supports high-performance ingestion and time-based analytics via `robomotion questdb`. Do NOT use for TimescaleDB, InfluxDB, or other time-series databases.",
        "title": "QuestDB",
        "intro": "The `robomotion questdb` CLI connects to QuestDB for time-series database operations. It executes SQL queries optimized for time-series data, inserts records with timestamps, and manages connections to QuestDB instances.",
        "use_cases": [
            "Execute time-series SQL queries with time-based aggregations",
            "Insert time-series data points into QuestDB tables",
            "Query sensor, metrics, or event data with time filters",
        ],
        "prereq": "QuestDB connection credentials configured via Robomotion vault",
        "workflow": [
            "Install: `robomotion install questdb`",
            "Connect: `robomotion questdb questdb_connect` → returns a `conn-id`",
            "Query: `robomotion questdb questdb_execute_query --conn-id <id>` (with SQL in context)",
            "Disconnect: `robomotion questdb questdb_disconnect --conn-id <id>`",
        ],
    },
    "rabbitmq": {
        "desc": "RabbitMQ message broker — publish and consume messages, manage queues and exchanges. Supports message routing, queue binding, and queue management via `robomotion rabbitmq`. Do NOT use for Kafka, Redis pub/sub, SQS, or other message brokers.",
        "title": "RabbitMQ",
        "intro": "The `robomotion rabbitmq` CLI connects to RabbitMQ for message broker operations. It publishes messages to exchanges, consumes from queues, creates and manages queues and exchanges, and handles queue binding and message routing.",
        "use_cases": [
            "Publish messages to RabbitMQ exchanges or queues",
            "Consume messages from queues",
            "Create, delete, and manage queues and exchanges",
            "Bind queues to exchanges with routing keys",
        ],
        "prereq": "RabbitMQ connection URI configured via Robomotion vault",
        "workflow": [
            "Install: `robomotion install rabbitmq`",
            "Connect: `robomotion rabbitmq rabbitmq_connect` → returns a `client-id`",
            "Publish: `robomotion rabbitmq rabbitmq_publish --client-id <id> --queue <queue> --message <json>`",
            "Consume: `robomotion rabbitmq rabbitmq_consume --client-id <id> --queue <queue>`",
            "Disconnect: `robomotion rabbitmq rabbitmq_disconnect --client-id <id>`",
        ],
    },
    "redis": {
        "desc": "Redis — perform key-value operations on strings, hashes, lists, sets, and pub/sub channels. Supports TTL, pattern matching, and all core Redis data structures via `robomotion redis`. Do NOT use for PostgreSQL, MongoDB, Memcached, or other databases.",
        "title": "Redis",
        "intro": "The `robomotion redis` CLI connects to Redis for key-value and data structure operations. It supports strings (get/set with TTL), hashes (hset/hget/hgetall), lists (push/pop/range), sets (add/remove/members), key management (exists/expire/keys), and pub/sub messaging.",
        "use_cases": [
            "Get, set, or delete key-value pairs with optional TTL",
            "Work with hashes, lists, and sets (full CRUD)",
            "Publish messages to channels (pub/sub)",
            "Search keys by pattern, check existence, and manage expiration",
        ],
        "prereq": "Redis connection credentials configured via Robomotion vault",
        "workflow": [
            "Install: `robomotion install redis`",
            "Connect: `robomotion redis redis_connect` → returns a `client-id`",
            "Set: `robomotion redis redis_set --client-id <id> --key <key> --value <val>`",
            "Get: `robomotion redis redis_get --client-id <id> --key <key>`",
            "Disconnect: `robomotion redis redis_disconnect --client-id <id>`",
        ],
    },
    "replicate-ai": {
        "desc": "Replicate AI — run ML model predictions for image, video, text, and audio generation. Supports model execution, async predictions, streaming, and model management via `robomotion replicateai`. Do NOT use for OpenAI, Fal.ai, Stability AI, or other AI platforms.",
        "title": "Replicate AI",
        "intro": "The `robomotion replicateai` CLI runs AI model predictions on Replicate's cloud infrastructure. It supports running models synchronously or asynchronously, streaming predictions, listing and searching models, and managing prediction lifecycle.",
        "use_cases": [
            "Run AI model predictions (image gen, LLMs, audio, video)",
            "Submit async predictions and retrieve results later",
            "Stream prediction outputs in real-time",
            "Search and discover Replicate models",
        ],
        "prereq": "Replicate API token configured via Robomotion vault",
        "workflow": [
            "Install: `robomotion install replicateai`",
            "Connect: `robomotion replicateai replicateai_connect` → returns a `client-id`",
            "Run model: `robomotion replicateai replicateai_run --client-id <id> --model <owner/model> --input <json>`",
            "Disconnect: `robomotion replicateai replicateai_disconnect --client-id <id>`",
        ],
    },
    "resend": {
        "desc": "Resend email API — send transactional emails, manage contacts, audiences, and domains. Supports HTML/text emails, batch sending, and domain verification via `robomotion resend`. Do NOT use for Gmail, Outlook, SendGrid, or other email services.",
        "title": "Resend",
        "intro": "The `robomotion resend` CLI connects to Resend for transactional email delivery. It sends emails (HTML and text), manages contacts and audiences, handles domain verification, and supports batch email operations.",
        "use_cases": [
            "Send transactional emails with HTML or plain text content",
            "Manage contacts and audience lists",
            "Verify and manage sending domains",
            "Send batch emails to multiple recipients",
        ],
        "prereq": "Resend API key configured via Robomotion vault",
        "workflow": [
            "Install: `robomotion install resend`",
            "Connect: `robomotion resend resend_connect` → returns a `client-id`",
            "Send email: `robomotion resend resend_send_email --client-id <id> --from <from> --to <to> --subject <subj> --html <body>`",
            "Disconnect: `robomotion resend resend_disconnect --client-id <id>`",
        ],
    },
    "rundeck": {
        "desc": "Rundeck — execute automation jobs, manage projects, and monitor job executions. Supports runbook automation and job scheduling via `robomotion rundeck`. Do NOT use for Ansible, Jenkins, GitHub Actions, or other CI/CD tools.",
        "title": "Rundeck",
        "intro": "The `robomotion rundeck` CLI connects to Rundeck for runbook automation and job execution. It lists projects, executes jobs with parameters, and monitors execution status.",
        "use_cases": [
            "Execute Rundeck automation jobs with parameters",
            "List and manage Rundeck projects",
            "Monitor job execution status and results",
        ],
        "prereq": "Rundeck URL and API token configured via Robomotion vault",
        "workflow": [
            "Install: `robomotion install rundeck`",
            "Connect: `robomotion rundeck rundeck_connect` → returns a `client-id`",
            "Run job: `robomotion rundeck rundeck_run_job --client-id <id> --job-id <job>`",
            "Disconnect: `robomotion rundeck rundeck_disconnect --client-id <id>`",
        ],
    },
    "s3-storage": {
        "desc": "Amazon S3 — upload, download, list, delete, and manage objects in S3 buckets. Supports bucket management, presigned URLs, and multi-part uploads via `robomotion amazons3`. Do NOT use for Google Cloud Storage, Dropbox, OneDrive, or other storage services.",
        "title": "Amazon S3",
        "intro": "The `robomotion amazons3` CLI connects to Amazon S3 for object storage operations. It uploads, downloads, lists, copies, and deletes objects; manages buckets; generates presigned URLs; and handles file operations across S3 buckets.",
        "use_cases": [
            "Upload or download files between local filesystem and S3",
            "List, copy, or delete objects in S3 buckets",
            "Create or manage S3 buckets",
            "Generate presigned URLs for temporary access",
        ],
        "prereq": "AWS access key and secret key configured via Robomotion vault",
        "workflow": [
            "Install: `robomotion install amazons3`",
            "Connect: `robomotion amazons3 connect` → returns a `client-id`",
            "Upload: `robomotion amazons3 upload_file --client-id <id> --bucket <bucket> --key <key> --file-path <file>`",
            "List: `robomotion amazons3 list_objects --client-id <id> --bucket <bucket>`",
            "Disconnect: `robomotion amazons3 disconnect --client-id <id>`",
        ],
    },
    "searchapi": {
        "desc": "SearchAPI — search Google, Bing, YouTube, Google Maps, News, Scholar, Shopping, and more through a unified API. Supports multiple search engines and result types via `robomotion searchapi`. Do NOT use for Serper, Tavily, or direct Google API.",
        "title": "SearchAPI",
        "intro": "The `robomotion searchapi` CLI connects to SearchAPI.io for multi-engine web search. It searches Google, Bing, YouTube, Google Maps, News, Scholar, Shopping, and more through a unified interface with configurable result limits and search parameters.",
        "use_cases": [
            "Search Google, Bing, or YouTube for web results",
            "Get Google Maps, News, Scholar, or Shopping results",
            "Search for images or videos across engines",
            "Access multiple search engines through one API",
        ],
        "prereq": "SearchAPI.io API key configured via Robomotion vault",
        "workflow": [
            "Install: `robomotion install searchapi`",
            "Connect: `robomotion searchapi searchapi_connect` → returns a `client-id`",
            "Search Google: `robomotion searchapi searchapi_google --client-id <id> --query <text>`",
            "Search YouTube: `robomotion searchapi searchapi_youtube --client-id <id> --query <text>`",
            "Disconnect: `robomotion searchapi searchapi_disconnect --client-id <id>`",
        ],
    },
    "seatable": {
        "desc": "SeaTable — manage rows, tables, and bases in SeaTable collaborative databases. Supports CRUD, filtering, linking, file attachments, and view management via `robomotion seatable`. Do NOT use for Airtable, Baserow, NocoDB, or other no-code databases.",
        "title": "SeaTable",
        "intro": "The `robomotion seatable` CLI connects to SeaTable for collaborative database management. It manages rows (CRUD with filtering and sorting), tables, bases, links between records, file attachments, and views.",
        "use_cases": [
            "List, create, update, or delete rows in SeaTable tables",
            "Search and filter rows with SQL-like conditions",
            "Manage links between records and file attachments",
            "List tables, views, and manage base schemas",
        ],
        "prereq": "SeaTable API token configured via Robomotion vault",
        "workflow": [
            "Install: `robomotion install seatable`",
            "Connect: `robomotion seatable seatable_connect` → returns a `client-id`",
            "List rows: `robomotion seatable seatable_list_rows --client-id <id> --table-name <table>`",
            "Create row: `robomotion seatable seatable_create_row --client-id <id> --table-name <table> --row <json>`",
            "Disconnect: `robomotion seatable seatable_disconnect --client-id <id>`",
        ],
    },
    "sentry": {
        "desc": "Sentry error tracking — monitor application errors and capture events. Supports error reporting, issue listing, and event tracking via `robomotion sentry`. Do NOT use for Datadog, Splunk, New Relic, or other APM platforms.",
        "title": "Sentry",
        "intro": "The `robomotion sentry` CLI connects to Sentry for application error tracking. It captures and reports events, monitors errors, and manages issue tracking.",
        "use_cases": [
            "Capture and report error events to Sentry",
            "Monitor application errors and exceptions",
            "Track issues and event history",
        ],
        "prereq": "Sentry DSN or API token configured via Robomotion vault",
        "workflow": [
            "Install: `robomotion install sentry`",
            "Connect: `robomotion sentry sentry_connect` → returns a `client-id`",
            "Capture event: `robomotion sentry sentry_capture_event --client-id <id> --message <text>`",
            "Disconnect: `robomotion sentry sentry_disconnect --client-id <id>`",
        ],
    },
    "serper": {
        "desc": "Serper Google Search API — search Google for web, image, video, news, shopping, scholar, places, and autocomplete results. Supports multiple search types and result formats via `robomotion serper`. Do NOT use for SearchAPI, Tavily, or direct Google API.",
        "title": "Serper",
        "intro": "The `robomotion serper` CLI connects to Serper's Google Search API for fast, structured search results. It searches Google web, images, videos, news, shopping, scholar, places, and provides autocomplete and related searches.",
        "use_cases": [
            "Search Google for web results, images, videos, or news",
            "Get Google Shopping, Scholar, or Places results",
            "Use autocomplete and related searches",
            "Access structured search results in JSON format",
        ],
        "prereq": "Serper API key configured via Robomotion vault",
        "workflow": [
            "Install: `robomotion install serper`",
            "Connect: `robomotion serper serper_connect` → returns a `client-id`",
            "Search web: `robomotion serper serper_search --client-id <id> --query <text>`",
            "Search images: `robomotion serper serper_images --client-id <id> --query <text>`",
            "Disconnect: `robomotion serper serper_disconnect --client-id <id>`",
        ],
    },
    "sharepoint365": {
        "desc": "Microsoft SharePoint 365 — manage sites, lists, list items, document libraries, and files via Microsoft Graph API. Supports site search, list CRUD, and file operations via `robomotion sharepoint365`. Do NOT use for OneDrive personal, Google Drive, or Confluence.",
        "title": "Microsoft SharePoint 365",
        "intro": "The `robomotion sharepoint365` CLI connects to Microsoft SharePoint 365 via the Graph API for site and content management. It manages sites, lists, list items, document libraries, and files — supporting search, CRUD operations, and file upload/download.",
        "use_cases": [
            "List, search, and manage SharePoint sites",
            "Create, read, update, and delete list items",
            "Upload and download files from document libraries",
            "Manage lists, views, and site content",
        ],
        "prereq": "Microsoft 365 OAuth2 credentials configured via Robomotion vault",
        "workflow": [
            "Install: `robomotion install sharepoint365`",
            "Connect: `robomotion sharepoint365 sp_connect` → returns a `client-id`",
            "List sites: `robomotion sharepoint365 sp_list_sites --client-id <id>`",
            "Get list items: `robomotion sharepoint365 sp_get_list_items --client-id <id> --site-id <site> --list-id <list>`",
            "Disconnect: `robomotion sharepoint365 sp_disconnect --client-id <id>`",
        ],
    },
    "shopify": {
        "desc": "Shopify — manage products, orders, customers, inventory, collections, and fulfillments. Supports full ecommerce operations including order processing and inventory tracking via `robomotion shopify`. Do NOT use for WooCommerce, Magento, or other ecommerce platforms.",
        "title": "Shopify",
        "intro": "The `robomotion shopify` CLI connects to Shopify for ecommerce management. It handles products (CRUD with variants), orders (create/fulfill/cancel), customers, inventory levels, collections, and fulfillment tracking — covering the full online store workflow.",
        "use_cases": [
            "Create, update, list, or delete products and variants",
            "Manage orders — create, fulfill, cancel, and track",
            "Search and manage customer records",
            "Track inventory levels and manage collections",
        ],
        "prereq": "Shopify store URL and API access token configured via Robomotion vault",
        "workflow": [
            "Install: `robomotion install shopify`",
            "Connect: `robomotion shopify shopify_connect` → returns a `client-id`",
            "List products: `robomotion shopify shopify_list_products --client-id <id>`",
            "Create order: `robomotion shopify shopify_create_order --client-id <id> --line-items <json>`",
            "Disconnect: `robomotion shopify shopify_disconnect --client-id <id>`",
        ],
    },
    "slack": {
        "desc": "Slack — send messages, manage channels, list users, upload files, and receive messages via Socket Mode. Supports channel management and file operations via `robomotion slack`. Do NOT use for Discord, Teams, Telegram, or other messaging platforms.",
        "title": "Slack",
        "intro": "The `robomotion slack` CLI connects to Slack workspaces for messaging and channel management. It sends messages to channels, lists channels and users, uploads and deletes files, and receives messages via Socket Mode for real-time interaction.",
        "use_cases": [
            "Send messages to Slack channels by name",
            "List channels, users, and workspace information",
            "Upload or delete files in channels",
            "Receive messages via Socket Mode",
        ],
        "prereq": "Slack bot token configured via Robomotion vault",
        "workflow": [
            "Install: `robomotion install slack`",
            "Connect: `robomotion slack connect` → returns a `client-id`",
            "Send: `robomotion slack send_message --client-id <id> --channel-name <channel> --message <text>`",
            "List channels: `robomotion slack list_channels --client-id <id>`",
            "Disconnect: `robomotion slack disconnect --client-id <id>`",
        ],
    },
    "splunk": {
        "desc": "Splunk — search logs, submit events, manage indexes, and run saved searches. Supports SPL queries, event ingestion, and search job management via `robomotion splunk`. Do NOT use for Datadog, Sentry, ELK Stack, or other log platforms.",
        "title": "Splunk",
        "intro": "The `robomotion splunk` CLI connects to Splunk for log management and search. It submits events to indexes, runs SPL search queries, manages search jobs, accesses saved searches, and handles index management.",
        "use_cases": [
            "Search logs and events using SPL (Search Processing Language)",
            "Submit events to Splunk indexes for ingestion",
            "Manage search jobs and retrieve results",
            "List and manage indexes and saved searches",
        ],
        "prereq": "Splunk instance URL and API credentials configured via Robomotion vault",
        "workflow": [
            "Install: `robomotion install splunk`",
            "Connect: `robomotion splunk splunk_connect` → returns a `client-id`",
            "Search: `robomotion splunk splunk_search --client-id <id> --query <spl>`",
            "Submit event: `robomotion splunk splunk_submit_event --client-id <id> --index <idx> --event <json>`",
            "Disconnect: `robomotion splunk splunk_disconnect --client-id <id>`",
        ],
    },
    "sqlite": {
        "desc": "SQLite — execute queries and manage embedded SQLite database files. Supports SELECT, INSERT, UPDATE, DELETE, batch transactions, and local database operations via `robomotion sqlite`. Do NOT use for PostgreSQL, MySQL, or server-based databases.",
        "title": "SQLite",
        "intro": "The `robomotion sqlite` CLI works with local SQLite database files for embedded SQL operations. It executes queries and non-query statements, manages batch transactions, and handles schema operations on `.db` files without requiring a database server.",
        "use_cases": [
            "Execute SQL SELECT queries on local SQLite databases",
            "Run INSERT, UPDATE, DELETE, and DDL statements",
            "Use batch transactions for atomic operations",
            "Create and manage local SQLite database files",
        ],
        "prereq": "No external credentials needed — works with local `.db` files",
        "workflow": [
            "Install: `robomotion install sqlite`",
            "Connect: `robomotion sqlite connect` → returns a `conn-id` (provide database file path)",
            "Query: `robomotion sqlite execute_query --conn-id <id>` (with SQL in context)",
            "Disconnect: `robomotion sqlite disconnect --conn-id <id>`",
        ],
    },
    "ssh": {
        "desc": "SSH — execute remote commands and transfer files via SSH/SCP/SFTP. Supports command execution, file upload/download, and tunneling via `robomotion ssh`. Do NOT use for local shell commands, Ansible, or Terraform.",
        "title": "SSH",
        "intro": "The `robomotion ssh` CLI connects to remote servers via SSH for command execution and file transfer. It runs commands on remote hosts, uploads and downloads files via SCP/SFTP, and manages SSH connections.",
        "use_cases": [
            "Execute commands on remote servers via SSH",
            "Upload or download files using SCP/SFTP",
            "Manage SSH connections to multiple hosts",
        ],
        "prereq": "SSH host, username, and key/password configured via Robomotion vault",
        "workflow": [
            "Install: `robomotion install ssh`",
            "Connect: `robomotion ssh ssh_connect` → returns a `client-id`",
            "Execute: `robomotion ssh ssh_execute --client-id <id> --command <cmd>`",
            "Upload: `robomotion ssh ssh_upload --client-id <id> --local-path <file> --remote-path <dest>`",
            "Disconnect: `robomotion ssh ssh_disconnect --client-id <id>`",
        ],
    },
    "stability-ai": {
        "desc": "Stability AI — generate and edit images using Stable Diffusion models. Supports text-to-image, image-to-image, upscaling, and style control via `robomotion stabilityai`. Do NOT use for DALL-E, Leonardo AI, Midjourney, or other image generation services.",
        "title": "Stability AI",
        "intro": "The `robomotion stabilityai` CLI connects to Stability AI for image generation and editing. It generates images from text prompts using Stable Diffusion models, performs image-to-image transformation, upscales images, and supports various style and quality controls.",
        "use_cases": [
            "Generate images from text prompts (text-to-image)",
            "Transform existing images with text guidance (image-to-image)",
            "Upscale images to higher resolutions",
            "Control generation with style presets and parameters",
        ],
        "prereq": "Stability AI API key configured via Robomotion vault",
        "workflow": [
            "Install: `robomotion install stabilityai`",
            "Connect: `robomotion stabilityai stabilityai_connect` → returns a `client-id`",
            "Generate: `robomotion stabilityai stabilityai_generate --client-id <id> --prompt <text>`",
            "Disconnect: `robomotion stabilityai stabilityai_disconnect --client-id <id>`",
        ],
    },
    "stripe-payments": {
        "desc": "Stripe — manage payments, customers, subscriptions, invoices, and products. Supports charge creation, refunds, and billing lifecycle via `robomotion stripe`. Do NOT use for PayPal, Square, or other payment processors.",
        "title": "Stripe Payments",
        "intro": "The `robomotion stripe` CLI connects to Stripe for payment processing and billing management. It creates charges, manages customers and subscriptions, handles invoices and refunds, and manages products and pricing.",
        "use_cases": [
            "Create charges and process payments",
            "Manage customers, subscriptions, and billing",
            "Handle invoices and refunds",
            "Manage products and pricing plans",
        ],
        "prereq": "Stripe API key configured via Robomotion vault",
        "workflow": [
            "Install: `robomotion install stripe`",
            "Connect: `robomotion stripe connect` → returns a `client-id`",
            "Create charge: `robomotion stripe create_charge --client-id <id> --amount <amount> --currency <cur>`",
            "List customers: `robomotion stripe list_customers --client-id <id>`",
            "Disconnect: `robomotion stripe disconnect --client-id <id>`",
        ],
    },
    "supabase": {
        "desc": "Supabase — query tables, manage storage, and call remote procedures on Supabase projects. Supports database CRUD, file storage, and RPC calls via `robomotion supabase`. Do NOT use for Firebase, direct PostgreSQL, or other BaaS platforms.",
        "title": "Supabase",
        "intro": "The `robomotion supabase` CLI connects to Supabase projects for database and storage operations. It queries and modifies table data with filters, manages files in Supabase storage buckets, and calls server-side remote procedure calls (RPCs).",
        "use_cases": [
            "Select, insert, update, or delete rows in Supabase tables with filters",
            "Upload, download, and manage files in Supabase storage",
            "Call remote procedure calls (RPCs) on Supabase",
            "Manage Supabase project connections",
        ],
        "prereq": "Supabase project URL and API key configured via Robomotion vault",
        "workflow": [
            "Install: `robomotion install supabase`",
            "Connect: `robomotion supabase supabase_connect` → returns a `client-id`",
            "Select: `robomotion supabase supabase_select --client-id <id> --table <table> --columns <cols>`",
            "Insert: `robomotion supabase supabase_insert --client-id <id> --table <table> --data <json>`",
            "Disconnect: `robomotion supabase supabase_disconnect --client-id <id>`",
        ],
    },
    "tavily": {
        "desc": "Tavily — AI-powered web search, content extraction, site crawling, and URL mapping. Supports search depth control, domain filtering, and structured content extraction via `robomotion tavily`. Do NOT use for Google Search, Serper, SearchAPI, or Perplexity.",
        "title": "Tavily",
        "intro": "The `robomotion tavily` CLI connects to Tavily for AI-powered web search and content extraction. It searches the web with relevance scoring, extracts content from URLs, crawls websites to discover pages, and maps site structure — all with configurable depth and domain filtering.",
        "use_cases": [
            "Search the web with AI-powered relevance scoring and topic filtering",
            "Extract clean content from one or more URLs",
            "Crawl websites starting from a root URL",
            "Map site structure to discover all URLs",
        ],
        "prereq": "Tavily API key configured via Robomotion vault",
        "workflow": [
            "Install: `robomotion install tavily`",
            "Connect: `robomotion tavily tavily_connect` → returns a `client-id`",
            "Search: `robomotion tavily tavily_search --client-id <id> --search-query <query>`",
            "Extract: `robomotion tavily tavily_extract --client-id <id> --ur-ls <urls>`",
            "Disconnect: `robomotion tavily tavily_disconnect --client-id <id>`",
        ],
    },
    "teams365": {
        "desc": "Microsoft Teams 365 — send messages, manage teams/channels/members, and handle channel conversations via Microsoft Graph API. Supports message threading, channel creation, and member management via `robomotion teams365`. Do NOT use for Slack, Discord, Telegram, or other messaging.",
        "title": "Microsoft Teams 365",
        "intro": "The `robomotion teams365` CLI connects to Microsoft Teams via the Graph API for team collaboration. It sends and lists messages in channels, manages teams and channels, handles members and membership, and supports threaded conversations.",
        "use_cases": [
            "Send messages to Teams channels with threading support",
            "List and manage teams, channels, and members",
            "Create channels and manage team settings",
            "Read channel messages and conversations",
        ],
        "prereq": "Microsoft 365 OAuth2 credentials configured via Robomotion vault",
        "workflow": [
            "Install: `robomotion install teams365`",
            "Connect: `robomotion teams365 teams_connect` → returns a `client-id`",
            "Send message: `robomotion teams365 teams_send_message --client-id <id> --team-id <team> --channel-id <channel> --message <text>`",
            "List teams: `robomotion teams365 teams_list_teams --client-id <id>`",
            "Disconnect: `robomotion teams365 teams_disconnect --client-id <id>`",
        ],
    },
    "telegram": {
        "desc": "Telegram Bot — send messages, photos, documents, manage chats, and handle updates. Supports inline keyboards, chat management, and file operations via `robomotion telegrambot`. Do NOT use for WhatsApp, Slack, Discord, or other messaging platforms.",
        "title": "Telegram Bot",
        "intro": "The `robomotion telegrambot` CLI operates a Telegram bot for messaging and chat interaction. It sends text messages, photos, and documents; manages chats and members; handles inline keyboards; and processes incoming updates.",
        "use_cases": [
            "Send text messages, photos, or documents to Telegram chats",
            "Manage chats, members, and chat settings",
            "Create inline keyboards for interactive bot responses",
            "Listen for and process incoming messages/updates",
        ],
        "prereq": "Telegram bot token configured via Robomotion vault",
        "workflow": [
            "Install: `robomotion install telegrambot`",
            "Connect: `robomotion telegrambot connect` → returns a `client-id`",
            "Send message: `robomotion telegrambot send_message --client-id <id> --chat-id <chat> --text <text>`",
            "Disconnect: `robomotion telegrambot disconnect --client-id <id>`",
        ],
    },
    "tidbcloud": {
        "desc": "TiDB Cloud — execute SQL queries and manage data in distributed TiDB Cloud databases. Supports MySQL-compatible SQL operations via `robomotion tidbcloud`. Do NOT use for MySQL, PostgreSQL, CockroachDB, or other databases.",
        "title": "TiDB Cloud",
        "intro": "The `robomotion tidbcloud` CLI connects to TiDB Cloud (distributed MySQL-compatible database) for SQL operations. It executes queries, runs non-query statements, and manages transactions on TiDB Cloud instances.",
        "use_cases": [
            "Execute SQL SELECT queries on TiDB Cloud databases",
            "Run INSERT, UPDATE, DELETE, and DDL statements",
            "Use batch transactions for atomic operations",
        ],
        "prereq": "TiDB Cloud connection credentials configured via Robomotion vault",
        "workflow": [
            "Install: `robomotion install tidbcloud`",
            "Connect: `robomotion tidbcloud tidbcloud_connect` → returns a `conn-id`",
            "Query: `robomotion tidbcloud tidbcloud_execute_query --conn-id <id>` (with SQL in context)",
            "Disconnect: `robomotion tidbcloud tidbcloud_disconnect --conn-id <id>`",
        ],
    },
    "timescaledb": {
        "desc": "TimescaleDB — manage time-series data with hypertables, time-bucket queries, compression, and continuous aggregates. Supports high-performance time-series analytics via `robomotion timescaledb`. Do NOT use for QuestDB, InfluxDB, or plain PostgreSQL.",
        "title": "TimescaleDB",
        "intro": "The `robomotion timescaledb` CLI connects to TimescaleDB for time-series database operations. It manages hypertables, runs time-bucket aggregation queries, handles data insertion with timestamps, configures compression policies, and manages continuous aggregates.",
        "use_cases": [
            "Create hypertables and insert time-series data",
            "Run time-bucket queries for time-based aggregations",
            "Configure compression policies and continuous aggregates",
            "Execute standard SQL queries on TimescaleDB",
        ],
        "prereq": "TimescaleDB connection credentials configured via Robomotion vault",
        "workflow": [
            "Install: `robomotion install timescaledb`",
            "Connect: `robomotion timescaledb timescaledb_connect` → returns a `conn-id`",
            "Query: `robomotion timescaledb timescaledb_execute_query --conn-id <id>` (with SQL in context)",
            "Disconnect: `robomotion timescaledb timescaledb_disconnect --conn-id <id>`",
        ],
    },
    "travisci": {
        "desc": "Travis CI — manage builds, repositories, jobs, and build logs. Supports build triggering, status monitoring, and repository management via `robomotion travisci`. Do NOT use for GitHub Actions, Jenkins, CircleCI, or other CI/CD platforms.",
        "title": "Travis CI",
        "intro": "The `robomotion travisci` CLI connects to Travis CI for build management and CI/CD operations. It lists and triggers builds, manages repositories, monitors job status, views build logs, and handles build lifecycle operations.",
        "use_cases": [
            "List and trigger builds for repositories",
            "Monitor build and job status in real-time",
            "View build logs and job details",
            "Manage repository settings and activation",
        ],
        "prereq": "Travis CI API token configured via Robomotion vault",
        "workflow": [
            "Install: `robomotion install travisci`",
            "Connect: `robomotion travisci travisci_connect` → returns a `client-id`",
            "List builds: `robomotion travisci travisci_list_builds --client-id <id> --repo <repo>`",
            "Trigger build: `robomotion travisci travisci_trigger_build --client-id <id> --repo <repo>`",
            "Disconnect: `robomotion travisci travisci_disconnect --client-id <id>`",
        ],
    },
    "trello": {
        "desc": "Trello — manage boards, lists, cards, labels, checklists, and members for visual project management. Supports full card lifecycle including attachments, comments, and checklist items via `robomotion trello`. Do NOT use for Jira, ClickUp, Asana, or other PM tools.",
        "title": "Trello",
        "intro": "The `robomotion trello` CLI connects to Trello for visual project management. It manages boards, lists, and cards with full lifecycle support — creating, moving, archiving cards; adding labels, checklists, and attachments; managing members; and handling comments.",
        "use_cases": [
            "Create, update, move, or archive cards across lists and boards",
            "Manage labels, checklists, and checklist items on cards",
            "Add attachments and comments to cards",
            "List and manage boards, lists, and members",
        ],
        "prereq": "Trello API key and token configured via Robomotion vault",
        "workflow": [
            "Install: `robomotion install trello`",
            "Connect: `robomotion trello trello_connect` → returns a `client-id`",
            "Create card: `robomotion trello trello_create_card --client-id <id> --list-id <list> --name <name>`",
            "List cards: `robomotion trello trello_list_cards --client-id <id> --list-id <list>`",
            "Disconnect: `robomotion trello trello_disconnect --client-id <id>`",
        ],
    },
    "twilio": {
        "desc": "Twilio — send SMS/MMS messages, make phone calls, and manage communication resources. Supports messaging, voice calls, and phone number lookup via `robomotion twilio`. Do NOT use for WhatsApp, Telegram, email, or other messaging platforms.",
        "title": "Twilio",
        "intro": "The `robomotion twilio` CLI connects to Twilio for cloud communications. It sends SMS and MMS messages, initiates phone calls, looks up phone number information, and manages Twilio messaging resources.",
        "use_cases": [
            "Send SMS or MMS messages to phone numbers",
            "Initiate and manage phone calls",
            "Look up phone number carrier and format information",
            "Manage messaging services and resources",
        ],
        "prereq": "Twilio Account SID and Auth Token configured via Robomotion vault",
        "workflow": [
            "Install: `robomotion install twilio`",
            "Connect: `robomotion twilio twilio_connect` → returns a `client-id`",
            "Send SMS: `robomotion twilio twilio_send_sms --client-id <id> --to <phone> --body <text>`",
            "Disconnect: `robomotion twilio twilio_disconnect --client-id <id>`",
        ],
    },
    "typeform": {
        "desc": "Typeform — manage forms, collect responses, and analyze submission data. Supports form listing, response retrieval, and form management via `robomotion typeform`. Do NOT use for Google Forms, SurveyMonkey, or other form builders.",
        "title": "Typeform",
        "intro": "The `robomotion typeform` CLI connects to Typeform for form and survey management. It lists forms, retrieves responses with filtering, manages form settings, and handles form lifecycle operations.",
        "use_cases": [
            "List forms and retrieve form details",
            "Collect and filter form responses/submissions",
            "Manage form settings and configuration",
        ],
        "prereq": "Typeform API token configured via Robomotion vault",
        "workflow": [
            "Install: `robomotion install typeform`",
            "Connect: `robomotion typeform typeform_connect` → returns a `client-id`",
            "List forms: `robomotion typeform typeform_list_forms --client-id <id>`",
            "Get responses: `robomotion typeform typeform_list_responses --client-id <id> --form-id <form>`",
            "Disconnect: `robomotion typeform typeform_disconnect --client-id <id>`",
        ],
    },
    "vikunja": {
        "desc": "Vikunja — manage projects, tasks, labels, teams, and task assignments in self-hosted Vikunja instances. Supports full task lifecycle including comments, attachments, and team management via `robomotion vikunja`. Do NOT use for Jira, Trello, ClickUp, or other PM tools.",
        "title": "Vikunja",
        "intro": "The `robomotion vikunja` CLI connects to Vikunja (open-source task management) for project and task operations. It manages projects, tasks with due dates and priorities, labels, teams, task comments, and attachments — supporting the full task lifecycle.",
        "use_cases": [
            "Create, update, or delete tasks with due dates and priorities",
            "Manage projects, labels, and team members",
            "Add comments and attachments to tasks",
            "List and filter tasks across projects",
        ],
        "prereq": "Vikunja instance URL and API token configured via Robomotion vault",
        "workflow": [
            "Install: `robomotion install vikunja`",
            "Connect: `robomotion vikunja vikunja_connect` → returns a `client-id`",
            "List tasks: `robomotion vikunja vikunja_list_tasks --client-id <id> --project-id <proj>`",
            "Create task: `robomotion vikunja vikunja_create_task --client-id <id> --project-id <proj> --title <title>`",
            "Disconnect: `robomotion vikunja vikunja_disconnect --client-id <id>`",
        ],
    },
    "web-scraper": {
        "desc": "DOM Parser web scraper — extract data from HTML pages using CSS selectors and XPath queries. Supports structured data extraction, attribute reading, and HTML parsing via `robomotion domparser`. Do NOT use for Apify, Puppeteer, or browser automation.",
        "title": "Web Scraper (DOM Parser)",
        "intro": "The `robomotion domparser` CLI parses and extracts data from HTML web pages. It loads HTML content, queries elements using CSS selectors or XPath, extracts text and attributes, and outputs structured data from web pages.",
        "use_cases": [
            "Extract data from HTML pages using CSS selectors",
            "Query DOM elements with XPath expressions",
            "Parse HTML content and extract text or attributes",
        ],
        "prereq": "No external credentials needed — works with HTML content/URLs",
        "workflow": [
            "Install: `robomotion install domparser`",
            "Load HTML: `robomotion domparser load --url <url>` or `--html <content>`",
            "Extract: `robomotion domparser query --selector <css>` or `--xpath <xpath>`",
        ],
    },
    "whatsapp": {
        "desc": "WhatsApp Business API — send text messages, media, templates, and interactive messages. Supports message sending, contact management, and template messaging via `robomotion whatsapp`. Do NOT use for Telegram, Twilio SMS, or other messaging services.",
        "title": "WhatsApp Business",
        "intro": "The `robomotion whatsapp` CLI connects to the WhatsApp Business API for messaging operations. It sends text messages, images, documents, and template messages; manages contacts; and handles interactive message types.",
        "use_cases": [
            "Send text, image, document, or video messages via WhatsApp",
            "Send template messages for notifications and alerts",
            "Manage contacts and conversation threads",
        ],
        "prereq": "WhatsApp Business API credentials configured via Robomotion vault",
        "workflow": [
            "Install: `robomotion install whatsapp`",
            "Connect: `robomotion whatsapp connect` → returns a `client-id`",
            "Send message: `robomotion whatsapp send_message --client-id <id> --to <phone> --text <text>`",
            "Disconnect: `robomotion whatsapp disconnect --client-id <id>`",
        ],
    },
    "wikipedia": {
        "desc": "Wikipedia — search articles, retrieve page content, get summaries, and access Wikipedia data. Supports full-text search, page retrieval, and content extraction via `robomotion wikipedia`. Do NOT use for Google Search, web scraping, or other encyclopedias.",
        "title": "Wikipedia",
        "intro": "The `robomotion wikipedia` CLI connects to Wikipedia for article search and content retrieval. It searches for articles, retrieves full page content or summaries, and accesses structured Wikipedia data.",
        "use_cases": [
            "Search Wikipedia for articles by keyword",
            "Retrieve full article content or summaries",
            "Get page metadata and structured data",
        ],
        "prereq": "No external credentials needed — Wikipedia API is public",
        "workflow": [
            "Install: `robomotion install wikipedia`",
            "Connect: `robomotion wikipedia wikipedia_connect` → returns a `client-id`",
            "Search: `robomotion wikipedia wikipedia_search --client-id <id> --query <text>`",
            "Get page: `robomotion wikipedia wikipedia_get_page --client-id <id> --title <title>`",
            "Disconnect: `robomotion wikipedia wikipedia_disconnect --client-id <id>`",
        ],
    },
    "woocommerce": {
        "desc": "WooCommerce — manage products, orders, customers, coupons, and categories in WordPress-based online stores. Supports full ecommerce operations via `robomotion woocommerce`. Do NOT use for Shopify, Magento, or other ecommerce platforms.",
        "title": "WooCommerce",
        "intro": "The `robomotion woocommerce` CLI connects to WooCommerce stores for ecommerce management. It manages products with variations, handles orders and fulfillments, administers customers and coupons, and organizes product categories — covering the full WordPress-based store workflow.",
        "use_cases": [
            "Create, update, list, or delete products and variations",
            "Manage orders — create, update status, and track",
            "Search and manage customer records and coupons",
            "Organize product categories and tags",
        ],
        "prereq": "WooCommerce store URL, consumer key, and consumer secret configured via Robomotion vault",
        "workflow": [
            "Install: `robomotion install woocommerce`",
            "Connect: `robomotion woocommerce woocommerce_connect` → returns a `client-id`",
            "List products: `robomotion woocommerce woocommerce_list_products --client-id <id>`",
            "Create order: `robomotion woocommerce woocommerce_create_order --client-id <id> --line-items <json>`",
            "Disconnect: `robomotion woocommerce woocommerce_disconnect --client-id <id>`",
        ],
    },
    "wordpress": {
        "desc": "WordPress — manage posts, pages, categories, tags, media, users, and comments. Supports content publishing, media uploads, and site administration via `robomotion wordpress`. Do NOT use for Ghost, Medium, or other CMS platforms.",
        "title": "WordPress",
        "intro": "The `robomotion wordpress` CLI connects to WordPress sites via the REST API for content management. It creates and manages posts and pages, handles categories and tags, uploads media, and administers users and comments.",
        "use_cases": [
            "Create, update, list, or delete posts and pages",
            "Manage categories, tags, and media uploads",
            "Administer users and moderate comments",
        ],
        "prereq": "WordPress site URL and API credentials configured via Robomotion vault",
        "workflow": [
            "Install: `robomotion install wordpress`",
            "Connect: `robomotion wordpress wordpress_connect` → returns a `client-id`",
            "Create post: `robomotion wordpress wordpress_create_post --client-id <id> --title <title> --content <html> --status draft`",
            "List posts: `robomotion wordpress wordpress_list_posts --client-id <id>`",
            "Disconnect: `robomotion wordpress wordpress_disconnect --client-id <id>`",
        ],
    },
    "xano": {
        "desc": "Xano — manage database records, search data, and call custom API endpoints on Xano backends. Supports CRUD operations and custom API calls via `robomotion xano`. Do NOT use for Supabase, Firebase, or direct PostgreSQL.",
        "title": "Xano",
        "intro": "The `robomotion xano` CLI connects to Xano (no-code backend platform) for database and API operations. It queries, creates, updates, and deletes records; searches data with filters; and calls custom API endpoints built in Xano.",
        "use_cases": [
            "Query, create, update, or delete records in Xano tables",
            "Search and filter data with conditions",
            "Call custom API endpoints built in Xano",
        ],
        "prereq": "Xano instance URL and API key configured via Robomotion vault",
        "workflow": [
            "Install: `robomotion install xano`",
            "Connect: `robomotion xano xano_connect` → returns a `client-id`",
            "List records: `robomotion xano xano_list --client-id <id> --table <table>`",
            "Create record: `robomotion xano xano_create --client-id <id> --table <table> --data <json>`",
            "Disconnect: `robomotion xano xano_disconnect --client-id <id>`",
        ],
    },
    "zoom": {
        "desc": "Zoom — create and manage meetings, list recordings, and handle meeting participants. Supports meeting scheduling, recording management, and participant tracking via `robomotion zoom`. Do NOT use for Google Meet, Microsoft Teams, or other video platforms.",
        "title": "Zoom",
        "intro": "The `robomotion zoom` CLI connects to Zoom for meeting and recording management. It creates and schedules meetings, lists upcoming and past meetings, manages recordings, handles participants, and supports meeting lifecycle operations.",
        "use_cases": [
            "Create, schedule, update, or delete Zoom meetings",
            "List upcoming meetings and past meeting instances",
            "Manage and download meeting recordings",
            "Track meeting participants and registration",
        ],
        "prereq": "Zoom OAuth2 or JWT credentials configured via Robomotion vault",
        "workflow": [
            "Install: `robomotion install zoom`",
            "Connect: `robomotion zoom zoom_connect` → returns a `client-id`",
            "Create meeting: `robomotion zoom zoom_create_meeting --client-id <id> --topic <title> --start-time <time>`",
            "List meetings: `robomotion zoom zoom_list_meetings --client-id <id>`",
            "Disconnect: `robomotion zoom zoom_disconnect --client-id <id>`",
        ],
    },
}


def rewrite_skill_md(skill_dir, name, data):
    """Rewrite the SKILL.md preserving Commands Reference and Environment sections."""
    md_path = os.path.join(skill_dir, "SKILL.md")
    with open(md_path) as f:
        content = f.read()

    # Extract Commands Reference section (if exists)
    commands_section = ""
    m = re.search(r'(## Commands Reference\n.*?)(?=\n## |\Z)', content, re.DOTALL)
    if m:
        commands_section = m.group(1).rstrip()

    # Extract Environment section (if exists)
    env_section = ""
    m = re.search(r'(## Environment\n.*?)$', content, re.DOTALL)
    if m:
        env_section = m.group(1).rstrip()

    # Build new SKILL.md
    lines = []
    lines.append("---")
    lines.append(f'name: "{name}"')
    lines.append(f'description: "{data["desc"]}"')
    lines.append("---")
    lines.append("")
    lines.append(f"# {data['title']}")
    lines.append("")
    lines.append(data["intro"])
    lines.append("")
    lines.append("## When to use")
    for uc in data["use_cases"]:
        lines.append(f"- {uc}")
    lines.append("")
    lines.append("## Prerequisites")
    lines.append("- `robomotion` CLI installed")
    cli_name = re.search(r'`robomotion (\S+)`', data["desc"])
    if cli_name:
        lines.append(f"- Package installed: `robomotion install {cli_name.group(1)}`")
    lines.append(f"- {data['prereq']}")
    lines.append("")
    lines.append("## Workflow")
    for i, step in enumerate(data["workflow"], 1):
        lines.append(f"{i}. {step}")

    if commands_section:
        lines.append("")
        lines.append(commands_section)

    if env_section:
        lines.append("")
        lines.append(env_section)

    lines.append("")

    with open(md_path, "w") as f:
        f.write("\n".join(lines))


def main():
    # Allow filtering
    filter_names = set()
    if len(sys.argv) > 1 and sys.argv[1] != "--all":
        filter_names = set(sys.argv[1:])

    done = 0
    skipped = 0

    for name, data in sorted(REWRITES.items()):
        if filter_names and name not in filter_names:
            continue

        skill_dir = os.path.join(SKILLS_DIR, name)
        if not os.path.isdir(skill_dir):
            print(f"  SKIP (no dir): {name}")
            skipped += 1
            continue

        rewrite_skill_md(skill_dir, name, data)
        done += 1

    print(f"\nDone: {done} rewritten, {skipped} skipped")

    # Update skills-index.json descriptions
    if not filter_names or filter_names == {"--all"}:
        with open(INDEX_PATH) as f:
            index = json.load(f)

        for entry in index["skills"]:
            if entry["name"] in REWRITES:
                desc_full = REWRITES[entry["name"]]["desc"]
                # Use the part before "Do NOT" for the index description
                short = desc_full.split(". Do NOT")[0] + f" via `robomotion {entry['path'].split('/')[-1]}`." if ". Do NOT" in desc_full else desc_full
                # Actually, extract cli name from description properly
                m = re.search(r'via `robomotion (\S+)`', desc_full)
                if m:
                    cli = m.group(1)
                    short_desc = desc_full.split(". Do NOT")[0]
                    # Remove "via `robomotion xxx`" from the end if present, we'll add it standardized
                    short_desc = re.sub(r'\s*via `robomotion \S+`\.?$', '', short_desc)
                    entry["description"] = f"{short_desc} via the `robomotion {cli}` CLI."
                else:
                    entry["description"] = desc_full.split(". Do NOT")[0] + "."

        with open(INDEX_PATH, "w") as f:
            json.dump(index, f, indent=2)
            f.write("\n")
        print("Updated skills-index.json")


if __name__ == "__main__":
    main()
