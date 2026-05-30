---
name: messaging-ab-tester
description: Turn a messaging debate into data — generate 3-5 strategically distinct messaging variants for a value proposition, design a structured A/B test (LinkedIn organic and/or cold email), then normalize and score the returned metrics with a fixed weighting + significance gate to declare a winner and recommend where to deploy it. You (the agent) generate variants and write the narrative; deterministic scripts lay out the test schedule and score the results.
metadata:
  version: 1.0.1
  category: brand
  type: composite
---

# Messaging A/B Tester

A composite that is mostly **your** reasoning: you generate the angle-typed variants and
write the "why it won / what it reveals about ICP psychology" narrative. Two deterministic
scripts keep the test design and scoring consistent — the schedule/split planner and the
weighted scorer with the significance gate.

## When to use

- "Which value prop should we lead with?" / "Test our messaging angles and tell me which works."
- "I can't decide between [message A] and [message B]" for an ICP.
- A seed/Series-A team with enough LinkedIn impressions or cold-email volume (but not enough
  web traffic) to test messaging fast.

## How to run

### 1. Generate variants (you, the agent)

Produce **3–5 variants that test distinct strategic angles, not word tweaks** — choose from
outcome-, pain-, identity-, proof-, contrast-driven. For each, write:
a hypothesis tied to ICP psychology, a LinkedIn post, an email subject line, an email opening
hook, and a website headline. If a **brand-voice-extractor** profile is available, keep all
copy on-voice; if a **launch-positioning-builder** doc exists, pull the value prop from it.

### 2. Design the test (schedule + split + thresholds)

```bash
python3 ${SKILL_DIR}/scripts/test_schedule.py \
  --channel both \
  --num-variants 4 \
  --start 2026-06-02 --post-time 09:00 \
  --linkedin-impressions 6000 --email-list 1200 \
  --output ${WORKSPACE}/schedule.json
```

Emits the LinkedIn consecutive-daily-post plan and/or the even email split, with the
significance thresholds baked in (email >= 50 sends/variant directional, 200+ confident, >20%
relative lift to win; LinkedIn >= 500 impressions/post scorable, single posts directional).

### 3. Deploy (optional)

Either hand the variants + `schedule.json` back to the user to run, or — if the agent is
wired for it — deploy through the connected channels (LinkedIn via the agent's social tooling,
cold-email A/B via the agent's sequencer). The core generate-and-analyze loop needs no
deploy keys; channel keys are only used when auto-deploying (see `env.optional`).

### 4. Collect + normalize results

Accept pasted metrics, a CSV export, or a dashboard screenshot. Normalize into the scorer's
input shape (one array per channel):

```json
{
  "linkedin": [{"variant":"A","impressions":820,"engagements":48,"comment_quality":7,"profile_visits":12}],
  "email":    [{"variant":"A","sends":210,"opens":105,"replies":18,"positive_replies":11}]
}
```

`comment_quality` is a 0–10 rating you assign by reading the comments (quality, not count). If
results arrive as a screenshot, read the numbers from it yourself, then write this JSON; if
extraction is unreliable, ask the user to paste the numbers.

### 5. Score + apply the significance gate

```bash
python3 ${SKILL_DIR}/scripts/score_results.py \
  --input ${WORKSPACE}/results.json \
  --output ${WORKSPACE}/scored.json
```

Applies the fixed weights (LinkedIn engagement 30 / comment_quality 30 / impressions 20 /
profile_visits 20; email open 30 / reply 40 / positive-reply 30), normalizes each metric to
its in-channel max, ranks variants, and emits a per-channel `verdict` with a `confidence`
level that respects the significance gate. It also sets `channels_disagree` when LinkedIn and
email pick different winners.

### 6. Write the results report (you, the agent)

From `scored.json`, write the Markdown report: test-design table, per-channel results tables,
weighted scores, **declared winner with rationale** (respect the verdict's `confidence` — never
upgrade a "directional"/"insufficient" call to "confident"), runner-up, what it reveals about
ICP psychology, recommended deployments (headline / deck / bio / email), and "what to test
next." If `channels_disagree`, surface that as signal — say where each message works best
rather than forcing one global winner.

## Outputs

- `schedule.json`, `scored.json` — deterministic test design + scoring artifacts.
- **Variant set** + **Results report** Markdown — your synthesis, returned as the result and
  saved to the workspace; shareable via the Agent Teams channel.

## Credentials / env

- **Required:** none. Variant generation, scoring narrative, and the deterministic scripts run
  with no key — the agent is the model. The **default (keyless) path** is manual handoff: the
  agent returns the variants + schedule for the user to deploy and the user pastes results back.
- **Optional (auto-deploy / auto-collect upgrades, each with a manual-handoff fallback):**
  - LinkedIn organic — if `PHANTOMBUSTER_API_KEY` (+ LinkedIn cookie) or `APIFY_API_TOKEN`
    (harvestapi LinkedIn actor) is set → auto-post variants and pull analytics. If not set →
    default: agent returns posts + schedule for the user to publish and paste metrics back.
  - Cold-email A/B — if `LEMLIST_API_KEY` or `INSTANTLY_API_KEY` is set → auto-create the
    sequence and pull campaign analytics. If not set → default: agent exports variants + even
    split for the user to run and paste results back.
  - One-off sends — if `SENDGRID_API_KEY` or `RESEND_API_KEY` is set → send test emails
    directly. If not set → default: agent hands the copy to the user to send.
  - The paid gate is only tripped when the agent deploys or pulls analytics automatically; the
    core generate-and-score loop never needs a key. See `env.optional`.

## Notes & edge cases

- Test **angles, not wording** — each variant must be a distinct strategic bet, or the test is
  noise.
- The significance gate is enforced in `score_results.py`: < 50 email sends/variant or < 500
  LinkedIn impressions/post = directional at best, never a "confident" call.
- Different channels may produce different winners — `channels_disagree` flags it; report it as
  "where each message works best."
- LinkedIn tests are organic-only (never boost posts) so the comparison stays clean.
- Align variant labels (A/B/C...) across channels before scoring so rows match.
