---
name: create-html-carousel
description: DEPRECATED — superseded by graphics-studio (--format carousel). Generates a LinkedIn/Instagram carousel as square 1080×1080 PNG slides. Retained thin for backward compatibility; route new carousel work to graphics-studio, which owns the style catalog and shared render pipeline.
metadata:
  version: 1.0.1
  category: content
  type: capability
---

# Create HTML Carousel — DEPRECATED

> **DEPRECATED.** Superseded by **`graphics-studio`**, where "carousel" is one of seven
> formats with a far larger style catalog and a shared HTML→PNG render pipeline. This spec
> is retained thin for one release cycle — do not extend it.

## When to use

- Only for backward compatibility while callers migrate. **New work → `graphics-studio`.**

## How to run

Delegate to `graphics-studio` with the carousel format:

```bash
# 1. (once) set up the renderer
cd ${SKILL_DIR}/../graphics-studio/scripts && npm install && npx playwright install chromium

# 2. author one 1080x1080 HTML file per slide (cover hook -> one point per slide -> CTA),
#    then render each:
node ${SKILL_DIR}/../graphics-studio/scripts/render.mjs \
  --html ${WORKSPACE}/slide1.html --out ${WORKSPACE}/slide1.png --format carousel
```

See `graphics-studio/SKILL.md` for the style catalog, format density rules, and full flags.

## Outputs

A folder of 1080×1080 PNG slides (+ HTML source) — produced by `graphics-studio`.

## Credentials / env

- **Required:** none (the agent authors slide copy; the render pipeline is keyless — the
  default).
- **Optional:** **no paid service is applicable here** (deprecated, render-only). Any
  image-sourcing keys (`UNSPLASH_ACCESS_KEY` / generative-art) live on `graphics-studio`,
  which this delegates to: if set → real/generated imagery, if not → keyless picsum/ASCII.

## Notes & edge cases

- Keep each slide scannable in 2–3 seconds; max 3–4 list items; high contrast for mobile.
- Always close with a CTA ("Follow for more", "Repost if useful").
- Reminder: this is deprecated — prefer `graphics-studio --format carousel`.
