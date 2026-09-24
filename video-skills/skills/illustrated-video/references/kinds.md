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

## Recipe or how-to (steps)

- **Spine**: a voiceover's words when there is one; otherwise the pacing
  grid (`spine.py --silent <seconds>`). Most recipe videos are silent: the
  steps are on screen.
- **Start from** `templates/recipe-scenes.js` and `howto.js`
  (`references/paperkit.md`, "How-to parts"). Fill in the recipe data: the
  vessel, each step's kind (`items`, `pour`, `stir`, `twist`, `note`), its
  amount, its card text and when it happens.
- **Structure**: the title lands first (about 2 s), then one step at a time,
  each with its own action in the picture, its card and its dot on the rail;
  end on the finished thing with a short celebration and the whole recipe in
  one line (1 : 1 : 1, the ratio, the serving).
- **Timing**: a pour needs about 4.5 s, a drop of a few items 2 s, a stir 4 s,
  a garnish 2.5 s. A 30 s recipe holds five or six steps.
- **Receipts**: the real amounts in the units the person used, and both
  units when it helps (1 oz · 30 ml). Never invent a step or an amount; when
  the person gave only the dish's name, use the standard recipe and say so.
- **Not a drink?** The vessel is a glass, a jar or a bowl (`topW`, `botW`,
  `unit`); `items` can be anything with a `draw` function (a scoop, a slice);
  `note` steps (bake 20 min, rest overnight) carry a card and a dot with no
  action in the vessel. For steps that are not about filling at all (fold,
  knead, plate), draw the action as its own shot and keep the card and rail.

## Brand piece or promo over a music bed (no words)

- **Spine**: beats and sections only. There is no chip.
- **Type** carries the message: short hero lines, one per phrase, on the
  downbeats. Three to six lines for 20 to 30 seconds.
- **Structure**: build in energy with the music; the logo or the call to
  action lands on the biggest hit.

## No sound

A video can have no sound at all: a recipe, a loop for a screen, anything
the person did not ask sound for. Build it on the pacing grid
(`spine.py --silent <seconds>`, then `scaffold.sh <dir> - spine.json`), keep
the type on screen long enough to read (about 0.3 s a word, never under
1.5 s), and let motion carry the rhythm: things land on the grid's beats.

## Length and format

- Social cuts: 9:16 (1080×1920) or 1:1; move the chip up (y ≈ 1500 for 9:16)
  and stack type vertically. Set the canvas size in `PaperKit.create`
  (`width`, `height`) and in `index.html` (`data-width`, `data-height`).
- A hook in the first two seconds matters more the shorter the piece.
