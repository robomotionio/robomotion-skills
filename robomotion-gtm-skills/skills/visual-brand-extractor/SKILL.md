---
name: visual-brand-extractor
description: Extract a client's visual identity from their website — color palette, typography pairing, and aesthetic/layout patterns — and emit reusable style presets: a slide-style CSS preset and a brand-config JSON for downstream slide/content-asset generators. Deterministic scripts render the site, harvest CSS/font/color signals, capture a hero screenshot, and sample dominant colors; you (the agent) classify color roles, choose fonts, and synthesize the vibe.
metadata:
  version: 1.0.1
  category: brand
  type: capability
---

# Visual Brand Extractor

Render a site with Playwright, harvest its raw visual signals (CSS custom properties,
color declarations, fonts, theme-color meta, Tailwind classes, layout patterns), capture
a hero screenshot, and sample its dominant colors numerically. **You then classify color
roles, pick the typography, and synthesize the vibe** into a reusable preset. Scripts do
only extraction/measurement.

## When to use

- "Extract visual branding from [url] for [client]."
- Onboarding a client with no brand/style guide when downstream skills (slides, carousels,
  content assets) need consistent colors/fonts.
- A feeder for any visual-output skill that takes a brand config (theme, fonts, accent).

## How to run

The Playwright extractor needs Chromium; the Python helpers are stdlib-first (Pillow used
if present, with a stdlib PNG fallback so they run with no install).

### 1. Render + harvest signals (+ hero screenshot)

```bash
# one-time: npm --prefix ${SKILL_DIR}/scripts install && npx playwright install chromium
node ${SKILL_DIR}/scripts/extract_brand.mjs \
  --url https://acme.com \
  --client "Acme" \
  --pages https://acme.com/product https://acme.com/blog \
  --screenshot ${WORKSPACE}/hero.png \
  --output ${WORKSPACE}/signals.json
```

`signals.json` carries, per page: `custom_properties` (`--color-*`/`--bg-*`/`--accent`),
`meta_colors` (theme-color), `colors_ranked` (by on-page frequency), `fonts`, `font_links`
(Google/Fontshare/Typekit), `tailwind_classes`, `tailwind_config_snippet`, and `layout`
(border-radius / gradient / shadow / animation signals).

### 2. Sample dominant colors from the hero screenshot (numeric cross-check)

```bash
python3 ${SKILL_DIR}/scripts/sample_colors.py \
  --image ${WORKSPACE}/hero.png \
  --num-colors 8 \
  --output ${WORKSPACE}/palette.json
```

Returns ranked dominant colors with `share` + `luminance`, a `theme_type_guess`
(dark/light/mixed from background luminance), and a `background_guess`. Use this to resolve
ties and confirm the accent/CTA color when CSS is sparse.

### 3. Resolve Tailwind color classes to hex (if the site is Tailwind)

```bash
python3 ${SKILL_DIR}/scripts/tailwind_map.py \
  --signals ${WORKSPACE}/signals.json \
  --output ${WORKSPACE}/tw_colors.json
```

Maps harvested `bg-*/text-*/border-*/...` classes against the default Tailwind palette;
custom theme tokens it can't resolve are listed under `unresolved_custom`.

### 4. Synthesize the Visual Brand Identity (you, the agent)

Combine `signals.json` + `palette.json` (+ `tw_colors.json` + the `hero.png` you can view)
and write the artifact. Extract in priority order: **CSS custom properties → meta tags →
ranked color declarations → Tailwind classes**, cross-checked against the screenshot's
dominant colors. Then:

1. **Color roles** — classify into bg-primary/secondary, text-primary/secondary, accent,
   accent-secondary, card. Determine theme type from bg-primary luminance. Buttons/CTAs and
   SVG `fill` reveal the accent. Aim for **5–7 colors** — don't over-extract.
2. **Typography** — display vs body from `fonts`/`font_links`; for proprietary fonts not on
   Google/Fontshare, map to the closest web-available equivalent. Aim for **1–2 fonts**.
3. **Visual patterns** — vibe (2–4 adjectives), one-line layout description, and **3–4**
   reproducible signature CSS elements, using the `layout` signals + the screenshot.
4. **Emit two formats** in one Markdown artifact:
   - **Slide preset** — vibe, layout, display/body typography, a `:root` CSS custom-property
     color block, 3–4 signature CSS elements, and a Google Fonts / Fontshare load tag.
   - **Brand config JSON** — `{name, primary_color, secondary_color, accent_color,
     background, text_color, font_heading, font_body, logo_url?}`.
5. **Extraction Notes** — proprietary-font mappings, multiple/dark-mode themes, sparse-CSS
   caveats.

## Outputs

- `signals.json`, `hero.png`, `palette.json`, `tw_colors.json` — deterministic extraction
  artifacts.
- **Visual Brand Identity** Markdown (`<client>/brand/visual-identity.md`) with the slide
  preset + brand-config JSON + extraction notes — your synthesis, returned as the result
  and saved to the workspace; for team use, post to the Agent Teams channel.

## Credentials / env

- **Required:** none. Rendering and color sampling are keyless (the default). Role
  classification, font choice, and vibe synthesis are done by you (the agent) — no LLM key is
  consumed by scripts.
- **Optional (paid upgrade, with a keyless fallback):**
  - `APIFY_API_TOKEN` — if set → route a too-hostile site through an Apify rendering/extractor
    actor and screenshot. If not set → default keyless path: `extract_brand.mjs` (Playwright
    render + hero screenshot) and `sample_colors.py`; if even Playwright is blocked, ask the
    user for a screenshot/brand guidelines and sample that. Last resort, never required.
  - See `env.optional`.

## Notes & edge cases

- **JS-rendered sites** (Next.js/React) return thin static CSS — `extract_brand.mjs` renders
  first (`networkidle`) so computed styles and webfonts are real. It also captures any
  inlined `tailwind.config` from `<script>` tags.
- **Light/dark mode:** the extractor reads the default (non-media-query) computed theme; note
  any `prefers-color-scheme` dark variant in Extraction Notes.
- **Too many colors** (enterprise sites): the hero screenshot's `dominant_colors` (frequency-
  ranked) + the button/CTA colors define the brand — `sample_colors.py` resolves ties.
- `sample_colors.py` prefers Pillow but falls back to a built-in PNG decoder, so it runs with
  no pip install on the PNG `extract_brand.mjs` writes.
- If a site is unrenderable even via Playwright, ask the user for a screenshot or brand
  guidelines and run `sample_colors.py` against that screenshot as the rescue path.
- Don't over-extract — a 3-color palette + one font family at two weights is a clean preset.
