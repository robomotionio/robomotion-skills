# fal.ai: the playbook

fal.ai hosts hundreds of image, video, lip-sync, audio and utility models
behind one API. `scripts/fal.mjs` is your client. It needs `FAL_KEY` for
anything that runs a model; searching and reading schemas are free and need
no key.

## The loop, every time

1. **Find** the model: start from the table below, then confirm it is
   current: `node $SKILL_DIR/scripts/fal.mjs search "<what you need>"`.
   Models change monthly; a newer version of the same family is usually
   better and often cheaper.
2. **Read its schema**: `fal.mjs schema <endpoint>`. It prints every input
   with its type, allowed values, default, and the model's price line. Use
   exactly these field names and values: `run` refuses anything else before
   spending.
3. **Estimate** the cost from the price line (per image, per second of
   output, per minute of input) and pass it as `--est`.
4. **Run** one first, look at it, then batch the rest:

```bash
node $SKILL_DIR/scripts/fal.mjs run minimax/h3-max/lip-sync/image-to-video \
  --input '{"image_url":"assets/gen/hero-cu.png","audio_url":"assets/slices/s03.mp3","resolution":"768P"}' \
  --est 0.56 --name s03 --out assets/fal
```

Local paths in the input are uploaded for you. Every file in the result
(videos, images, audio) is downloaded to `--out` as `<name>_<field>.<ext>`,
next to `<name>.json` (the full request and result).

5. **Batch** independent jobs: write `jobs.json` as
   `[{"name":"s03","endpoint":"...","input":{...},"est":0.56}, ...]` and run
   `fal.mjs batch jobs.json --concurrency 4`. Failures are listed in
   `.fal/batch-failures.json`; rerun only those.

A job that outlives its timeout keeps running on fal: fetch it later with
`fal.mjs result <endpoint> <request_id>` rather than submitting again.

## Money

- Set the budget before the first job: `fal.mjs budget <usd>`. Every `run`
  and `batch` is refused when it would pass it. `fal.mjs spend` shows the
  ledger. Estimates are yours, so estimate honestly and round up.
- Draft cheap, finish expensive: 480p or the fast/lite variant while you are
  finding the shot, the full model only for the take you will keep.
- Never loop a generation to "see what happens". Change one thing per retry
  (the prompt, the seed, the framing of the reference), and stop after three
  failed tries at the same shot: change the plan for that shot instead.
- Raising the budget needs the person's yes, in so many words.

## Which model for which job (checked 2026-09; confirm with `search`)

| Job | Endpoint | Price | Notes |
|---|---|---|---|
| Character and style sheets, set plates | `fal-ai/nano-banana-2` | $0.08 / image (1K) | Strong at following a style description; 2K ×1.5 |
| Variants from references (poses, expressions, mouth shapes, same character new scene) | `fal-ai/nano-banana-2/edit` | $0.08 / image | `image_urls` = the character sheet + style sheet. The workhorse for consistency |
| Finest detail and lettering in a still | `fal-ai/nano-banana-pro`, `/edit` | $0.15 / image | When a still carries text or fine linework |
| Alternative look, layered output | `bytedance/seedream/v5/pro/edit`, `.../layerize` | ~$0.07 / image | Layerize splits an image into layers (character off its background) |
| Remove a background | `pixelcut/background-removal` | small | Only when multiply over paper is not enough (dark backgrounds) |
| **Lip-sync from a still** (talking or singing close-up) | `minimax/h3-max/lip-sync/image-to-video` | $0.05 / s 480P, $0.08 768P, $0.16 1080P | Audio 5–14.8 s (longer is cut). Face large in frame. `enable_transcription: true` for speech. The default for performance close-ups |
| Lip-sync from a still, alternative | `fal-ai/sync-lipsync/v3/image-to-video` | $0.133 / s | Good on illustration; try when H3 fails a shot twice |
| Re-sync an existing clip's mouth to new audio | `fal-ai/sync-lipsync/v3`, `veed/lipsync/v2` | ~$0.07–0.13 / s | Video in, video out |
| **Performance with body, camera, several characters** | `bytedance/seedance-2.5/reference-to-video` | $0.22 / s 480p, $0.47 720p | Up to 30 images, 10 videos, 10 audio refs (1.8–30 s each), named `@Image1`, `@Audio1` in the prompt. Dance, choreography, a singer on a set |
| One image into motion | `bytedance/seedance-2.5/image-to-video` | same | `image_url` (+ `end_image_url` to land on a pose) |
| Camera move over a still (parallax, push, orbit) | `minimax/h3-max/camera-controls` | $0.025–0.08 / s (launch rate) | Scene frozen, only the camera moves: cheap depth for set plates |
| Stylised motion | `minimax/h3-max/styles/hand-drawn`, `retro-toon-70s`, ... | per second | When the whole shot should move in that style |
| Word timings for sung vocals | `fal-ai/elevenlabs/speech-to-text/scribe-v2` | $0.008 / min | Better than local whisper on singing; use it when `spine.py` reports many GUESSED lines |
| Sound effects | `fal-ai/elevenlabs/sound-effects/v2` | small | `text`, `duration_seconds`; whooshes, stamps, clicks for the hits |
| Music bed | `elevenlabs/music/v2.5` | $0.60 / min | Only when the person asked for music and gave none |
| Upscale a clip | `fal-ai/seedvr/upscale/video`, `fal-ai/bytedance-upscaler/upscale/video` | ~$0.007 / s | After inkify is not needed: upscale the raw clip first, then inkify |

Prices move; the `schema` price line is the truth.

## Prompts that work

- Say what moves and how, and what the camera does, in production terms
  (push in, tracking shot, handheld, whip pan). One main action and one
  camera move per shot.
- Name the references by role: "@Image1 is the character (keep her face,
  hair and outfit exactly), @Image2 is the set, @Audio1 is her vocal: she
  sings it to camera, lips in sync".
- Keep the style words identical across every prompt of a video (paste the
  same style line from the style sheet). Consistency comes from the same
  references plus the same words.
- For anything laid in with multiply: "flat [paper colour] background, no
  shadows on the background, no gradient".
- Ask for no text in generated images and clips; the kit does all type.

## Safety and honesty

- Generate only people the person has the right to show: their own brand
  mascot, an invented character, or someone who consented. Never a real
  public figure's likeness singing or saying things.
- Do not pass private or customer data into prompts.
- A generated image or clip is never presented as footage of a real event.
