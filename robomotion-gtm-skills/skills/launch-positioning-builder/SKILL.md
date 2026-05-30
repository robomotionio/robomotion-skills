---
name: launch-positioning-builder
description: Research the competitive landscape, mine competitor messaging and (optionally) reviews and ad copy, then produce a complete, opinionated positioning document — category definition, competitive alternatives, value propositions, proof-point library, messaging hierarchy, a 2x2 positioning map, and a deployment plan — usable in website copy, sales decks, and investor materials. Deterministic scripts fetch competitor pages and extract positioning signals; you (the agent) build the April-Dunford framework and write the doc.
metadata:
  version: 1.0.1
  category: brand
  type: composite
---

# Launch Positioning Builder

A composite: deterministic scripts pull each competitor's marketing pages and surface their
positioning signals (tagline, hero claim, category language, CTAs), then **you synthesize**
the positioning framework and write the doc. Review mining and ad-copy analysis are optional
enrichment that degrade gracefully.

## When to use

- "Build a positioning doc for [product]" / "We need positioning before our launch."
- "How should we differentiate from [competitor]?" / "Our positioning is too generic."
- A seed/Series-A PMM or founder defining or refreshing positioning ahead of a launch,
  rebrand, or competitive shift.

## How to run

### 1. Fetch competitor marketing pages + positioning signals

```bash
python3 ${SKILL_DIR}/scripts/fetch_competitors.py \
  --competitors "Acme=https://acme.com" "Globex=https://globex.io" \
  --output ${WORKSPACE}/competitors.json
```

Per competitor, tries homepage/pricing/about (+ common variants) and extracts each page's
`title`, `meta_description`, `hero_headline`, `hero_subhead`, `ctas`, and
`positioning_phrases` ("the only ...", "we help ...", "platform for ...", "the #1 ..."). A
competitor flagged `likely_js_rendered: true` (thin static text) should be re-fetched with
the Playwright fallback:

```bash
# one-time: npm --prefix ${SKILL_DIR}/scripts install && npx playwright install chromium
node ${SKILL_DIR}/scripts/fetch_competitors_js.mjs \
  --name "Acme" \
  --urls https://acme.com https://acme.com/pricing https://acme.com/about \
  --output ${WORKSPACE}/acme.json
```

Also fetch **your own** `product_url` the same way so the doc contrasts you against the set.

### 2. (Optional) Review mining + ad-copy analysis — enrichment, degrade gracefully

For competitor G2/Capterra/Trustpilot reviews or Meta Ad Library / Google Ads Transparency
pages (JS/anti-bot), use the Playwright fallback with a screenshot:

```bash
node ${SKILL_DIR}/scripts/fetch_competitors_js.mjs \
  --name "Acme reviews" \
  --urls "https://www.g2.com/products/acme/reviews" \
  --screenshot ${WORKSPACE}/acme-reviews.png \
  --output ${WORKSPACE}/acme-reviews.json
```

If a review site or ad library blocks even Playwright and no `APIFY_API_TOKEN` is set, **proceed
with site + search evidence and note the gap in the doc** — these steps are not blockers.

### 3. Build the positioning framework + write the doc (you, the agent)

Read `competitors.json` (+ JS/review JSON) plus the intake inputs (`product_name`,
`one_sentence_pitch`, `icp`, believed `differentiators`, existing `proof_points`, `trigger`).
If a **brand-voice-extractor** profile is available, pass it through so drafted
headlines/hooks stay on-voice. Then produce the **Positioning Document** (`positioning-<YYYY-MM-DD>.md`):

1. **Positioning statement.**
2. **Category decision** (April Dunford, early-stage-adapted): existing / subcategory / new —
   **rule:** don't create a new category if the ICP already searches the existing one or you'd
   spend >50% of sales calls explaining it.
3. **Competitive landscape table** — tagline / strength / your-wedge per competitor (use their
   `hero_headline` + `positioning_phrases`; complaints from reviews become your wedge).
4. **Value props** — map unique attribute → value prop → proof.
5. **Proof-point library.**
6. **Per-persona messaging hierarchy.**
7. **2x2 positioning map** on dimensions where the product wins >= 1 axis.
8. **"Where to deploy" asset table** (site / deck / investor / email).
9. **"What we're NOT saying"** guardrail list.

Keep it opinionated, not a generic template (built for a first PMM hire / founder).

## Sub-skills this composite chains

- **review-site-scraper** (review mining) — if present in the agent's skill set, prefer its
  scripts for G2/Capterra/Trustpilot over the raw Playwright fallback here.
- **brand-voice-extractor** — optional input; its voice profile keeps drafted copy on-voice.
- The host agent routes between them; the scripts here are the unique competitor-page glue.

## Outputs

- `competitors.json` (+ optional JS/review JSON and screenshots) — deterministic extraction.
- **Positioning Document** Markdown — your synthesis, returned as the result and saved to the
  workspace; share via the Agent Teams channel for the PMM team. Store the structured
  proof-point library for reuse if a table store is available.

## Credentials / env

- **Required:** none. Competitor page fetch is keyless (the default); the positioning synthesis
  is done by you (the agent) — no LLM key is consumed by any script.
- **Optional (paid upgrades, each with a keyless fallback):**
  - `APIFY_API_TOKEN` — if set → route hostile review sites / ad libraries (and any competitor
    page Playwright can't render) through an Apify actor. If not set → default keyless path:
    `fetch_competitors.py` then the Playwright fallback `fetch_competitors_js.mjs`; if even
    Playwright is blocked, proceed with site + search evidence and flag the gap. Last resort,
    never required.
  - `DATAFORSEO_LOGIN`/`DATAFORSEO_PASSWORD` (or `SERPER_API_KEY`/`SEARCHAPI_API_KEY`) — if set
    → use SERP to discover competitor pages, review URLs, and ad-library entries with better
    recall. If not set → default keyless discovery (provided inputs + the agent's own web search
    + direct fetch).

## Notes & edge cases

- Review mining and ad-copy analysis are enrichment, not blockers — if they fail, build from
  site + search evidence and flag the gap.
- Different competitors render differently — `likely_js_rendered` tells you when to escalate to
  Playwright; fetch your own product pages too for a fair contrast.
- Scripts back off on 429/503 and space requests (0.3s); throttle and (at the platform layer)
  route through a geo proxy when scraping many competitor sites to avoid IP blocks.
- The 2x2 image can be rendered downstream for deck use; the doc itself is text/Markdown.
