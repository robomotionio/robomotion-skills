#!/usr/bin/env python3
"""
Generate Robomotion skill files (SKILL.md + eval-set.json) for all missing packages.
Also updates skills-index.json with new entries.

Usage:
    python3 scripts/generate_skills.py           # Generate all 85 skills
    python3 scripts/generate_skills.py --dry-run  # Preview without writing
"""

import json
import os
import sys

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SKILLS_DIR = os.path.join(REPO_ROOT, "skills")
INDEX_PATH = os.path.join(REPO_ROOT, "skills-index.json")

# ─── All 85 skill definitions ────────────────────────────────────────────────
# Each entry: (skill_name, cli_name, display_name, category, description_verb,
#              use_cases, exclusions, tags, neg_triggers, quality_case)

SKILLS = [
    # ── Tier 1: High Priority (25) ──────────────────────────────────────────
    {
        "name": "dropbox",
        "cli": "dropbox",
        "display": "Dropbox",
        "category": "storage",
        "verb": "upload, download, or manage files in Dropbox",
        "use_cases": [
            "Upload or download files from Dropbox",
            "List files and folders in Dropbox",
            "Share files or manage Dropbox links",
            "Move, copy, or delete files in Dropbox",
        ],
        "exclusions": "Google Drive, S3, OneDrive, or local filesystem operations",
        "tags": ["storage", "dropbox", "cloud", "files"],
        "neg": [
            ("upload a file to Google Drive", False),
            ("store data in an S3 bucket", False),
            ("copy files on the local filesystem", False),
        ],
        "quality": {
            "query": "upload report.pdf to the /reports folder in Dropbox",
            "criteria": [
                "Uses robomotion dropbox upload or file upload command",
                "Specifies the source file path",
                "Specifies the destination folder in Dropbox",
            ],
        },
    },
    {
        "name": "google-calendar",
        "cli": "googlecalendar",
        "display": "Google Calendar",
        "category": "productivity",
        "verb": "create, read, or manage calendar events via Google Calendar",
        "use_cases": [
            "Create or update events in Google Calendar",
            "List upcoming events or check availability",
            "Delete or cancel calendar events",
            "Search for events by date or keyword",
        ],
        "exclusions": "Outlook Calendar, Calendly, Cal.com, or other scheduling platforms",
        "tags": ["google", "calendar", "events", "scheduling", "productivity"],
        "neg": [
            ("schedule a meeting in Outlook Calendar", False),
            ("create a booking on Calendly", False),
            ("send an email via Gmail", False),
        ],
        "quality": {
            "query": "create a Google Calendar event for 'Team Standup' tomorrow at 9am for 30 minutes",
            "criteria": [
                "Uses robomotion googlecalendar create event command",
                "Specifies event title, date, and duration",
                "Includes proper calendar API parameters",
            ],
        },
    },
    {
        "name": "google-slides",
        "cli": "googleslides",
        "display": "Google Slides",
        "category": "productivity",
        "verb": "create, read, or update Google Slides presentations",
        "use_cases": [
            "Create new presentations in Google Slides",
            "Add or update slides in a presentation",
            "Read slide content or metadata",
            "Export presentations to PDF",
        ],
        "exclusions": "PowerPoint, Keynote, or other presentation tools",
        "tags": ["google", "slides", "presentation", "productivity"],
        "neg": [
            ("create a PowerPoint presentation", False),
            ("edit a Google Docs document", False),
            ("upload a file to Google Drive", False),
        ],
        "quality": {
            "query": "create a new Google Slides presentation titled 'Q1 Review'",
            "criteria": [
                "Uses robomotion googleslides create or new presentation command",
                "Specifies the presentation title",
                "References proper Google Slides API parameters",
            ],
        },
    },
    {
        "name": "google-translate",
        "cli": "googletranslate",
        "display": "Google Translate",
        "category": "ai",
        "verb": "translate text between languages via Google Translate",
        "use_cases": [
            "Translate text from one language to another",
            "Detect the language of input text",
            "Batch translate multiple texts",
        ],
        "exclusions": "OpenAI, Claude, or other AI models for translation; DeepL or other translation services",
        "tags": ["google", "translate", "language", "ai", "localization"],
        "neg": [
            ("use OpenAI to translate this text", False),
            ("generate text with Claude", False),
            ("search Google for translations", False),
        ],
        "quality": {
            "query": "translate 'Hello, how are you?' from English to Spanish using Google Translate",
            "criteria": [
                "Uses robomotion googletranslate translate command",
                "Specifies source and target languages",
                "Includes the text to translate",
            ],
        },
    },
    {
        "name": "google-storage",
        "cli": "googlestorage",
        "display": "Google Cloud Storage",
        "category": "storage",
        "verb": "upload, download, or manage files in Google Cloud Storage buckets",
        "use_cases": [
            "Upload or download files from GCS buckets",
            "List objects in a Google Cloud Storage bucket",
            "Create or delete GCS buckets",
            "Manage object metadata and permissions",
        ],
        "exclusions": "S3, Dropbox, Google Drive, or local filesystem operations",
        "tags": ["google", "gcs", "storage", "cloud", "buckets"],
        "neg": [
            ("upload a file to Amazon S3", False),
            ("store files in Google Drive", False),
            ("manage Dropbox files", False),
        ],
        "quality": {
            "query": "upload data.csv to the gs://my-bucket/data/ folder in Google Cloud Storage",
            "criteria": [
                "Uses robomotion googlestorage upload command",
                "Specifies the local file path",
                "Specifies the GCS bucket and destination path",
            ],
        },
    },
    {
        "name": "excel365",
        "cli": "excel365",
        "display": "Microsoft Excel 365",
        "category": "spreadsheet",
        "verb": "read, write, or manage data in Microsoft Excel 365 workbooks",
        "use_cases": [
            "Read or write data in Excel 365 workbooks",
            "Manage worksheets, tables, and ranges",
            "Create or update Excel workbooks in OneDrive/SharePoint",
            "Format cells or apply formulas in Excel 365",
        ],
        "exclusions": "Google Sheets, local Excel files, LibreOffice Calc, or CSV processing",
        "tags": ["microsoft", "excel", "spreadsheet", "office365", "data"],
        "neg": [
            ("update a Google Sheets spreadsheet", False),
            ("read data from a local CSV file", False),
            ("create a Word document", False),
        ],
        "quality": {
            "query": "read all rows from Sheet1 in the Excel 365 workbook 'Sales Report.xlsx'",
            "criteria": [
                "Uses robomotion excel365 read or get range command",
                "Specifies the workbook name",
                "Specifies the worksheet or range",
            ],
        },
    },
    {
        "name": "outlook365",
        "cli": "outlook365",
        "display": "Microsoft Outlook 365",
        "category": "email",
        "verb": "send, read, or manage emails and calendar events via Microsoft Outlook 365",
        "use_cases": [
            "Send emails via Outlook 365",
            "Read or search emails in Outlook mailbox",
            "Manage Outlook calendar events",
            "Organize mail folders and categories",
        ],
        "exclusions": "Gmail, generic SMTP, Yahoo Mail, or non-Microsoft email services",
        "tags": ["microsoft", "outlook", "email", "office365", "calendar"],
        "neg": [
            ("send an email via Gmail", False),
            ("post a message on Slack", False),
            ("manage Google Calendar events", False),
        ],
        "quality": {
            "query": "send an email via Outlook 365 to bob@company.com with subject 'Project Update'",
            "criteria": [
                "Uses robomotion outlook365 send email command",
                "Specifies recipient and subject",
                "Uses proper Outlook 365 API parameters",
            ],
        },
    },
    {
        "name": "onedrive365",
        "cli": "onedrive365",
        "display": "Microsoft OneDrive 365",
        "category": "storage",
        "verb": "upload, download, or manage files in Microsoft OneDrive",
        "use_cases": [
            "Upload or download files from OneDrive",
            "List files and folders in OneDrive",
            "Share files or create sharing links",
            "Move, copy, or delete files in OneDrive",
        ],
        "exclusions": "Google Drive, Dropbox, S3, SharePoint document libraries, or local filesystem",
        "tags": ["microsoft", "onedrive", "storage", "cloud", "files", "office365"],
        "neg": [
            ("upload a file to Google Drive", False),
            ("store files in Dropbox", False),
            ("manage files on the local filesystem", False),
        ],
        "quality": {
            "query": "upload quarterly-report.pdf to the /Reports folder in OneDrive",
            "criteria": [
                "Uses robomotion onedrive365 upload command",
                "Specifies the source file path",
                "Specifies the destination folder in OneDrive",
            ],
        },
    },
    {
        "name": "teams365",
        "cli": "teams365",
        "display": "Microsoft Teams 365",
        "category": "messaging",
        "verb": "send messages or manage channels in Microsoft Teams",
        "use_cases": [
            "Send messages to Teams channels",
            "List teams, channels, or members",
            "Create or manage Teams channels",
            "Reply to messages in Teams conversations",
        ],
        "exclusions": "Slack, Discord, Telegram, or other messaging platforms",
        "tags": ["microsoft", "teams", "messaging", "chat", "office365", "collaboration"],
        "neg": [
            ("send a message on Slack", False),
            ("post in a Discord channel", False),
            ("send an email via Outlook", False),
        ],
        "quality": {
            "query": "send a message to the 'Engineering' channel in Microsoft Teams saying 'Deployment complete'",
            "criteria": [
                "Uses robomotion teams365 send message command",
                "Specifies the channel name",
                "Includes the message text",
            ],
        },
    },
    {
        "name": "word365",
        "cli": "word365",
        "display": "Microsoft Word 365",
        "category": "document",
        "verb": "create, read, or manage Word documents in Microsoft 365",
        "use_cases": [
            "Create new Word documents in OneDrive/SharePoint",
            "List or download Word documents",
            "Export Word documents to PDF",
            "Manage document metadata and properties",
        ],
        "exclusions": "Google Docs, local Word files, LibreOffice Writer, or PDF processing",
        "tags": ["microsoft", "word", "document", "office365", "writing"],
        "neg": [
            ("create a Google Docs document", False),
            ("process a PDF file", False),
            ("edit a local .docx file", False),
        ],
        "quality": {
            "query": "list all Word documents in the /Projects folder on OneDrive using Word 365",
            "criteria": [
                "Uses robomotion word365 list documents command",
                "Specifies the folder path",
                "References Microsoft 365 API parameters",
            ],
        },
    },
    {
        "name": "powerpoint365",
        "cli": "powerpoint365",
        "display": "Microsoft PowerPoint 365",
        "category": "presentation",
        "verb": "create, manage, or export PowerPoint presentations in Microsoft 365",
        "use_cases": [
            "Create presentations from templates",
            "Add slides or replace text/images in presentations",
            "Export presentations to PDF",
            "Duplicate or manage slides in PowerPoint 365",
        ],
        "exclusions": "Google Slides, Keynote, local PowerPoint files, or other presentation tools",
        "tags": ["microsoft", "powerpoint", "presentation", "office365", "slides"],
        "neg": [
            ("create a Google Slides presentation", False),
            ("edit a local .pptx file", False),
            ("create a Word document", False),
        ],
        "quality": {
            "query": "create a PowerPoint 365 presentation from template and replace title text with 'Annual Report'",
            "criteria": [
                "Uses robomotion powerpoint365 create or template command",
                "Specifies template-based creation",
                "Includes text replacement parameters",
            ],
        },
    },
    {
        "name": "sharepoint365",
        "cli": "sharepoint365",
        "display": "Microsoft SharePoint 365",
        "category": "collaboration",
        "verb": "manage sites, lists, and files in Microsoft SharePoint 365",
        "use_cases": [
            "List or search SharePoint sites",
            "Manage SharePoint lists and list items",
            "Upload or download files from SharePoint document libraries",
            "Create or update SharePoint list items",
        ],
        "exclusions": "OneDrive personal storage, Google Drive, Confluence, or other collaboration platforms",
        "tags": ["microsoft", "sharepoint", "collaboration", "office365", "lists", "sites"],
        "neg": [
            ("manage files in OneDrive personal", False),
            ("create a Notion page", False),
            ("upload to Google Drive", False),
        ],
        "quality": {
            "query": "list all items in the 'Tasks' list on the SharePoint site 'Engineering'",
            "criteria": [
                "Uses robomotion sharepoint365 list items command",
                "Specifies the site name",
                "Specifies the list name",
            ],
        },
    },
    {
        "name": "mysql",
        "cli": "mysql",
        "display": "MySQL",
        "category": "database",
        "verb": "query or manage a MySQL database",
        "use_cases": [
            "Execute SQL queries against MySQL",
            "Insert, update, or delete records in MySQL tables",
            "Manage MySQL database connections",
        ],
        "exclusions": "PostgreSQL, MongoDB, SQLite, MSSQL, or other database systems",
        "tags": ["database", "mysql", "sql", "query"],
        "neg": [
            ("query the PostgreSQL database", False),
            ("insert data into MongoDB", False),
            ("send an email", False),
        ],
        "quality": {
            "query": "connect to MySQL and run SELECT * FROM customers WHERE country = 'US'",
            "criteria": [
                "Uses robomotion mysql execute query or similar command",
                "Specifies the SQL query",
                "Includes connection parameters or references credentials",
            ],
        },
    },
    {
        "name": "supabase",
        "cli": "supabase",
        "display": "Supabase",
        "category": "database",
        "verb": "perform database operations, storage, or RPC calls via Supabase",
        "use_cases": [
            "Query or insert data in Supabase tables",
            "Manage files in Supabase storage",
            "Call Supabase remote procedure calls (RPC)",
            "Manage Supabase database connections",
        ],
        "exclusions": "Firebase, PostgreSQL direct connections, MongoDB, or other BaaS platforms",
        "tags": ["database", "supabase", "baas", "storage", "sql"],
        "neg": [
            ("query a PostgreSQL database directly", False),
            ("use Firebase to store data", False),
            ("upload files to S3", False),
        ],
        "quality": {
            "query": "query all active users from the 'users' table in Supabase",
            "criteria": [
                "Uses robomotion supabase select or query command",
                "Specifies the table name",
                "Includes filter criteria",
            ],
        },
    },
    {
        "name": "twilio",
        "cli": "twilio",
        "display": "Twilio",
        "category": "communication",
        "verb": "send SMS, make calls, or manage communications via Twilio",
        "use_cases": [
            "Send SMS or MMS messages via Twilio",
            "Make or manage phone calls",
            "Look up phone number information",
            "Manage Twilio messaging services",
        ],
        "exclusions": "WhatsApp, Telegram, Slack, email, or other messaging platforms",
        "tags": ["communication", "twilio", "sms", "voice", "phone"],
        "neg": [
            ("send a WhatsApp message", False),
            ("send an email via Gmail", False),
            ("post a message on Slack", False),
        ],
        "quality": {
            "query": "send an SMS via Twilio to +1234567890 with message 'Your order has shipped'",
            "criteria": [
                "Uses robomotion twilio send SMS or message command",
                "Specifies the recipient phone number",
                "Includes the message body",
            ],
        },
    },
    {
        "name": "airtable",
        "cli": "airtable",
        "display": "Airtable",
        "category": "database",
        "verb": "read, create, or manage records in Airtable bases",
        "use_cases": [
            "List or search records in Airtable tables",
            "Create, update, or delete Airtable records",
            "Manage Airtable bases and tables",
            "Filter and sort Airtable data",
        ],
        "exclusions": "Google Sheets, Excel, Notion databases, Baserow, or other spreadsheet/database tools",
        "tags": ["database", "airtable", "no-code", "spreadsheet", "records"],
        "neg": [
            ("update a Google Sheets spreadsheet", False),
            ("insert data into a PostgreSQL table", False),
            ("create a Notion database entry", False),
        ],
        "quality": {
            "query": "list all records from the 'Contacts' table in Airtable filtered by Status = 'Active'",
            "criteria": [
                "Uses robomotion airtable list or get records command",
                "Specifies the table name",
                "Includes a filter parameter",
            ],
        },
    },
    {
        "name": "trello",
        "cli": "trello",
        "display": "Trello",
        "category": "project-mgmt",
        "verb": "manage boards, lists, and cards in Trello",
        "use_cases": [
            "Create or update Trello cards",
            "List boards, lists, or cards in Trello",
            "Move cards between lists",
            "Manage Trello board members and labels",
        ],
        "exclusions": "Jira, Asana, ClickUp, Notion, or other project management tools",
        "tags": ["project-management", "trello", "boards", "cards", "kanban"],
        "neg": [
            ("create a Jira issue", False),
            ("manage tasks in ClickUp", False),
            ("send an email notification", False),
        ],
        "quality": {
            "query": "create a new Trello card titled 'Fix login bug' in the 'To Do' list on the 'Development' board",
            "criteria": [
                "Uses robomotion trello create card command",
                "Specifies the card title",
                "Specifies the list and board",
            ],
        },
    },
    {
        "name": "clickup",
        "cli": "clickup",
        "display": "ClickUp",
        "category": "project-mgmt",
        "verb": "manage workspaces, tasks, and projects in ClickUp",
        "use_cases": [
            "Create or update tasks in ClickUp",
            "List spaces, folders, lists, or tasks",
            "Manage task comments and assignments",
            "Organize ClickUp workspaces and projects",
        ],
        "exclusions": "Jira, Trello, Asana, Notion, or other project management tools",
        "tags": ["project-management", "clickup", "tasks", "workspace", "productivity"],
        "neg": [
            ("create a Jira issue", False),
            ("add a card in Trello", False),
            ("update a Google Sheets spreadsheet", False),
        ],
        "quality": {
            "query": "create a new task in ClickUp titled 'Update documentation' in the 'Engineering' list",
            "criteria": [
                "Uses robomotion clickup create task command",
                "Specifies the task name",
                "Specifies the list or space",
            ],
        },
    },
    {
        "name": "shopify",
        "cli": "shopify",
        "display": "Shopify",
        "category": "ecommerce",
        "verb": "manage products, orders, customers, and inventory in Shopify",
        "use_cases": [
            "List, create, or update products in Shopify",
            "Manage orders and fulfillments",
            "Search or manage customer records",
            "Track inventory levels",
        ],
        "exclusions": "WooCommerce, Stripe payments, Amazon, or other ecommerce platforms",
        "tags": ["ecommerce", "shopify", "products", "orders", "store"],
        "neg": [
            ("manage a WooCommerce store", False),
            ("process a Stripe payment", False),
            ("update a CRM contact", False),
        ],
        "quality": {
            "query": "list all products in the Shopify store that are out of stock",
            "criteria": [
                "Uses robomotion shopify list products command",
                "Includes inventory or stock filter",
                "References proper Shopify API parameters",
            ],
        },
    },
    {
        "name": "wordpress",
        "cli": "wordpress",
        "display": "WordPress",
        "category": "cms",
        "verb": "create, manage, or publish content on WordPress sites",
        "use_cases": [
            "Create or update WordPress posts and pages",
            "Manage WordPress categories and tags",
            "Upload media to WordPress",
            "Manage WordPress users and comments",
        ],
        "exclusions": "Ghost, Medium, Webflow, or other CMS platforms",
        "tags": ["cms", "wordpress", "blog", "content", "publishing"],
        "neg": [
            ("publish a post on Ghost", False),
            ("create a web page with HTML", False),
            ("send an email newsletter", False),
        ],
        "quality": {
            "query": "create a new WordPress post titled 'Product Launch Announcement' with status 'draft'",
            "criteria": [
                "Uses robomotion wordpress create post command",
                "Specifies the post title",
                "Sets the post status to draft",
            ],
        },
    },
    {
        "name": "zoom",
        "cli": "zoom",
        "display": "Zoom",
        "category": "communication",
        "verb": "manage meetings and recordings in Zoom",
        "use_cases": [
            "Create or schedule Zoom meetings",
            "List upcoming meetings or past recordings",
            "Manage meeting participants and settings",
            "Download Zoom recordings",
        ],
        "exclusions": "Google Meet, Microsoft Teams, WebEx, or other video conferencing platforms",
        "tags": ["communication", "zoom", "meetings", "video", "conferencing"],
        "neg": [
            ("schedule a meeting in Microsoft Teams", False),
            ("send a message on Slack", False),
            ("create a Google Calendar event", False),
        ],
        "quality": {
            "query": "create a Zoom meeting titled 'Sprint Planning' scheduled for next Monday at 10am",
            "criteria": [
                "Uses robomotion zoom create meeting command",
                "Specifies the meeting title",
                "Includes date and time parameters",
            ],
        },
    },
    {
        "name": "resend",
        "cli": "resend",
        "display": "Resend",
        "category": "email",
        "verb": "send emails and manage contacts via Resend",
        "use_cases": [
            "Send transactional or marketing emails via Resend",
            "Manage email contacts and audiences",
            "Manage email domains and API keys",
            "Track email delivery status",
        ],
        "exclusions": "Gmail, Outlook, SendGrid, Mailchimp, or other email services",
        "tags": ["email", "resend", "transactional", "api", "communication"],
        "neg": [
            ("send an email via Gmail", False),
            ("send an email via Outlook", False),
            ("post a message on Slack", False),
        ],
        "quality": {
            "query": "send an email via Resend to user@example.com with subject 'Welcome' and HTML body",
            "criteria": [
                "Uses robomotion resend send email command",
                "Specifies recipient and subject",
                "Includes email body content",
            ],
        },
    },
    {
        "name": "redis",
        "cli": "redis",
        "display": "Redis",
        "category": "database",
        "verb": "perform key-value operations and pub/sub messaging in Redis",
        "use_cases": [
            "Get, set, or delete keys in Redis",
            "Work with Redis hashes, lists, and sets",
            "Publish or subscribe to Redis channels",
            "Manage Redis database connections",
        ],
        "exclusions": "PostgreSQL, MongoDB, Memcached, or other database systems",
        "tags": ["database", "redis", "cache", "key-value", "pub-sub"],
        "neg": [
            ("query a PostgreSQL database", False),
            ("insert a document into MongoDB", False),
            ("store data in a local file", False),
        ],
        "quality": {
            "query": "connect to Redis and set the key 'session:123' to value 'active' with TTL of 3600",
            "criteria": [
                "Uses robomotion redis set command",
                "Specifies the key and value",
                "Includes TTL or expiration parameter",
            ],
        },
    },
    {
        "name": "sqlite",
        "cli": "sqlite",
        "display": "SQLite",
        "category": "database",
        "verb": "query or manage a SQLite database",
        "use_cases": [
            "Execute SQL queries against SQLite databases",
            "Insert, update, or delete records in SQLite",
            "Create or manage SQLite database files",
        ],
        "exclusions": "PostgreSQL, MySQL, MongoDB, or other database systems",
        "tags": ["database", "sqlite", "sql", "embedded", "local"],
        "neg": [
            ("query a PostgreSQL database", False),
            ("insert data into MySQL", False),
            ("store data in MongoDB", False),
        ],
        "quality": {
            "query": "connect to SQLite database app.db and run SELECT * FROM users WHERE active = 1",
            "criteria": [
                "Uses robomotion sqlite execute query or similar command",
                "Specifies the database file path",
                "Includes the SQL query",
            ],
        },
    },
    {
        "name": "ssh",
        "cli": "ssh",
        "display": "SSH",
        "category": "devops",
        "verb": "execute commands or transfer files via SSH",
        "use_cases": [
            "Execute remote commands via SSH",
            "Transfer files using SCP/SFTP",
            "Manage SSH connections to remote servers",
        ],
        "exclusions": "local shell commands, Ansible, Terraform, or other DevOps tools",
        "tags": ["devops", "ssh", "remote", "server", "shell"],
        "neg": [
            ("run a local bash command", False),
            ("deploy using Cloudflare Workers", False),
            ("manage DNS records", False),
        ],
        "quality": {
            "query": "connect via SSH to server 192.168.1.100 and run 'df -h' to check disk space",
            "criteria": [
                "Uses robomotion ssh execute or run command",
                "Specifies the server host",
                "Includes the command to execute",
            ],
        },
    },

    # ── Tier 2: Medium Priority (27) ────────────────────────────────────────
    {
        "name": "ollama",
        "cli": "ollama",
        "display": "Ollama",
        "category": "ai",
        "verb": "run local AI models via Ollama",
        "use_cases": [
            "Generate text using local LLM models via Ollama",
            "List available Ollama models",
            "Run chat completions with local models",
        ],
        "exclusions": "OpenAI, Claude, Gemini, or other cloud AI services",
        "tags": ["ai", "llm", "ollama", "local", "text-generation"],
        "neg": [
            ("use OpenAI to generate text", False),
            ("call Claude API for summarization", False),
            ("search the web for information", False),
        ],
        "quality": {
            "query": "use Ollama to generate a product description using the llama3 model",
            "criteria": [
                "Uses robomotion ollama generate or chat command",
                "Specifies the model name",
                "Includes the prompt text",
            ],
        },
    },
    {
        "name": "openrouter",
        "cli": "openrouter",
        "display": "OpenRouter",
        "category": "ai",
        "verb": "access AI models via the OpenRouter unified API",
        "use_cases": [
            "Generate text using models through OpenRouter",
            "Access 480+ AI models via a unified API",
            "Run chat completions with streaming support",
            "Generate images via OpenRouter models",
        ],
        "exclusions": "Direct OpenAI, Claude, or Gemini API calls; Ollama local models",
        "tags": ["ai", "llm", "openrouter", "multi-model", "text-generation"],
        "neg": [
            ("use OpenAI API directly", False),
            ("call Claude API for text generation", False),
            ("run a local Ollama model", False),
        ],
        "quality": {
            "query": "use OpenRouter to generate a summary using Claude model through the unified API",
            "criteria": [
                "Uses robomotion openrouter generate or chat command",
                "Specifies a model identifier",
                "Includes the prompt or messages",
            ],
        },
    },
    {
        "name": "replicate-ai",
        "cli": "replicateai",
        "display": "Replicate AI",
        "category": "ai",
        "verb": "run AI models on Replicate",
        "use_cases": [
            "Run AI model predictions on Replicate",
            "Generate images or text using Replicate models",
            "List available models on Replicate",
            "Manage Replicate predictions and outputs",
        ],
        "exclusions": "OpenAI, Fal.ai, Stability AI, or other AI platforms",
        "tags": ["ai", "replicate", "models", "inference", "ml"],
        "neg": [
            ("use OpenAI to generate an image", False),
            ("run a model on Fal.ai", False),
            ("use Stability AI for image generation", False),
        ],
        "quality": {
            "query": "run a Replicate AI prediction using the stable-diffusion model to generate an image",
            "criteria": [
                "Uses robomotion replicateai run or predict command",
                "Specifies the model identifier",
                "Includes input parameters for generation",
            ],
        },
    },
    {
        "name": "perplexity",
        "cli": "perplexity",
        "display": "Perplexity",
        "category": "ai",
        "verb": "perform AI-powered search and chat via Perplexity",
        "use_cases": [
            "Search the web using Perplexity AI",
            "Run chat completions with real-time web data",
            "Get AI-powered answers with citations",
        ],
        "exclusions": "OpenAI, Claude, Google Search, Tavily, or other AI/search services",
        "tags": ["ai", "perplexity", "search", "chat", "web-data"],
        "neg": [
            ("search Google for information", False),
            ("use Tavily for web search", False),
            ("generate text with OpenAI", False),
        ],
        "quality": {
            "query": "use Perplexity to search for 'latest AI developments in 2024' with citations",
            "criteria": [
                "Uses robomotion perplexity search or chat command",
                "Specifies the search query",
                "References real-time web data capabilities",
            ],
        },
    },
    {
        "name": "elevenlabs-ai",
        "cli": "elevenlabsai",
        "display": "ElevenLabs AI",
        "category": "ai",
        "verb": "generate speech or clone voices via ElevenLabs AI",
        "use_cases": [
            "Convert text to natural-sounding speech",
            "Clone or manage voices in ElevenLabs",
            "Generate audio from text with custom voices",
        ],
        "exclusions": "OpenAI TTS, Google Speech, Amazon Polly, or other TTS services",
        "tags": ["ai", "elevenlabs", "tts", "speech", "voice"],
        "neg": [
            ("use OpenAI to generate speech", False),
            ("transcribe audio with Whisper", False),
            ("translate text with Google Translate", False),
        ],
        "quality": {
            "query": "use ElevenLabs to convert 'Welcome to our product demo' to speech with a professional voice",
            "criteria": [
                "Uses robomotion elevenlabsai text to speech or generate command",
                "Specifies the text content",
                "References voice selection or settings",
            ],
        },
    },
    {
        "name": "pinecone",
        "cli": "pinecone",
        "display": "Pinecone",
        "category": "vector-db",
        "verb": "store, query, or manage vector embeddings in Pinecone",
        "use_cases": [
            "Upsert vectors into Pinecone indexes",
            "Query Pinecone for similar vectors",
            "Manage Pinecone indexes and namespaces",
            "Delete vectors from Pinecone",
        ],
        "exclusions": "Qdrant, Weaviate, ChromaDB, or other vector databases",
        "tags": ["vector-db", "pinecone", "embeddings", "similarity-search"],
        "neg": [
            ("store vectors in Qdrant", False),
            ("query a PostgreSQL database", False),
            ("generate embeddings with OpenAI", False),
        ],
        "quality": {
            "query": "query Pinecone for the top 5 vectors similar to the given embedding in the 'products' namespace",
            "criteria": [
                "Uses robomotion pinecone query command",
                "Specifies the embedding vector or reference",
                "Includes top_k or namespace parameters",
            ],
        },
    },
    {
        "name": "qdrant",
        "cli": "qdrant",
        "display": "Qdrant",
        "category": "vector-db",
        "verb": "store, query, or manage vector embeddings in Qdrant",
        "use_cases": [
            "Upsert points into Qdrant collections",
            "Search for similar vectors in Qdrant",
            "Manage Qdrant collections and indexes",
            "Perform filtered vector search",
        ],
        "exclusions": "Pinecone, Weaviate, ChromaDB, or other vector databases",
        "tags": ["vector-db", "qdrant", "embeddings", "similarity-search"],
        "neg": [
            ("store vectors in Pinecone", False),
            ("query a MongoDB database", False),
            ("generate embeddings with OpenAI", False),
        ],
        "quality": {
            "query": "search Qdrant collection 'articles' for vectors similar to the query embedding with limit 10",
            "criteria": [
                "Uses robomotion qdrant search or query command",
                "Specifies the collection name",
                "Includes limit or filter parameters",
            ],
        },
    },
    {
        "name": "sentry",
        "cli": "sentry",
        "display": "Sentry",
        "category": "monitoring",
        "verb": "monitor errors and track issues via Sentry",
        "use_cases": [
            "List or search Sentry issues and events",
            "Manage Sentry projects and alerts",
            "Track error rates and performance metrics",
            "Resolve or assign Sentry issues",
        ],
        "exclusions": "Datadog, Splunk, New Relic, or other monitoring/APM platforms",
        "tags": ["monitoring", "sentry", "errors", "debugging", "observability"],
        "neg": [
            ("monitor metrics with Datadog", False),
            ("search logs in Splunk", False),
            ("create a Jira issue", False),
        ],
        "quality": {
            "query": "list all unresolved Sentry issues for the 'backend-api' project",
            "criteria": [
                "Uses robomotion sentry list issues command",
                "Specifies the project name",
                "Includes status filter for unresolved",
            ],
        },
    },
    {
        "name": "datadog",
        "cli": "datadog",
        "display": "Datadog",
        "category": "monitoring",
        "verb": "monitor infrastructure, submit metrics, and manage alerts via Datadog",
        "use_cases": [
            "Submit custom metrics to Datadog",
            "Query Datadog logs and events",
            "Manage Datadog monitors and alerts",
            "Schedule maintenance downtimes",
        ],
        "exclusions": "Sentry, Splunk, Prometheus, Grafana, or other monitoring platforms",
        "tags": ["monitoring", "datadog", "metrics", "logs", "alerts", "observability"],
        "neg": [
            ("track errors in Sentry", False),
            ("search logs in Splunk", False),
            ("deploy an application", False),
        ],
        "quality": {
            "query": "submit a custom metric 'api.response_time' with value 250 to Datadog",
            "criteria": [
                "Uses robomotion datadog submit metric command",
                "Specifies the metric name and value",
                "Includes proper Datadog API parameters",
            ],
        },
    },
    {
        "name": "monitoring",
        "cli": "monitoring",
        "display": "Monitoring",
        "category": "monitoring",
        "verb": "monitor websites, APIs, and services for uptime and performance",
        "use_cases": [
            "Check website or API uptime status",
            "Monitor HTTP endpoint health",
            "Set up monitoring checks for services",
            "Get alerts for downtime events",
        ],
        "exclusions": "Sentry error tracking, Datadog APM, Splunk log analysis, or cloud-specific monitoring",
        "tags": ["monitoring", "uptime", "health-check", "api", "availability"],
        "neg": [
            ("track application errors in Sentry", False),
            ("submit metrics to Datadog", False),
            ("scrape a website for data", False),
        ],
        "quality": {
            "query": "check the uptime status of https://api.example.com/health using monitoring",
            "criteria": [
                "Uses robomotion monitoring check or ping command",
                "Specifies the URL or endpoint",
                "References health check parameters",
            ],
        },
    },
    {
        "name": "rabbitmq",
        "cli": "rabbitmq",
        "display": "RabbitMQ",
        "category": "messaging",
        "verb": "publish and consume messages via RabbitMQ",
        "use_cases": [
            "Publish messages to RabbitMQ queues or exchanges",
            "Consume messages from RabbitMQ queues",
            "Manage RabbitMQ queues and exchanges",
            "Set up message routing and bindings",
        ],
        "exclusions": "Kafka, Redis pub/sub, SQS, or other message brokers",
        "tags": ["messaging", "rabbitmq", "queue", "broker", "amqp"],
        "neg": [
            ("send a message on Slack", False),
            ("publish to Redis pub/sub", False),
            ("send an email", False),
        ],
        "quality": {
            "query": "publish a message to the RabbitMQ queue 'orders' with payload '{\"orderId\": 123}'",
            "criteria": [
                "Uses robomotion rabbitmq publish command",
                "Specifies the queue name",
                "Includes the message payload",
            ],
        },
    },
    {
        "name": "oracle",
        "cli": "oracle",
        "display": "Oracle",
        "category": "database",
        "verb": "query or manage an Oracle database",
        "use_cases": [
            "Execute SQL queries against Oracle databases",
            "Insert, update, or delete records in Oracle",
            "Manage Oracle database connections",
        ],
        "exclusions": "PostgreSQL, MySQL, MSSQL, MongoDB, or other database systems",
        "tags": ["database", "oracle", "sql", "enterprise"],
        "neg": [
            ("query a PostgreSQL database", False),
            ("insert data into MySQL", False),
            ("store data in MongoDB", False),
        ],
        "quality": {
            "query": "connect to Oracle and run SELECT * FROM employees WHERE department_id = 10",
            "criteria": [
                "Uses robomotion oracle execute query or similar command",
                "Specifies the SQL query",
                "Includes connection parameters or references credentials",
            ],
        },
    },
    {
        "name": "mssql",
        "cli": "mssql",
        "display": "Microsoft SQL Server",
        "category": "database",
        "verb": "query or manage a Microsoft SQL Server database",
        "use_cases": [
            "Execute SQL queries against MSSQL databases",
            "Insert, update, or delete records in SQL Server",
            "Manage MSSQL database connections",
        ],
        "exclusions": "PostgreSQL, MySQL, Oracle, MongoDB, or other database systems",
        "tags": ["database", "mssql", "sql-server", "microsoft", "sql"],
        "neg": [
            ("query a PostgreSQL database", False),
            ("insert data into MySQL", False),
            ("manage MongoDB collections", False),
        ],
        "quality": {
            "query": "connect to MSSQL and run SELECT TOP 100 * FROM orders WHERE status = 'pending'",
            "criteria": [
                "Uses robomotion mssql execute query or similar command",
                "Specifies the SQL query",
                "Includes connection parameters or references credentials",
            ],
        },
    },
    {
        "name": "onenote365",
        "cli": "onenote365",
        "display": "Microsoft OneNote 365",
        "category": "productivity",
        "verb": "manage notebooks, sections, and pages in Microsoft OneNote 365",
        "use_cases": [
            "Create or read OneNote pages and sections",
            "List notebooks and section groups",
            "Update page content in OneNote",
            "Manage OneNote notebooks in OneDrive/SharePoint",
        ],
        "exclusions": "Notion, Evernote, Google Keep, or other note-taking apps",
        "tags": ["microsoft", "onenote", "notes", "office365", "productivity"],
        "neg": [
            ("create a Notion page", False),
            ("write a Google Docs document", False),
            ("send an email via Outlook", False),
        ],
        "quality": {
            "query": "create a new page in OneNote 365 notebook 'Work Notes' section 'Meeting Minutes' with title 'Sprint Review'",
            "criteria": [
                "Uses robomotion onenote365 create page command",
                "Specifies the notebook and section",
                "Includes the page title",
            ],
        },
    },
    {
        "name": "google-forms",
        "cli": "googleforms",
        "display": "Google Forms",
        "category": "productivity",
        "verb": "create, read, or manage Google Forms and responses",
        "use_cases": [
            "Create new Google Forms",
            "Read form responses and submissions",
            "Manage form questions and settings",
            "List available forms",
        ],
        "exclusions": "Typeform, SurveyMonkey, Microsoft Forms, or other form builders",
        "tags": ["google", "forms", "survey", "responses", "productivity"],
        "neg": [
            ("create a Typeform survey", False),
            ("read Google Sheets data", False),
            ("send a Google Calendar invite", False),
        ],
        "quality": {
            "query": "list all responses from the Google Form with ID 'abc123'",
            "criteria": [
                "Uses robomotion googleforms list responses command",
                "Specifies the form ID",
                "References response data retrieval",
            ],
        },
    },
    {
        "name": "google-maps",
        "cli": "googlemaps",
        "display": "Google Maps",
        "category": "location",
        "verb": "geocode addresses, find places, or get directions via Google Maps",
        "use_cases": [
            "Geocode addresses to coordinates",
            "Search for places or businesses",
            "Get directions or distance between locations",
            "Reverse geocode coordinates to addresses",
        ],
        "exclusions": "OpenStreetMap, Mapbox, HERE Maps, or other mapping services",
        "tags": ["google", "maps", "geocoding", "places", "directions", "location"],
        "neg": [
            ("search the web for a location", False),
            ("check the weather for a city", False),
            ("send a message with coordinates", False),
        ],
        "quality": {
            "query": "use Google Maps to geocode the address '1600 Amphitheatre Parkway, Mountain View, CA'",
            "criteria": [
                "Uses robomotion googlemaps geocode command",
                "Specifies the address string",
                "References latitude and longitude output",
            ],
        },
    },
    {
        "name": "google-speech",
        "cli": "googlespeech",
        "display": "Google Speech",
        "category": "ai",
        "verb": "transcribe audio or synthesize speech via Google Speech",
        "use_cases": [
            "Transcribe audio files to text",
            "Convert text to speech",
            "Recognize speech in multiple languages",
        ],
        "exclusions": "OpenAI Whisper, ElevenLabs, Amazon Polly, or other speech services",
        "tags": ["google", "speech", "transcription", "tts", "stt", "ai"],
        "neg": [
            ("transcribe audio with OpenAI Whisper", False),
            ("generate speech with ElevenLabs", False),
            ("translate text with Google Translate", False),
        ],
        "quality": {
            "query": "transcribe the audio file recording.wav to text using Google Speech",
            "criteria": [
                "Uses robomotion googlespeech transcribe or recognize command",
                "Specifies the audio file path",
                "References language or transcription settings",
            ],
        },
    },
    {
        "name": "docusign",
        "cli": "docusign",
        "display": "DocuSign",
        "category": "document",
        "verb": "send documents for signature and manage envelopes via DocuSign",
        "use_cases": [
            "Send documents for electronic signature",
            "Manage DocuSign envelopes and templates",
            "Track signature status and recipients",
            "Create signing workflows",
        ],
        "exclusions": "Adobe Sign, HelloSign, PandaDoc, or other e-signature platforms",
        "tags": ["document", "docusign", "esignature", "contracts", "signing"],
        "neg": [
            ("create a PDF document", False),
            ("send an email with an attachment", False),
            ("manage Google Docs", False),
        ],
        "quality": {
            "query": "send a contract.pdf via DocuSign to signer@company.com for electronic signature",
            "criteria": [
                "Uses robomotion docusign send or create envelope command",
                "Specifies the document and recipient",
                "References signature request parameters",
            ],
        },
    },
    {
        "name": "woocommerce",
        "cli": "woocommerce",
        "display": "WooCommerce",
        "category": "ecommerce",
        "verb": "manage products, orders, and customers in WooCommerce stores",
        "use_cases": [
            "List or create products in WooCommerce",
            "Manage orders and order status",
            "Search or update customer records",
            "Manage coupons and discounts",
        ],
        "exclusions": "Shopify, Magento, BigCommerce, or other ecommerce platforms",
        "tags": ["ecommerce", "woocommerce", "wordpress", "products", "orders", "store"],
        "neg": [
            ("manage a Shopify store", False),
            ("process a Stripe payment", False),
            ("create a WordPress post", False),
        ],
        "quality": {
            "query": "list all pending orders in the WooCommerce store",
            "criteria": [
                "Uses robomotion woocommerce list orders command",
                "Includes status filter for pending",
                "References WooCommerce API parameters",
            ],
        },
    },
    {
        "name": "calendly",
        "cli": "calendly",
        "display": "Calendly",
        "category": "scheduling",
        "verb": "manage scheduling events and bookings via Calendly",
        "use_cases": [
            "List scheduled events and invitees",
            "Manage Calendly event types",
            "Check availability and booking status",
            "Cancel or reschedule events",
        ],
        "exclusions": "Cal.com, Google Calendar, Outlook Calendar, or other scheduling platforms",
        "tags": ["scheduling", "calendly", "booking", "events", "meetings"],
        "neg": [
            ("schedule a meeting on Cal.com", False),
            ("create a Google Calendar event", False),
            ("send a Zoom meeting invite", False),
        ],
        "quality": {
            "query": "list all upcoming Calendly events for the current user",
            "criteria": [
                "Uses robomotion calendly list events command",
                "Specifies upcoming or date range filter",
                "References user or organization scope",
            ],
        },
    },
    {
        "name": "calcom",
        "cli": "calcom",
        "display": "Cal.com",
        "category": "scheduling",
        "verb": "manage bookings, events, and availability via Cal.com",
        "use_cases": [
            "List or create bookings on Cal.com",
            "Manage event types and schedules",
            "Check availability slots",
            "Cancel or reschedule bookings",
        ],
        "exclusions": "Calendly, Google Calendar, Outlook Calendar, or other scheduling platforms",
        "tags": ["scheduling", "calcom", "booking", "events", "availability"],
        "neg": [
            ("create a Calendly event", False),
            ("manage Google Calendar events", False),
            ("send an email invitation", False),
        ],
        "quality": {
            "query": "list all bookings on Cal.com for the next 7 days",
            "criteria": [
                "Uses robomotion calcom list bookings command",
                "Specifies a date range filter",
                "References proper Cal.com API parameters",
            ],
        },
    },
    {
        "name": "pcloud",
        "cli": "pcloud",
        "display": "pCloud",
        "category": "storage",
        "verb": "upload, download, or manage files in pCloud",
        "use_cases": [
            "Upload or download files from pCloud",
            "List files and folders in pCloud",
            "Manage file sharing and links",
            "Create or delete folders in pCloud",
        ],
        "exclusions": "Dropbox, Google Drive, OneDrive, S3, or other cloud storage",
        "tags": ["storage", "pcloud", "cloud", "files"],
        "neg": [
            ("upload a file to Dropbox", False),
            ("store files in Google Drive", False),
            ("manage S3 buckets", False),
        ],
        "quality": {
            "query": "upload backup.zip to the /backups folder in pCloud",
            "criteria": [
                "Uses robomotion pcloud upload command",
                "Specifies the source file",
                "Specifies the destination folder",
            ],
        },
    },
    {
        "name": "nextcloud",
        "cli": "nextcloud",
        "display": "NextCloud",
        "category": "storage",
        "verb": "manage files, sharing, and users in NextCloud",
        "use_cases": [
            "Upload or download files from NextCloud",
            "List files and manage folders",
            "Share files and manage permissions",
            "Administer NextCloud users",
        ],
        "exclusions": "Dropbox, Google Drive, OneDrive, or other cloud storage platforms",
        "tags": ["storage", "nextcloud", "self-hosted", "files", "sharing"],
        "neg": [
            ("upload a file to Google Drive", False),
            ("manage Dropbox files", False),
            ("store data in S3", False),
        ],
        "quality": {
            "query": "list all files in the /documents folder on NextCloud",
            "criteria": [
                "Uses robomotion nextcloud list files command",
                "Specifies the folder path",
                "References NextCloud API parameters",
            ],
        },
    },
    {
        "name": "tavily",
        "cli": "tavily",
        "display": "Tavily",
        "category": "search",
        "verb": "search the web, extract content, and crawl sites via Tavily",
        "use_cases": [
            "Search the web using Tavily AI-powered search",
            "Extract content from web pages",
            "Crawl websites and generate site maps",
            "Get search results with relevance scoring",
        ],
        "exclusions": "Google Search, Serper, SearchAPI, Perplexity, or other search services",
        "tags": ["search", "tavily", "web", "ai-search", "extraction"],
        "neg": [
            ("search Google using Serper", False),
            ("use Perplexity for AI search", False),
            ("scrape a website with dom parser", False),
        ],
        "quality": {
            "query": "use Tavily to search for 'best practices for microservices architecture'",
            "criteria": [
                "Uses robomotion tavily search command",
                "Specifies the search query",
                "References search depth or result parameters",
            ],
        },
    },
    {
        "name": "searchapi",
        "cli": "searchapi",
        "display": "SearchAPI",
        "category": "search",
        "verb": "search Google, Bing, YouTube, and more via SearchAPI",
        "use_cases": [
            "Search Google, Bing, or YouTube via SearchAPI",
            "Get Google Maps, News, or Scholar results",
            "Search for images, shopping results, or videos",
        ],
        "exclusions": "Serper, Tavily, direct Google API, or other search services",
        "tags": ["search", "searchapi", "google", "bing", "youtube", "web"],
        "neg": [
            ("search using Serper", False),
            ("use Tavily for web search", False),
            ("use Perplexity AI for search", False),
        ],
        "quality": {
            "query": "use SearchAPI to search Google for 'machine learning tutorials' and get the top 10 results",
            "criteria": [
                "Uses robomotion searchapi search command",
                "Specifies the search query",
                "Includes result limit or engine parameter",
            ],
        },
    },
    {
        "name": "serper",
        "cli": "serper",
        "display": "Serper",
        "category": "search",
        "verb": "search Google via the Serper API",
        "use_cases": [
            "Search Google for web results via Serper",
            "Get image, video, news, or shopping results",
            "Search Google Scholar or Google Places",
        ],
        "exclusions": "SearchAPI, Tavily, direct Google API, or other search services",
        "tags": ["search", "serper", "google", "web", "images", "news"],
        "neg": [
            ("search using SearchAPI", False),
            ("use Tavily for web search", False),
            ("query a database", False),
        ],
        "quality": {
            "query": "use Serper to search Google for 'climate change statistics 2024'",
            "criteria": [
                "Uses robomotion serper search command",
                "Specifies the search query",
                "References search type or result format",
            ],
        },
    },
    {
        "name": "stability-ai",
        "cli": "stabilityai",
        "display": "Stability AI",
        "category": "ai",
        "verb": "generate images via Stability AI models",
        "use_cases": [
            "Generate images from text prompts",
            "Create visual art using Stable Diffusion",
            "Generate image variations or edits",
        ],
        "exclusions": "DALL-E/OpenAI images, Midjourney, Leonardo AI, or other image generation services",
        "tags": ["ai", "stability-ai", "image-generation", "stable-diffusion"],
        "neg": [
            ("generate an image with DALL-E", False),
            ("use Leonardo AI for image creation", False),
            ("edit a photo with image processing", False),
        ],
        "quality": {
            "query": "use Stability AI to generate an image of 'a futuristic city at sunset' in 1024x1024",
            "criteria": [
                "Uses robomotion stabilityai generate image command",
                "Specifies the text prompt",
                "Includes size or quality parameters",
            ],
        },
    },

    # ── Tier 3: Lower Priority (33) ─────────────────────────────────────────
    {
        "name": "baserow",
        "cli": "baserow",
        "display": "Baserow",
        "category": "database",
        "verb": "manage rows, tables, and fields in Baserow",
        "use_cases": [
            "List, create, or update rows in Baserow tables",
            "Manage Baserow tables and fields",
            "Filter and sort Baserow data",
        ],
        "exclusions": "Airtable, NocoDB, Google Sheets, or other no-code database platforms",
        "tags": ["database", "baserow", "no-code", "open-source", "tables"],
        "neg": [
            ("manage Airtable records", False),
            ("update NocoDB tables", False),
            ("query a PostgreSQL database", False),
        ],
        "quality": {
            "query": "list all rows from the 'Projects' table in Baserow",
            "criteria": [
                "Uses robomotion baserow list rows command",
                "Specifies the table name",
                "References Baserow API parameters",
            ],
        },
    },
    {
        "name": "nocodb",
        "cli": "nocodb",
        "display": "NocoDB",
        "category": "database",
        "verb": "manage tables, records, and databases in NocoDB",
        "use_cases": [
            "List, create, or update records in NocoDB",
            "Manage NocoDB tables and databases",
            "Filter and search NocoDB data",
        ],
        "exclusions": "Airtable, Baserow, Google Sheets, or other no-code database platforms",
        "tags": ["database", "nocodb", "no-code", "open-source", "airtable-alternative"],
        "neg": [
            ("manage Airtable records", False),
            ("update Baserow tables", False),
            ("insert into PostgreSQL", False),
        ],
        "quality": {
            "query": "create a new record in the NocoDB 'Customers' table with name 'Acme Corp'",
            "criteria": [
                "Uses robomotion nocodb create record command",
                "Specifies the table name",
                "Includes field values",
            ],
        },
    },
    {
        "name": "seatable",
        "cli": "seatable",
        "display": "SeaTable",
        "category": "database",
        "verb": "manage rows, tables, and bases in SeaTable",
        "use_cases": [
            "List, create, or update rows in SeaTable",
            "Manage SeaTable tables and bases",
            "Filter and search SeaTable data",
        ],
        "exclusions": "Airtable, Baserow, NocoDB, or other no-code database platforms",
        "tags": ["database", "seatable", "no-code", "tables", "collaboration"],
        "neg": [
            ("manage Airtable records", False),
            ("update Baserow tables", False),
            ("manage Google Sheets data", False),
        ],
        "quality": {
            "query": "list all rows from the 'Inventory' table in SeaTable",
            "criteria": [
                "Uses robomotion seatable list rows command",
                "Specifies the table name",
                "References SeaTable API parameters",
            ],
        },
    },
    {
        "name": "odoo",
        "cli": "odoo",
        "display": "Odoo",
        "category": "erp",
        "verb": "manage contacts, sales, invoices, and records in Odoo ERP",
        "use_cases": [
            "Manage contacts and leads in Odoo",
            "Create or update sales orders and invoices",
            "Manage products and inventory",
            "Query any Odoo model via XML-RPC",
        ],
        "exclusions": "SAP, NetSuite, Salesforce, or other ERP/CRM platforms",
        "tags": ["erp", "odoo", "crm", "sales", "invoices", "open-source"],
        "neg": [
            ("manage HubSpot contacts", False),
            ("create a Jira ticket", False),
            ("process a Stripe payment", False),
        ],
        "quality": {
            "query": "list all open sales orders in Odoo for customer 'Acme Corp'",
            "criteria": [
                "Uses robomotion odoo search or list command",
                "Specifies the model (sale.order)",
                "Includes a customer filter",
            ],
        },
    },
    {
        "name": "mautic",
        "cli": "mautic",
        "display": "Mautic",
        "category": "marketing",
        "verb": "manage contacts, campaigns, and segments in Mautic",
        "use_cases": [
            "Manage marketing contacts and companies",
            "Create or manage marketing campaigns",
            "Manage segments and lead scoring",
            "Track marketing engagement",
        ],
        "exclusions": "Mailchimp, HubSpot Marketing, SendGrid, or other marketing platforms",
        "tags": ["marketing", "mautic", "automation", "campaigns", "contacts", "open-source"],
        "neg": [
            ("manage HubSpot contacts", False),
            ("send an email via Resend", False),
            ("create a WordPress post", False),
        ],
        "quality": {
            "query": "list all contacts in the 'Active Leads' segment in Mautic",
            "criteria": [
                "Uses robomotion mautic list contacts command",
                "Specifies the segment filter",
                "References Mautic API parameters",
            ],
        },
    },
    {
        "name": "ghost",
        "cli": "ghost",
        "display": "Ghost",
        "category": "cms",
        "verb": "manage posts, pages, members, and tags in Ghost CMS",
        "use_cases": [
            "Create or update Ghost blog posts",
            "Manage Ghost pages and tags",
            "Manage Ghost members and subscriptions",
            "Publish or schedule content",
        ],
        "exclusions": "WordPress, Medium, Webflow, or other CMS platforms",
        "tags": ["cms", "ghost", "blog", "publishing", "content"],
        "neg": [
            ("create a WordPress post", False),
            ("publish on Medium", False),
            ("send a newsletter email", False),
        ],
        "quality": {
            "query": "create a new Ghost blog post titled 'Getting Started with AI' with status 'draft'",
            "criteria": [
                "Uses robomotion ghost create post command",
                "Specifies the post title",
                "Includes the status parameter",
            ],
        },
    },
    {
        "name": "fibery",
        "cli": "fibery",
        "display": "Fibery",
        "category": "productivity",
        "verb": "manage entities, databases, and documents in Fibery",
        "use_cases": [
            "Create or update entities in Fibery",
            "Manage Fibery databases and spaces",
            "Search and filter Fibery data",
            "Manage documents and views",
        ],
        "exclusions": "Notion, ClickUp, Monday.com, or other productivity platforms",
        "tags": ["productivity", "fibery", "workspace", "databases", "entities"],
        "neg": [
            ("create a Notion page", False),
            ("manage ClickUp tasks", False),
            ("update a Google Sheets spreadsheet", False),
        ],
        "quality": {
            "query": "create a new 'Feature' entity in Fibery with name 'Dark Mode Support'",
            "criteria": [
                "Uses robomotion fibery create entity command",
                "Specifies the entity type",
                "Includes the entity name",
            ],
        },
    },
    {
        "name": "homeassistant",
        "cli": "homeassistant",
        "display": "Home Assistant",
        "category": "iot",
        "verb": "control smart home devices and services via Home Assistant",
        "use_cases": [
            "Control smart home devices and lights",
            "Get device states and sensor readings",
            "Call Home Assistant services",
            "Monitor events and automations",
        ],
        "exclusions": "AWS IoT, Google Home direct API, SmartThings, or other IoT platforms",
        "tags": ["iot", "homeassistant", "smart-home", "automation", "devices"],
        "neg": [
            ("deploy a cloud function", False),
            ("manage a database", False),
            ("send a notification", False),
        ],
        "quality": {
            "query": "turn on the living room lights using Home Assistant",
            "criteria": [
                "Uses robomotion homeassistant call service or turn on command",
                "Specifies the device or entity ID",
                "References the correct service domain",
            ],
        },
    },
    {
        "name": "instantly",
        "cli": "instantly",
        "display": "Instantly",
        "category": "email",
        "verb": "manage cold email campaigns, leads, and analytics via Instantly",
        "use_cases": [
            "Manage cold email campaigns",
            "Add or manage leads and contacts",
            "Track email campaign analytics",
            "Manage email accounts and sending",
        ],
        "exclusions": "Lemlist, Mailchimp, Gmail, Outlook, or other email/outreach platforms",
        "tags": ["email", "instantly", "cold-email", "outreach", "campaigns"],
        "neg": [
            ("send an email via Gmail", False),
            ("manage Lemlist campaigns", False),
            ("create a Mautic campaign", False),
        ],
        "quality": {
            "query": "list all active campaigns in Instantly with their open rates",
            "criteria": [
                "Uses robomotion instantly list campaigns command",
                "Includes status filter for active",
                "References analytics or metrics",
            ],
        },
    },
    {
        "name": "lemlist",
        "cli": "lemlist",
        "display": "Lemlist",
        "category": "email",
        "verb": "manage email outreach campaigns and leads via Lemlist",
        "use_cases": [
            "Manage email outreach campaigns",
            "Add or manage leads in Lemlist",
            "Track campaign performance",
            "Manage email sequences",
        ],
        "exclusions": "Instantly, Mailchimp, Gmail, Outlook, or other email/outreach platforms",
        "tags": ["email", "lemlist", "outreach", "cold-email", "campaigns"],
        "neg": [
            ("send an email via Gmail", False),
            ("manage Instantly campaigns", False),
            ("send an email via Resend", False),
        ],
        "quality": {
            "query": "add a new lead to the Lemlist campaign 'Q1 Outreach' with email john@example.com",
            "criteria": [
                "Uses robomotion lemlist add lead command",
                "Specifies the campaign name",
                "Includes the lead email",
            ],
        },
    },
    {
        "name": "dropcontact",
        "cli": "dropcontact",
        "display": "Dropcontact",
        "category": "enrichment",
        "verb": "enrich and verify contact information via Dropcontact",
        "use_cases": [
            "Enrich contact data with company information",
            "Verify and clean email addresses",
            "Find professional email addresses",
        ],
        "exclusions": "Apollo enrichment, Clearbit, Hunter.io, or other data enrichment services",
        "tags": ["enrichment", "dropcontact", "contacts", "email-verification", "data"],
        "neg": [
            ("search leads with Apollo", False),
            ("verify emails with MillionVerifier", False),
            ("manage HubSpot contacts", False),
        ],
        "quality": {
            "query": "enrich the contact john.doe@company.com using Dropcontact to get company details",
            "criteria": [
                "Uses robomotion dropcontact enrich command",
                "Specifies the email or contact data",
                "References enrichment output fields",
            ],
        },
    },
    {
        "name": "phantombuster",
        "cli": "phantombuster",
        "display": "Phantombuster",
        "category": "automation",
        "verb": "run web scraping and automation Phantoms via Phantombuster",
        "use_cases": [
            "Run Phantombuster Phantoms for data extraction",
            "Automate web scraping tasks",
            "Manage and schedule Phantom executions",
            "Extract data from social media profiles",
        ],
        "exclusions": "Apify, Selenium, Puppeteer, or direct web scraping tools",
        "tags": ["automation", "phantombuster", "scraping", "data-extraction", "phantoms"],
        "neg": [
            ("run an Apify actor", False),
            ("scrape a page with dom parser", False),
            ("search the web with Google", False),
        ],
        "quality": {
            "query": "launch the Phantombuster LinkedIn scraper Phantom to extract company data",
            "criteria": [
                "Uses robomotion phantombuster launch or run command",
                "Specifies the Phantom name or ID",
                "Includes input parameters",
            ],
        },
    },
    {
        "name": "millionverifier",
        "cli": "millionverifier",
        "display": "MillionVerifier",
        "category": "email",
        "verb": "verify email addresses via MillionVerifier",
        "use_cases": [
            "Verify single email addresses",
            "Bulk verify email lists",
            "Check email deliverability status",
        ],
        "exclusions": "Dropcontact, ZeroBounce, NeverBounce, or other email verification services",
        "tags": ["email", "millionverifier", "verification", "deliverability"],
        "neg": [
            ("enrich contacts with Dropcontact", False),
            ("send an email via Gmail", False),
            ("manage email campaigns", False),
        ],
        "quality": {
            "query": "verify the email address user@example.com using MillionVerifier",
            "criteria": [
                "Uses robomotion millionverifier verify command",
                "Specifies the email address",
                "References verification result status",
            ],
        },
    },
    {
        "name": "splunk",
        "cli": "splunk",
        "display": "Splunk",
        "category": "monitoring",
        "verb": "search logs, collect events, and manage indexes in Splunk",
        "use_cases": [
            "Search and query Splunk logs",
            "Submit events to Splunk indexes",
            "Manage Splunk indexes and saved searches",
            "Collect and analyze log data",
        ],
        "exclusions": "Datadog, Sentry, ELK Stack, or other log management platforms",
        "tags": ["monitoring", "splunk", "logs", "search", "analytics", "siem"],
        "neg": [
            ("submit metrics to Datadog", False),
            ("track errors in Sentry", False),
            ("query a database", False),
        ],
        "quality": {
            "query": "search Splunk for all error events in the 'web-app' index from the last 24 hours",
            "criteria": [
                "Uses robomotion splunk search command",
                "Specifies the index and query",
                "Includes a time range filter",
            ],
        },
    },
    {
        "name": "rundeck",
        "cli": "rundeck",
        "display": "Rundeck",
        "category": "devops",
        "verb": "execute automation jobs and manage projects in Rundeck",
        "use_cases": [
            "Execute Rundeck automation jobs",
            "List or manage Rundeck projects",
            "Monitor job execution status",
            "Schedule and trigger runbook automations",
        ],
        "exclusions": "Ansible, Jenkins, GitHub Actions, or other CI/CD and automation tools",
        "tags": ["devops", "rundeck", "automation", "jobs", "runbook"],
        "neg": [
            ("run a GitHub Actions workflow", False),
            ("deploy with Cloudflare", False),
            ("execute an SSH command", False),
        ],
        "quality": {
            "query": "execute the Rundeck job 'deploy-staging' in the 'web-services' project",
            "criteria": [
                "Uses robomotion rundeck execute or run job command",
                "Specifies the job name",
                "Specifies the project",
            ],
        },
    },
    {
        "name": "questdb",
        "cli": "questdb",
        "display": "QuestDB",
        "category": "database",
        "verb": "query and insert data in QuestDB time-series database",
        "use_cases": [
            "Execute SQL queries against QuestDB",
            "Insert time-series data into QuestDB",
            "Manage QuestDB tables and connections",
        ],
        "exclusions": "TimescaleDB, InfluxDB, PostgreSQL, or other time-series databases",
        "tags": ["database", "questdb", "time-series", "sql", "analytics"],
        "neg": [
            ("query TimescaleDB", False),
            ("insert data into PostgreSQL", False),
            ("store data in ClickHouse", False),
        ],
        "quality": {
            "query": "query QuestDB for the average temperature over the last hour from the 'sensors' table",
            "criteria": [
                "Uses robomotion questdb query or select command",
                "Specifies a SQL query with aggregation",
                "Includes a time-based filter",
            ],
        },
    },
    {
        "name": "timescaledb",
        "cli": "timescaledb",
        "display": "TimescaleDB",
        "category": "database",
        "verb": "manage time-series data, hypertables, and compression in TimescaleDB",
        "use_cases": [
            "Execute time-series queries against TimescaleDB",
            "Manage hypertables and continuous aggregates",
            "Insert time-series data with time-bucket queries",
            "Manage compression policies",
        ],
        "exclusions": "QuestDB, InfluxDB, PostgreSQL without TimescaleDB, or other databases",
        "tags": ["database", "timescaledb", "time-series", "hypertable", "sql"],
        "neg": [
            ("query QuestDB", False),
            ("insert data into PostgreSQL", False),
            ("store data in ClickHouse", False),
        ],
        "quality": {
            "query": "query TimescaleDB for hourly average CPU usage using time_bucket from the 'metrics' hypertable",
            "criteria": [
                "Uses robomotion timescaledb query or select command",
                "References time_bucket function",
                "Specifies the hypertable name",
            ],
        },
    },
    {
        "name": "tidbcloud",
        "cli": "tidbcloud",
        "display": "TiDB Cloud",
        "category": "database",
        "verb": "execute SQL queries and manage data in TiDB Cloud",
        "use_cases": [
            "Execute SQL queries against TiDB Cloud",
            "Insert, update, or delete data in TiDB Cloud",
            "Manage TiDB Cloud database connections",
        ],
        "exclusions": "MySQL, PostgreSQL, CockroachDB, or other cloud database services",
        "tags": ["database", "tidbcloud", "distributed-sql", "cloud", "mysql-compatible"],
        "neg": [
            ("query a MySQL database", False),
            ("insert data into PostgreSQL", False),
            ("manage a MongoDB database", False),
        ],
        "quality": {
            "query": "connect to TiDB Cloud and run SELECT * FROM orders WHERE status = 'shipped'",
            "criteria": [
                "Uses robomotion tidbcloud execute query or similar command",
                "Specifies the SQL query",
                "References TiDB Cloud connection parameters",
            ],
        },
    },
    {
        "name": "travisci",
        "cli": "travisci",
        "display": "Travis CI",
        "category": "ci-cd",
        "verb": "manage builds, repositories, and jobs in Travis CI",
        "use_cases": [
            "List or trigger Travis CI builds",
            "Manage repositories in Travis CI",
            "Monitor build and job status",
            "View build logs and artifacts",
        ],
        "exclusions": "GitHub Actions, Jenkins, CircleCI, or other CI/CD platforms",
        "tags": ["ci-cd", "travisci", "builds", "testing", "automation"],
        "neg": [
            ("run a GitHub Actions workflow", False),
            ("trigger a Jenkins build", False),
            ("deploy to Cloudflare", False),
        ],
        "quality": {
            "query": "list all recent builds for the 'my-app' repository on Travis CI",
            "criteria": [
                "Uses robomotion travisci list builds command",
                "Specifies the repository name",
                "References build status or results",
            ],
        },
    },
    {
        "name": "vikunja",
        "cli": "vikunja",
        "display": "Vikunja",
        "category": "project-mgmt",
        "verb": "manage projects, tasks, labels, and teams in Vikunja",
        "use_cases": [
            "Create or update tasks in Vikunja",
            "Manage projects and task lists",
            "Assign labels and team members",
            "Track task progress and due dates",
        ],
        "exclusions": "Jira, Trello, ClickUp, Todoist, or other project management tools",
        "tags": ["project-management", "vikunja", "tasks", "open-source", "self-hosted"],
        "neg": [
            ("create a Jira issue", False),
            ("add a Trello card", False),
            ("manage ClickUp tasks", False),
        ],
        "quality": {
            "query": "create a new task in Vikunja project 'Website Redesign' titled 'Update homepage layout'",
            "criteria": [
                "Uses robomotion vikunja create task command",
                "Specifies the project name",
                "Includes the task title",
            ],
        },
    },
    {
        "name": "xano",
        "cli": "xano",
        "display": "Xano",
        "category": "backend",
        "verb": "manage database records and call API endpoints in Xano",
        "use_cases": [
            "Query or manage database records in Xano",
            "Call custom API endpoints",
            "Search and filter Xano data",
        ],
        "exclusions": "Supabase, Firebase, direct PostgreSQL, or other BaaS platforms",
        "tags": ["backend", "xano", "no-code", "api", "database"],
        "neg": [
            ("query Supabase tables", False),
            ("call a Firebase function", False),
            ("insert into PostgreSQL directly", False),
        ],
        "quality": {
            "query": "get all records from the 'products' table in Xano where price > 100",
            "criteria": [
                "Uses robomotion xano get or list records command",
                "Specifies the table name",
                "Includes a filter condition",
            ],
        },
    },
    {
        "name": "typeform",
        "cli": "typeform",
        "display": "Typeform",
        "category": "forms",
        "verb": "manage forms and collect responses via Typeform",
        "use_cases": [
            "List or manage Typeform forms",
            "Retrieve form responses and submissions",
            "Create or update form settings",
        ],
        "exclusions": "Google Forms, SurveyMonkey, JotForm, or other form builders",
        "tags": ["forms", "typeform", "survey", "responses", "data-collection"],
        "neg": [
            ("create a Google Form", False),
            ("manage Airtable records", False),
            ("send an email survey", False),
        ],
        "quality": {
            "query": "list all responses from the Typeform form 'Customer Feedback'",
            "criteria": [
                "Uses robomotion typeform list responses command",
                "Specifies the form name or ID",
                "References response data retrieval",
            ],
        },
    },
    {
        "name": "wikipedia",
        "cli": "wikipedia",
        "display": "Wikipedia",
        "category": "reference",
        "verb": "search and retrieve content from Wikipedia",
        "use_cases": [
            "Search Wikipedia for articles",
            "Retrieve Wikipedia article content",
            "Get summaries of Wikipedia pages",
        ],
        "exclusions": "Google Search, web scraping, or other encyclopedias and reference sources",
        "tags": ["reference", "wikipedia", "encyclopedia", "knowledge", "search"],
        "neg": [
            ("search Google for information", False),
            ("scrape a website for content", False),
            ("use Perplexity for research", False),
        ],
        "quality": {
            "query": "search Wikipedia for 'Artificial Intelligence' and get the article summary",
            "criteria": [
                "Uses robomotion wikipedia search or get article command",
                "Specifies the search term",
                "References summary or content output",
            ],
        },
    },
    {
        "name": "openweather",
        "cli": "openweather",
        "display": "OpenWeather",
        "category": "weather",
        "verb": "get weather data, forecasts, and air quality from OpenWeatherMap",
        "use_cases": [
            "Get current weather for a location",
            "Retrieve weather forecasts",
            "Check air quality data",
            "Get historical weather information",
        ],
        "exclusions": "AccuWeather, Weather.com, or other weather services",
        "tags": ["weather", "openweather", "forecast", "api", "climate"],
        "neg": [
            ("search Google for the weather", False),
            ("get location data from Google Maps", False),
            ("send a weather notification", False),
        ],
        "quality": {
            "query": "get the current weather for London, UK using OpenWeather",
            "criteria": [
                "Uses robomotion openweather get weather command",
                "Specifies the city or coordinates",
                "References temperature or weather data output",
            ],
        },
    },
    {
        "name": "pushover",
        "cli": "pushover",
        "display": "Pushover",
        "category": "notifications",
        "verb": "send push notifications via Pushover",
        "use_cases": [
            "Send push notifications to devices",
            "Send alerts with priority levels",
            "Attach images or URLs to notifications",
        ],
        "exclusions": "Slack notifications, email alerts, Twilio SMS, or other notification services",
        "tags": ["notifications", "pushover", "alerts", "push", "mobile"],
        "neg": [
            ("send a Slack message", False),
            ("send an SMS via Twilio", False),
            ("send an email notification", False),
        ],
        "quality": {
            "query": "send a high-priority Pushover notification with title 'Server Alert' and message 'CPU usage above 90%'",
            "criteria": [
                "Uses robomotion pushover send notification command",
                "Specifies the title and message",
                "Includes priority parameter",
            ],
        },
    },
    {
        "name": "falai",
        "cli": "falai",
        "display": "Fal AI",
        "category": "ai",
        "verb": "run AI models for image, video, and audio generation on Fal.ai",
        "use_cases": [
            "Generate images using AI models on Fal.ai",
            "Run video generation models",
            "Generate text-to-speech audio",
            "Execute custom ML models on Fal.ai",
        ],
        "exclusions": "OpenAI, Stability AI, Replicate, or other AI inference platforms",
        "tags": ["ai", "falai", "image-generation", "video", "inference"],
        "neg": [
            ("generate an image with Stability AI", False),
            ("run a model on Replicate", False),
            ("use OpenAI for text generation", False),
        ],
        "quality": {
            "query": "use Fal AI to generate an image using the flux model with prompt 'mountain landscape'",
            "criteria": [
                "Uses robomotion falai run or generate command",
                "Specifies the model name",
                "Includes the input prompt",
            ],
        },
    },
    {
        "name": "canvas",
        "cli": "canvas",
        "display": "Canvas LMS",
        "category": "lms",
        "verb": "manage courses, assignments, and users in Canvas LMS",
        "use_cases": [
            "Manage courses and enrollments",
            "Create or grade assignments",
            "Manage users and submissions",
            "Create pages, modules, and announcements",
        ],
        "exclusions": "Moodle, Google Classroom, Blackboard, or other LMS platforms",
        "tags": ["lms", "canvas", "education", "courses", "assignments"],
        "neg": [
            ("create a Google Classroom assignment", False),
            ("manage a Notion workspace", False),
            ("send an email to students", False),
        ],
        "quality": {
            "query": "list all assignments for the 'Introduction to CS' course in Canvas LMS",
            "criteria": [
                "Uses robomotion canvas list assignments command",
                "Specifies the course name or ID",
                "References assignment data output",
            ],
        },
    },
    {
        "name": "polymarket",
        "cli": "polymarket",
        "display": "Polymarket",
        "category": "prediction",
        "verb": "access prediction market data, pricing, and analytics from Polymarket",
        "use_cases": [
            "Get prediction market data and pricing",
            "Access orderbooks and positions",
            "Analyze trading data and trends",
            "Query market outcomes and probabilities",
        ],
        "exclusions": "Binance, stock trading platforms, or other financial services",
        "tags": ["prediction", "polymarket", "markets", "data", "analytics"],
        "neg": [
            ("trade on Binance", False),
            ("get stock market data", False),
            ("check cryptocurrency prices", False),
        ],
        "quality": {
            "query": "get the current pricing and probability for the top Polymarket markets",
            "criteria": [
                "Uses robomotion polymarket get markets or list command",
                "References pricing or probability data",
                "Includes market selection parameters",
            ],
        },
    },
    {
        "name": "leonardo-ai",
        "cli": "leonardoai",
        "display": "Leonardo AI",
        "category": "ai",
        "verb": "generate images via Leonardo AI",
        "use_cases": [
            "Generate images from text prompts",
            "Create AI art and visual content",
            "Manage image generation models and presets",
        ],
        "exclusions": "DALL-E/OpenAI, Stability AI, Midjourney, or other image generation services",
        "tags": ["ai", "leonardo-ai", "image-generation", "art", "creative"],
        "neg": [
            ("generate an image with DALL-E", False),
            ("use Stability AI for images", False),
            ("run a model on Fal.ai", False),
        ],
        "quality": {
            "query": "use Leonardo AI to generate a photorealistic image of 'a modern office space'",
            "criteria": [
                "Uses robomotion leonardoai generate image command",
                "Specifies the text prompt",
                "References style or model parameters",
            ],
        },
    },
    {
        "name": "binance",
        "cli": "binance",
        "display": "Binance",
        "category": "crypto",
        "verb": "access cryptocurrency market data and trading on Binance",
        "use_cases": [
            "Get cryptocurrency prices and market data",
            "Access trading pairs and orderbooks",
            "Monitor account balances and positions",
            "Execute trades on Binance",
        ],
        "exclusions": "Gate.io, Coinbase, Ethereum direct, or other crypto exchanges",
        "tags": ["crypto", "binance", "trading", "exchange", "market-data"],
        "neg": [
            ("trade on Gate.io", False),
            ("interact with Ethereum blockchain", False),
            ("check Polymarket predictions", False),
        ],
        "quality": {
            "query": "get the current BTC/USDT price and 24h volume from Binance",
            "criteria": [
                "Uses robomotion binance get price or ticker command",
                "Specifies the trading pair",
                "References price or volume data",
            ],
        },
    },
    {
        "name": "ethereum",
        "cli": "ethereum",
        "display": "Ethereum",
        "category": "crypto",
        "verb": "interact with the Ethereum blockchain",
        "use_cases": [
            "Get Ethereum account balances",
            "Read smart contract data",
            "Send Ethereum transactions",
            "Monitor blockchain events",
        ],
        "exclusions": "Binance, centralized exchanges, Bitcoin, or other blockchains",
        "tags": ["crypto", "ethereum", "blockchain", "web3", "smart-contracts"],
        "neg": [
            ("trade on Binance", False),
            ("get Bitcoin prices", False),
            ("manage a database", False),
        ],
        "quality": {
            "query": "get the ETH balance for wallet address 0x1234...abcd using Ethereum",
            "criteria": [
                "Uses robomotion ethereum get balance command",
                "Specifies the wallet address",
                "References ETH balance or Wei units",
            ],
        },
    },
    {
        "name": "gateio",
        "cli": "gateio",
        "display": "Gate.io",
        "category": "crypto",
        "verb": "access cryptocurrency market data and trading on Gate.io",
        "use_cases": [
            "Get cryptocurrency prices and market data from Gate.io",
            "Access trading pairs and orderbooks",
            "Monitor account positions",
            "Execute trades on Gate.io",
        ],
        "exclusions": "Binance, Coinbase, Ethereum direct, or other crypto exchanges",
        "tags": ["crypto", "gateio", "trading", "exchange", "market-data"],
        "neg": [
            ("trade on Binance", False),
            ("interact with Ethereum blockchain", False),
            ("check stock market data", False),
        ],
        "quality": {
            "query": "get the current BTC/USDT price from Gate.io",
            "criteria": [
                "Uses robomotion gateio get price or ticker command",
                "Specifies the trading pair",
                "References price data output",
            ],
        },
    },
    {
        "name": "microsoft-ad",
        "cli": "activedirectory",
        "display": "Active Directory",
        "category": "identity",
        "verb": "manage users, groups, and organizational units in Active Directory",
        "use_cases": [
            "List or search Active Directory users",
            "Manage AD groups and memberships",
            "Create or update user accounts",
            "Manage organizational units",
        ],
        "exclusions": "Azure AD/Entra ID cloud-only, Okta, Auth0, or other identity providers",
        "tags": ["identity", "active-directory", "microsoft", "ldap", "users", "groups"],
        "neg": [
            ("manage users in Auth0", False),
            ("send an email via Outlook", False),
            ("manage Azure cloud resources", False),
        ],
        "quality": {
            "query": "list all users in the 'Engineering' organizational unit in Active Directory",
            "criteria": [
                "Uses robomotion activedirectory list users command",
                "Specifies the organizational unit",
                "References user attributes output",
            ],
        },
    },
]


def generate_skill_md(skill):
    """Generate SKILL.md content for a skill."""
    return f"""---
name: "{skill['name']}"
description: "Use when the user wants to call the Robomotion {skill['display']} package to {skill['verb']} via the `robomotion {skill['cli']}` CLI. Do NOT use for {skill['exclusions']}."
---

# {skill['display']} Skill

## When to use
{chr(10).join(f"- {uc}" for uc in skill['use_cases'])}

## Prerequisites
- `robomotion` CLI installed
- Package installed: `robomotion install {skill['cli']}`
- Credentials configured via Robomotion vault or environment variables

## Workflow
1. Install the package: `robomotion install {skill['cli']}`
2. Run commands: `robomotion {skill['cli']} <command> [flags]`

## Environment
- ROBOMOTION_API_TOKEN (if vault credentials are needed)
"""


def generate_eval_set(skill):
    """Generate eval-set.json content for a skill."""
    use_cases = skill["use_cases"]
    primary_action = use_cases[0].lower()
    if primary_action.startswith("list "):
        primary_action = primary_action
    secondary_action = use_cases[1].lower() if len(use_cases) > 1 else primary_action

    cases = [
        {
            "id": "trigger-pos-1",
            "type": "trigger",
            "query": f"use robomotion {skill['cli']} to {primary_action.rstrip('.')}",
            "expect_triggered": True,
        },
        {
            "id": "trigger-pos-2",
            "type": "trigger",
            "query": f"run robomotion {skill['cli']} command to {secondary_action.rstrip('.')}",
            "expect_triggered": True,
        },
        {
            "id": "trigger-pos-3",
            "type": "trigger",
            "query": f"call robomotion {skill['cli']} to {(use_cases[2].lower() if len(use_cases) > 2 else primary_action).rstrip('.')}",
            "expect_triggered": True,
        },
    ]

    # Add negative triggers
    for i, (query, expected) in enumerate(skill["neg"], 1):
        cases.append(
            {
                "id": f"trigger-neg-{i}",
                "type": "trigger",
                "query": query,
                "expect_triggered": expected,
            }
        )

    # Boundary case
    cases.append(
        {
            "id": "trigger-boundary-1",
            "type": "trigger",
            "query": "write a Python function to sort a list of numbers",
            "expect_triggered": False,
        }
    )

    # Quality case
    cases.append(
        {
            "id": "quality-1",
            "type": "quality",
            "query": skill["quality"]["query"],
            "criteria": skill["quality"]["criteria"],
        }
    )

    return {"skill_name": skill["name"], "cases": cases}


def generate_index_entry(skill):
    """Generate a skills-index.json entry for a skill."""
    # Build a short description matching existing pattern
    verb_phrase = skill["verb"]
    cli = skill["cli"]
    desc = f"{verb_phrase[0].upper()}{verb_phrase[1:]} via the `robomotion {cli}` CLI."
    return {
        "name": skill["name"],
        "path": f"skills/{skill['name']}",
        "description": desc,
        "version": "1.0.0",
        "author": "robomotion",
        "tags": skill["tags"],
        "license": "Apache-2.0",
    }


def main():
    dry_run = "--dry-run" in sys.argv

    # Load existing index
    with open(INDEX_PATH, "r") as f:
        index = json.load(f)

    existing_names = {s["name"] for s in index["skills"]}
    created = 0
    skipped = 0

    for skill in SKILLS:
        skill_dir = os.path.join(SKILLS_DIR, skill["name"])

        if skill["name"] in existing_names:
            print(f"  SKIP (exists in index): {skill['name']}")
            skipped += 1
            continue

        if dry_run:
            print(f"  DRY-RUN: {skill['name']}")
            created += 1
            continue

        # Create directory
        os.makedirs(skill_dir, exist_ok=True)

        # Write SKILL.md
        skill_md = generate_skill_md(skill)
        with open(os.path.join(skill_dir, "SKILL.md"), "w") as f:
            f.write(skill_md)

        # Write eval-set.json
        eval_set = generate_eval_set(skill)
        with open(os.path.join(skill_dir, "eval-set.json"), "w") as f:
            json.dump(eval_set, f, indent=2)
            f.write("\n")

        # Add to index
        entry = generate_index_entry(skill)
        index["skills"].append(entry)
        existing_names.add(skill["name"])

        print(f"  CREATED: {skill['name']}")
        created += 1

    # Write updated index
    if not dry_run:
        with open(INDEX_PATH, "w") as f:
            json.dump(index, f, indent=2)
            f.write("\n")

    print(f"\nDone: {created} created, {skipped} skipped")
    print(f"Total skills in index: {len(index['skills'])}")


if __name__ == "__main__":
    main()
