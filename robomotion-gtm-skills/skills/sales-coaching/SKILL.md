---
name: sales-coaching
description: An AI sales coach that analyzes a rep's own data — email templates + replies, call transcripts, pipeline outcomes — to find what they do well and where they struggle, then produces a personalized skill scorecard, a winning-pattern playbook reconstructed from their best work, a surprise finding, and a 30-day coaching plan. Coaches the worker. Metrics are computed; the coaching synthesis is the agent's.
metadata:
  version: 2.0.1
  category: research
  type: composite
---

# Sales Coaching

Three deterministic analyzers compute the rep's mechanical metrics; **you, the agent, do
the pattern-finding, scorecard, playbook, surprise finding, and 30-day plan.** Every grade
must cite specific metrics/quotes from the rep's own data.

> **v2.0.0 — depth upgrade.** `analyze_calls.py` now computes a **discovery-quality score**
> (question volume + open-vs-closed ratio + MEDDIC/BANT topic coverage), **objection-handling
> detection** (objection cues + whether the rep acknowledged/clarified vs. steamrolled), and
> the won-vs-lost split now includes discovery score and open ratio. This SKILL.md carries
> the discovery & objection rubrics, the role-specific skill tables (SDR/AE/Founder), and
> the recommendation logic.

## When to use

- "Coach me", "how can I improve my sales", "what am I doing wrong", "review my selling style".
- "Why am I losing deals?", "analyze my calls"; periodic self-improvement.

## How to run

Run whichever analyzers match the data the rep has (degrades by availability — any one
source works; emails+calls+pipeline is best).

### Email patterns (deterministic, keyless CSV)

```bash
python3 ${SKILL_DIR}/scripts/analyze_emails.py --input ${WORKSPACE}/emails.csv \
  --top-n 3 --output ${WORKSPACE}/email_metrics.json
```

CSV: `template,sends,replies,positive_replies[,subject,body]`. Returns per-template reply
rates + a top/bottom split (ranking templates with ≥100 sends).

### Call patterns (deterministic, keyless transcripts)

```bash
python3 ${SKILL_DIR}/scripts/analyze_calls.py --input ${WORKSPACE}/calls.json \
  --rep-name "Alex" --output ${WORKSPACE}/call_metrics.json
```

`calls.json` = array of `{call_id, outcome, turns:[{speaker,text}]}`. Returns talk:listen
ratio, rep talk %, longest monologue, question count + **open/closed split**, filler rate,
a **MEDDIC/BANT coverage** flag-set, a **discovery_score (0–100)**, **objection-handling**
detection, and a won-vs-lost split (now incl. discovery score & open ratio). If only audio
exists, transcribe first (out of scope here) — normally transcripts are given.

**Discovery score (0–100)** = question volume (40 pts, full at ~12 Qs) + open-question
ratio (25 pts) + qualification-topic coverage (35 pts across 8 topics). **MEDDIC/BANT
topics detected:** pain · budget · authority · timeline · metrics · champion ·
decision_process · competition. **Objection handling** = for each prospect objection cue,
did the rep's next turn acknowledge/clarify (or ask a question) vs. plow ahead?

### Deal patterns (deterministic, keyless CSV)

```bash
python3 ${SKILL_DIR}/scripts/analyze_deals.py --input ${WORKSPACE}/deals.csv \
  --output ${WORKSPACE}/deal_metrics.json
```

CSV: `deal,stage,amount,outcome,created_at,closed_at,industry,size`. Returns win rate,
win rate by industry/size (sweet-spot/kill-zone), avg cycle, and loss-stage distribution.

### Scorecard rubric (per-skill grade anchors)

Grade each skill A–F against the rep's own metrics — never generic. Anchors:

| Skill | A (strong) | C (developing) | F (problem) | Primary metric |
|---|---|---|---|---|
| **Discovery** | score ≥70, open ratio ≥0.6, ≥6 topics | 40–69, ratio ~0.4 | <40, mostly closed Qs | `discovery_score`, `open_question_ratio`, `topics_covered` |
| **Talk/listen** | 35–45% talk on discovery | 46–60% | >65% talk (monologuing) | `rep_talk_pct`, `longest_rep_monologue_words` |
| **Qualification** | 6–8 MEDDIC/BANT topics | 3–5 | ≤2 (no budget/authority/timeline) | `meddic_bant_coverage` |
| **Objection handling** | handles ≥80% of objections | ~50% | steamrolls (<30%) | `objection_handling_rate` |
| **Conciseness** | filler <2/100w | 2–4/100w | >5/100w | `rep_filler_per_100w` |
| **Email** | reply rate top-quartile of own templates | mid | bottom templates dominate sends | `reply_rate`, `positive_rate` |
| **Deal execution** | win rate ≥ peer, fast cycle | average | loses late-stage repeatedly | `win_rate`, `loss_stage_distribution`, `avg_cycle_days_won` |

### Role-specific emphasis (weight the scorecard by the rep's role)

| Skill dimension | **SDR** | **AE** | **Founder-led sales** |
|---|---|---|---|
| Pipeline generation / prospecting volume | ●●● core | ●● | ●● |
| Email copy & reply quality | ●●● core | ● | ●● |
| Discovery depth (open Qs, pain) | ●● | ●●● core | ●●● core |
| MEDDIC/BANT qualification | ●● (budget/authority/timeline) | ●●● core | ●● (don't over-qualify early) |
| Objection handling | ●● | ●●● core | ●●● core (vision objections) |
| Talk/listen discipline | ● | ●●● core | ●●● core (founders over-pitch) |
| Multi-threading / decision process | ○ | ●●● core | ●● |
| Closing / next-step discipline | ● | ●●● core | ●● |

Read it as: an **SDR**'s scorecard leans on email + prospecting + booking-the-meeting; an
**AE**'s leans on discovery + qualification + objection handling + closing; a **Founder**
selling their own product almost always over-talks and under-discovers — check talk% and
discovery_score first, that's the usual surprise.

### Recommendation logic (metric → diagnosis → exercise)

| Metric pattern | Diagnosis | Coaching exercise |
|---|---|---|
| `open_question_ratio` < 0.4 | Interrogating, not exploring | Replace closed Qs with "what/how/why"; 5 open Qs per discovery call. |
| `rep_talk_pct` > 65% | Monologuing / pitching too early | 40/60 talk target; pause after each value statement and ask. |
| `topics_covered` ≤ 3 (missing budget/authority/timeline) | Deals stall late from no qualification | Run a MEDDIC checklist; never advance a stage without budget+authority+timeline. |
| `objection_handling_rate` low | Steamrolling objections | Acknowledge→clarify→reframe→proof; practice the top 3 objections. |
| won_avg `discovery_score` ≫ lost | Discovery is the differentiator for THIS rep | Make great discovery non-negotiable; reverse-engineer their best call. |
| `rep_filler_per_100w` > 5 | Verbal tics undercut authority | Record + count; pause instead of filling. |

### Synthesize the coaching report (you, the agent)

Read the metrics JSONs **and** the underlying copy/transcripts. Produce: a sales scorecard
(per-skill grades A-F + trend, weighted by the rep's role above), "what you're great at"
(strengths first), prioritized "where to improve" (evidence + root cause + exercise +
own-data proof + measurable goal), a personalized playbook reconstructed from the rep's top
performers, the **surprise finding** (validate their self-assessed weakness against the data
— the won-vs-lost discovery/talk split is usually where the surprise lives; self-assessments
are wrong ~60% of the time), and a 30-day plan with check-back metrics.

## Outputs

- `sales-coaching-[YYYY-MM-DD].md` — scorecard, strengths, improvement areas, playbook,
  surprise finding, 30-day plan. Workspace + Agent Teams channel attachment.

## Credentials / env

- **Required:** none for the CSV/transcript path — all three analyzers are keyless. No LLM
  key (the coaching synthesis is your job as the agent).
- **Optional:** if a source key is set → pull the rep's data live; if not → keyless
  CSV/transcript exports (default). `LEMLIST_API_KEY` / `INSTANTLY_API_KEY` (email), a
  call-tool API key (Gong/Fireflies/etc., transcripts), a CRM key (`HUBSPOT_API_KEY` /
  `PIPEDRIVE_API_TOKEN` / `SALESFORCE_*`, pipeline) each gate their own live source;
  without them, paste/export the corresponding data.

## Notes & edge cases

- Degrades by data availability: pipeline-only = win/loss patterns only; minimum viable =
  any one source. Prioritize call coaching when transcripts exist (higher ROI per fix).
- Keep grading evidence-anchored — every grade cites a metric or quote from the rep's own
  data; no generic advice.
- Pure analysis — no scraping; cost is the rep's own tool data.
