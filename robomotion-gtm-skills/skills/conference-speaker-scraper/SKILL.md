---
name: conference-speaker-scraper
description: Extract speaker names, titles, companies, and bios from a conference's /speakers page for pre-event research and outreach targeting. Tries multiple keyless extraction strategies (CSS cards, heading+paragraph blocks, JSON-LD, Sched/Sessionize) and falls back to a headless browser for JS-heavy sites.
metadata:
  version: 1.0.0
  category: lead-generation
  type: capability
---

# Conference Speaker Scraper

Pull a speaker list from a conference site for pre-event prospecting. The keyless script
tries several extraction strategies and keeps whichever yields the most speakers; a
Playwright degrade handles JS-rendered pages.

## When to use

- "Who's speaking at [conference]? Get their titles and companies."
- "Scrape the speaker list from [conference URL]."
- Front-end for the `event-prospecting-pipeline`.

## How to run

### Primary — keyless multi-strategy

```bash
python3 ${SKILL_DIR}/scripts/scrape_speakers.py \
  --url https://conf.example.com/speakers \
  --conference "ExampleConf" \
  --output json   # json | csv | summary
```

Strategies tried: (a) speaker/presenter/faculty/panelist CSS cards; (b) repeated
heading+paragraph blocks; (c) JSON-LD `schema.org/Person`; (d) Sched/Sessionize embed
detection. It keeps the single best-yielding strategy (never merges conflicting ones).

If it prints a "no speakers extracted" / "platform embed detected" warning, the page is
JS-rendered — use the degrade below.

### Degrade — JS-heavy pages (Playwright)

```bash
cd ${SKILL_DIR}/scripts && npm install && npx playwright install chromium
node ${SKILL_DIR}/scripts/scrape_speakers_pw.mjs \
  --url https://conf.example.com/speakers \
  --conference "ExampleConf" \
  --output ${WORKSPACE}/speakers.json
```

Renders the page (waits for `networkidle`) then extracts cards. If that's also blocked and
`APIFY_API_TOKEN` is available, route to an Apify cheerio/web-scraper actor; otherwise
return partial results and note the gap.

## Outputs

`{conference, strategy, platform, speakers: [{name, title, company, bio, conference}]}`
as JSON, or a CSV / human summary with `--output`.

## Credentials / env

- **Required:** none — direct extraction uses keyless fetch + Robomotion Proxy equivalents.
- **Optional:** `APIFY_API_TOKEN` — only for the managed-scraper fallback on JS-heavy /
  anti-bot speaker pages.

## Notes & edge cases

- Pick the strategy returning the most speakers; don't merge conflicting strategy outputs
  (the script enforces this).
- Many conferences embed Sched/Sessionize — the script flags `platform` so you can parse
  those directly before falling to the browser.
- Without `APIFY_API_TOKEN`, JS-heavy pages degrade to Playwright; if that's blocked, return
  partial results and note the gap.
- Bios may be truncated on cards; follow per-speaker links only if cheap.
