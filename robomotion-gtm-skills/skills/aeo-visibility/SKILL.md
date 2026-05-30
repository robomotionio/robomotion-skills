---
name: aeo-visibility
description: Measure a brand's visibility across AI answer engines (Perplexity, ChatGPT/OpenAI, Gemini, Tavily) — how often and how prominently it is mentioned, and where competitors get cited instead — then audit the site's AI-readability and produce prioritized recommendations. Use for a one-shot AEO baseline ("how visible are we in ChatGPT/Perplexity?", "audit our site for AI search"). Requires at least one answer-engine API key (Perplexity is canonical).
metadata:
  version: 1.0.1
  category: seo
  type: capability
---

# AEO Visibility

A one-shot Answer-Engine-Optimization snapshot: query the engines with buyer-intent
prompts, capture answers + citations, then **you, the agent, score** mention rate,
prominence, and share-of-voice and write the recommendations. The script queries
engines; it does not score — scoring is your job. This is the legitimate paid-API case.

## When to use

- "How visible are we in ChatGPT/Perplexity?", "check our AEO", "are AI engines
  recommending us?", "audit our site for AI search".
- A first-time AEO baseline for a domain. For scheduled/recurring tracking, use
  `aeo-visibility-monitor` (which wraps this).

## How to run

Scripts are Python 3 stdlib only. Use `${WORKSPACE}` for scratch files.

### 1. Generate the prompt set (you, the agent)

From the company description, generate ~50 buyer-intent prompts a prospect would ask an
AI ("best X tool for Y", "alternatives to Z", "how to do W"). Surface a 10-prompt batch
for human review before committing the full set. Write them to `${WORKSPACE}/prompts.json`
(a JSON array of strings). Auto-discover competitors by including a "who are the main
competitors of {company}" prompt in an exploratory call.

### 2. Query the answer engines (script — the API case)

```bash
python3 ${SKILL_DIR}/scripts/query_engines.py \
  --queries-file ${WORKSPACE}/prompts.json \
  --engines perplexity,openai,gemini \
  --output ${WORKSPACE}/responses.json
```

Each engine is gated by its own key (`PERPLEXITY_API_KEY`, `OPENAI_API_KEY`,
`GEMINI_API_KEY`, `TAVILY_API_KEY`); engines without a key are **skipped, not fatal**.
At least one key must be set. Output is `{query, engines:{engine:{answer, citations, error}}}`.
**Cost**: ~50 prompts × N engines per run — confirm with the user before the full run.

### 3. Score each response (you, the agent — no script)

For every response, judge: is `company_name`/`domain` mentioned? how prominently (first
sentence / list position)? which competitor brands and which source domains appear?
Aggregate into mention rate, prominence, and share-of-voice — overall, per-engine,
per-query. All-zero visibility is a valid baseline ("AI engines aren't mentioning you yet"),
not an error.

### 4. Site AI-readability audit (mode=audit)

```bash
python3 ${SKILL_DIR}/scripts/fetch_page.py \
  --urls-file ${WORKSPACE}/key_pages.json \
  --output ${WORKSPACE}/page_signals.json
```

`fetch_page.py` returns title, meta, headers, word count, lists, links, and schema.org
types per page. From these, score the 6 dimensions (Positioning Clarity, Structured
Content, Query Alignment, Technical Signals, Content Depth, Comparison Content) and roll
up to a 0–10 overall with best/worst pages. If a page returns no HTML (JS-rendered), the
script flags it — fall back to a browser tool (Robomotion `web-automation`).

### 5. Recommendations + report (you, the agent)

Derive visibility gaps, source opportunities (frequently-cited domains to pitch),
competitor insights, and prioritized actions. Return a conversational summary with 2–3
concrete next steps — not raw dumps.

## Outputs

- Visibility report: overall/per-engine mention rate, prominence, share-of-voice;
  per-query brand-vs-competitor citation breakdown; cited source domains.
- Site AI-readability audit (mode=audit): 0–10 overall + 6 dimension scores with per-page highlights.
- Recommendations (mode=recommend): gaps, source opportunities, competitor insights, prioritized actions.
- Raw artifacts: `responses.json`, `page_signals.json`.

## Credentials / env

- **Required (inherent):** `PERPLEXITY_API_KEY` — querying answer engines *is* the task, so
  one engine key stays required; there is no synthetic fallback for "what does ChatGPT/
  Perplexity say about us". Perplexity is the canonical default engine and competitor-
  discovery path. The additional engines are optional and the run degrades to whatever keys
  are present. (If you wire a different single engine, set that one instead — the script
  needs at least one of the engine keys.)
- **Optional:** `OPENAI_API_KEY` (ChatGPT engine), `GEMINI_API_KEY` (Gemini engine),
  `TAVILY_API_KEY` (cited-web fallback) — each gates only its own engine; absent → skipped.
  `SUPABASE_URL`/`SUPABASE_KEY` — persist the run for later diffing (powers the monitor);
  absent → single-shot only, acceptable for a one-off.

## Notes & edge cases

- **No LLM key needed for scoring** — the host agent is the model; scoring/synthesis is
  prose-instructed here, not a script call.
- **Cost**: surface a dry-run estimate (≈ prompts × engines) and confirm before the full run.
- **Partial run failure**: each engine returns its own `error` field — report per-engine
  success/failure rather than failing the whole run; never silently swallow an engine error.
- **No paid SEO API** is involved — this is purely answer-engine querying + agent scoring.
