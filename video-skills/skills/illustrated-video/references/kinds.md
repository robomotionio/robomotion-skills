# Kinds of video: what changes

The method is the same for every kind. The spine, the hook and where the
type goes change.

## Music video / lyric video (a song)

- **Spine**: beats, bars, sections, and the sung words (always pass the
  lyrics as `--script`, and repair GUESSED lines).
- **Structure**: sections set the shape. Each chorus returns to a home set,
  louder each time; verses travel. Cut on bars in verses, on beats in
  choruses; hold on the last line of a section.
- **Type**: every sung line gets the chip; hero words for the lines' key
  words; the chorus hook as the biggest type of the video.
- **Performance**: close-up lip-sync on the lines that carry the song (the
  first line, the hook, the last line); dance on the chorus; inserts and
  sets for the rest.
- **Clock**: whatever the song is about moving forward (dates, a counter, a
  meter that climbs each chorus).

## Product demo or promo with a voiceover

- **Spine**: the voiceover's words (`--no-beats` unless there is music under
  it; with a bed, run the beat grid on the bed alone and the words on the
  voice). Cuts on line starts and on the stressed word of each claim.
- **Structure**: problem → product → how it works (two or three moves, each
  one screen) → proof (a real number, a real quote) → the call to action.
- **Screens**: real screenshots (captured from the site or given by the
  person) in `screen()`, printed in the inks, with `cursor` and `callout` to
  show the one action each shot is about. Push the camera into the part of
  the screen being talked about.
- **Type**: the product name and each claim's key word as hero type; the
  chip carries the voiceover.
- **Cast**: optional. A mascot or presenter can say the first and last lines
  (lip-sync), or react in inserts. The product is the hero.
- **Receipts**: real numbers from the site or the brief as labels and
  stamps. Never invent a metric, a customer or a quote.

## Explainer (a topic, text or article)

- **Spine**: voiceover words, or phrases timed to a music bed when silent.
- **Structure**: one idea per shot; each idea gets one drawn diagram (chart,
  flow of shapes, before/after) built on screen as the words arrive.
- **Type**: the term being explained as hero type when it is first said;
  definitions as `mid`.

## Brand piece or promo over a music bed (no words)

- **Spine**: beats and sections only. There is no chip.
- **Type** carries the message: short hero lines, one per phrase, on the
  downbeats. Three to six lines for 20 to 30 seconds.
- **Structure**: build in energy with the music; the logo or the call to
  action lands on the biggest hit.

## Length and format

- Social cuts: 9:16 (1080×1920) or 1:1; move the chip up (y ≈ 1500 for 9:16)
  and stack type vertically. Set the canvas size in `PaperKit.create`
  (`width`, `height`) and in `index.html` (`data-width`, `data-height`).
- A hook in the first two seconds matters more the shorter the piece.
