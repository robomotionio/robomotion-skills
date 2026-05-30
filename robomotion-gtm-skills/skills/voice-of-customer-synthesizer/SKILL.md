---
name: voice-of-customer-synthesizer
description: Aggregate scattered customer feedback (support tickets, NPS/CSAT, Slack, G2/Capterra reviews, call transcripts, churn surveys, feature requests, social mentions) into a single VoC report — theme clustering, sentiment, trend detection vs prior period, and team-specific (product/CS/marketing) action items. Runs on user-provided data; optional review scraping. Normalization is deterministic; the synthesis is the agent's.
metadata:
  version: 1.0.1
  category: research
  type: composite
---

# Voice of Customer Synthesizer

A deterministic normalizer merges every feedback source into one corpus; **you, the agent,
do the sentiment classification, theme clustering, trend detection, and team-specific
recommendations.** Themes recurring across multiple sources are the most trustworthy.

## When to use

- "What are our customers saying?" / "Build a VoC report for the product team."
- "Synthesize customer feedback from last quarter." / "What themes are coming up?"

## How to run

### Step 1 (optional) — scrape external reviews (keyed)

If a product is listed on review sites and you want them included:

```bash
python3 ${SKILL_DIR}/scripts/scrape_reviews.py --product "Acme" \
  --url "https://www.g2.com/products/acme/reviews" --months 6 \
  --output ${WORKSPACE}/scraped_reviews.json
```

Requires `APIFY_API_TOKEN`. Skip entirely if you only have internal data — the skill runs
fully on user-provided exports.

### Step 2 — normalize all sources into one corpus (deterministic, keyless)

```bash
python3 ${SKILL_DIR}/scripts/normalize_feedback.py \
  --source "tickets=${WORKSPACE}/tickets.csv" \
  --source "nps=${WORKSPACE}/nps.csv" \
  --source "churn_surveys=${WORKSPACE}/churn.csv" \
  --source "feature_requests=${WORKSPACE}/features.csv" \
  --reviews-json ${WORKSPACE}/scraped_reviews.json \
  --output ${WORKSPACE}/corpus.json
```

Each `--source` is `type=path.csv`; columns are matched case-insensitively (date,
customer, segment, text, rating, sentiment). Emits standard rows `{source, type, date,
customer, segment, text, rating, sentiment_hint}` plus by-source counts and a sentiment
hint distribution. The `sentiment_hint` is a keyword/rating pre-tag only — **you refine
sentiment yourself.** For a Slack feedback channel, read it via the Slack tool and pass it
as one more CSV/source.

### Step 3 — cluster + analyze + recommend (you, the agent)

From `corpus.json`: theme clustering bottom-up (topics mentioned by 3+ customers / 3+
sources → themes ranked by frequency × severity; build theme cards with verbatim quotes,
segments affected, root-cause hypothesis, retention/expansion/acquisition impact);
sentiment overview, source comparison (tickets skew negative, reviews bipolar — weight
accordingly), segment analysis, trend detection vs a prior-period corpus (new/resolved
themes). Split recommendations by Product (P0/P1/P2), CS, Marketing. For high volume,
optionally embed items with `pinecone`/`qdrant` to cluster semantically. Preserve exact
quotes for marketing reuse.

## Outputs

- `voc-report-[YYYY-MM-DD].md` — exec summary, sentiment overview (+ net score vs prior),
  top themes ranked by impact (quotes + action + owner), what customers love/want/pain
  points, trends vs prior, team-specific action items, appendix of all theme cards.
  Workspace + Agent Teams channel attachment.

## Credentials / env

- **Required:** none. `normalize_feedback.py` is keyless and the synthesis is your job as
  the agent (no LLM key in the script layer). The skill runs entirely on user-provided
  internal data.
- **Optional:** if `APIFY_API_TOKEN` is set → Apify G2/Capterra/Trustpilot review scraping;
  if not → keyless provided exports + search snippets (default). `SLACK_BOT_TOKEN` (Slack
  feedback-channel read). `PINECONE_API_KEY` / `QDRANT_URL` — if set → semantic theme
  clustering at high volume; if not → the agent clusters directly (default).

## Notes & edge cases

- Works with whatever sources exist — more sources = higher-confidence themes; note source
  overlap. Trend detection needs a prior-period corpus stored; skip trends on first run.
- Tie every recommendation to evidence strength (mention count, source count, churn-signal).
- Apify is pay-per-result — cap to the time window and cache scraped reviews across runs.
