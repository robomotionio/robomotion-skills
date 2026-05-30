---
name: linkedin-job-scraper
description: Find LinkedIn job postings by search term and location, returning structured jobs (title, company, location, salary, job type, description, URL) for GTM research, hiring-signal sourcing, and job-pipeline building. Apify LinkedIn jobs actor when a token is set; keyless site:linkedin.com/jobs search otherwise.
metadata:
  version: 1.0.0
  category: lead-generation
  type: capability
---

# LinkedIn Job Scraper

LinkedIn-only raw job sourcing. Overlaps `job-scraper` (multi-source) and
`job-posting-intent` (scored intent) — this one is LinkedIn-only structured sourcing.

## When to use

- "Find jobs on LinkedIn." / "Search for open roles." / "What roles is [company] hiring for?"
- "Build a job pipeline" / "source job targets for GTM research."

## How to run

```bash
python3 ${SKILL_DIR}/scripts/linkedin_jobs.py \
  --search "Sales Engineer" \
  --location "Remote" \
  --results 25 \
  --output ${WORKSPACE}/jobs.json
```

- **With `APIFY_API_TOKEN`:** runs the LinkedIn jobs actor (clean structured fields at
  scale, no cookies).
- **Without it:** degrades to a keyless `site:linkedin.com/jobs` search (shallower, less
  structured).

Override the actor with `APIFY_LINKEDIN_JOBS_ACTOR`.

## Outputs

`jobs.json` — `[{title, company, location, salary, job_type, description, url, source}]`,
deduped by title+company+url. `source` is `linkedin` (Apify) or `linkedin/serp` (keyless).

## Credentials / env

- **Required:** none — the keyless serp degrade needs no key.
- **Optional:** `APIFY_API_TOKEN` (LinkedIn jobs actor; without it, shallower serp search);
  `APIFY_LINKEDIN_JOBS_ACTOR` to override the actor id.

## Notes & edge cases

- Proxy + throttle any direct LinkedIn access; LinkedIn rate-limits aggressively. The
  keyless endpoint also rate-limits — the script backs off.
- Dedup repeated postings of the same role (the script does this).
- Salary/description may be sparse depending on the posting.
