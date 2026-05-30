---
name: ad-campaign-analyzer
description: Turn raw ad-campaign performance data (Google, Meta, LinkedIn) into clear cut/scale/test decisions — diagnose waste, identify winners, check statistical significance, and produce a concrete cross-channel budget-reallocation plan with scenario modeling and dollar-amount shifts. For founders/paid-media owners who need a specialist's read, not a dashboard summary.
metadata:
  version: 1.0.1
  category: ads
  type: composite
---

# Ad Campaign Analyzer

Composite: **ingest/normalize → diagnostics → significance → funnel → reallocation →
report.** This is fundamentally a **reasoning** skill: the scripts normalize the data and
compute statistical significance deterministically; **you (the agent) do the diagnostics,
verdicts, funnel diagnosis, and the reallocation plan.**

## When to use

- "Analyze my Google/Meta Ads performance" / "Which ads should I kill?"
- "Where am I wasting ad spend?" / "Is this campaign working?"
- "How should I split my budget across channels?" / "Google or Meta?"

## How to run

### 1 — Normalize the data + build the channel rollup

If the input is dashboard screenshots, first OCR/transcribe them into a CSV or JSON (the
agent does this), then:

```bash
python3 ${SKILL_DIR}/scripts/normalize_campaigns.py --csv ${WORKSPACE}/perf.csv \
  --funnel ${WORKSPACE}/funnel.json \
  --output ${WORKSPACE}/normalized.json
```

Maps the many possible column names to a standard schema, derives CTR/CPC/conv-rate/CPA/
ROAS where computable, rolls up per channel, and (when `--funnel` is given with
`lead_to_mql` / `mql_to_sql` / `sql_to_close` / `avg_deal_size`) computes
**funnel-adjusted CAC** per channel. `--funnel` is optional.

### 2 — Diagnostics (you, the agent)

Over `normalized.json`: health-check each item vs. benchmarks (CTR, CPC, conv rate, CPA,
ROAS, impression share); detect waste (zero-conversion items, >3× CPA outliers, low-CTR
ads, broad-match bleed); identify winners (lowest CPA / highest conv-rate keywords, ads,
audiences, times). Label each Scale / Optimize / Pause.

### 3 — A/B significance (deterministic — do NOT eyeball it)

For any A/B pair, call the test so verdicts rest on real math, not a guessed p-value:

```bash
# CTR test (two-proportion z-test)
python3 ${SKILL_DIR}/scripts/ab_significance.py --metric ctr \
  --a-clicks 320 --a-impr 12000 --b-clicks 410 --b-impr 12500

# CPA / conversion-rate test
python3 ${SKILL_DIR}/scripts/ab_significance.py --metric cpa \
  --a-conv 45 --a-clicks 900 --b-conv 60 --b-clicks 880
```

It enforces minimum samples (100 clicks/variant for CTR, 30 conv/variant for CPA) and
returns `enough_data:false` when below them. **If `enough_data` is false, report "not enough
data" — never force a verdict.** You only narrate the returned result.

### 4 — Funnel + reallocation (you)

Diagnose the biggest impression→click→conversion→revenue drop-off. Then build a
**budget-neutral** cross-channel reallocation: efficiency index per channel, marginal-
return / saturation read, funnel-stage coverage gaps, and a dollar-shift table. Keep it
budget-neutral unless the user explicitly asks for a budget-increase scenario. Where target
CPA/ROAS weren't supplied, fetch category benchmarks via web search (Robomotion Proxy):
**if `DATAFORSEO_LOGIN`/`DATAFORSEO_PASSWORD` (or `SERPER_API_KEY`) is set → structured SERP
API; else → the agent's keyless web search (default).**

### 5 — Scenarios + render

Model conservative (±20%), aggressive (±40%), and (if requested) budget-increase scenarios
with projected conversions/CPA. Write `campaign-analysis-<YYYY-MM-DD>.md` to `${WORKSPACE}`
and attach to the Agent Teams channel.

## Outputs

`campaign-analysis-<YYYY-MM-DD>.md` — performance dashboard, budget-waste report ($ +
items), winners to scale, A/B significance verdicts, funnel drop-off diagnosis, channel
efficiency ranking, current-vs-recommended allocation table, 3 scenarios, phased action plan.

## Credentials / env

- **Required:** none — the core path is data-in → analysis-out; `normalize_campaigns.py` and
  `ab_significance.py` are stdlib and keyless. The verdicts/reallocation are the agent's
  reasoning (no LLM key in scripts).
- **Optional (each with a keyless default fallback):**
  - CRM keys (`HUBSPOT_API_KEY` / `SALESFORCE_ACCESS_TOKEN` / `PIPEDRIVE_API_TOKEN`) — if set
    → pull live conversion/close data from the CRM; else → use the supplied performance
    file/CSV (default).
  - `DATAFORSEO_LOGIN`/`DATAFORSEO_PASSWORD` (or `SERPER_API_KEY`) — if set → structured SERP
    API for missing-benchmark lookups; else → the agent's keyless web search (default).

## Notes & edge cases

- No scraping in the core path; a web search is used only to fetch missing benchmarks.
- Significance is computed deterministically (z-test via stdlib `math.erf`), never by the
  LLM — this avoids hallucinated p-values.
- Refuse to over-claim on thin data: surface "not enough data" rather than a forced verdict.
- Keep reallocation budget-neutral unless a budget-increase scenario is explicitly requested.
