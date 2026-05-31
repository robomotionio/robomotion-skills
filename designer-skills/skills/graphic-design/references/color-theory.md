# Color theory

## Models

- **RGB / HEX** — additive, for screens. Everything you render for digital lives
  here (`#RRGGBB`).
- **HSL / HSB** — author colors by Hue, Saturation, Lightness/Brightness. Easiest
  for building harmonious sets: hold S/L, rotate H.
- **CMYK** — subtractive, for print only. Convert at the end; expect colors to
  desaturate vs screen.
- **LAB / OKLCH** — perceptually uniform; best when you need steps that look
  evenly spaced. OKLCH is the modern choice for programmatic palettes.

## Harmony schemes (pick one, deliberately)

- **Monochromatic** — one hue, varied S/L. Calm, cohesive, easy to keep on-brand.
- **Analogous** — 2-3 adjacent hues. Harmonious, low tension.
- **Complementary** — opposite hues. Maximum contrast/energy; use one as accent,
  not 50/50.
- **Split-complementary** — a base + the two neighbors of its complement. Strong
  contrast, less harsh than straight complementary.
- **Triadic** — three evenly spaced hues. Vibrant; let one dominate.
- **Tetradic** — two complementary pairs. Rich but hard; needs one lead color.

## The 60-30-10 rule

Allocate a composition roughly **60%** dominant, **30%** secondary, **10%**
accent. The accent is where the eye goes — reserve it for the focal point / CTA.
Define a palette as roles, not a pile of swatches: *dominant, secondary, accent,
+ neutrals (a near-black and a near-white that aren't pure #000/#FFF)*.

## Contrast & legibility (WCAG)

When real text sits on color, contrast is non-negotiable.

- Contrast ratio runs 1:1 (none) to 21:1 (black on white).
- **AA:** ≥ **4.5:1** for normal text, **3:1** for large text (≥24px, or ≥18.66px
  bold) and meaningful UI/graphics.
- **AAA:** ≥ **7:1** normal, **4.5:1** large.
- Ratio uses relative luminance, not hue — two vivid colors of similar lightness
  can be unreadable together. Don't rely on hue alone to carry meaning.
- For text over a photo/illustration, add a scrim (semi-opaque overlay) or place
  text in negative space you reserved in the prompt.

## Color psychology (cultural, not absolute)

Red = urgency/energy/appetite · Orange = friendly/affordable/energetic ·
Yellow = optimism/caution · Green = growth/health/finance/"go" · Blue =
trust/calm/corporate/tech · Purple = premium/creative/wisdom · Black =
luxury/authority · White = clean/simple/space · Brown/beige = earthy/craft.
Saturation and lightness shift meaning as much as hue (a pale blue ≠ navy).
Treat these as starting points and defer to brand guidelines when they exist.

## Practical

- Tints (add white), shades (add black), tones (add grey) of your brand hues give
  you a working range without leaving the palette.
- Avoid pure black on pure white for large fields — slightly off-black/off-white
  is easier on the eye and looks more designed.
- In prompts, state palette as roles + hexes: "navy `#0A1428` background, teal
  `#14B8A6` accent on the focal element, warm off-white highlights".
