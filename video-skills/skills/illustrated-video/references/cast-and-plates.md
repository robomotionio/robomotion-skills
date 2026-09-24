# Cast and plates: generated stills that belong together

Consistency comes from order: a style sheet first, then a character sheet
made to the style, then every other picture made **from those two as
reference images**, with the same style words every time.

## Which image tool

- `generate_image` (the OpenRouter image toolkit, on Robomotion credits):
  pass `output_dir` inside the project (e.g.
  `/workspace/videos/<project>/assets/gen`) so the files land where the
  terminal can read them, and `reference_images` (paths) for every variant.
  `google/gemini-3.1-flash-image` for drafts, `google/gemini-3-pro-image`
  for finals and anything with lettering.
- fal (`FAL_KEY`): `fal-ai/nano-banana-2` and `/edit` (see `fal.md`).

Both are the same family of model; use whichever is wired in. Never both
for one cast: the look drifts.

## 1. The style sheet

One 16:9 image that fixes the medium: a paper swatch, the ink swatches, a
sample of line weight, a halftone ramp, a small figure and a small prop in
the style. Prompt it from the video's ink set, e.g.:

> Style reference sheet for a hand-printed animation. Risograph print on
> warm cream paper (#EEE6D6): only four inks, navy (#27306B) for all
> linework, fluorescent orange (#F2692E), fluorescent pink (#EE4E9B),
> sunflower yellow (#F2B632). Flat ink fills, halftone dot shading, slightly
> uneven confident brush-pen outlines, visible paper grain, slight plate
> misregistration. Show: ink swatches, a halftone ramp, a line-weight
> sample, one small character and one small prop in the style. Flat
> background, no gradients, no 3D, no text.

Keep the medium sentence (from "Risograph" to "misregistration") as the
**style line** and paste it into every prompt after this.

## 2. The character sheet

A turnaround of the protagonist on flat paper colour: front, three-quarter,
side, back, plus three expressions. Design for the medium and the
audience, not for a generic mascot:

- one silhouette you can recognise at thumbnail size (a hair shape, a
  hat, a colour block);
- a signature ink (the character owns one of the loud inks);
- details that survive halftone: big shapes, few small ones;
- an outfit that says what the video is about (a headset for a pop singer,
  a lanyard for an office product, overalls for a maker).

For an ensemble, make one sheet per member with a shared outfit language
and each member in their own ink, then one line-up image of all of them
from the individual sheets.

## 3. Variants, always from the sheet

Every pose, expression, close-up and mouth shape is an edit of the sheet
(`reference_images` / `image_urls` = character sheet + style sheet):

> Same character as the reference sheet, exactly the same face, hair,
> outfit and colours. [the pose / expression / framing]. [style line]. Flat
> #EEE6D6 background, no floor shadow, no text.

Make what the storyboard needs, not a library: typically a head-and-
shoulders close-up for lip-sync, two or three full-body poses, and one
reaction. For drawn lip flaps, make closed / open / wide from the close-up,
changing only the mouth.

## 4. Set plates

Backgrounds are either drawn with the kit (sunbursts, grids, charts,
tunnels, rooms from shapes) or generated as plates in the same style: a
stage, a room, a street, a vault. Generate plates **without characters**,
with the horizon and the empty space where the storyboard puts the
character and the type. 16:9, 2K if the camera pushes in.

## 5. Check before you animate

Put the sheet, a variant and a plate side by side (`ffmpeg ... hstack`) and
look: same face? same inks? same line? If a variant drifted, regenerate it
from the sheet, do not fix it with more variants. Then run every image
through `inkify.sh` with the video's inks: it snaps stray colours to the
set and turns soft shading into dots.

## Laying them in

Draw stills with `kit.image` / `kit.puppet` (multiply by default): the paper
background vanishes. A still with a dark or busy background needs a
background removal first (`pixelcut/background-removal` on fal) and
`blend: 'source-over'`. Animate stills: breathe and beat-bob (`puppet`),
swap pose variants on beats (limited animation), push the camera, slide
parallax layers at different speeds. A still that never moves reads as a
mistake.
