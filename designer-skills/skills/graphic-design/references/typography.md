# Typography

Most AI-rendered text is unreliable, so you usually set **real type in the
layout/CMS**, not in the image. This is how to do that well (and how to describe
type when a design genuinely needs it in-art).

## Classification

- **Serif** — bracketed strokes; authoritative, editorial, traditional
  (Georgia, Merriweather, Playfair Display, Times).
- **Sans-serif** — no serifs; modern, clean, neutral (Inter, Helvetica, Roboto,
  Work Sans). Grotesque (Helvetica) vs humanist (Inter, Open Sans) vs geometric
  (Futura, Poppins).
- **Slab serif** — heavy rectangular serifs; sturdy, confident (Roboto Slab).
- **Monospace** — fixed width; technical/code (JetBrains Mono, IBM Plex Mono).
- **Script / display** — decorative; for logos and large headlines only, never
  body.

## Pairing

- **Safest:** one family, multiple weights/styles. Cohesive by construction.
- **Classic contrast:** a serif display + a sans body (or vice-versa). Pair on
  *contrast* (clearly different) while sharing a mood/x-height.
- **Avoid** two fonts that are *similar but not the same* (two humanist sans) —
  reads as a mistake. Cap it at two families (three with a mono for code).
- Reliable, free, broadly available pairings: Inter (everything) · Playfair
  Display + Inter · Merriweather + Open Sans · Poppins + Inter · Space Grotesk +
  Inter.

## Scale & hierarchy

- Use a **modular scale**, not arbitrary sizes. Common ratios: 1.25 (major
  third), 1.333 (perfect fourth), 1.5. From a 16px base, ×1.25 → 16, 20, 25, 31,
  39, 49…
- Establish **3-4 levels**: display/H1, subhead, body, caption. Differentiate by
  size *and* weight, not size alone.
- Hierarchy = contrast: size, weight, color, case, and space all signal "read me
  first".

## Spacing & rhythm

- **Line length:** 45-75 characters for body (≈ 50-65 ideal). Too wide tires the
  eye; too narrow breaks rhythm.
- **Line height (leading):** ~1.4-1.6× body size; tighter for large headlines
  (~1.0-1.2).
- **Letter-spacing (tracking):** slightly negative on big headings, slightly
  positive on all-caps/small labels. Leave body at default.
- **Alignment:** left-aligned is the default for legibility. Center only short
  blocks (headlines, cards). Justify only with hyphenation, rarely on web.

## When type must be in the image

Keep it to a single short word or number, choose Gemini over gpt-image, and still
expect to verify spelling. Describe it explicitly: the word, its placement, the
font character ("bold geometric sans"), and that it must be spelled exactly.
Otherwise: reserve negative space in the prompt and add the type in layout.
