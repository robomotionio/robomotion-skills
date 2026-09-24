# Review: look at your own video

You cannot judge a video by reading its code. Render, then look, several
times, at three distances. Budget at least two full passes; the second one
always finds things the first did not.

## The commands

```bash
npx hyperframes check .                                    # lint, runtime, layout: must pass
npx hyperframes snapshot . --at 1.0,12.5,31.0              # a few exact frames, fast, no render
npx hyperframes render . -q draft -o renders/draft.mp4 --fps 30
python3 $SKILL_DIR/scripts/sheet.py renders/draft.mp4 --every 2 --spine spine.json -o out/check/whole.jpg
python3 $SKILL_DIR/scripts/sheet.py renders/draft.mp4 --at 22.8:24.2 --step .1 --spine spine.json -o out/check/hook.jpg
python3 $SKILL_DIR/scripts/sheet.py renders/draft.mp4 --times 3.1,3.3 --crop 900,150,700,600 --w 700 -o out/check/face.jpg
```

Open every sheet with your image-reading tool and look properly. The
`--spine` labels show the words playing at each frame, so you can see
whether the picture says what the sound says.

## What to look for

**The whole piece** (one tile every 1 to 2 s):
- Is it one world? Same inks, same paper, same character design everywhere.
- Does the colour arc move as planned? Does the chorus look like the chorus?
- Is there a dead stretch where nothing changes for three or more tiles?
- Are the first two seconds the strongest frames?

**Every hook, hit and transition** (a strip every 0.1 s):
- Does hero type land on its word (the label shows the word)?
- Do cuts sit on the music? Does a transition cover the cut?
- Anything that pops in without a move, or snaps between two poses?
- Does each read have time before the next starts?

**Faces and text** (crops at full size):
- Faces on model; mouths shaped for the sound in lip-sync shots.
- Every word spelled right, nothing cut by the frame edge, nothing under the
  chip band, nothing on a busy background.
- Receipts exactly right (titles, numbers, names).

**Sound and picture**:
- `ffprobe` shows one video and one audio stream and the right duration.
- Performance clips pass `sync_check.py` (and look right on the mouth sheet).

## Fixing

Fix the cheapest way: timing and layout in `scenes.js`, a clip's offset in
`data-media-start`, a bad still by regenerating from the sheet. Re-render
only what you need (`check` and `snapshot` for layout, a draft render for
motion), then look again at the same places.
