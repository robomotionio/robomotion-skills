---
name: sequence-performance
description: Email campaign/sequence diagnostic beyond vanity metrics — pulls sends/opens/replies/bounces by touch and variant, reads the copy you sent and every reply, then produces a prioritized report on what's working, what's not, and what to do. Tool-agnostic (Instantly/Lemlist/CSV). Metrics are computed; reply classification, copy grading, and recommendations are the agent's.
metadata:
  version: 2.0.1
  category: research
  type: composite
---

# Sequence Performance

Deterministic pull + rate math; **you, the agent, classify every reply, grade the copy,
assess lead quality, and write the recommendations.** Metrics stay computed (trustworthy).

> **v2.0.0 — depth upgrade.** `analyze_sequence.py` now computes per-touch & per-variant
> open/reply/**positive** rates, compares against a built-in **per-segment reference table**
> (SMB / MidMarket / Enterprise × cold/warm), normalizes pre-tagged replies into a canonical
> **reply-category taxonomy**, and extracts **copy-grading signals** (subject length, CTA,
> personalization tokens, spam triggers). This SKILL.md carries the full benchmark tables,
> the reply taxonomy, the copy rubric, and the output skeleton.

## When to use

- "How's my campaign doing", "sequence performance", "campaign review", "email analytics".
- "Why isn't my campaign working", "review my email results" (after 7+ days of data).

## How to run

### Step 1 — pull the campaign bundle (deterministic)

```bash
python3 ${SKILL_DIR}/scripts/fetch_campaign.py --tool instantly --campaign "Q1 Cold" \
  --output ${WORKSPACE}/bundle.json
```

Tools: `instantly`, `lemlist`, or keyless `csv`:

```bash
python3 ${SKILL_DIR}/scripts/fetch_campaign.py --tool csv --campaign "Q1 Cold" \
  --metrics-csv ${WORKSPACE}/metrics.csv \
  --replies-csv ${WORKSPACE}/replies.csv \
  --copy-csv ${WORKSPACE}/copy.csv \
  --output ${WORKSPACE}/bundle.json
```

CSV shapes: metrics = `touch,variant,sends,opens,replies,bounces`; replies =
`date,from,text`; copy = `touch,variant,subject,body`. The API tools return overall
totals; for per-touch/per-variant depth use the CSV path or supplement.

### Step 2 — compute rates + confidence (deterministic)

```bash
python3 ${SKILL_DIR}/scripts/analyze_sequence.py --bundle ${WORKSPACE}/bundle.json \
  --outreach-type cold --segment SMB \
  --benchmark-reply-rate 0.03 --benchmark-open-rate 0.40 \
  --output ${WORKSPACE}/metrics.json
```

Computes overall + per-touch + per-variant open/reply/**positive**/bounce rates, marginal
reply share per touch, vs-passed-benchmark deltas, a **per-segment** comparison (pick
`--segment SMB|MidMarket|Enterprise`), a normalized **reply taxonomy** (from any pre-tagged
reply categories in the bundle), **copy signals** per touch/variant, and a variant
confidence label (insufficient <50 / low / moderate / significant 250+). `data_quality`
flags missing open tracking / variant data / reply text / positive tracking / copy.

### Built-in segment benchmarks (cold; the bar the script compares against)

| Segment | Open | Reply | Positive-reply | Bounce ceiling |
|---|---|---|---|---|
| SMB | 45% | 5.0% | 1.5% | 3% |
| MidMarket | 40% | 3.5% | 1.2% | 3% |
| Enterprise | 35% | 2.5% | 0.8% | 3% |

(Warm/nurture rows run higher — opted-in lists clear ~2–3× the reply bar.) `segment_comparison`
emits a verdict per metric: `above` (≥1.2× bench) · `at` (0.8–1.2×) · `below` (<0.8×).
Enterprise opens lower but each reply is worth more — weigh **positive_rate**, not raw reply.

### Reply-category taxonomy (the script normalizes; you refine from text)

Canonical buckets the script maps any pre-tagged `reply.category` into — classify every
raw reply you read into the same buckets so the counts and your narrative agree:

| Bucket | What lands here | What it means |
|---|---|---|
| `positive` | interested / meeting / demo / "yes" | The win metric. Track positive_rate, not reply_rate. |
| `objection` | not relevant · budget · competitor · already have | >20% "not relevant" = **targeting** problem, not copy. |
| `not_now` | timing / next quarter / circle back | Nurture, don't kill — sequence them later. |
| `referral` | wrong/right person, forwarded | A win in disguise — re-route to the named person. |
| `out_of_office` | auto-replies | Noise; exclude from reply-quality math. |
| `unsubscribe` | remove / opt-out / GDPR | List/targeting hygiene + compliance flag. |
| `other` | anything unmatched | Read and re-bucket manually. |

### Copy-grading rubric (signals → letter grade)

The script extracts **signals**; you assign the A–F grade. Targets for cold outbound:

| Signal | Healthy target | Read |
|---|---|---|
| `subject_word_len` | 3–7 words | Long/clickbait subjects tank opens. |
| `body_word_count` | 50–125 words | Walls of text kill replies. |
| `has_cta` | true | One clear, low-friction ask (a question, a 15-min). |
| `personalization_token_count` | ≥1 real token | Zero tokens on cold = spray-and-pray. |
| `spam_trigger_count` | 0 | Each trigger word risks the spam folder (deliverability). |
| `question_count` | 1–2 | A question invites a reply; none = a monologue. |

Grade each subject + body A–F on hook, value prop, proof, personalization, CTA, filler,
and sequence progression (does touch 2 add a new angle or just "bumping this"?).

### Step 3 — analyze + write the report (you, the agent)

1. **Reply analysis** — read `bundle.json` replies; classify each (positive / meeting /
   warm / objection-timing/budget/competitor/relevance/authority / not-interested / OOO /
   referral / question); extract objection + positive-signal patterns; preserve exact
   objection language. Assign a reply-quality score.
2. **Copy quality** — grade subjects + bodies A-F (hook, value prop, proof,
   personalization, CTA, filler, sequence progression).
3. **Lead quality** — compare titles/industry/seniority/size to ICP; infer targeting
   issues from reply patterns (e.g. >20% "not relevant" = targeting, not copy).
4. **Diagnose by pattern**: low open = subject; good open + low reply = body; high bounce
   = list hygiene; low deliverability = SPF/DKIM/DMARC. Don't kill a variant under 100
   sends. Write the exec summary (grades + top 3 actions), the detailed sections, and a
   kill list.

**Diagnostic decision table:**

| Symptom (from metrics) | Root cause | Fix |
|---|---|---|
| `open_rate` below segment, reply ok | Subject line / sender reputation | Rewrite subjects (3–7 words); warm up the domain. |
| `open_rate` at/above, `reply_rate` below | Body / offer / CTA | Tighten body to 50–125 words; one clear ask; stronger proof. |
| `positive_rate` low but `reply_rate` ok | Wrong audience or weak offer | Re-check ICP fit; reply taxonomy heavy on `objection`/`not relevant` = targeting. |
| `bounce_rate` over ceiling | List hygiene | Re-verify the list (email-validator); pause sends. |
| Reply taxonomy heavy `unsubscribe` | Targeting/compliance | Tighten list; review consent + frequency. |
| Variant gap with `confidence` < significant | Not enough data | **Don't kill it** — keep running to ≥250 sends. |
| A later touch has high `marginal_reply_share` | Follow-ups are doing the work | Keep the sequence long enough; don't stop at touch 1. |

**Output skeleton:**

```markdown
# Sequence Performance — [Campaign]
## Executive Summary
- Open X% / Reply X% / Positive X% / Bounce X% — vs [segment] benchmark: [verdicts]
- Copy grade: [A–F overall] · Confidence: [label]
- **Top 3 actions:** 1) … 2) … 3) …
## Metrics vs Benchmark  (overall + per-touch + per-variant table w/ confidence)
## Reply Deep-Dive  (taxonomy counts + % + verbatim objection language)
## Copy Assessment  (per touch/variant: signals → A–F grade + the rewrite)
## Lead-Quality Assessment  (ICP fit + targeting verdict from reply patterns)
## Recommendations & Kill List  (what to fix, what to pause, what to scale)
```

## Outputs

- `sequence-performance-[YYYY-MM-DD].md` — exec summary, detailed metrics (vs benchmark,
  per-touch, per-variant w/ confidence), reply deep-dive, copy assessment, lead-quality
  assessment, prioritized recommendations + kill list. Workspace + Agent Teams attachment.

## Credentials / env

- **Required:** none for the CSV path (both scripts are keyless). No LLM key — the
  classification, grading, and recommendations are your job as the agent.
- **Optional:** if an outreach-tool key is set (`INSTANTLY_API_KEY` or `LEMLIST_API_KEY`) →
  `fetch_campaign.py` pulls the campaign via API; if not → the keyless `--tool csv` path
  (default).

## Notes & edge cases

- Degrades gracefully: minimum viable = sends + reply count + copy text. Missing reply
  text drops classification; missing variant data drops A/B analysis; missing open
  tracking drops open-rate analysis — the rest still runs (see `data_quality`).
- Reply analysis is where the insight is — metrics say WHAT, replies say WHY.
- Pure reasoning over the user's tool data — no scraping, no paid API.
