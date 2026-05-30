---
name: signal-scanner
description: A scheduled scanner that detects buying signals across a stored TAM and persona watchlist, writes them to a signals store, and sets up downstream activation. Three phases — free diff-based signals, paid scraped signals, then dedup/score/status updates. Always dry-runs before writing.
metadata:
  version: 1.0.1
  category: lead-generation
  type: capability
---

# Signal Scanner

Runs over a `tam-builder`-populated TAM to surface timing-based outreach triggers. **Dry-run
is the default and the script refuses to write without explicit approval.** Storage is
optional: with Supabase env it reads/writes the durable store (recommended); without it,
it reads a TAM CSV/JSON export (`--snapshots`) and writes signals to a workspace file.

## When to use

- After `tam-builder` has populated companies + personas.
- As a recurring (daily/weekly) scan to surface timing-based outreach triggers.

## How to run

### Phase 1 — free diff signals (always run; always dry-run first)

```bash
python3 ${SKILL_DIR}/scripts/signal_scan.py \
  --client acme --config ${WORKSPACE}/signals.json --phase 1 \
  --scope '{"tier":1}'
```

Diffs stored company/person snapshots for headcount growth >10%/90d, tech-stack changes,
and funding rounds. Prints a preview with `mode: DRY_RUN`.

**Keyless storage degrade (no Supabase env):** pass a TAM export and a signals output path:

```bash
python3 ${SKILL_DIR}/scripts/signal_scan.py \
  --client acme --config ${WORKSPACE}/signals.json --phase 1 \
  --snapshots ${WORKSPACE}/tam_scored.csv --signals-out ${WORKSPACE}/signals.json
```

Snapshot rows carry the prior-period fields (`prev_employees`, `prev_tech_stack`,
`prev_funding_stage`); the keyless run is durable only if you reuse the same files.

### Present, then commit (approval gate)

After presenting the dry-run summary to a human and getting a yes:

```bash
python3 ${SKILL_DIR}/scripts/signal_scan.py \
  --client acme --config ${WORKSPACE}/signals.json --phase 1 \
  --commit --approved
```

`--commit` without `--approved` **hard-refuses** and exits.

### Phase 2 — paid scrape scope

```bash
python3 ${SKILL_DIR}/scripts/signal_scan.py --client acme --config ${WORKSPACE}/signals.json --phase 2
```

Emits the company targets + job titles to scrape. Run `job-posting-intent` and the LinkedIn
engager skills over them (metered — gate by `scan_scope`/tier), then feed results to Phase 3.

### Phase 3 — dedup, score, write (with approval)

```bash
python3 ${SKILL_DIR}/scripts/signal_scan.py --client acme --config ${WORKSPACE}/signals.json \
  --phase 3 --results ${WORKSPACE}/scraped_signals.json --commit --approved
```

`signals.json` enables/disables each signal type and sets thresholds + `job_titles`. Table
names override via `SIGNAL_COMPANIES_TABLE` / `SIGNAL_SIGNALS_TABLE` / `SIGNAL_LOG_TABLE`.

## Outputs

A preview (dry-run) or written rows: detected signals (`company, signal_type, evidence,
priority, score`) → `signals`; an `enrichment_log` row; patched company/person snapshots.

## Credentials / env

- **Required:** none. Phase 1 runs keyless against a `--snapshots` TAM export; Phase 2 emits
  scrape *scope* only (the agent runs the engager/jobs skills, each with its own degrade).
- **Optional:**
  - `SUPABASE_URL` + `SUPABASE_SERVICE_ROLE_KEY` — if set → durable Supabase TAM/signals store
    (recommended; the substrate `tam-builder` writes). If not → keyless workspace-file
    fallback (`--snapshots` in, `--signals-out`).
  - `APIFY_API_TOKEN` (or `PHANTOMBUSTER_API_KEY` + LinkedIn cookie) — Phase-2 scraped signals
    via the engager/jobs sub-skills; each degrades to a keyless serp/Playwright path without it.
  - `ANTHROPIC_API_KEY` — LLM content analysis (Phase 2 degrades to non-LLM signals without it).
  - `SIGNAL_*_TABLE` — Supabase table-name overrides.

## Notes & edge cases

- **CRITICAL:** never write signals or change lead statuses without explicit approval —
  always `--dry-run` first (the default), present, then `--commit --approved`. Bad signals →
  bad timing. The script enforces this gate.
- Phase 1 is free (diffs) — run it always; Phase 2 (Apify/Phantombuster) is metered — gate
  by `scan_scope`/tier.
- Requires `tam-builder` output to scan against; pairs with `signal-detection-pipeline` for
  ad-hoc, non-TAM scans.
- Proxy + throttle LinkedIn scrapes; respect Apify per-job costs.
