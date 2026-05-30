---
name: pipeline-review
description: Pull deals from any CRM (HubSpot/Salesforce/Pipedrive/Close/CSV), compute pipeline metrics across seven dimensions (volume, qualification, source attribution, stage velocity, stuck deals, win/loss, forecast/coverage), and produce a one-page executive summary plus a detailed diagnostic with data-cited, prioritized recommendations. Tool-agnostic; metrics are computed, narrative is the agent's.
metadata:
  version: 2.0.1
  category: research
  type: composite
---

# Pipeline Review

Two deterministic scripts pull and crunch the pipeline; **you, the agent, write the exec
summary, the diagnostic, and the recommendations.** Numbers stay computed (trustworthy);
the model only narrates and selects recommendations.

> **v2.0.0 — depth upgrade.** `analyze_pipeline.py` now computes per-stage age/velocity,
> stage-to-stage conversion, weighted pipeline (amount × stage-probability), slippage rate,
> per-owner win rate + avg deal size, and tiered forecast coverage. This SKILL.md carries
> the full metric taxonomy, recommendation-logic tables, and a complete output skeleton.

## When to use

- "Review my pipeline", "deal review", "how's our pipeline looking".
- "1:1 prep", "board meeting prep", weekly/monthly/quarterly sales review.

## How to run

### Step 1 — pull deals (deterministic)

```bash
python3 ${SKILL_DIR}/scripts/fetch_deals.py --crm hubspot --output ${WORKSPACE}/deals.json
```

CRMs: `hubspot`, `pipedrive`, `close`, `salesforce`, or keyless `csv`:

```bash
python3 ${SKILL_DIR}/scripts/fetch_deals.py --crm csv --csv ${WORKSPACE}/export.csv \
  --map "name=Deal Name,stage=Stage,amount=Amount,source=Source,created_at=Create Date,closed_at=Close Date" \
  --output ${WORKSPACE}/deals.json
```

Emits the standard record `{id, name, stage, amount, source, created_at, closed_at,
owner}`. For a comparison trend, pull the prior same-length window into a second file.

### Step 2 — compute metrics (deterministic)

```bash
python3 ${SKILL_DIR}/scripts/analyze_pipeline.py --deals ${WORKSPACE}/deals.json \
  --stage-order "Lead,Qualified,Demo,Proposal,Negotiation,Closed Won,Closed Lost" \
  --qualified-stages "Qualified,Demo,Proposal,Negotiation" \
  --won-stages "Closed Won" --lost-stages "Closed Lost" \
  --period-start 2025-01-01 --period-end 2025-03-31 \
  --expected-cycle-days 45 --target-pipeline 500000 --quota 400000 \
  --stage-probabilities "Lead=0.05,Qualified=0.2,Demo=0.4,Proposal=0.6,Negotiation=0.8" \
  --output ${WORKSPACE}/metrics.json
```

`--stage-order` (ordered funnel) unlocks stage-to-stage conversion; `--stage-probabilities`
sets weighted-pipeline factors (a sensible built-in ramp is used for any stage you omit);
`--quota` drives the weighted-coverage tier. Run again on the comparison-period deals for
trends.

### Metric taxonomy (what every block means)

| Block | Field | Definition / how to read it |
|---|---|---|
| **volume** | `total/open/won/lost`, `open_pipeline_value` | Raw funnel size. Open count without open value = amount hygiene gap. |
| **qualification** | `qualification_rate` | Qualified+won ÷ total. <40% on inbound-heavy = leaky top; >80% = stages too loose. |
| **source_attribution** | per-source `deals/won/won_value/win_rate` | Where revenue truly comes from. Compare win_rate, not volume — a low-volume/high-win source is the scale target. |
| **per_stage** | `open_deals/open_value/weighted_value/avg_age_days/median_age_days` | Per-stage concentration + how long deals sit. avg_age ≫ median = a few zombies skewing it. |
| **stage_conversion** | per-step `conversion_rate` | % that advance from stage→next. The lowest step is your bottleneck; size the fix by the value pooled there. |
| **velocity** | `avg/median_cycle_days_won` | Won-deal cycle time. Median is the honest number; avg − median gap = long-tail deals. |
| **stuck_deals** | list sorted by `age_days` | Open > expected cycle. These are the 1:1 action list. |
| **slippage** | `slippage_rate` | Open deals past their expected close ÷ open deals with a close date. >30% = forecast you can't trust / sandbagged dates. |
| **win_loss** | `win_rate`, `avg_won_amount` | Closed-won ÷ closed. Segment by owner/source before drawing conclusions. |
| **by_owner** | per-owner `win_rate/avg_won_amount/open_pipeline_value` | Coaching + capacity signal. Low win_rate + high open value = at-risk number. |
| **forecast** | `weighted_pipeline_value`, `coverage_ratio`/`tier`, `weighted_coverage_ratio`/`tier` | Σ(amount×stage-prob) is the realistic call. Coverage tiers below. |

**Forecast coverage tiers** (open or weighted ÷ target/quota): `healthy ≥4.0` · `adequate
≥3.0` · `thin ≥2.0` · `at-risk <2.0`. Raw coverage uses open pipeline ÷ target; weighted
coverage uses weighted pipeline ÷ quota and is the one to trust for a forecast call.

### Recommendation logic (metric → diagnosis → action)

| If the metric says… | Likely diagnosis | Recommended action |
|---|---|---|
| One `stage_conversion` step ≪ the others | Bottleneck stage (e.g. Demo→Proposal) | Inspect those deals; fix the stage exit criteria / enablement for that motion. |
| `avg_age_days` high in a mid-stage | Deals stalling, not dying | Force a next-step or disqualify; add a stage-age SLA. |
| `slippage_rate` > 0.3 | Dates are fiction / deals slipping | Re-date every slipped deal with a real reason; tighten close-date discipline. |
| `weighted_coverage_tier` = thin/at-risk | Not enough realistic pipeline to hit quota | Trigger pipeline-gen now; don't wait for stage math to fix itself. |
| A `by_owner` rep: low win_rate + high open value | Rep needs deal help or has junk pipeline | Deal coaching + scrub their open deals for stage accuracy. |
| `qualification_rate` very high but win_rate low | Stages entered too early (sandbagging the top) | Tighten qualification gate; recount what "Qualified" requires. |
| A `source` with high win_rate, low volume | Under-invested winning channel | Shift spend/effort toward it; it's the scale lever. |
| `median_cycle_days_won` ≫ expected cycle | Slow motion / multi-threading gap | Map the slow step; add mutual action plans. |

### Step 3 — write the report (you, the agent)

Read `metrics.json` and write an **executive summary** + a **detailed diagnostic**, every
claim citing the metric that drove it. Use the `data_quality` block to caveat any section
its gaps undermine (mostly-blank `source` → caveat attribution; `stages_without_probability`
→ note the weighted figure under-counts those stages; high `open_deals_missing_expected_close`
→ slippage is partial).

**Output skeleton (fill, don't invent numbers):**

```markdown
# Pipeline Review — [Period]

## Executive Summary
| Metric | Value | vs prior / benchmark |
|---|---|---|
| Open pipeline | $X (N deals) | … |
| Weighted pipeline | $X | … |
| Coverage (weighted ÷ quota) | X.X× — [tier] | … |
| Win rate | X% | … |
| Avg won deal | $X | … |
| Median cycle (won) | N days | … |
| Slippage rate | X% | … |

**🔴 Red flags:** [worst conversion step · at-risk coverage · slippage · stuck value]
**🟢 Green lights:** [healthy stages · winning sources · strong owners]
**Top 3 actions:** 1) … 2) … 3) … (each tied to a metric above)

## Diagnostic
### Volume & Qualification — [commentary + rec]
### Source Attribution — [win_rate by source, where to invest + rec]
### Stage Conversion & Velocity — [the bottleneck step + the slow stage + rec]
### Stuck Deals — table (name · stage · amount · age · owner) + per-deal next step
### Slippage & Forecast Integrity — [slippage_rate read + date-discipline rec]
### Win/Loss & Owner Performance — [by_owner table + coaching/capacity rec]
### Forecast & Coverage — [weighted call + coverage tier + pipeline-gen rec]

## Data-Quality Caveats
[which sections are weakened by which blank fields]
```

## Outputs

- `pipeline-review-[YYYY-MM-DD].md` — exec summary + diagnostic + stuck-deal action list +
  structured recommendations. Workspace file + Agent Teams channel attachment; optional
  export to Sheets/Notion/Slack/email.

## Credentials / env

- **Required:** none. The default `--crm csv` path is keyless (CSV/paste export of deals).
  No LLM key — the report prose is your job as the agent.
- **Optional:** if a CRM key is set (`HUBSPOT_API_KEY` / `PIPEDRIVE_API_TOKEN` /
  `CLOSE_API_KEY` / `SALESFORCE_ACCESS_TOKEN` + `SALESFORCE_INSTANCE_URL`) → `fetch_deals.py`
  pulls deals live from that CRM; if not → the keyless `--crm csv` path (default).
  Export-target creds (Google Sheets, Notion MCP, `SLACK_*`, an email API) used only if you
  export the finished report.

## Notes & edge cases

- Degrades gracefully: minimum viable = deal name + stage + created date. Missing
  `amount` drops revenue/forecast; missing `source` drops attribution — the script still
  emits every other block and counts the gaps in `data_quality`.
- Stage roles are passed as flags so the skill is CRM-agnostic; map your funnel's exact
  stage names into `--qualified/won/lost-stages`.
- Report depth auto-scales with period length (weekly → volume/stuck; quarterly →
  trends/forecast). Skip trends if no comparison window was pulled.
