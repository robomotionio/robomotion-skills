---
name: battlecard-generator
description: Research one competitor from every public angle — website/messaging, G2/Capterra reviews, ads, social chatter, and pricing — and synthesize an opinionated sales battlecard (positioning traps, landmine questions, objection handlers, win/loss themes). Use when prepping reps for competitive deals or building a competitive program. Keyless backbone; the agent does all synthesis.
metadata:
  version: 1.0.1
  category: competitive-intel
  type: composite
---

# Battlecard Generator

Composite: deterministic scripts collect public competitor signal (pages, reviews, ads,
pricing); **you, the agent, do all scoring and write the battlecard**. Scoped to ONE
competitor — breadth dilutes the card.

## When to use

- "Build a battlecard against [competitor]." / "Help me win deals against [competitor]."
- "We keep losing to [competitor] — why? What weaknesses can we exploit?"
- Prepping a sales team for competitive deals or entering a market with an incumbent.

## How to run

### 1. Capture competitor pages (keyless)

```bash
python3 ${SKILL_DIR}/scripts/fetch_pages.py \
  --url https://competitor.com https://competitor.com/pricing \
        https://competitor.com/about https://competitor.com/product \
  --output ${WORKSPACE}/competitor_pages.json
```

Returns per page: title, meta description, headings, paragraphs, list items,
`candidate_claims` (hero/value-prop lines), links, and `stats.likely_js_rendered`.

If a page has `likely_js_rendered: true` (or `error`), re-fetch it rendered:

```bash
npx playwright install chromium   # first run only
node ${SKILL_DIR}/scripts/render_page.mjs \
  --url https://competitor.com/pricing --output ${WORKSPACE}/competitor_pricing_rendered.json
```

### 2. Mine reviews (G2 / Capterra — JS + anti-bot, use the renderer)

Find the review URL with your own web search (`"[competitor]" site:g2.com` /
`site:capterra.com`), then render it:

```bash
node ${SKILL_DIR}/scripts/render_page.mjs \
  --url "https://www.g2.com/products/<competitor>/reviews" \
  --selector "[itemprop='review'], .paper--white" \
  --output ${WORKSPACE}/g2_reviews.json
```

`selected.text` holds the review blocks. Pull top praised features (their moat) and top
complaints (your attack angles). If blocked, fall back to `APIFY_API_TOKEN` (see Notes).

### 3. Ads & social signal

- Ads: render Meta Ad Library / Google Ads Transparency Center result pages with
  `render_page.mjs` (use `--wait 6000`, they hydrate slowly).
- Social/community: use your own web search for `"[competitor]" site:reddit.com` and
  community frustrations; render specific threads if needed.

### 4. Synthesize the battlecard (you, the agent — no script)

Read all the collected JSON and write an **opinionated** markdown battlecard with:
30-second quick reference, competitor overview, positioning traps, landmine questions,
objection handlers, honest feature comparison (Them / Us / Net), "their customers say"
(real review quotes only), pricing comparison + attack angle, win/loss themes, and
ready-to-paste email/chat responses. Stamp date + a confidence rating keyed to data
freshness. "Where We Lose" must include mitigation, not just admission.

Save to `${WORKSPACE}/battlecard-[competitor]-[YYYY-MM-DD].md` and post as a channel
attachment.

## Outputs

- `${WORKSPACE}/competitor_pages.json`, `g2_reviews.json`, etc. — raw collected signal.
- `${WORKSPACE}/battlecard-[competitor]-[date].md` — the rep-facing battlecard (your synthesis).

## Credentials / env

- **Required:** none — `fetch_pages.py` and `render_page.mjs` are keyless; synthesis is
  the agent (platform-default model).
- **Optional:** `APIFY_API_TOKEN` — deeper G2/Capterra/Reddit scraping when the renderer
  is blocked. Degrades to keyless fetch + browser without it. `DATAFORSEO_LOGIN`/
  `DATAFORSEO_PASSWORD` or `SERPER_API_KEY` — if set, the review/ad/social discovery
  searches use a paid SERP; if not, the agent's own web search (the default) does them.

## Notes & edge cases

- G2/Capterra and ad libraries are hostile, JS-heavy targets — always use `render_page.mjs`
  (a real headless browser), not the urllib fetcher. Escalate to Apify only on a hard block.
- Apify degrade path (when set):
  `curl -s "https://api.apify.com/v2/acts/<actor>/run-sync-get-dataset-items?token=$APIFY_API_TOKEN" -H 'Content-Type: application/json' -d '{...}'`
- Keep it to ONE competitor. Output must be opinionated, not a neutral feature grid.
- Never invent review quotes or ad copy — if a section can't be retrieved, mark it
  "[NEEDS VERIFICATION]" and still ship the card from website + pricing.
- Stamp data freshness and confidence; reviews and ads age fast.
