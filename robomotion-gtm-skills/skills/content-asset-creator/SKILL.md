---
name: content-asset-creator
description: Produce branded, self-contained content assets — industry reports, landing pages, comparison sheets, one-pagers — as styled HTML the agent authors, then exported to high-res PNG and/or print-ready PDF for lead magnets and marketing collateral. Use when a campaign or launch needs a polished downloadable deliverable, not just copy.
metadata:
  version: 1.0.1
  category: content
  type: capability
---

# Content Asset Creator

Turn structured content data into a polished, downloadable asset. **You (the agent)** author
the styled, self-contained HTML — selecting the asset-type template, expanding thin inputs
into narrative + headline + a single CTA, and injecting brand tokens (colors, fonts, logo).
The deterministic `render_asset.mjs` exports it to PNG and/or PDF.

## When to use

- "Create a 2-page industry report on [topic] with these stats."
- "Build a comparison sheet: [our product] vs [competitor]."
- "Make a one-pager / landing-page asset for [campaign]."
- When a campaign or launch needs a polished downloadable deliverable, not just copy.

## Setup (once)

```bash
cd ${SKILL_DIR}/scripts && npm install && npx playwright install chromium
```

## How to run

1. Pick the `asset_type` (`report` / `landing-page` / `comparison` / `one-pager`) and read
   its structure + render width from `scripts/asset_types.json`. Validate `content_data`.
2. Author one self-contained HTML file (inline CSS), rendering each section block
   (hero-stat, stat-grid, comparison-table, chart, cta, footer) per the brand tokens. Add
   Open Graph meta tags so the asset previews well on LinkedIn/X. For multi-page reports,
   author one HTML file per page.
3. Export:

```bash
# PNG (full-page, deviceScaleFactor 2) at the asset's render width
node ${SKILL_DIR}/scripts/render_asset.mjs --html ${WORKSPACE}/report-p1.html --png ${WORKSPACE}/report-p1.png --width 1200

# PDF (print-ready) — assemble a multi-page report
node ${SKILL_DIR}/scripts/render_asset.mjs --html ${WORKSPACE}/report.html --pdf ${WORKSPACE}/report.pdf --pdf-format A4
```

`node ${SKILL_DIR}/scripts/render_asset.mjs --help` lists all flags.

4. Deliver the HTML source + rendered PNG/PDF; post as workspace files / channel attachment.

## Outputs

A self-contained HTML file plus a rendered PNG (full-page, 2x) and optional print-ready PDF.
Multi-page reports produce one PNG per page; combine to a single PDF via one `--pdf` HTML
that stacks the pages, or page-break CSS.

## Credentials / env

- **Required:** none — the HTML-template + Playwright render path is fully self-hosted and
  key-free (the promoted default).
- **Optional:**
  - `LEONARDO_API_KEY` / `STABILITY_API_KEY` / `FAL_KEY` (paid generative imagery, with a
    fallback) — If one is set → generate a bespoke hero image for the asset (higher visual
    quality). If none is set → use a stock/placeholder image or skip the hero entirely (the
    keyless default); the asset still renders fully.
  - `ANTHROPIC_API_KEY` / `OPENAI_API_KEY` — not used by any script (the agent authors the
    copy/HTML); listed only because that authoring is the agent's job.
  - (Hosted Gamma/v0 generation has no Robomotion package — dropped; the render covers the same
    outcome.)

## Notes & edge cases

- Keep reports to 2–3 pages; lead with the biggest stat; one takeaway per section.
- Verify fonts loaded and colors match before delivery — the renderer uses deviceScaleFactor
  2 and waits for `document.fonts.ready` for crisp text.
- Store reusable brand configs (colors/fonts/logo) so repeat assets stay consistent.
- For web distribution, the OG meta tags you add make the asset preview cleanly on social.
