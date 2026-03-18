# Excluded Packages — Not Suitable for Agent Skills

These 65 packages have `config.json` in `/home/faik/packages-src/packages-main/src/` but are intentionally excluded from skills generation.

## Internal Utilities / Data Types (25)
- `array` — Array manipulation utilities
- `boolean` — Boolean operations
- `number` — Number operations
- `string` — String operations
- `object` — Object operations
- `json` — JSON parsing/serialization
- `encoding` — Encoding/decoding utilities
- `datetime` — Date/time operations
- `compress` — Compression utilities
- `cryptography` — Crypto operations
- `barcode` — Barcode generation/reading
- `cookie-store` — Cookie management
- `memory-queue` — In-memory queue
- `mime-tools` — MIME type utilities
- `grule` — Rule engine
- `markdown` — Markdown processing
- `subtitles` — Subtitle file handling
- `email-validator` — Email validation
- `2fa` — Two-factor authentication
- `oauth2` — OAuth2 flow handling
- `datatable` — DataTable operations
- `pandas` — Data analysis (Python-style)
- `keyword-analysis` — Keyword analysis
- `technical-analysis` — Technical/financial analysis

## Internal / Platform (7)
- `agents` — Internal agent framework
- `agent-tools` — Internal agent tooling
- `robomotion-assistant` — Internal assistant
- `robomotion-chat-assistant` — Internal chat assistant
- `robomotion-serp` — Internal SERP
- `mcp` — Model Context Protocol (internal)
- `document-processor` — Internal document pipeline

## Legacy / Desktop Automation (5)
- `image-automation` — Desktop image automation
- `image-processing` — Image processing
- `audio_processing` — Audio processing
- `web-automation` — Browser automation (legacy)
- `windows-automation` — Windows desktop automation
- `javaautomation` — Java UI automation

## Legacy Microsoft (duplicated by 365 versions) (6)
- `microsoft/msgraph` — Base Graph API (use specific 365 packages)
- `microsoft/exchange` — Exchange (use outlook365)
- `microsoft/msexcel` — Legacy Excel (use excel365)
- `microsoft/msoutlook` — Legacy Outlook (use outlook365)
- `microsoft/msword` — Legacy Word (use word365)
- `microsoft/teams` — Legacy Teams (use teams365)
- `microsoft/microsoft365-mail` — Legacy mail (use outlook365)

## Legacy Google (covered by existing skills) (5)
- `google/vision` — Covered by ocr-extraction skill
- `google/document-ai` — Covered by ocr-extraction skill
- `google/vertex-ai` — Overlaps with gemini-ai skill
- `google/natural-language` — Niche NLP API
- `google/dialogflow` — Niche chatbot API
- `google/search-console` — Niche SEO API
- `google/trends` — Niche trends API

## Legacy / Duplicate / Too Niche (7)
- `pdfbox` — Legacy PDF (covered by pdf skill)
- `word` — Legacy Word (covered by word365)
- `pipedrive` — Similar to hubspot-crm
- `anticaptcha` — CAPTCHA solving
- `capmonster` — CAPTCHA solving
- `ffmpeg` — Media processing CLI wrapper
- `giphy` — GIF search
- `badgerdb` — Embedded key-value DB
- `instagram` — Instagram API (restricted)
- `telegram-user` — Telegram user client (not bot)
- `tesseract` — OCR (covered by ocr-extraction)
- `abbyy/cloud` — ABBYY Cloud OCR
- `abbyy/fine-reader-sdk` — ABBYY FineReader
- `abbyy/flexi-capture` — ABBYY FlexiCapture
