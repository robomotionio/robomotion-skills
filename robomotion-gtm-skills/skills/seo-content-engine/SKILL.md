---
name: seo-content-engine
description: Build and run a compounding SEO content engine for a client end-to-end — audit current state, identify gaps, build keyword architecture by funnel stage, generate a prioritized content calendar, draft content in the client's brand voice, design internal linking, then publish and monitor on an ongoing cadence. A standing engagement (not a one-off report) that orchestrates the SEO sub-skills with mandatory human checkpoints. Requires an answer-engine key (via the AEO sub-step).
metadata:
  version: 1.1.1
  category: seo
  type: playbook
---

# SEO Content Engine

A standing playbook that orchestrates the SEO sub-skills into a compounding engine. It is
mostly agent orchestration + human checkpoints; the only bundled deterministic glue is a
calendar-to-CSV renderer. Each phase reuses a sub-skill's scripts by path.

## When to use

- "Build an SEO content strategy/engine for [client]", "what content should [company] be publishing?".
- A standing engagement, not a one-off report.

## Sub-skills it orchestrates

- **`seo-content-audit`** — content inventory, performance signals, gap matrices, brand voice.
- **`aeo-visibility`** — answer-engine visibility for key queries (this is the env-gating sub-skill).
- **`topical-authority-mapper`** and/or **`programmatic-seo-planner`** — content architecture.
- A content-drafting step — done by you, the agent, primed on the brand-voice profile.

Invoke a sub-skill's scripts by relative path, e.g.:
```bash
python3 ${SKILL_DIR}/../seo-content-audit/scripts/crawl_sitemap.py --domain client.com ...
python3 ${SKILL_DIR}/../aeo-visibility/scripts/query_engines.py --queries-file prompts.json ...
python3 ${SKILL_DIR}/../topical-authority-mapper/scripts/expand_keywords.py --seeds "..." ...
```

## How to run (phased, with checkpoints)

### Phase 1 — Audit current state
Run `seo-content-audit` (inventory, performance, gap matrices, **brand-voice profile**) and
`aeo-visibility` (answer-engine visibility for key queries). Output: a complete picture of
where the client stands. **[Human checkpoint after gap analysis — surface to the team channel, wait.]**

### Phase 2 — Identify content gaps
From the audit, surface competitive gaps, funnel gaps (missing TOFU/MOFU/BOFU), topic gaps,
and comparison gaps. Prioritize by search volume × commercial intent × competitive difficulty
(volume directional unless a paid API is connected).

> **Measured-metric enrichment propagates from the sub-skills.** This playbook ships no
> enrichment adapter of its own — when `DATAFORSEO_LOGIN`/`DATAFORSEO_PASSWORD` are set, the
> `seo-content-audit` / `topical-authority-mapper` / `programmatic-seo-planner` sub-skills run
> their own bundled `scripts/paid_seo.py` (DataForSEO) in their optional enrichment step,
> upgrading volume/difficulty/authority/backlinks from "directional" to "measured". Those
> measured numbers flow up into this playbook's Phase-2 prioritization and Phase-4 calendar
> automatically. Absent creds → the keyless directional path is the default end-to-end; the
> adapter exits gracefully and nothing in the playbook breaks. (Semrush/Ahrefs are alternative
> providers, not implemented.)

### Phase 3 — Build keyword architecture by funnel stage
Expand funnel-stage keyword variants and bucket them:
```bash
python3 ${SKILL_DIR}/../topical-authority-mapper/scripts/expand_keywords.py \
  --seeds "category, use cases, comparisons" --output ${WORKSPACE}/kw.json
python3 ${SKILL_DIR}/../seo-content-audit/scripts/serp_probe.py \
  --queries-file ${WORKSPACE}/kw.json --output ${WORKSPACE}/kw_serp.json
```
Bucket TOFU ("what is [category]", how-to) / MOFU (comparison, how-to-choose) / BOFU
("[Company] vs [Competitor]", "[Competitor] alternatives", pricing/migration); map each
cluster to a content type.

### Phase 4 — Create the content calendar
Sequence by urgency — **BOFU-first** (comparison/alternatives pages, especially if
competitors run attack content), then MOFU, then TOFU + programmatic templates, plus 2–3
editorial/week ongoing. Build the calendar JSON, then render the deliverable:
```bash
python3 ${SKILL_DIR}/scripts/calendar_to_csv.py --input ${WORKSPACE}/calendar.json \
  --capacity 3 --period week --output ${WORKSPACE}/content-calendar-$(date +%F).csv
```
`calendar_to_csv.py` warns (stderr) on any week over `--capacity`. **[Human checkpoint before drafting.]**

### Phase 5 — Draft content (you, the agent)
Per piece: **match the client brand voice from the Phase 1 voice profile** (never draft
without it — it is the quality gate), weave target keywords naturally, build internal links
to related content, add clear CTAs, include schema-markup recommendations. **[Human
checkpoint before publishing.]**

### Phase 6 — Internal-linking architecture
Design the link graph: TOFU→MOFU→BOFU→product/signup; all pages → relevant pillar.

### Phase 7 — Publish & monitor (ongoing cadence)
Publish or hand drafts to the client. Track organic traffic by cluster, rankings by keyword
(recurring `serp_probe.py` checks), and content→signup conversion. Wire a recurring trigger:
weekly publish/monitor, monthly refresh, quarterly re-audit. Persist the metric series to
Supabase if configured; deliver digests to the team channel.

## Outputs

Phase artifacts to the workspace + team channel: audit report + brand-voice profile; gap
analysis with priorities; keyword architecture by funnel stage; the prioritized content
calendar (`content-calendar-*.csv`); drafted pieces in client voice with internal links,
CTAs, schema recs; an internal-linking map; an ongoing performance dashboard.

## Credentials / env

- **Required (inherent):** `PERPLEXITY_API_KEY` — querying answer engines *is* the task of the
  Phase 1 AEO sub-step (`aeo-visibility`), which hard-requires one answer-engine key; a
  sub-skill's hard requirement propagates to the playbook. (Any single answer-engine key the
  AEO sub-step uses satisfies this; Perplexity is canonical.) The additional engines are
  optional and degrade to whatever keys are present.
- **Optional (each with a keyless fallback):**
  - `OPENAI_API_KEY`/`GEMINI_API_KEY`/`TAVILY_API_KEY` — extra AEO engines; absent → that
    engine is skipped.
  - `DATAFORSEO_LOGIN`/`DATAFORSEO_PASSWORD` — if set → the sub-skills' bundled
    `scripts/paid_seo.py` returns measured volume/authority/backlinks; if not → SERP-derived
    directional signals (default; backlinks unavailable). `SEMRUSH_API_KEY`/`AHREFS_API_TOKEN`/
    `KEYWORD_ANALYSIS_API_KEY` are alternative providers (not implemented in the adapter).
  - `SUPABASE_URL`/`SUPABASE_KEY` — performance-tracking history; absent → one-pass only.
  - channel/CMS creds (`SLACK_*` etc.) — auto-publish + digests; absent → drafts + workspace digest.
  - `APIFY_API_TOKEN` — hostile-site crawl fallback for the audit; absent → SERP + sitemap crawl.

## Notes & edge cases

- **Human checkpoints are mandatory** after gap analysis (Phase 1), before drafting (Phase 4),
  and before publishing (Phase 5) — surface each to the team channel and wait for go-ahead.
- **Brand-voice fidelity** is the quality gate on drafts — always prime drafting with the
  audit's voice profile; never draft without it.
- **BOFU-first sequencing** — comparison/alternatives pages ship first; they convert fastest.
- **Degrade gracefully**: without a paid SEO/keyword API, prioritization leans on SERP-derived
  signals (Autocomplete demand, SERP rank, indexation) — flag volumes as directional.
- **Ongoing cadence is the point** — wire the recurring trigger for weekly publish/monitor,
  monthly refresh, quarterly re-audit; store metrics in Supabase to show compounding.
- **Anti-block**: route crawling/audit fetches through Robomotion Proxy + geo for volume.
