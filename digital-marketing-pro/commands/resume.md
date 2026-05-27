---
description: Resume a long-running DMP workflow (engagement / campaign-plan / content-engine / seo-audit / competitor-analysis / campaign-audit / launch-campaign) that was interrupted partway through
argument-hint: "[workflow] [run-id] (both optional — omit to auto-pick latest in-progress)"
---

# Resume Interrupted Workflow

Pick up a long-running DMP workflow that stopped before the final step — instead of restarting from scratch, load the saved part outputs and continue from the next part.

## Trigger

User runs `/digital-marketing-pro:resume` (with optional `workflow` and/or `run-id` arguments). Also surface this command in any error message when a workflow terminates abnormally.

## What this fixes

DMP's headline workflow `/digital-marketing-pro:engagement` runs the 12-Part Strategy Flow producing 50-60 canonical files in roughly 60 minutes on Opus 4.7. Pre-v3.7.7, if the session terminated partway through (context-window exhaustion, network blip, the user cancels, machine sleeps), the in-memory part outputs were lost and the user had to restart from Part 1. The same applied to `/campaign-plan`, `/content-engine`, `/seo-audit`, `/competitor-analysis`, `/campaign-audit`, `/launch-campaign`.

As of v3.7.7 every part of every long workflow writes its output via `scripts/checkpoint-manager.py`, so a fresh session can reload those artifacts and skip the parts that already completed. This is the direct fix for the v3.12.2-cycle user-team feedback that "dm pro also taking too long to process" — the workflow itself is not made faster, but a single interruption no longer means losing 30+ minutes of work.

## Process

### Step 1: Pick the run to resume

If the user supplied a `run-id`, use it directly. If they supplied only a `workflow` (e.g. `engagement` / `campaign-plan`), filter to in-progress runs of that workflow and pick the most recent. Otherwise list every in-progress run and ask the user to choose if there's ambiguity.

```bash
# Auto-pick the most recent in-progress run for the active brand
python3 ${CLAUDE_PLUGIN_ROOT}/scripts/checkpoint-manager.py resume --brand "{active_brand}"

# Filter to a specific workflow
python3 ${CLAUDE_PLUGIN_ROOT}/scripts/checkpoint-manager.py resume --brand "{active_brand}" --workflow engagement

# Resume a specific run id
python3 ${CLAUDE_PLUGIN_ROOT}/scripts/checkpoint-manager.py resume --brand "{active_brand}" --run-id "{run_id}"

# List everything (use when there are several)
python3 ${CLAUDE_PLUGIN_ROOT}/scripts/checkpoint-manager.py list --brand "{active_brand}"
```

The `resume` action returns the status of the selected run, including `completed_steps`, `remaining_steps`, `next_step`, `next_step_label`, and the absolute path of every saved artifact.

If there are no in-progress runs, say so and offer to start a fresh workflow. Do NOT silently start a new run.

### Step 2: Reload the saved artifacts

For each completed step, load the saved file via `checkpoint-manager.py load` and put its contents back into context:

```bash
python3 ${CLAUDE_PLUGIN_ROOT}/scripts/checkpoint-manager.py load \
    --brand "{active_brand}" --run-id "{run_id}" --step 1
# ... repeat for every step in completed_steps
```

Use the loaded content as the **input** to the next step that has NOT been checkpointed — do not re-execute earlier steps.

### Step 3: Continue from `next_step`

For the `engagement` workflow, hand control to the agent or sub-flow that owns the next part (see the 12-Part Strategy Flow in [`README.md`](../README.md)). After that part finishes, save its output:

```bash
python3 ${CLAUDE_PLUGIN_ROOT}/scripts/checkpoint-manager.py save \
    --brand "{active_brand}" --run-id "{run_id}" \
    --step {step_id} --content-file {tmp_output_path} --extension {md|json}
```

Continue until every step is checkpointed, then:

```bash
python3 ${CLAUDE_PLUGIN_ROOT}/scripts/checkpoint-manager.py finalize \
    --brand "{active_brand}" --run-id "{run_id}" --status completed
```

Optionally bulk-publish every artifact to the user-visible output folder:

```bash
python3 ${CLAUDE_PLUGIN_ROOT}/scripts/output-publisher.py publish-run \
    --brand "{active_brand}" --run-id "{run_id}"
```

### Step 4: Surface the resumption summary

Before continuing, tell the user what's being skipped vs re-run:

```
🔁 Resuming {workflow} run {run_id}
   Topic: {topic}
   Brand: {brand}

   ✅ Already completed (skipping): Part 1, Part 2, Part 3 (Four Core Documents)
   ➡️  Resuming from: Part 4 (Competitive / customer / market analysis)
   📋 Remaining: 4 → 5 → 6 → 7 → 8 → 9 → 10 → 11 → 12

   Estimated remaining time: ~30 min on Opus 4.7 (based on the part-time benchmarks)
```

## Edge cases

- **Resume mid-loop.** If a part failed its quality gate and triggered a loop back to an earlier part, the checkpoint reflects whatever was last saved. The user should re-run that part's quality gate after resuming.
- **Ancient run.** If `last_updated` is more than 7 days old, warn before resuming — market data has drifted, sources may have moved. Offer to start fresh instead.
- **Multiple in-progress runs.** If there are several, list them with `list` and ask which to resume rather than guessing.
- **No checkpoint manager script.** Sessions started before v3.7.7 have no checkpoints. `list` returns an empty `runs` array — tell the user no resumable runs exist and offer to start a new workflow.

## Related

- [`commands/engagement.md`](engagement.md) — the headline 12-Part workflow this command resumes
- [`commands/campaign-plan.md`](campaign-plan.md), [`commands/content-engine.md`](content-engine.md), [`commands/seo-audit.md`](seo-audit.md), [`commands/competitor-analysis.md`](competitor-analysis.md) — other long workflows that benefit from checkpointing
- [`commands/output-folder.md`](output-folder.md) — reveal the user-visible `~/Documents/DigitalMarketingPro/` folder where published artifacts land
- [`scripts/checkpoint-manager.py`](../scripts/checkpoint-manager.py) — the storage layer
- [`scripts/output-publisher.py`](../scripts/output-publisher.py) — the dual-copy publisher
