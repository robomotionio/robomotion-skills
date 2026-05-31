# Format specs (dimensions & aspect ratios)

Set the **right aspect at generation time** — composition is baked in, so
cropping later wrecks it. Pick from the use-case below, then map to your
toolkit: OpenAI uses `WIDTHxHEIGHT`; Gemini uses `aspect_ratio` (+ `size`).

## Web / content

| Use | Aspect | Typical px |
|---|---|---|
| Blog hero / cover | 16:9 | 1600×900 (or 1536×1024 ≈ 3:2) |
| In-article / section image | 16:9 or 3:2 | 1200×675 / 1200×800 |
| Square inline / thumbnail | 1:1 | 1080×1080 |
| Wide site banner | 21:9 / 3:1 | 1920×640 |

## Open Graph & social shares

| Platform | Aspect | px |
|---|---|---|
| Open Graph (FB/LinkedIn link preview) | 1.91:1 | **1200×630** |
| X / Twitter summary-large-image | 1.91:1 | 1200×628 |
| Instagram feed (square) | 1:1 | 1080×1080 |
| Instagram portrait | 4:5 | 1080×1350 |
| Stories / Reels / TikTok (vertical) | 9:16 | 1080×1920 |
| YouTube thumbnail | 16:9 | 1280×720 |
| LinkedIn shared image | 1.91:1 | 1200×627 |

OG/link-preview = **1200×630 (1.91:1)** is the single most useful share size;
when in doubt for "a social card", use it.

## Ads (common display units, px)

Leaderboard 728×90 · Medium rectangle 300×250 · Large rectangle 336×280 ·
Wide skyscraper 160×600 · Mobile leaderboard 320×50 · Half-page 300×600 ·
Billboard 970×250. (Generate the artwork at the aspect; real ad copy/CTA is added
in layout.)

## Icons & favicons (px, square)

App icon 1024×1024 (master) · favicon 16/32/48 · touch icon 180×180 · Android
512×512. Design at 1024² and downscale; keep the mark legible at 16px (simple,
high-contrast, minimal detail).

## Print (when asked)

- Work in **CMYK**, not RGB; expect duller color than screen.
- **Resolution: 300 DPI** at final size (so a 4×6in card = 1200×1800px).
- **Bleed:** extend art **3mm (0.125in)** past every trimmed edge; keep text
  inside a safe margin ~3-5mm from the trim.
- Common: business card 3.5×2in, A-series (A4 210×297mm), US Letter 8.5×11in,
  poster 18×24in.

## Rules of thumb

- Generate at **2× the display size** for retina crispness when cheap to do so.
- Reserve negative space for any format that will carry a headline (covers, OG
  cards, ads) — see `references/composition-layout.md`.
- gpt-image arbitrary `WIDTHxHEIGHT` and Gemini `gemini-3-pro-image` support
  larger/explicit sizes; the lighter flash image models are aspect-ratio first.
