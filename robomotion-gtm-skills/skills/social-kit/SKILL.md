---
name: social-kit
description: One brief → voice-tuned X variants + voice-tuned LinkedIn variants + a matching social graphic. A thin orchestrator over create-x-content, create-linkedin-content, and graphics-studio, with a voice-guide pre-flight check and sensible defaults. Use for the end-to-end content moment when you want copy and a visual together, in the user's voice.
metadata:
  version: 1.0.1
  category: content
  type: composite
---

# Social Kit

A thin **orchestrator** over three sub-skills — **`create-x-content`** (X variants),
**`create-linkedin-content`** (LinkedIn variants), and **`graphics-studio`** (the graphic) —
with **`generate-voice-guide`** as a recommended one-time prerequisite. The bundled
`init_run.py` scaffolds the run folder and prints the orchestration plan; everything else is
delegation to the sub-skills (the agent drafts/authors).

## When to use

- "Give me X + LinkedIn posts and a graphic for [brief]."
- When you want copy and a visual together, in the user's voice.

## How to run

1. **Scaffold the run + get the plan:**

```bash
python3 ${SKILL_DIR}/scripts/init_run.py --brief "Shipped a 10x faster lead scraper" \
  --output ${WORKSPACE}/content
# optional: --skip-x / --skip-linkedin / --skip-graphic, --format poster, --style ...,
#           --variants-x N, --variants-linkedin N
```

Creates `content/YYYY-MM-DD-<topic-slug>/` (+ a `graphic/` subfolder) and prints
`{topic_slug, folder, steps, voice_guide_preflight}`.

2. **Voice-guide pre-flight** — for each non-skipped platform, ensure an X and a LinkedIn
   voice guide exist; for any missing one, delegate to `generate-voice-guide`, paste a path,
   or skip that platform. **Never proceed without resolving it** — generic posts are the
   failure mode.
3. **Draft X variants** (unless `--skip-x`) via `create-x-content`, writing into the run
   folder. Capture the most substantive variant for the graphic brief.
4. **Draft LinkedIn variants** (unless `--skip-linkedin`) via `create-linkedin-content`.
5. **Pick the graphic format** — use `--format` if given, else recommend 1–2 from the brief
   shape (poster / carousel / infographic / tweet / story / slides / chart) and ask.
6. **Pick a style** — `--style` if given, else the house default.
7. **Generate the graphic** via `graphics-studio` from a distilled brief (headline + 2–4 key
   beats + must-appear strings, drawn from the strongest X variant), output to `graphic/`.
8. **Deliver** a combined, cross-linked summary; post files as Agent Teams / Slack attachments.

Invoke each sub-skill's scripts by path, e.g.:
```bash
python3 ${SKILL_DIR}/../create-x-content/scripts/lint_post.py --file <variant> ...
node ${SKILL_DIR}/../graphics-studio/scripts/render.mjs --html <slide> --out <png> --format <fmt>
```

`python3 ${SKILL_DIR}/scripts/init_run.py --help` lists all flags.

## Outputs

A single run folder with X variant files, LinkedIn variant files, and a `graphic/` subfolder
(HTML source + PNG exports + preview), plus a summary linking drafts to the graphic.

## Credentials / env

- **Required:** none. The agent drafts the copy and authors the graphic HTML; all sub-skill
  render/lint scripts are keyless — the whole kit runs key-free by default.
- **Optional (all paid, all with a fallback; belong to a sub-skill's path; skip flags drop
  any arm):**
  - `APIFY_API_TOKEN` / `PHANTOMBUSTER_API_KEY` — voice-guide corpus scraping
    (`generate-voice-guide`). If set → auto-scrape; if not → paste-text fallback (the
    default).
  - `UNSPLASH_ACCESS_KEY` and generative-art keys (`LEONARDO`/`STABILITY`/`FAL`) — graphic
    image sourcing (`graphics-studio`). If set → real/generated imagery; if not → keyless
    picsum/ASCII (the default).

## Notes & edge cases

- Never proceed without resolving the voice guide for each non-skipped platform.
- Distill the graphic brief from the strongest X variant (headline + 2–4 beats + verbatim
  must-keep strings like tool names, commands, prices).
- Pair drafts with graphics intentionally — a long mechanism variant suits a carousel; a
  short hype variant suits a poster.
- First-time setup is `generate-voice-guide` once; iterate on voice before iterating on copy.
