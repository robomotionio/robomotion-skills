---
name: graphics-studio
description: The unified visual generator — turn a brief into rendered high-res PNG/PDF graphics across seven fixed formats (carousel, story, infographic, slides, poster, chart, tweet). Resolve a style from a 16-style catalog, extract an ad-hoc style from a reference image, or synthesize a brand style from hex colors + fonts; source imagery (Unsplash or keyless) and ASCII art; the agent authors the HTML content while a deterministic driver binds design tokens to templates, runs a WCAG contrast check, and a Playwright renderer screenshots single files or whole slide directories at deviceScaleFactor 2. Supersedes create-html-carousel and create-html-slides. Use for any "make me a graphic / carousel / slides / poster / infographic / story" request and as the visual arm of social-kit.
metadata:
  version: 2.0.1
  category: content
  type: composite
---

# Graphics Studio

A real graphics engine that turns a brief into rendered PNG/PDF graphics across **seven
fixed formats**. The split is strict and idiomatic: **you (the agent) author the content
HTML** — the deterministic scripts do everything else (resolve a style into CSS tokens,
source images, bind tokens to a per-format template, check accessibility, screenshot at
the locked canvas size).

## When to use

- Any "make me a graphic / carousel / slides / poster / infographic / story" request.
- As the visual arm of `social-kit` and the upgrade path for the deprecated
  `create-html-carousel` / `create-html-slides` skills.

## The pipeline (one driver orchestrates it)

```
brief ─▶ STYLE (catalog / --ref image / --brand colors) ─▶ design tokens
      ─▶ FORMAT (one of 7) ─▶ canvas + density rules + content schema
      ─▶ (optional) IMAGES (Unsplash / keyless / ASCII)
      ─▶ agent authors the content fragment(s)
      ─▶ COMPOSE: template + :root tokens + content + font links  ──▶ render-ready HTML
      ─▶ CONTRAST check (WCAG AA warn) ─▶ RENDER (Playwright) ─▶ PNG(s) / PDF
```

`scripts/graphics.py` is the driver; everything below is invoked through its subcommands or
directly.

## Setup (once)

```bash
cd ${SKILL_DIR}/scripts && npm install && npx playwright install chromium
```

`extract_style.py` / `source_images.py` are stdlib-only (Pillow optional). The renderer
needs Playwright chromium.

## How to run

**1. Plan** — resolve a style + format, get the canvas, density rules, content schema,
`:root` token CSS, Google-font links, and a contrast report in one JSON:

```bash
python3 ${SKILL_DIR}/scripts/graphics.py plan --format carousel --style vibrant-tech
# or extract a style from a reference image:
python3 ${SKILL_DIR}/scripts/graphics.py plan --format poster --ref ${WORKSPACE}/brand.png
# or synthesize from brand colors + fonts (brand mode):
python3 ${SKILL_DIR}/scripts/graphics.py plan --format story \
  --brand "#101820,#FF6F3C" --brand-heading "Archivo" --brand-body "Inter"
```

**2. (Optional) Source imagery** — Unsplash when `UNSPLASH_ACCESS_KEY` is set, deterministic
keyless URLs otherwise; ASCII art with `--ascii`:

```bash
python3 ${SKILL_DIR}/scripts/source_images.py --query "startup office" --count 2 \
  --width 1080 --height 1350 --out-dir ${WORKSPACE}/assets
python3 ${SKILL_DIR}/scripts/source_images.py --ascii LAUNCH --out-dir ${WORKSPACE}/assets
```

**3. Author the content** — write ONE HTML content fragment per slide (root element
`<div class="slide">…`), honoring the format's density rules and content schema from the
plan. Reference sourced images by relative path. Use `.kicker .card .pill .stat-num
.page-no .grad-text` helpers and the `--accent/--text/--surface/...` CSS vars from `_base.css`.

**4. Compose** — bind the style tokens + base CSS + font links around your fragment:

```bash
python3 ${SKILL_DIR}/scripts/graphics.py compose --format carousel --style vibrant-tech \
  --content ${WORKSPACE}/frag1.html --out ${WORKSPACE}/slides/slide1.html
```

**5. Render** — single file, or a whole directory of slides to one PNG each (+ optional PDF):

```bash
# single
node ${SKILL_DIR}/scripts/render.mjs --html ${WORKSPACE}/slides/slide1.html \
  --out ${WORKSPACE}/out/slide1.png --format carousel
# multi-slide directory -> one PNG per file, plus a combined PDF deck
node ${SKILL_DIR}/scripts/render.mjs --dir ${WORKSPACE}/slides --out-dir ${WORKSPACE}/out \
  --format carousel --pdf ${WORKSPACE}/out/deck.pdf
```

`graphics.py render` wraps the same call. `--help` on any script lists all flags.

**6. Preview before committing** — render ONE deterministic style-preview slide (swatches +
type sample) so the user can approve the direction before a full run:

```bash
python3 ${SKILL_DIR}/scripts/graphics.py preview --format poster --style luxe-dark \
  --out-dir ${WORKSPACE}/preview
```

**7. Deliver** — list the output folder (HTML source + PNG/PDF per slide) and the preview
path; post PNGs as Agent Teams / Slack attachments.

## Style catalog

`scripts/styles.json` ships **16 named styles**, each with full CSS design tokens — palette
(`bg, surface, primary, accent, text, muted, gradient?`), typography (Google/web-safe font
stacks + scale ratio), `radius`, `shadow`, `spacing_unit`, `mood_tags`, and `motifs`:
`minimal-light, bold-dark, editorial-serif, glassmorphism, brutalist, pastel-soft,
corporate-clean, gradient-mesh, retro-print, mono-technical, luxe-dark, playful-rounded,
newsprint, neon-cyber, organic-warm, vibrant-tech`. Any style binds to any format template
via `:root` custom properties.

Three ways to get a style:
- **Catalog** — `--style <id>`.
- **Extract from a reference image** — `--ref <image>` runs `extract_style.py`: dominant
  palette via k-means (Pillow if importable, else a pure-stdlib PNG decoder), light/dark
  theme inference, best-accent pick, readable text/muted roles — emits a style in the same
  schema.
- **Brand mode** — `--brand "#bg,#accent" --brand-heading F --brand-body F` synthesizes a
  custom style from brand colors + fonts.

## Formats

`scripts/formats.json` — seven fixed formats, each `{canvas{w,h}, multi_slide,
density_rules, content_schema}`:

| format | canvas | multi-slide |
|---|---|---|
| carousel | 1080×1350 | yes (4–10) |
| story | 1080×1920 | no |
| infographic | 1080×tall | no (full-page capture) |
| slides | 1920×1080 | yes |
| poster | 1080×1350 | no |
| chart | 1080×1080 | no |
| tweet | 1080×1080 | no |

Map any community/odd size to one of these via its `aliases` before rendering — the renderer
is locked to this allow-list. An unmappable size means the format is misconfigured: stop and
report.

## Accessibility

Every `plan` / `compose` / `contrast` run prints a **WCAG contrast report** (text/bg,
accent/bg, muted/bg) and **warns on AA failure** so low-legibility combinations (e.g. a
pastel accent on a pale bg) surface before render. Gradients are approximated by their first
color stop for the check.

## Outputs

A dated output folder with generated HTML source + high-resolution PNG export(s) — one per
slide for `carousel`/`slides` — at the format's canvas size, rendered at deviceScaleFactor 2,
plus an optional combined PDF deck and a style-preview slide.

## Credentials / env

- **Required:** none. The whole pipeline (style resolution, extraction, keyless image
  sourcing, templating, contrast check, Playwright render) runs key-free. The agent authors
  the copy, so no LLM key is consumed by a script.
- **Optional:**
  - `UNSPLASH_ACCESS_KEY` (paid tier, with a fallback) — If set → real attributed Unsplash
    photos (better imagery). If not set → deterministic keyless seeded picsum URLs
    (`source_images.py` falls back automatically, including on API failure). Keyless is the
    default.
  - `LEONARDO_API_KEY` / `STABILITY_API_KEY` / `FAL_KEY` (paid generative imagery, with a
    fallback) — If one is set → generate bespoke imagery. If none → fall back to stock
    (Unsplash or keyless picsum) or ASCII art (the default); the graphic renders regardless.
  - `ANTHROPIC_API_KEY` / `OPENAI_API_KEY` — not used by any script (you are the model);
    listed only because content authoring + `--ref` vision refinement are your job.

## Notes & edge cases

- "Surprise me" → pick `carousel` + a random style; ask only for the topic.
- Multi-format → run the pipeline once per format, same content/style, separate subfolders.
- Always offer the **preview** slide before a full render so the user can approve direction.
- The renderer awaits `document.fonts.ready` + every `<img>` decode + a settle delay so text
  and images are crisp; bump `--wait` if a heavy font/image still renders late.
- `infographic` captures full-page (tall) automatically; use a tall canvas + `--full-page`
  for any custom tall layout.
- Default slides sit on the solid `--bg` for predictable contrast; add class `bleed` to a
  `.slide` for a full-bleed `--gradient` background, or `grad-text` for a gradient headline.
