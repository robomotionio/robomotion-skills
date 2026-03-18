# Populate Real CLI Commands for All 110 Skills

## Goal
Each skill's `SKILL.md` needs a **Commands Reference** section populated with real command names and flags extracted from the Robomotion CLI (`robomotion <cli> --list-commands --output json`). Currently the 85 newly generated skills have no commands, and the 25 existing skills already have them.

## Steps
1. For each skill: `robomotion install <cli-name>`
2. Extract commands: `robomotion <cli-name> --list-commands --output json`
3. Regenerate `SKILL.md` with real Commands Reference section
4. Mark checkbox below when done

## Existing Skills (25) — Already have commands
- [x] apify (cli: apify)
- [x] apollo (cli: apollo)
- [x] claude-ai (cli: claude)
- [x] clickhouse (cli: clickhouse)
- [x] cloudflare (cli: cloudflare)
- [x] discord-bot (cli: discordbot)
- [x] gemini-ai (cli: googlegemini)
- [x] gmail (cli: gmail)
- [x] google-docs (cli: googledocs)
- [x] google-drive (cli: googledrive)
- [x] google-sheets (cli: googlesheets)
- [x] hubspot-crm (cli: hubspot)
- [x] jira (cli: jira)
- [x] mongodb (cli: mongodb)
- [x] notion (cli: notion)
- [x] ocr-extraction (cli: googlevision/googledocumentai)
- [x] openai (cli: openai)
- [x] pdf (cli: pdfprocessor)
- [x] postgresql (cli: postgresql)
- [x] s3-storage (cli: amazons3)
- [x] slack (cli: slack)
- [x] stripe-payments (cli: stripe)
- [x] telegram (cli: telegrambot)
- [x] web-scraper (cli: domparser)
- [x] whatsapp (cli: whatsapp)

## Tier 1: High Priority (25 new skills)
- [x] dropbox (cli: dropbox) — 12 commands
- [x] google-calendar (cli: googlecalendar) — 7 commands
- [x] google-slides (cli: googleslides) — 9 commands
- [x] google-translate (cli: googletranslate) — 1 command
- [x] google-storage (cli: googlestorage) — 10 commands
- [x] excel365 (cli: excel365) — 30 commands
- [x] outlook365 (cli: outlook365) — 17 commands
- [x] onedrive365 (cli: onedrive365) — 14 commands
- [x] teams365 (cli: teams365) — 17 commands
- [x] powerpoint365 (cli: powerpoint365) — 11 commands
- [x] sharepoint365 (cli: sharepoint365) — 18 commands
- [x] mysql (cli: mysql) — 12 commands
- [x] supabase (cli: supabase) — 12 commands
- [x] twilio (cli: twilio) — 8 commands
- [x] airtable (cli: airtable) — 14 commands
- [x] trello (cli: trello) — 20 commands
- [x] clickup (cli: clickup) — 27 commands
- [x] shopify (cli: shopify) — 23 commands
- [x] wordpress (cli: wordpress) — 11 commands
- [x] zoom (cli: zoom) — 12 commands
- [x] resend (cli: resend) — 11 commands
- [x] redis (cli: redis) — 24 commands
- [x] sqlite (cli: sqlite) — 9 commands
- [x] ssh (cli: ssh) — 5 commands

## Tier 2: Medium Priority (27 new skills)
- [x] ollama (cli: ollama) — 9 commands
- [x] openrouter (cli: openrouter) — 15 commands
- [x] replicate-ai (cli: replicateai) — 10 commands
- [x] perplexity (cli: perplexity) — 4 commands
- [x] elevenlabs-ai (cli: elevenlabsai) — 20 commands
- [x] pinecone (cli: pinecone) — 10 commands
- [x] qdrant (cli: qdrant) — 16 commands
- [x] sentry (cli: sentry) — 1 command
- [x] datadog (cli: datadog) — 14 commands
- [x] monitoring (cli: monitoring) — 6 commands
- [x] rabbitmq (cli: rabbitmq) — 10 commands
- [x] oracle (cli: oracle) — 7 commands
- [x] mssql (cli: mssql) — 10 commands
- [x] onenote365 (cli: onenote365) — 15 commands
- [x] google-forms (cli: googleforms) — 7 commands
- [x] google-maps (cli: googlemaps) — 4 commands
- [x] google-speech (cli: googlespeech) — 2 commands
- [x] docusign (cli: docusign) — 11 commands
- [x] woocommerce (cli: woocommerce) — 22 commands
- [x] calendly (cli: calendly) — 12 commands
- [x] calcom (cli: calcom) — 13 commands
- [x] pcloud (cli: pcloud) — 9 commands
- [x] nextcloud (cli: nextcloud) — 13 commands
- [x] tavily (cli: tavily) — 6 commands
- [x] searchapi (cli: searchapi) — 14 commands
- [x] serper (cli: serper) — 14 commands
- [x] stability-ai (cli: stabilityai) — 9 commands

## Tier 3: Lower Priority (33 new skills)
- [x] baserow (cli: baserow) — 8 commands
- [x] seatable (cli: seatable) — 17 commands
- [x] mautic (cli: mautic) — 18 commands
- [x] ghost (cli: ghost) — 20 commands
- [x] fibery (cli: fibery) — 7 commands
- [x] homeassistant (cli: homeassistant) — 11 commands
- [x] instantly (cli: instantly) — 12 commands
- [x] lemlist (cli: lemlist) — 6 commands
- [x] dropcontact (cli: dropcontact) — 3 commands
- [x] splunk (cli: splunk) — 9 commands
- [x] rundeck (cli: rundeck) — 4 commands
- [x] questdb (cli: questdb) — 5 commands
- [x] timescaledb (cli: timescaledb) — 10 commands
- [x] tidbcloud (cli: tidbcloud) — 7 commands
- [x] travisci (cli: travisci) — 10 commands
- [x] vikunja (cli: vikunja) — 17 commands
- [x] xano (cli: xano) — 11 commands
- [x] typeform (cli: typeform) — 8 commands
- [x] wikipedia (cli: wikipedia) — 6 commands
- [x] openweather (cli: openweather) — 6 commands
- [x] pushover (cli: pushover) — 5 commands
- [x] falai (cli: falai) — 7 commands
- [x] canvas (cli: canvas) — 22 commands
- [x] polymarket (cli: polymarket) — 15 commands
- [x] leonardo-ai (cli: leonardoai) — 12 commands
- [x] binance (cli: binance) — 20 commands
- [x] ethereum (cli: ethereum) — 22 commands
- [x] gateio (cli: gateio) — 13 commands
- [x] microsoft-ad (cli: activedirectory) — 14 commands

## Summary
- **Completed**: 80 new skills with real CLI commands verified via `robomotion install` + `--list-commands`
- **Removed**: 5 skills (word365, nocodb, odoo, phantombuster, millionverifier) — could not verify, moved to `later.md`
- **Total skills**: 105 (25 existing + 80 new)
