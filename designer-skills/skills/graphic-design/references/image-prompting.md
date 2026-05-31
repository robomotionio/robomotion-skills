# Image-model prompting (gpt-image & Gemini / Nano Banana)

The prompt is where design judgment becomes a result. A vague prompt yields a
generic stock-looking image; a directed one yields something that reads as
designed. This is the method, a reusable style lexicon, and the model-specific
notes.

## The prompt skeleton

Build every prompt from these slots, in roughly this order. Omit a slot only
when you genuinely don't care about it.

1. **Image type / medium** — set expectations first. e.g. "Flat 2D vector
   illustration", "Isometric 3D render", "Minimal single-line icon", "Editorial
   photograph, 50mm", "Risograph-style print", "Watercolor spot illustration".
2. **Subject + single action** — one clear subject doing one clear thing.
3. **Composition** — placement of the focal point, camera angle/crop, and
   explicit **negative space**: "centered", "subject lower-right, large empty sky
   upper-left for a headline", "flat lay, top-down".
4. **Color palette** — dominant, secondary, accent, background. Give hex codes
   when you have brand colors: "palette: deep navy #0A1428 background, teal
   #14B8A6 accents, warm off-white highlights".
5. **Style descriptors** — line weight, shading (cel/soft/none), texture, level
   of detail, era/movement ("Bauhaus", "80s synthwave", "Swiss/International").
6. **Light & mood** — direction and quality of light, contrast, atmosphere:
   "soft diffused light, low contrast, calm" vs "hard rim light, high contrast,
   dramatic".
7. **Constraints / exclusions** — orientation, and a short "no" list ("no text,
   no logos, no busy background, no border").

## Style lexicon (vocabulary that steers the model)

- **Illustration:** flat vector, flat with subtle gradients, cel-shaded, line
  art, isometric, low-poly, claymation/3D clay, paper-cut/collage, risograph,
  woodcut, gouache/watercolor, technical blueprint, hand-drawn doodle.
- **Photographic:** studio product shot, lifestyle/editorial, macro, aerial/
  top-down flat lay, golden-hour, film/35mm grain, long exposure, tilt-shift.
- **Movements/eras:** Bauhaus, Swiss/International typographic, Art Deco,
  Memphis, mid-century modern, brutalist, vaporwave/synthwave, Y2K.
- **Lighting:** soft/diffused, hard/direct, rim/back light, volumetric, neon
  glow, chiaroscuro, ambient occlusion (for 3D).
- **Finish:** matte, glossy, grainy/textured, clean/smooth, high-key (bright),
  low-key (dark).

Name the *quality* you want, not just the noun. "Professional" and "beautiful"
do nothing; "flat vector, two-tone, generous negative space, soft gradients" do.

## The on-style set (the most important technique)

A blog post or campaign needs images that look like a family. Don't re-roll each
from scratch — they'll drift in palette and rendering. Instead:

1. Generate the **lead image** (usually the cover/hero) with `generate_image`,
   fully art-directed.
2. For every other image, call `edit_image` with the **lead image as a
   reference** (`image_paths`) and a prompt like: "In the **same** flat-vector
   style, palette, line weight and lighting as the reference image: <new subject
   and composition>. Keep the look consistent; change only the subject."
3. You can pass **multiple references** (a style frame + a brand mark, or several
   prior pieces) — Gemini accepts up to 14, gpt-image up to 16.

For variants/sizes of the *same* concept (e.g. a 16:9 hero and a 1:1 social
crop), reference the approved image and ask for the new aspect with the subject
re-composed to fit — don't just crop.

## Iterating a near-miss

- Change **one thing** per edit; describe the delta, not the whole image again:
  "same image, but move the subject left and add more empty space on the right",
  "warmer palette, reduce background clutter".
- If composition is wrong, it's usually faster to re-`generate_image` with a
  sharper composition line than to edit.
- If the style is right but the subject is off, `edit_image` the result.

## Model-specific notes

- **gpt-image (OpenAI, primary):** strong general aesthetic and prompt
  adherence; `size` is explicit `WIDTHxHEIGHT`; `quality` low/medium/high — use
  `high` only for heroes (slower, costlier). Weak at long/exact text.
- **Gemini / Nano Banana (optional):** excellent multi-reference consistency and
  the **best in-image text** of the two — prefer it when a design genuinely needs
  a short, correct word in the art, or when matching many references. Uses
  `aspect_ratio` + `size` (`1K`/`2K`/`4K`; `2K`/`4K` only on `gemini-3-pro-image`).
- **Both:** still avoid baking in body text or logos; add real type in the
  layout. Both occasionally add unwanted borders/frames — exclude them
  explicitly if you see them.

## Common failure modes → fixes

- *Looks generic / stocky* → add a specific style + era + palette; remove generic
  adjectives.
- *Cluttered, no focus* → name one focal point; add "minimal, lots of negative
  space".
- *Set doesn't match* → use the reference-image workflow, don't re-roll.
- *Garbled text* → remove text from the prompt; reserve space for real type.
- *Wrong crop for the platform* → set the right aspect on the first call.
- *Colors off-brand* → specify exact hexes and which element each maps to.
