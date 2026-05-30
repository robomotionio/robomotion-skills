---
name: churn-risk-detector
description: Aggregate support, communication, usage, and commercial signals per account into a scored churn-risk report with severity tiers, root-cause hypotheses, and specific save plays. Built for seed/Series A teams with no CS platform — a spreadsheet of customers, a Slack channel, and a support inbox. Scoring is deterministic; the agent writes hypotheses and save plays.
metadata:
  version: 2.0.1
  category: research
  type: composite
---

# Churn Risk Detector

Deterministic signal extraction + composite scoring; **you, the agent, write the
root-cause hypotheses, save plays, and talk tracks.** The model never invents scores —
weights and tiers are fixed in code.

> **v2.0.0 — depth upgrade.** `detect_signals.py` now carries a comprehensive signal catalog
> across six lenses — usage decline, login-frequency drop, feature abandonment, support-ticket
> spike, escalation language, renewal proximity, payment failure, downgrade/**seat reduction**,
> **NPS/CSAT drop**, **champion departure**, **exec/sponsor turnover** — each with a fixed
> threshold + severity feeding the scorecard. This SKILL.md carries the full signal taxonomy,
> the save-play library, and the output skeleton.

## When to use

- "Which customers are at risk of churning?" / "Run the weekly churn risk scan."
- "Who haven't we heard from in a while?" / scheduled weekly customer-health rhythm.

## How to run

### Step 1 — extract mechanical signals (deterministic, keyless CSV)

```bash
python3 ${SKILL_DIR}/scripts/detect_signals.py \
  --customers ${WORKSPACE}/customers.csv \
  --tickets ${WORKSPACE}/tickets.csv \
  --comms ${WORKSPACE}/comms.csv \
  --usage ${WORKSPACE}/usage.csv \
  --billing ${WORKSPACE}/billing.csv \
  --survey ${WORKSPACE}/survey.csv \
  --people ${WORKSPACE}/people.csv \
  --silence-days 30 --renewal-window 60 \
  --output ${WORKSPACE}/signals.json
```

Detects threshold/keyword signals across six lenses. Only the customer list is required;
each missing CSV drops its lens. If the customer list lives in a CRM, pull it first with
`fetch_customers.py` (below), or export from the CRM directly.

### Signal catalog (lens · signal · threshold · severity → points)

Severity → composite points are **fixed in `score_accounts.py`**: critical 25 · high 15 ·
medium 8 · low 3 (capped 100). The detector emits these deterministically:

| Lens | Signal | Threshold / trigger | Severity |
|---|---|---|---|
| **usage** | login-frequency drop | `--usage-drop-pct` (def 30%); ≥2× → high | medium→high |
| **usage** | active-user / usage decline | same threshold on active_users | medium→high |
| **usage** | feature abandonment | `--feature-drop-pct` (def 40%) | medium |
| **support** | ticket unresolved | open + `resolution_days` > `--unresolved-days` (7) | high |
| **support** | escalation language | cancel/competitor/refund/churn/terminate… | critical |
| **support** | ticket-volume spike | ≥ `--ticket-spike` (5) tickets | medium |
| **engagement** | gone silent | last touch ≥ `--silence-days` (30); ≥2× → high | medium→high |
| **commercial** | renewal proximity | within `--renewal-window` (60d); ≤14d → critical | high→critical |
| **commercial** | payment failure | billing event | critical |
| **commercial** | downgrade | billing event | high |
| **commercial** | seat reduction | billing event OR seats drop ≥ `--seat-drop-pct` (15%) | high |
| **commercial** | discount request | billing event | medium |
| **sentiment** | NPS drop | prev−curr ≥ `--nps-drop` (2) | high |
| **sentiment** | CSAT drop | prev−curr ≥ `--csat-drop` (1) | high |
| **sentiment** | NPS detractor / low CSAT | NPS ≤6 / CSAT ≤2.5 | medium |
| **relationship** | champion departure | `people.csv` champion/advocate status=departed | critical |
| **relationship** | exec/sponsor turnover | exec/VP/director status=departed | high |
| **relationship** | key contact departure | any other contact departed | medium |

**Agent-added (non-mechanical) signals** — read the ticket/Slack text yourself and merge in
as `{name, severity, lens, note}` before scoring: negative-sentiment *tone* shift (vs a
numeric NPS drop), champion *disengagement* (still there but quiet), new-stakeholder asking
basic onboarding questions (relationship reset), buying-committee reorg.

### Step 2 — score + tier (deterministic)

```bash
python3 ${SKILL_DIR}/scripts/score_accounts.py \
  --input ${WORKSPACE}/signals.json \
  --prior ${WORKSPACE}/last_week_scored.json \
  --output ${WORKSPACE}/scored.json
```

Composite = Σ severity points (critical 25 / high 15 / medium 8 / low 3, capped 100);
tiers Red 70-100, Orange 40-69, Yellow 20-39, Green 0-19. Emits per-account breakdown,
tier counts, MRR-at-risk by tier, signal distribution, and (with `--prior`) week-over-week
score deltas.

### Save-play library (dominant lens → root cause → play)

Pick the play by the account's dominant `lens_breakdown` lens, then tailor with the
specific signals:

| Dominant lens | Likely root cause | Save play |
|---|---|---|
| **usage** | Not getting value / adoption stalled | Re-onboard the lapsed feature; share an ROI/usage recap; book an enablement session for the team that went quiet. |
| **support** | Product friction eroding trust | Escalate the open ticket to a named owner with a deadline; exec apology + fix timeline; close the loop personally. |
| **commercial** | Renewal/budget at risk | Get ahead of renewal: value review + business case; bring in the economic buyer; pre-empt the discount ask with proof of ROI. |
| **engagement** | Relationship gone cold | Multi-thread — you've lost the thread with one contact; re-establish via a colleague; lead with insight, not a check-in. |
| **sentiment** | Dissatisfaction surfaced (NPS/CSAT) | Close the feedback loop fast; "you rated us low — what would make this a 9?"; visible fix + follow-up survey. |
| **relationship** | Champion/sponsor left | Treat as a fresh sale to the replacement; re-sell the value from zero; find/build a new champion before renewal. |

**Severity-tier response cadence:** Red (70-100) = same-week exec-involved save plan; Orange
(40-69) = CSM owns a 2-week plan; Yellow (20-39) = watch + one proactive touch; Green = BAU.

### Step 3 — write the report (you, the agent)

For each Red/Orange account in `scored.json`, write a card: signals → **root-cause
hypothesis** → **3-step save play** (from the library, tailored) → **talk track** →
escalation trigger + owner + deadline. Add the Yellow watch table, the week-over-week trend
(from deltas), the signal distribution, and a "focus this week".

**Output skeleton:**

```markdown
# Churn Risk Report — [YYYY-MM-DD]
## Summary
| Tier | Accounts | MRR at risk |
|---|---|---|
| 🔴 Red | N | $X |
| 🟠 Orange | N | $X |
| 🟡 Yellow | N | $X |
Week-over-week: [Red→Green wins · new risks · churned-since-last]

## 🔴 / 🟠 Account Cards  (one per at-risk account)
**[Account] — score X (tier) — $MRR — renews [date]**
- Signals: [list w/ severity + lens]
- Root-cause hypothesis: …
- Save play (3 steps): 1) … 2) … 3) …
- Talk track: "…"
- Owner · deadline · escalation trigger

## 🟡 Watch Table  (account · score · top signal · one action)
## Signal Distribution  (which lenses dominate the book this week)
## Focus This Week  (the 3 accounts/actions with the most MRR leverage)
```

### Optional — CRM customer list

```bash
python3 ${SKILL_DIR}/scripts/fetch_customers.py --crm hubspot --output ${WORKSPACE}/customers.csv
```

## Outputs

- `risk-report-[YYYY-MM-DD].md` — summary table (tier counts + MRR at risk), Red/Orange
  cards, Yellow watch table, week-over-week trend, signal distribution, "focus this week".
  Workspace + Agent Teams channel attachment; optional Slack push of the summary.

## Credentials / env

- **Required:** none for the CSV path — `detect_signals.py` and `score_accounts.py` are
  keyless. No LLM key (the agent writes hypotheses + save plays).
- **Optional:** if a CRM key is set (`HUBSPOT_API_KEY` / `PIPEDRIVE_API_TOKEN` /
  `SALESFORCE_*`) → `fetch_customers.py` pulls the customer list live; if not → the keyless
  CSV/paste path (default). `SLACK_BOT_TOKEN` — if set → communication-signal source +
  push; if not → skip. `SUPABASE_*` — if set → persist run scores for trend history; if not
  → workspace CSV ledger (default).

## Notes & edge cases

- Degrades gracefully: scoring runs on whatever signals exist; minimum viable = customer
  list + one signal source.
- Keep scoring deterministic (the script's fixed weights); reserve your reasoning for
  hypotheses, save plays, and sentiment — never hand-edit the composite numbers.
- Persist each run's `scored.json` so next week's `--prior` yields Red→Green wins, new
  risks, and churned-since-last movement.
- Pure analysis — no scraping, no external paid API.
