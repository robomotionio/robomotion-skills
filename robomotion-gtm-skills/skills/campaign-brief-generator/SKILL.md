---
name: campaign-brief-generator
description: From a campaign goal, ICP, and product context, produce a complete, opinionated, execution-ready campaign brief — channel strategy, 3-tier messaging architecture, a 4-week content calendar, success metrics + north star, explicit scope cuts ("what we're NOT doing"), and a pre-launch asset checklist. A pure-reasoning composite for founders and small GTM teams; the agent synthesizes the brief grounded by a bundled intake/rubric schema. Produces the plan that feature-launch-playbook, content-brief-factory, and social-kit then execute.
metadata:
  version: 1.0.1
  category: content
  type: composite
---

# Campaign Brief Generator

A **pure-reasoning composite** — no scraping, no external feeds. **You (the agent) write the
entire brief.** The bundled `scripts/intake.json` grounds the intake pass and the
channel/messaging/content rubrics so the output is opinionated and concrete, not a template.

## When to use

- "Plan a campaign for [launch/feature/segment]."
- "We're targeting [ICP] — what channels and content should we run?"
- "I need a 30-day campaign plan / write me a campaign brief for [goal]."

## How to run

1. **Intake** — read `${SKILL_DIR}/scripts/intake.json` for the required inputs (goal,
   trigger, timeline, ICP, product, constraints). Gather any missing ones in **one grouped
   pass** via the agent's channel — make it feel fast, not like a form.
2. **Channel strategy** — recommend 2–4 channels (role, expected output, effort + budget,
   owner, metric) using the `channel_selection` rubric. Cap at 4 for seed/Series A.
3. **Messaging architecture** — a primary message + two secondaries, each with evidence and
   channel fit (`messaging_architecture` rubric).
4. **Content plan** — concrete pieces with **working titles** mapped week-by-week (weeks 1–4)
   with owners and goals — never "write some posts".
5. **Success metrics** — a KPI table by funnel phase + a single north-star metric.
6. **Assemble the brief** — emit every `required_section` (incl. "what we're NOT doing" and
   the pre-launch asset checklist) as a single markdown document; save to workspace / channel.

There is no script to execute beyond reading the schema — the synthesis is yours.

## Outputs

A single markdown campaign brief: goal, ICP, timeline, 2–4 channel plan, 3-tier messaging,
weeks-1–4 content calendar, success-metric table + north star, "what we're NOT doing", and a
pre-launch asset checklist. Saved to workspace / Agent Teams channel.

## Credentials / env

- **Required:** none. The skill is agent reasoning; no script makes an external/LLM call (the
  agent is the model).
- **Optional:** none. **No paid service is applicable** — this is a pure-reasoning composite
  with no external-data step, so there is nothing to gate behind a paid key. Any enrichment
  package (`apollo` for ICP sizing, `blog-feed-monitor` for competitive context) is strictly
  additive if the agent already has that data feeding the prompt.

## Notes & edge cases

- Output must be opinionated and concrete — working titles, named owners, specific metrics.
- For seed/Series A, cap channels at 4 — execution quality beats channel breadth.
- The "what we're NOT doing" section is a feature, not filler — it prevents scope creep.
- Downstream, this brief feeds `feature-launch-playbook`, `content-brief-factory`,
  `social-kit`, and the social-drafting skills.
