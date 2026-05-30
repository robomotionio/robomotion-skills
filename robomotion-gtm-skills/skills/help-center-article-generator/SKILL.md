---
name: help-center-article-generator
description: Turn support-ticket clusters, FAQ patterns, feature docs, or product walkthroughs into structured help-center articles (steps, screenshot placeholders, troubleshooting, related links). Batch mode clusters a ticket export into ranked topics and generates an article per topic to deflect repetitive support volume. A composite: the agent writes each article; a bundled keyless script clusters and frequency-ranks the ticket export.
metadata:
  version: 1.0.1
  category: content
  type: composite
---

# Help Center Article Generator

A reasoning composite. **You (the agent) write each article** in the customer's language;
the only non-LLM work is ingesting and clustering ticket data, which the bundled keyless
`cluster_tickets.py` handles.

## When to use

- "Write help articles for our top support questions / from these tickets."
- "Generate docs for [feature]" / "build out our knowledge base."
- "Our support volume is too high — create self-serve content."

## How to run

### 1 — Intake
Gather sources (≥1): a ticket export CSV, an FAQ list, feature docs/specs, a described
walkthrough, or existing articles to improve. Capture `product_name` and optional
`audience` / `tone` / `structure`.

### 2 — Cluster (batch mode only)
For a ticket export, get frequency-ranked topics:

```bash
python3 ${SKILL_DIR}/scripts/cluster_tickets.py --input ${WORKSPACE}/tickets.csv --top 20 \
  --output ${WORKSPACE}/clusters.json
```

Auto-detects subject/description columns, groups near-duplicate subjects, ranks by
`ticket_count`, and suggests an `article_type` per cluster (how-to / troubleshooting /
overview / reference / getting-started). The agent refines clusters semantically if needed
(optionally with `pinecone`/`qdrant` for large exports).

### 3 — Generate each article (you)
From the type-appropriate template, in the customer's language, with `[Screenshot:
description]` placeholders at every UI step and ≥2 troubleshooting scenarios. Include
overview, steps, troubleshooting, FAQ, and related-article links.

### 4 — Quality-check (you)
Action-oriented title, scannable, complete, no internal jargon, screenshot placeholders
present, related links, search-friendly.

### 5 — Output
One markdown article per topic; batch mode adds an `_index.md` table of contents. Save to a
`help-center/` workspace folder / channel. Optionally push to a CMS/help-desk via `core` HTTP.

`python3 ${SKILL_DIR}/scripts/cluster_tickets.py --help` lists all flags.

## Outputs

One markdown article per topic (how-to / troubleshooting / overview / reference / getting-
started), each with overview, steps, screenshot placeholders, troubleshooting, FAQ, related
links. Batch mode adds `_index.md`.

## Credentials / env

- **Required:** none — the default path takes a pasted/CSV ticket export and emits markdown
  files; the agent is the generation engine; the clustering script is keyless.
- **Optional:** a help-desk/CMS API key (`ZENDESK_API_TOKEN` / `INTERCOM_ACCESS_TOKEN` / etc.,
  via `core` HTTP). If set → ingest tickets directly from, or publish finished articles back
  to, that system. If not set → paste/CSV export in and markdown files out (the keyless
  default — article generation itself needs no paid service). `ANTHROPIC_API_KEY` /
  `OPENAI_API_KEY` are not used by any script (the agent is the model).

## Notes & edge cases

- Insert `[Screenshot: description]` placeholders rather than inventing image URLs.
- Use the customer's wording, not internal jargon; every article needs ≥2 troubleshooting cases.
- Cross-link related articles to keep users inside the help center.
