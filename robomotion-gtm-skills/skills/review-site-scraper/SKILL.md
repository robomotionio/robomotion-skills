---
name: review-site-scraper
description: Scrape product reviews from G2, Capterra, or Trustpilot in one skill (platform dispatch), normalized into a common schema with platform extras preserved. Use to monitor competitor reviews, track product sentiment, and gather Voice-of-Customer. Per-platform Apify actors when APIFY_API_TOKEN is set; keyless Playwright degrade otherwise.
metadata:
  version: 1.1.1
  category: monitoring
  type: capability
---

# Review Site Scraper

One skill, three platforms. Dispatch on `--platform`: **G2** and **Trustpilot** take a
review-page `--url`; **Capterra** takes a `--company-name`. Two paths share one
normalized schema (platform-specific fields preserved):

- **Apify (when `APIFY_API_TOKEN` is set):** a per-platform review actor run via a
  **managed async run/poll lifecycle** (start, poll to terminal with backoff + a
  wall-clock timeout, then fetch the dataset) under a **cost gate**. Reliable; **some
  actors are pay-per-result**, so the gate matters. Replaces the old `run-sync` call that
  could time out or overspend.
- **Keyless (default):** a bundled Playwright scraper (`scripts/review_scrape.mjs`).
  Review sites are anti-bot and JS-rendered, so this is best-effort — lower volume.
  **Never cost-gated.**

## When to use

- You need reviews for a product on G2, Capterra, or Trustpilot.
- Competitor review monitoring, sentiment tracking, or VoC gathering.
- Recurring review monitoring with dedup across runs.

## How to run

```bash
python3 ${SKILL_DIR}/scripts/review_scraper.py --platform <g2|capterra|trustpilot> [options]
```

| Flag | Default | Meaning |
|---|---|---|
| `--platform` | (required) | `g2`, `capterra`, `trustpilot`. |
| `--url` | — | Review-page URL (required for `g2` / `trustpilot`). |
| `--company-name` | — | Company/product name (required for `capterra`). |
| `--max-reviews` | `50` | Cap on returned reviews. |
| `--keywords` | `""` | Comma-separated OR client-side filter on review text. |
| `--days` | `0` | Only reviews from last N days (0 = no limit). |
| `--use-apify` | off | Force the Apify path (auto when token set). |
| `--estimate-only` | off | **Cost gate:** print projected cost/limits and exit 0 (no spend). |
| `--yes` | off | **Cost gate:** confirm actual spend — required to start an Apify run. |
| `--max-cost-usd` | `1.00` | **Cost gate:** abort the run if reported usage exceeds this. |
| `--apify-timeout` | `600` | Run/poll wall-clock timeout (s); the run is aborted if it trips. |
| `--output` | `json` | `json` array or `summary` lines. |

## Cost gate & run/poll lifecycle (Apify path only)

The per-platform actor run starts async, polls to a terminal state with backoff and a
wall-clock timeout (aborting on timeout to stop the meter), then fetches the dataset only
on `SUCCEEDED`. Because **G2/Capterra/Trustpilot actors can be pay-per-result**, a **cost
gate** guards spend: `--estimate-only` prints the projection and **exits 0 without
spending**; starting a run **requires `--yes`** (else it refuses, non-zero exit); the run
is **aborted** if reported usage exceeds `--max-cost-usd` or the timeout trips
(`--max-cost-usd 0` forbids any spend). The **keyless Playwright path is never gated**.

Keyless path setup (once):

```bash
cd ${SKILL_DIR}/scripts && npm install && npx playwright install chromium
```

### Examples

```bash
# G2 reviews from a product page
python3 ${SKILL_DIR}/scripts/review_scraper.py --platform g2 \
  --url "https://www.g2.com/products/foo/reviews" --max-reviews 50

# Capterra by company name
python3 ${SKILL_DIR}/scripts/review_scraper.py --platform capterra \
  --company-name "Foo App" --output summary

# Trustpilot, last 90 days, reliable path — preview the (pay-per-result) cost, then confirm
APIFY_API_TOKEN=$APIFY_API_TOKEN python3 ${SKILL_DIR}/scripts/review_scraper.py \
  --platform trustpilot --url "https://www.trustpilot.com/review/foo.com" --use-apify --estimate-only
APIFY_API_TOKEN=$APIFY_API_TOKEN python3 ${SKILL_DIR}/scripts/review_scraper.py \
  --platform trustpilot --url "https://www.trustpilot.com/review/foo.com" --days 90 --use-apify --yes --max-cost-usd 1.00
```

## Outputs

Normalized JSON array. Common fields: `{platform, id, text, rating, author, date, url}`.
Per-platform extras: G2 adds `author_title/author_company/company_size/industry`;
Capterra adds `ease_of_use/customer_service/features/job_title/industry`; Trustpilot adds
`experienced_date/likes/input_source`.

## Recurring / sentiment-trending mode

Dedup on review `id` (a text hash when the platform exposes no id) and stamp first-seen:

```bash
python3 ${SKILL_DIR}/scripts/review_scraper.py --platform g2 --url "<url>" > ${WORKSPACE}/run.json
python3 ${SKILL_DIR}/scripts/dedup_history.py --input ${WORKSPACE}/run.json \
  --history ${WORKSPACE}/reviews_seen.csv --key id > ${WORKSPACE}/new.json
```

For a VoC digest / sentiment themes, the host agent reads the review rows and synthesizes
(no LLM call inside the scripts).

## Credentials / env

- **Required:** none — keyless Playwright degrade for all three platforms.
- **Optional (paid, if-set/else):**
  - `APIFY_API_TOKEN` — **if set → per-platform Apify review actors** (cost-gated; some are
    pay-per-result); **else → keyless Playwright** for all three platforms (the default, never gated).
  - `APIFY_G2_ACTOR` / `APIFY_CAPTERRA_ACTOR` / `APIFY_TRUSTPILOT_ACTOR` — override the default slugs.
  - `ANTHROPIC_API_KEY` — **if set → optional script-side LLM sentiment/theme synthesis**;
    **else → the host agent synthesizes** from the review rows (the default; no LLM key needed).
  - `SUPABASE_URL` / `SUPABASE_KEY` — **if set → Supabase cross-run history**;
    **else → workspace CSV** via `dedup_history.py` (the default).

## Notes & edge cases

- Input validation is enforced: G2/Trustpilot require `--url`, Capterra requires
  `--company-name`.
- Review sites are anti-bot heavy — route the Playwright path through a proxy; prefer the
  Apify actors when a token is available.
- For sentiment trending, dedup on review id/text-hash so re-runs only add new reviews.
