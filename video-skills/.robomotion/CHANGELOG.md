# Changelog — video-skills

All notable changes to the Robomotion-authored `video-skills/` group.

## [1.2.0] — 2026-09-24
- `paperkit.js`: a `texture` option on `PaperKit.create` (0..1) sets how much
  mottling the paper carries, so a clean, flat reference can get clean paper;
  the mottling now follows the canvas's aspect, so square and vertical
  videos get round blotches, not stretched ones. Documented in
  `references/paperkit.md`.

## [1.1.0] — 2026-09-24
- `illustrated-video` is now described as a look for any kind of video, so
  an agent chooses it when the illustrated look is asked for or shown, not
  whenever a request says "explainer" or "demo".
- Step 0, matching a reference: `references/match-reference.md` (read the
  paper, inks, line, type and layout off the picture, map them onto the
  kit, check side by side).
- Recipes and how-tos: `scripts/howto.js` (step rail and card, extruded
  type, a vessel that fills and mixes, items that drop and float, pours,
  level marks, stir, twist, burst) and `templates/recipe-scenes.js`, a
  data-driven recipe video.
- Videos with no sound: `spine.py --silent <seconds>` makes a pacing grid,
  and `scaffold.sh <dir> - spine.json` builds a project with no soundtrack.

## [1.0.0] — 2026-09-24
- Initial release. New `illustrated-video` skill: a method for videos that
  look drawn and printed and move with their sound, for a song, a
  voiceover or a music bed.
  - `paperkit.js`: a deterministic Canvas2D kit for HyperFrames (spot inks,
    halftone, grain, boiling linework; hero / mid / chip type tiers; labels,
    cards, stamps, sticky notes, charts; screens, cursor and callouts for
    product demos; multiply compositing for generated stills and clips).
  - `spine.py`: beats, bars, sections and script-corrected word timings,
    with guessed-line reporting and section re-transcription patches.
  - `fal.mjs`: a fal.ai client (search, live schema, validated runs,
    uploads, batches, spend ledger and budget cap).
  - `slice.py`, `sync_check.py`, `inkify.sh`, `envelope.py`, `sheet.py`,
    `scaffold.sh`: performance slicing, lip-sync verification, ink
    printing, drawn lip flaps, review sheets, project scaffold.
  - Ships its display fonts (OFL / Apache 2.0).
- Install hook: librosa for the beat grid.
