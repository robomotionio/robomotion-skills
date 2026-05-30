---
name: kol-content-monitor
description: Track what a defined set of Key Opinion Leaders (KOLs) post on LinkedIn and X, cluster posts into topics, and surface trending narratives early (Convergence / Spike / Underdog / Controversy) with a weekly digest and content-action recommendations. Use to ride a breaking wave instead of creating one. Composite — chains linkedin-profile-post-scraper + x-mention-tracker; the agent clusters topics.
metadata:
  version: 1.0.1
  category: monitoring
  type: composite
---

# KOL Content Monitor

A weekly content-intelligence composite. It scrapes each KOL's recent LinkedIn + X posts,
the **agent** labels each post with a 1-3 word topic, then a deterministic aggregator does
the math (per-topic KOL/post/engagement counts, week-over-week spike detection, signal
tagging). The digest narrative is the agent's.

## When to use

- "What are the top voices in [our space] posting about this week?"
- "Track [list of founders/experts] and tell me what they're saying."
- "Find trending narratives I can contribute to."

## Workflow

### 1. Intake / config

Gather the KOL list `[{name, linkedin, x}]`, `days_back` (7; 30 first run),
`min_reactions` (20; X floor = half), `keywords`. Persist as
`${WORKSPACE}/kol-monitor.json`.

### 2. Scrape LinkedIn (per KOL)

Reliable path: PhantomBuster (`PHANTOMBUSTER_API_KEY` + LinkedIn session cookie). Keyless
degrade (one-off, best-effort) — the bundled Playwright helper:

```bash
node ${SKILL_DIR}/scripts/linkedin_posts.mjs \
  --profile "https://www.linkedin.com/in/foo" --name "Foo" --max 20
```

Set `LINKEDIN_COOKIE` (the `li_at` value) for better results. Keep posts with
`engagement >= min_reactions`.

### 3. Scrape X (per handle)

Chain the sibling `x-mention-tracker` sub-skill with a `from:<handle>` query:

```bash
python3 ../x-mention-tracker/scripts/x_search.py \
  --query "from:foohandle" --since 2025-05-01 --max-posts 30 > ${WORKSPACE}/foo_tweets.json
```

Keep tweets with `likeCount >= min_reactions / 2`. Normalize LinkedIn + tweet records into
one array of `{topic, kol, engagement, comments, url, platform, text}` — **you (the agent)
assign `topic`** (1-3 words) per post.

### 4. Aggregate + tag signals (deterministic)

```bash
python3 ${SKILL_DIR}/scripts/aggregate_signals.py --input ${WORKSPACE}/posts.json \
  --history ${WORKSPACE}/kol_topics.csv --output ${WORKSPACE}/topics.json
```

Tags per topic: **Convergence** (≥3 KOLs), **Spike** (≥2× last week), **Underdog** (1 KOL),
**Controversy** (high comment/reaction ratio). Reads + appends a per-topic weekly-count
history CSV so Spike works across runs.

### 5. Synthesize digest (agent)

Read `topics.json`, pick best posts per topic, build the top-engagement table and emerging
topics, write content-action recommendations (this week / next week), and render markdown to
`output_path` (default `kol-monitor-[DATE].md`).

## Outputs

A markdown digest (workspace file / Agent Teams attachment): tracked-KOL counts, trending
topics with signal tags, best posts per topic + links, top-engagement table, emerging topics,
recommended content actions. Post/topic history persisted for spike detection.

## Credentials / env

- **Required:** none — both scrapers degrade keyless and synthesis is provider-swappable.
- **Optional (paid, if-set/else):**
  - `APIFY_API_TOKEN` — **if set → reliable Apify X scraping** via the `x-mention-tracker`
    sub-skill (cost-gated); **else → that sub-skill's keyless Playwright** (the default).
  - `PHANTOMBUSTER_API_KEY` (+ `LINKEDIN_COOKIE`) — **if set → reliable/at-scale LinkedIn post
    scraping**; **else → the bundled keyless Playwright** `linkedin_posts.mjs` (the default;
    `LINKEDIN_COOKIE` alone still improves it).
  - **KOL-set discovery (SERP):** `DATAFORSEO_LOGIN` / `DATAFORSEO_PASSWORD` (or `SERPER_API_KEY`)
    — **if set → paid SERP** to discover/expand the tracked-KOL list (e.g. "top voices in [space]");
    **else → the host agent's keyless web search** (the default). Discovery feeds the KOL list only;
    it never gates monitoring.
  - `ANTHROPIC_API_KEY` / `OPENAI_API_KEY` — **if set → optional script-side clustering/synthesis**;
    **else → the host agent** does topic labelling + digest synthesis (the default; no LLM key needed).
  - `SUPABASE_URL` / `SUPABASE_KEY` — **if set → Supabase cross-run spike history**;
    **else → workspace CSV** (the default; first run emits no Spike tag).

## Notes & edge cases

- LinkedIn and X are anti-bot heavy — prefer PhantomBuster / Apify; route Playwright
  fallbacks through a proxy and expect lower volume.
- X engagement runs lower than LinkedIn — hence the halved threshold.
- Spike detection needs persisted history; first run emits Convergence/Underdog/Controversy
  only (the aggregator reports `spike_available:false`).
- Schedule weekly to catch the week's peaks; dedup posts by URL across runs.
