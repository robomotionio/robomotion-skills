---
name: create-html-slides
description: DEPRECATED — superseded by graphics-studio (--format slides). Creates 16:9 (1920×1080) HTML presentations from scratch or by converting a PowerPoint. Retained thin for backward compatibility; route new deck work to graphics-studio, which owns the style catalog and shared render pipeline.
metadata:
  version: 1.0.1
  category: content
  type: capability
---

# Create HTML Slides — DEPRECATED

> **DEPRECATED.** Superseded by **`graphics-studio`**, where "slides" (1920×1080) is one of
> seven formats sharing a large style catalog and a single HTML→PNG render pipeline. This
> spec is retained thin for one release cycle — do not extend it.

## When to use

- Only for backward compatibility during migration. **New work → `graphics-studio`.**

## How to run

Delegate to `graphics-studio` with the slides format:

```bash
# 1. (once) set up the renderer
cd ${SKILL_DIR}/../graphics-studio/scripts && npm install && npx playwright install chromium

# 2. author one 1920x1080 HTML file per slide (one idea/slide, no scroll, density limits),
#    then render each:
node ${SKILL_DIR}/../graphics-studio/scripts/render.mjs \
  --html ${WORKSPACE}/deck1.html --out ${WORKSPACE}/deck1.png --format slides
```

For PPTX conversion, the agent first extracts slide text/images/notes (via a document/PDF
processor) into outlines, then authors the HTML per slide. See `graphics-studio/SKILL.md`.

## Outputs

A self-contained HTML presentation (optionally exported to PNG per slide / PDF) — produced
via `graphics-studio`.

## Credentials / env

- **Required:** none (the agent authors slide copy/structure; the render pipeline is keyless
  — the default).
- **Optional:** **no paid service is applicable here** (deprecated, render-only). Any
  image-sourcing keys (`UNSPLASH_ACCESS_KEY` / generative-art) live on `graphics-studio`,
  which this delegates to: if set → real/generated imagery, if not → keyless picsum/ASCII.

## Notes & edge cases

- Every slide must fit one viewport — split content rather than scroll (≤6 bullets/cards).
- Avoid generic "AI-slop" aesthetics; favor distinctive font pairings and cohesive palettes.
- Reminder: this is deprecated — prefer `graphics-studio --format slides`.
