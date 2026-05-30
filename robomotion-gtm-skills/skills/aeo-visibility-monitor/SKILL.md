---
name: aeo-visibility-monitor
description: Keep a brand's AI answer-engine visibility under continuous watch — on a recurring schedule re-run the AEO visibility check across Perplexity/ChatGPT/Gemini over a frozen prompt set, persist each run, diff against history, and alert the team only when mention rate, prominence, or share-of-voice materially moves (a competitor overtakes you, an engine drops you, a new citation source appears). The recurring wrapper around aeo-visibility. Requires one answer-engine key (Perplexity canonical); durable history defaults to a local JSONL ledger, with Supabase as an optional upgrade.
metadata:
  version: 1.0.1
  category: seo
  type: composite
---

# AEO Visibility Monitor

The recurring/scheduled wrapper around `aeo-visibility`. It inherits all engine-query
and scoring logic from that capability and adds: scheduling, frozen-query-set config,
durable history, deterministic diffing, and no-noise alerting.

> Clean-room note: no source skill of this name existed — it was designed from the
> README one-liner plus the `aeo-visibility` capability. All engine-query and scoring
> logic is inherited from `aeo-visibility`, not reinvented.

## When to use

- "Track AEO over time", "watch our AI visibility", "alert me when ChatGPT stops
  recommending us", "monitor competitor AEO weekly/monthly".
- Any standing AEO mandate rather than a one-off snapshot.

## How to run

Scripts are Python 3 stdlib only. Use `${WORKSPACE}` for scratch files.

### 1. Schedule the recurring run

Register a recurring trigger at the configured cadence (default weekly). On the
Robomotion platform this is a Cron/scheduled trigger firing the agent's flow; in this
harness, wire it via the scheduling mechanism available to you. Each fire runs steps 2–5.

### 2. Resolve the FROZEN config

On the **first run only**, generate the ~50 buyer-intent prompts (as in `aeo-visibility`),
get human review, then **freeze** them — store the prompt set, competitors, and engine
list durably. Later runs reuse the frozen set verbatim; changing prompts between runs
breaks comparability (note any deliberate change as a baseline reset).

### 3. Query engines + score (inherited from aeo-visibility)

```bash
python3 ${SKILL_DIR}/scripts/query_engines.py \
  --queries-file ${WORKSPACE}/frozen_prompts.json \
  --engines perplexity,openai,gemini \
  --output ${WORKSPACE}/responses.json
```

Then **you, the agent, score** each response into a metrics blob (see `diff_runs.py`
docstring for the exact shape): `{domain, timestamp, complete, overall, per_engine,
competitor_sov, competitor_citations, source_domains}`. Mark `complete:false` if any
engine errored, so the diff is skipped (avoids false drop-to-zero alerts). Write it to
`${WORKSPACE}/scored_run.json`.

### 4. Persist + diff against the prior run (script)

```bash
python3 ${SKILL_DIR}/scripts/diff_runs.py \
  --run ${WORKSPACE}/scored_run.json \
  --threshold 0.05 \
  --history ${WORKSPACE}/aeo_history.jsonl \
  --output ${WORKSPACE}/diff.json
```

`diff_runs.py` appends the run to durable history (**Supabase** when `SUPABASE_URL`/
`SUPABASE_KEY` are set — table `aeo_runs(domain, ts, payload jsonb)`; otherwise the
local JSONL ledger given by `--history`) and computes deltas: overall + per-engine
mention rate, prominence, share-of-voice vs each competitor, new/lost competitor
citations, new cited source domains. It emits an `alert` verdict on threshold crossings,
competitor overtakes, or drop-to-zero events. First run returns `baseline: true`.

### 5. Alert on material change (you, the agent)

If `diff.json` has `alert: true`, narrate the change (what/where/since-when + a suggested
action) and push it to the alert channel (Slack/Discord/Telegram, or write to the
workspace if no channel is configured). If `baseline: true`, emit "baseline established",
not an alert. Otherwise stay silent and just update the trend artifact.

## Outputs

- Per-cycle run appended to durable history (Supabase or JSONL), keyed by domain + timestamp.
- `diff.json`: deltas, new/lost competitor citations, new source domains, alert verdict.
- Trend artifact (markdown/CSV, agent-written) of the metric series over time.
- A threshold-triggered alert only when a material change occurs (silent when stable).

## Credentials / env

- **Required (inherent):** `PERPLEXITY_API_KEY` (or another single answer-engine key the
  `query_engines.py` run uses) — querying answer engines *is* the task, so one engine key
  stays required; the core engine query is dead without one. The additional engines are
  optional and the run degrades to whatever keys are present.
- **Optional:**
  - `OPENAI_API_KEY`, `GEMINI_API_KEY`, `TAVILY_API_KEY` — each gates only its own engine;
    absent → that engine is skipped, not a failure.
  - Storage — `SUPABASE_URL`/`SUPABASE_KEY`: if set → `diff_runs.py` persists each run to
    Supabase (durable, shareable). If not → the **default** keyless fallback is a local
    JSONL ledger via `--history <path>` (the step above always passes it), so the monitor
    runs fully without Supabase. `diff_runs.py` only exits if *neither* is available, and
    the skill always supplies `--history`.
  - Channel creds (`SLACK_*`/`DISCORD_*`/`TELEGRAM_*`) — needed only if alerting to a
    channel; absent → write the alert to the workspace.

## Notes & edge cases

- **Freeze the query set** after the first run — comparability depends on it.
- **No-noise alerting**: only fire on a threshold crossing or a hard event (overtake /
  drop-to-zero); otherwise update the trend silently.
- **Cost compounds with cadence** — weekly × 50 prompts × N engines adds up; keep the
  default engine set to 3 and let the user opt into more.
- **Partial-failure cycles**: mark the run `complete:false`; `diff_runs.py` then skips the
  diff rather than emitting false "dropped to zero" alerts.
- **First run** produces no diff — `diff_runs.py` returns `baseline: true`; emit "baseline
  established" instead of an alert.
