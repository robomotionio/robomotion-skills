---
name: email-drafting
description: Write high-converting cold emails — subject lines, single emails, or full sequences — using structured frameworks (PAS, BAB, AIDA, Signal-Proof-Ask), personalization tiers, proven subject-line patterns, and tone guidance. Use whenever you need cold-email copy; auto-loads as the drafting primitive for the signal composites and cold-email-outreach. Pure reasoning plus a deterministic copy linter.
metadata:
  version: 1.0.1
  category: outreach
  type: capability
---

# Email Drafting

Produce cold-email copy that follows proven frameworks and hard quality rules.
The **agent does all the writing** (this is a reasoning skill); the bundled
`email_lint.py` only *verifies* the output against the hard rules deterministically.

## When to use

- "Write a cold email" / "draft outreach" / "write a sequence" / "help with email copy."
- Any task that needs cold-email copy — including the signal composites
  (champion-move / funding / hiring / leadership / news) and `cold-email-outreach`,
  which call this skill for the drafting step.

## How to draft (agent steps)

1. **Intake** campaign context (product, problem, angle, trigger/signal), audience
   (title/seniority/dept, frustrations, objections), proof (peers, metrics — optional),
   tone, sender, sequence config, personalization tier. Ask everything at once; skip answered.
2. **Pick the framework** by angle:
   - **PAS** (Problem-Agitate-Solve) — pain-signal driven.
   - **BAB** (Before-After-Bridge) — aspirational/outcome driven.
   - **AIDA** (Attention-Interest-Desire-Action) — cold-database, no specific signal.
   - **Signal-Proof-Ask** — when a concrete trigger/signal exists (the composites' default).
3. **Pick the personalization tier** by lead volume vs ROI: 1 generic, 2 segment, 3 deep.
4. **Draft each touch** to word-count targets — opener (T1) 50-90, follow-ups 30-50,
   breakup 20-40 — structured Hook -> Evidence -> Offer.
5. **Write subject lines** from the proven patterns: < 50 chars, lowercase-ish, no emoji,
   no ALL-CAPS, never "quick question". Curiosity / specific-benefit / relevant-question.
6. **Design cadence** — T1 day 1, T2 day 3-5 (new angle, not a nag), breakup last.
7. **Enforce hard rules** — never lie about how you found them, never fabricate metrics or
   peer companies, exactly one CTA per email.

## How to run (the linter)

After drafting, write the draft(s) as JSON and verify them. The linter is Python 3
stdlib only — no install:

```bash
python3 ${SKILL_DIR}/scripts/email_lint.py --input ${WORKSPACE}/sequence.json
```

JSON shape — one object or a list:

```json
[
  {"touch_number":1,"send_day":1,"touch_type":"opener","framework":"Signal-Proof-Ask",
   "subject":"...","body":"..."},
  {"touch_number":2,"send_day":4,"touch_type":"followup","subject":"...","body":"..."},
  {"touch_number":3,"send_day":9,"touch_type":"breakup","subject":"...","body":"..."}
]
```

`touch_type` is one of `opener` | `followup` | `breakup` (drives the word-count target).

| Flag | Default | Meaning |
|---|---|---|
| `--input` | `-` (stdin) | JSON draft file. |
| `--max-subject` | `50` | Max subject characters (hard ERROR if exceeded). |
| `--output` | `text` | `text` report or `json`. |

The linter exits **1** on any ERROR (over-length subject, banned phrase, emoji in subject).
**Regenerate** the offending touch — never truncate to fit. Warnings (word count off target,
0 or >1 CTA) are advisory.

## Outputs

- The drafted email(s)/sequence as the result: per touch `{subject, body, word_count,
  framework, touch_number, send_day}` plus the chosen tier/tone — returned for review or
  persisted to a workspace draft / channel attachment for an orchestrator (`cold-email-outreach`,
  signal composites) to load into a sending tool.

## Credentials / env

- `env.required`: none for the linter. The drafting itself is done by the host agent (the
  reasoning model) — no LLM API key is consumed by this skill.
- `env.optional`: none. **No paid service is applicable** — this is a pure drafting + lint
  skill with no external-data step, so the paid-services-optional policy adds nothing here.

## Notes & edge cases

- This is a copy generator, not a sender — hand off to `cold-email-outreach` / lemlist /
  instantly for the actual send.
- If the linter flags an over-length subject, **regenerate** (rewrite shorter), never truncate.
- Never fabricate metrics or peer companies; if `proof` is absent, fall back to a softer
  curiosity/question angle rather than inventing claims.
- The champion-move composite intentionally flips the "never say how you found them" rule
  (you reference a real prior relationship) — that is the one allowed exception.
