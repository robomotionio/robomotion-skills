# Performance shots: singing, talking, dancing

A performance shot is a generated clip of the cast acting the sound: a
close-up singing the line, a presenter saying the claim, the ensemble
hitting the chorus move. They are the most expensive shots and the ones the
eye goes to, so use them for the lines that matter most, and make sure they
are in sync.

## Choose the engine per shot

| The shot | Engine | Why |
|---|---|---|
| A face singing or talking, little body motion | MiniMax H3 lip-sync (still + audio) | Cheapest per second, tight mouths, keeps the still's design exactly |
| Face with head and shoulder motion, camera drift | Seedance 2.5 reference-to-video with `@Audio1` | Motion and lip sync in one |
| Dance, several characters, a set, a camera move | Seedance 2.5 reference-to-video | Choreography and camera; mouths matter less |
| No fal key, or a mascot that should look drawn | Drawn lip flaps (`envelope.py` + mouth variants) | Free, always in sync, reads as animation |

## The loop

1. **Pick the shots** from the storyboard: the spans (track seconds) that
   get a performance. Write them to `shots.json`:
   `[{"name":"s03-sparks","s":2.35,"e":4.5}, ...]`.
2. **Slice the audio** to what the engine accepts:
   `python3 $SKILL_DIR/scripts/slice.py --audio assets/track.mp3 --shots shots.json --model h3 --out assets/slices`
   (`--model seedance` for Seedance). Short shots get a longer window
   around them; `slices.json` records each window and its `lead` (how far
   into the clip the shot starts).
3. **Frame the reference.** For lip-sync the face must be big: head and
   shoulders, face at least a third of the frame height, mouth unobstructed,
   looking at camera or three-quarters. Make a close-up still for it from
   the character sheet (see `cast-and-plates.md`) on flat paper colour.
4. **Generate one**, look at it (`sheet.py <clip> --every 0.5`), then batch
   the rest with the same settings.
   - H3: `{"image_url": "<still>", "audio_url": "<slice mp3>", "resolution": "768P", "enable_transcription": true}`
   - Seedance: `{"prompt": "...", "image_urls": ["<character sheet>", "<close-up still>", "<set plate>"], "audio_urls": ["<slice mp3>"], "resolution": "480p" (draft) / "720p" (final), "duration": "<window length rounded up>", "aspect_ratio": "16:9"}`,
     with a prompt like: "@Image1 is the singer (keep her face, hair and
     outfit exactly as drawn), @Image3 is the set. She sings @Audio1 to
     camera, lips exactly in sync with the vocal, small head moves on the
     beat. Slow push in. Flat print-illustration style, [style line], no
     text." For a vocal-only reference, set `generate_audio: false` when you
     do not need the model's own sound.
5. **Check sync** for every clip that shows a mouth:
   ```bash
   python3 $SKILL_DIR/scripts/sync_check.py --clip assets/fal/s03_video.mp4 \
     --slice assets/slices/s03-sparks.wav --face 0.38,0.42,0.24,0.2 \
     --words spine.json --win <win_s> --sheet out/check/s03-mouth.jpg
   ```
   - `--face` is the mouth box as fractions of the clip frame; find it on a
     sheet of the clip first. A wrong box gives a meaningless score.
   - **PASS**: use it. **SHIFT**: add the reported seconds to the clip's
     `data-media-start` and check again. **REDO**: regenerate (bigger face,
     another seed, the other engine).
   - The score is a guide, not proof: short clips and full mixes (drums
     under the voice) make it noisy. Always also open the mouth sheet and
     look: open mouths on open vowels, closed on m/b/p.
6. **Print it in the inks**: `sh $SKILL_DIR/scripts/inkify.sh <clip> assets/perf/s03.mp4 "<paper> <ink> <a> <b> <c>"`
   (same inks as the video, paper first).
7. **Place it** in `index.html` as a `<video class="perf clip">`: `data-start`
   = the shot's start, `data-duration` = its length, `data-media-start` =
   the slice's `lead` (+ any SHIFT), `muted`, sized and positioned with
   `style`. It sits between the back and front canvases and is multiplied, so
   paper disappears and the ink prints over the drawn set. Draw the set on the
   back canvas and the type on the front, as in any shot.

## Drawn lip flaps (no fal, or a drawn mascot)

Make three mouth variants of the close-up (closed, open, wide) with the
image model, from the same still, changing only the mouth. Then:

```bash
python3 $SKILL_DIR/scripts/envelope.py --audio assets/track.mp3 --fps 30 -o assets/mouth.json
```

Load it as a script (`window.MOUTH = ...`) and in the shot:

```js
const open = kit.mouth(MOUTH.env, MOUTH.fps, t);
kit.puppet(open > .55 ? IMG.wide : open > .18 ? IMG.open : IMG.closed, x, y, h);
```

On a full music mix raise `--gate` (0.25–0.35) so drums do not flap the
mouth, and check a strip of the shot against the words.

## Costs, roughly

A 2-minute song with performance on about a third of it: 40 s of H3 at 768P
is about $3.20 plus a few retries; the same 40 s on Seedance 720p is about
$19. Mix them: Seedance for the chorus and dance shots, H3 for verses.
