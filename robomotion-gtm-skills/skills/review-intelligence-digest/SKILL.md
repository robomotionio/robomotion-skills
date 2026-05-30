---
name: review-intelligence-digest
description: Scrape G2/Capterra/Trustpilot reviews for your product and competitors, then extract the marketing-relevant signal — exact customer language, metric-bearing proof points, recurring objections, competitive-displacement angles, and buyer vocabulary — into a periodic digest that feeds copywriting, positioning, and sales enablement. Apify-backed scrape; the agent does the synthesis.
metadata:
  version: 1.1.1
  category: research
  type: composite
---

# Review Intelligence Digest

Scrape reviews (deterministic), then **synthesize the digest yourself** — the script only
returns normalized review rows; you cluster themes, count frequencies, pull verbatim
quotes, and write the digest. Scrape path: **keyless Playwright by default**; if
`APIFY_API_TOKEN` is set, the Apify review actors give fuller, more reliable coverage.

## When to use

- "What are customers saying about us vs competitors?" / "Run a review audit for [client]."
- "Find proof points and objections from our G2 reviews."
- "What language do our customers use?" / "What are [competitor]'s customers complaining about?"

## How to run

### Step 1 — scrape reviews (deterministic)

**Default (keyless, no `APIFY_API_TOKEN`):** render each review page with Playwright and
dump its text — partial coverage, no key, possible blocks on the most hostile sites.

```bash
cd ${SKILL_DIR}/scripts && npm install && npx playwright install chromium
node ${SKILL_DIR}/scripts/fetch_page.mjs --url "<review-page>" --out ${WORKSPACE}/page.txt
# optionally route through a residential proxy if the site blocks the render:
node ${SKILL_DIR}/scripts/fetch_page.mjs --url "<review-page>" --proxy "<residential-proxy>" --out ${WORKSPACE}/page.txt
```

**Upgrade (with `APIFY_API_TOKEN`, cost-gated):** the Apify review actors handle anti-bot
sites and return full normalized rows. Recommended when you need complete coverage.

```bash
# Preview the projected Apify cost per target first (exits 0, no spend):
python3 ${SKILL_DIR}/scripts/scrape_reviews.py \
  --product "Acme" \
  --url "https://www.g2.com/products/acme/reviews" \
  --competitor "Rival=https://www.trustpilot.com/review/rival.com" \
  --months 3 --estimate-only

# Then confirm spend with --yes and a per-target budget cap:
python3 ${SKILL_DIR}/scripts/scrape_reviews.py \
  --product "Acme" \
  --url "https://www.g2.com/products/acme/reviews" \
  --competitor "Rival=https://www.trustpilot.com/review/rival.com" \
  --months 3 --yes --max-cost-usd 2.00 \
  --output ${WORKSPACE}/reviews.json
```

Python 3 stdlib only. Picks an Apify review actor per host (G2 / Capterra / Trustpilot)
and runs it via a **managed async run/poll lifecycle** (start the run, poll to terminal
with backoff + a wall-clock timeout, then fetch the dataset) under a **cost gate** — no
more fragile `run-sync` that could time out or overspend on a 500-item scrape. Normalizes
to rows: `{product, source, rating, title, body, pros, cons, reviewer_role,
reviewer_company, date}`, filtered to `--months`. Override the actor with `--actor
owner~actor-name` for non-default sites or accounts. If a review-page URL is unknown,
discover it first with your search tool.

**Cost gate:** `--estimate-only` prints the per-target projection and **exits 0 without
spending**. Starting any run **requires `--yes`** (else it refuses, non-zero exit). Each
target's run is **aborted** if reported usage exceeds `--max-cost-usd` (default `2.00`,
applied per target since this composite may scrape several) or the `--apify-timeout`
(default `600s`) trips. The keyless Playwright `fetch_page.mjs` default path is **not
gated** (it costs nothing). Run `scrape_reviews.py` without a token and it points you at
the Playwright command above.

### Step 2 — synthesize the digest (you, the agent)

From `reviews.json`, cluster across five lenses and write the digest:

1. **Proof Points Library** — 5-star reviews; **flag every quote containing a number**.
2. **Customer Pain Language** — verbatim "before [product] we were…" phrasing + themes with frequency.
3. **Objection Map** — 3-4 star / cons; frequency + verbatim + how to address.
4. **Competitive Displacement** — per competitor, from their review rows.
5. **SEO/Messaging Vocabulary** — category + comparison terms buyers actually use.

Preserve exact phrasing — verbatim language is the product; don't paraphrase quotes. For
high volume, optionally embed reviews with `pinecone`/`qdrant` to cluster themes.

## Outputs

- `review-digest-[YYYY-MM-DD].md` — the five sections above plus recommended immediate +
  strategic actions and a displacement angle per competitor. Workspace file + Agent Teams
  channel attachment.

## Credentials / env

- **Required:** none. The keyless Playwright `fetch_page.mjs` path renders review pages
  with no key (partial coverage on the most hostile sites).
- **Optional:** `APIFY_API_TOKEN` — if set → Apify review actors (full, reliable, anti-bot
  coverage; cost-gated); if not → keyless Playwright degrade (default). Recommended when
  you need complete coverage. `PINECONE_API_KEY` / `QDRANT_URL` — semantic theme clustering
  at high volume. A residential/Robomotion proxy (`HTTPS_PROXY`) for the `fetch_page.mjs`
  path on blocked sites.

## Notes & edge cases

- Apify is pay-per-result (~$0.20-0.50/product on Capterra/Trustpilot; G2 has a free
  tier) — the script caps at 500 items/run and filters to the window; cache `reviews.json`
  so re-runs don't re-pay.
- Run monthly (reviews move slowly); weekly is wasteful.
- The default actor ids are sensible defaults — if your Apify account exposes a different
  actor for a site, pass `--actor`.
