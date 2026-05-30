---
name: job-scraper
description: Search job postings across LinkedIn and Indeed by keyword, location, company, or job type — no logins or cookies — returning structured jobs (title, company, location, salary, description, seniority, apply URL) for hiring-signal detection, GTM research, and competitive intel. Apify actors when a token is set; keyless web search otherwise.
metadata:
  version: 1.0.0
  category: lead-generation
  type: capability
---

# Job Scraper

General job-data sourcing across LinkedIn + Indeed. The bundled script auto-selects the
Apify actor path (rich structured fields) when `APIFY_API_TOKEN` is set, and falls back to
a keyless `site:` web search otherwise. Intent scoring lives in `job-posting-intent`.

## When to use

- "Find jobs / open roles." / "Who is hiring for [role]?" / "What is [competitor] hiring for?"
- "Find companies growing their [domain] team."

## How to run

```bash
python3 ${SKILL_DIR}/scripts/jobs.py \
  --query "RevOps Manager" \
  --location "United States" \
  --company "Acme Corp" \
  --sources linkedin,indeed \
  --num-results 25 \
  --output ${WORKSPACE}/jobs.json
```

- **With `APIFY_API_TOKEN`:** runs the LinkedIn + Indeed actors for salary/seniority/full
  description. Cap `--num-results` — Apify is pay-per-job.
- **Without it:** degrades to a keyless `site:linkedin.com/jobs` / `site:indeed.com` search
  returning title + apply URL + snippet (no salary/seniority).

Actor ids default to common public actors and can be overridden with `APIFY_LINKEDIN_JOBS_ACTOR`
/ `APIFY_INDEED_JOBS_ACTOR`.

## Outputs

`jobs.json` — `[{title, company, location, salary, seniority, description, apply_url,
source}]`, deduped by title+company+location across sources. `source` is `linkedin` /
`indeed` (Apify) or `linkedin/serp` / `indeed/serp` (keyless).

## Credentials / env

- **Required:** none — the keyless serp degrade runs with no key.
- **Optional:** `APIFY_API_TOKEN` (LinkedIn/Indeed actors — structured fields, salary,
  seniority; without it, shallower serp search). `APIFY_LINKEDIN_JOBS_ACTOR` /
  `APIFY_INDEED_JOBS_ACTOR` to point at specific actors.

## Notes & edge cases

- This sources raw jobs; for budget-signal scoring + outreach context use `job-posting-intent`.
- Indeed actor carries the richest fields (salary, ratings); LinkedIn adds seniority/function.
- Dedup the same role posted on both boards (the script does this).
- Apify is pay-per-job — cap `--num-results`; note cost as optional. The keyless endpoint
  rate-limits — space calls (the script does).
