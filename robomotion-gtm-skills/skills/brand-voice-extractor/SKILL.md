---
name: brand-voice-extractor
description: Analyze a company's published content (blog posts, landing pages, case studies) and produce an actionable Brand Voice Profile — tone, vocabulary, sentence structure, formatting habits, and target persona — so later outreach, content, or campaigns sound like the existing brand. Deterministic scripts fetch and measure the corpus; you (the agent) write the voice profile. Keyless fetch.
metadata:
  version: 1.0.1
  category: brand
  type: capability
---

# Brand Voice Extractor

Fetch a brand's published pages, strip them to clean body text, compute deterministic
style metrics (readability, sentence/paragraph length, POV pronoun mix, header/list
density), then **you synthesize** the Brand Voice Profile from that evidence. The scripts
do only I/O and measurement — all voice/tone judgement is yours.

## When to use

- Before writing content/outreach/campaigns that must sound like an existing brand.
- "Extract brand voice for [company]" / "match [client]'s tone."
- Onboarding a new client with no voice/style guide.
- Upstream feeder for messaging, positioning, or content-generation skills.

## How to run

Scripts are Python 3 stdlib-only (no install). The JS fallback needs Playwright.

### 1. (Optional) Discover candidate URLs from a blog/site root

When you only have a root URL, enumerate + classify candidates (sitemap first, then crawl):

```bash
python3 ${SKILL_DIR}/scripts/discover_urls.py \
  --root https://acme.com/blog \
  --max 200 \
  --output ${WORKSPACE}/candidates.json
```

Then **you select a diverse 10–20 sample** from `candidates.json` — favor blog posts
(~8–10: how-to, opinion, product), 2–3 landing pages, 2–3 case studies, 1–2 comparison
pages; mix recent + older to catch voice evolution. Blog posts carry the strongest voice
signal; landing pages are formulaic — weight blogs.

### 2. Fetch + measure the chosen pages

```bash
python3 ${SKILL_DIR}/scripts/fetch_content.py \
  --company "Acme" \
  --urls https://acme.com/blog/a https://acme.com/blog/b ... \
  --num-pages 15 \
  --output ${WORKSPACE}/corpus.json
```

`corpus.json` has per-page `{url, title, word_count, text, metrics{...}}` plus a
`corpus_metrics` roll-up. Pages that come back as thin text (`errors[].error` mentions
"JS-rendered") should be re-fetched with the Playwright fallback:

```bash
# one-time: npx playwright install chromium   (and: npm --prefix ${SKILL_DIR}/scripts install)
node ${SKILL_DIR}/scripts/fetch_content_js.mjs \
  --company "Acme" \
  --urls https://acme.com/blog/js-page ... \
  --output ${WORKSPACE}/corpus-js.json
```

### 3. Synthesize the Brand Voice Profile (you, the agent)

Read `corpus.json` (+ any `corpus-js.json`) and write a Markdown **Brand Voice Profile**:

1. **Voice summary** — 2–3 sentences capturing the overall voice.
2. **Tone profile table** — formality, emotional register, authority stance, humor,
   directness; attach a **real quote** from the corpus as evidence per dimension.
3. **Language & vocabulary** — reading level (use `flesch_*` from metrics), jargon level,
   power words, signature phrases, words loved/avoided.
4. **Structure & formatting** — sentence/paragraph length (from metrics), header/list/
   emphasis density (from the `h`/`li`/`ul_ol`/`strong_em` counts), CTA + callout habits.
5. **Audience / persona** — target reader, knowledge assumptions, POV (use `pov_totals`:
   we/our vs I/me vs you to infer first-person-plural vs second-person address).
6. **Do / Don't writing guidelines** + 2–3 "how to match it" sample sentences on a neutral
   topic.
7. **Inconsistencies** — flag content types whose metrics/tone diverge sharply (possible
   multiple voice modes or ghost-writers) rather than averaging them away.

## Outputs

- `corpus.json` (and optional `corpus-js.json`) — deterministic fetch + metrics artifact.
- **Brand Voice Profile** Markdown (`brand-voice-profile-<company>.md`) — your synthesis,
  returned as the result and saved to the workspace; for team use, post to the Agent Teams
  channel rather than an invented path.

## Credentials / env

- **Required:** none. Page fetch is keyless (public HTTP); the keyless path is the default.
- **Optional (paid upgrades, each with a keyless fallback):**
  - `APIFY_API_TOKEN` — if set → route a too-hostile blog page through an Apify
    article-extractor actor. If not set → default keyless path: `fetch_content.py` (stdlib),
    then the Playwright fallback `fetch_content_js.mjs`. Apify is the last resort, never required.
  - `DATAFORSEO_LOGIN`/`DATAFORSEO_PASSWORD` (or `SERPER_API_KEY`/`SEARCHAPI_API_KEY`) — if set
    → use SERP to discover the brand's best content URLs (better recall on sites with no/partial
    sitemap). If not set → default keyless `discover_urls.py` (sitemap.xml → same-host crawl).
- Voice/tone synthesis is done by you (the host agent) — no LLM key is consumed by the
  scripts. See `env.optional`.

## Notes & edge cases

- 15 pages is the sweet spot: <10 misses variation, >25 adds cost without signal.
- `fetch_content.py` flags thin pages (`< --min-words`, default 80) as likely JS-rendered —
  escalate those to `fetch_content_js.mjs` before giving up.
- `discover_urls.py` tries `sitemap.xml` (incl. sitemap index) first, falls back to crawling
  same-host links on the root; it drops asset/tag/author/pagination URLs.
- All scripts back off on HTTP 429/503 and space requests (0.3s) to one domain. For heavy
  fetching from a single host behind IP limits, route through a proxy at the platform layer
  and/or reduce `--num-pages`.
- Metrics are deterministic facts (readability, lengths, pronoun counts) — score the voice
  from those real numbers, don't guess.
