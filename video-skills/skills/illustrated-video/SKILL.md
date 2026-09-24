---
name: illustrated-video
description: "The illustrated look for any kind of video: drawn and printed on paper in a few spot inks (halftone, grain, boiling linework), big kinetic type, paper inserts, a generated cast laid in with multiply, and optional lip-synced performances from fal.ai (MiniMax H3 lip-sync, Seedance 2.5). Use it when the look is asked for or shown, whatever the video is: a hand-drawn, illustrated, sketch, cartoon, riso, print, zine, comic, storybook or anime look; a reference image or video that is drawn rather than photographed (match it); a character, mascot or presenter, or anyone singing or talking on screen. It then builds the whole video for that kind: a song or lyric video, a promo or product demo, an explainer, a recipe or how-to (a step-by-step kit), a piece over a music bed, or a silent one. Not for a clean, photographic or UI-led video with no look asked for. Also the fal.ai playbook for any image, video, lip-sync or audio generation."
metadata:
  version: 1.2.0
---

# Illustrated video

You make short videos that look drawn and printed, not assembled from a
template, and that move exactly with their sound, or with a steady pace when
there is none. This skill is a **look**: once the look is chosen it builds
any kind of video, a music or lyric video, a product demo with a voiceover,
an explainer with a mascot, a recipe or how-to, a promo over a music bed.
What changes with the kind is the **spine**, the timing everything is cut
and animated to, and the parts it is built from (`references/kinds.md`).

The look is one medium held all the way through: a paper stock, three to
five spot inks, halftone for tone, grain over everything, linework that
boils a few times a second. Generated pictures and generated performance
footage are printed in the same inks and laid in with multiply, so they sit
on the page like everything else. Type is part of the picture: the key
words are big and land on the syllable, the rest follows in a small chip.

`SKILL_DIR` is this skill's folder. Work inside a HyperFrames project,
`/workspace/videos/<project>/` (create it with `hyperframes init`, see
`/hyperframes-cli`). Everything below is run from the project folder.

## What you need, and the three tiers

| Tier | What it adds | Needs |
|---|---|---|
| **Drawn** (always) | Paper, inks, sets, charts, kinetic type, chip, inserts, screenshots and logos the person gave you, printed in the inks | nothing |
| **Generated stills** | A cast (a character sheet with poses, expressions and mouth shapes), set plates, props | an image tool: `generate_image` (OpenRouter toolkit, Robomotion credits) or fal image models (`FAL_KEY`) |
| **Performance** | Real singing or talking with lip sync, dance and camera moves | `FAL_KEY` (fal.ai): MiniMax H3 lip-sync, Seedance 2.5 |

Pick the highest tier you have and say which in the plan. Every tier makes a
complete video; a drawn-only video is a real deliverable, not a fallback. If
`FAL_KEY` is missing, do not ask for one mid-run: make the video without
performance shots, and mention once, at the end, what a fal key would add.

Before the first fal call, read `references/fal.md` (models, prices, the
budget rule). **Money:** fal jobs cost real money. Set a budget before the
first job (`fal.mjs budget <usd>`): the amount the person gave, or $5 for a
short piece and $20 for a full song when they gave none, and say so in the
plan. Never raise it without their yes.

## The workflow

Post the plan (step 3) as one short message and go on; ask only when you
cannot tell what the video is for.

### 0. A reference: match it

When the person sent an image or a video to show the look, match it before
you invent anything. Read `references/match-reference.md`: take the palette,
the paper, the line, the type and the layout from it, write them down as the
video's look, and check your frames against it side by side. A reference
that shows a recipe, a step list or a product card also tells you the
parts: build those (`references/kinds.md`).

### 1. The spine: what the video is timed to

Put the audio at `assets/track.mp3` (a song, a voiceover, or a voiceover
mixed over a music bed; `hyperframes tts` makes a voiceover, `/media-use`
covers voices and music). Then:

```bash
npx hyperframes transcribe assets/track.mp3 --model small.en --json      # word timings → transcript.json
python3 $SKILL_DIR/scripts/spine.py --audio assets/track.mp3 \
    --transcript transcript.json --script script.txt -o spine.json     # + beats, bars, sections
```

- `--script` is the text the person gave you (lyrics, the voiceover
  script), one line per line. It fixes the words; the transcript gives the
  times. Always pass it when you have it.
- Speech only, no music: add `--no-beats`. Music with no words: omit
  `--transcript`.
- **No sound at all** (a silent recipe, a loop, nothing was asked for):
  `python3 $SKILL_DIR/scripts/spine.py --silent 30 -o spine.json` gives a
  steady pacing grid of that length, and `scaffold.sh <dir> - spine.json`
  builds the project with no soundtrack. Do not add a voice or music the
  person did not ask for.
- **Read spine.py's output.** It lists every line whose words were not
  heard as `GUESSED`. Sung vocals are often missed. For each guessed stretch
  cut that section, transcribe it again with `--model medium.en`, and pass it
  back: `--transcript transcript.json --transcript part.json@<start>`. Repeat
  until no line the video depends on is guessed.

`spine.json` has `bpm`, `offset`, `beats`, `bars`, `sections` (with an
energy label), `words` and `lines`, all in track seconds.

### 2. Direction: one idea, one world

Read `references/art-direction.md`. Decide, in writing, before any code:

- **The idea**: one sentence. What the video is about underneath the words.
- **The world**: ink set (from `PaperKit.INKSETS` or your own), paper, the
  recurring set pieces, a colour arc across the sections.
- **The cast** (tiers 2 and 3): the protagonist and any ensemble, designed
  for the medium. See `references/cast-and-plates.md`.
- **The clock**: one running device that shows the story advancing (a date
  that races forward, a counter, a meter, a version number).
- **The hook**: the first two seconds. Biggest type of the video, the
  protagonist's face or the product's promise, on the first word.
- **Receipts**: the real, specific things the piece refers to (a paper's
  title, a headline, a product's actual numbers, a quote). They become cards,
  labels and stamps. Real ones only: never invent a citation or a number.

### 3. Storyboard

Write `STORYBOARD.md` in the format in `references/storyboard.md`: one row
per shot with its time span (snapped to the spine), what is seen, the event,
the type tier and where the text sits, the layers it uses, and the
transition. Check it against the rules there (timing reads, one focal
action, text never fighting the picture, every seam a transition). Post a
short summary of it as the plan: length, the idea, the look, the tier, the
fal budget if any.

### 4. Cast, plates and performances (tiers 2 and 3)

- Stills: follow `references/cast-and-plates.md`. Style sheet first, then the
  character sheet, then every pose, expression and mouth variant made **from
  the sheet as a reference image**, then set plates. All on flat paper
  colour, so multiply removes the background.
- Performances: follow `references/performance.md`. Slice the audio per shot
  (`slice.py`), generate (`fal.mjs`), print in the inks (`inkify.sh`), check
  sync (`sync_check.py`), place.

### 5. Build

```bash
sh $SKILL_DIR/scripts/scaffold.sh . assets/track.mp3 spine.json
```

That writes `index.html` (the layers: back canvas → performance clips →
front canvas → soundtrack), `scenes.js` (your shots), `spine.js` and copies
the kit, the how-to parts (`howto.js`) and the fonts into `assets/`. For a
recipe or how-to, start from `templates/recipe-scenes.js` instead
(`cp $SKILL_DIR/templates/recipe-scenes.js scenes.js`): edit its recipe data
and colours, and it builds the steps. Write the shots in `scenes.js` with the
kit (`references/paperkit.md`). Each shot is a pure function of time and
paints the whole frame. Build and check one shot at a time.

### 6. Look, fix, look again

Follow `references/review.md`. At minimum: `npx hyperframes check .`
passes; a whole-video sheet; a strip (every 0.1 s) across every hook, hit
and transition; a close look at every face and every piece of text. Fix,
re-render the part, look again. Two full passes minimum.

### 7. Render and hand over

```bash
npx hyperframes render . -q standard -o renders/video.mp4 --fps 30
python3 $SKILL_DIR/scripts/sheet.py renders/video.mp4 --every 2 -o renders/contact-sheet.jpg
ffprobe -v error -show_entries format=duration:stream=codec_type -of compact renders/video.mp4
```

Hand over the MP4 and the contact sheet. Say what tier it used, what fal
spent (`fal.mjs spend`), what you would do with another pass, and anything
you could not verify (a guessed line, a lip-sync shot that only just passed).

## Rules that make it look designed

- **One medium.** Everything is ink on paper: no gradients, glows, drop
  shadows in grey, or photos left in their own colours. Photos,
  screenshots, generated stills and clips all go through `inkify`.
- **Type is picture.** Three tiers, never more on screen at once than the
  eye can read: `hero` (one to three words, huge, on the syllable), `mid`
  (a serif aside), `sub` (the chip). When hero type is up, the background
  goes quiet and the character moves to the other side.
- **The first two seconds are the most designed** frames of the video.
- **Everything lands on the spine.** Cuts on bars or line starts, type on
  its word, hits on beats, stamps on the stressed syllable.
- **Something happens in every shot**, and each shot has one thing to look at.
- **Receipts over decoration.** A real paper title on a clipping says more
  than an abstract shape.
- **Keep the bottom band clear** for the chip (y > 960) and keep faces and
  key type above it.
- **Never publish** anything anywhere, and never spend past the fal budget.

## Scripts

| Script | Does |
|---|---|
| `scripts/spine.py` | Beats, bars, sections, and script-corrected word/line timings |
| `scripts/scaffold.sh` | Layered HyperFrames project from the templates |
| `scripts/paperkit.js` | The drawing kit (copied into `assets/`) |
| `scripts/howto.js` | Recipe and how-to parts: step rail and card, a vessel that fills, pours, stir, twist (copied into `assets/`) |
| `scripts/fal.mjs` | fal.ai: search, schema, run, batch, upload, spend, budget |
| `scripts/slice.py` | Audio slices sized for a lip-sync or video model |
| `scripts/inkify.sh` | Print an image or clip in the video's inks |
| `scripts/sync_check.py` | Is a performance clip really in sync? PASS / SHIFT / REDO |
| `scripts/envelope.py` | Mouth openness per frame, for drawn lip flaps |
| `scripts/sheet.py` | Contact sheets and strips of a render, with the words |

## References

| Read | When |
|---|---|
| `references/match-reference.md` | Step 0: when the person sent a picture or video of the look |
| `references/art-direction.md` | Step 2: the look, the hook, attention, what to avoid |
| `references/storyboard.md` | Step 3: the shot list format and its checks |
| `references/cast-and-plates.md` | Step 4: style sheet, character sheet, variants, sets |
| `references/fal.md` | Before any fal call: models, prices, budget, batches |
| `references/performance.md` | Step 4: lip-sync and dance shots, and their sync loop |
| `references/paperkit.md` | Step 5: the kit's API |
| `references/kinds.md` | Step 2: what changes for a song, a voiceover demo, an explainer, a recipe or how-to, a music bed, no sound |
| `references/review.md` | Step 6: how to look at your own video |
