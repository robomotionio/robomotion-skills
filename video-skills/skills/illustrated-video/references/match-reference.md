# Matching a reference

When the person sends a picture or a video of the look they want, it is the
brief. The words around it ("an explainer", "a motion graphic") say what the
video is for; the reference says what it looks like. Match it before you
invent anything, and never skip looking at it: if the download fails, try
again, and if it still fails, say so in the plan and ask for it once.

## 1. Read it, and write the look down

Open it (`read_file` on the image, or a few frames of a video:
`ffmpeg -i ref.mp4 -vf fps=1/3,scale=640:-1 ref-%02d.png`) and write these
into your notes before any code. Name what you see, not what it reminds you of.

| | Write down |
|---|---|
| **Paper** | Its colour as a hex, and its texture: clean, lightly mottled, grainy, lined, gridded |
| **Inks** | Every colour that carries meaning, as hexes, with its job: ink (lines and text), the accent, the second accent, the colour of each object. Usually three to six. Pick them from the picture: `python3 -c "from PIL import Image; im=Image.open('ref.png').convert('RGB').quantize(8); print([('#%02X%02X%02X' % tuple(im.getpalette()[i*3:i*3+3]), n) for n, i in sorted(im.getcolors(), reverse=True)])"` |
| **Line** | Weight (thin, medium, bold) relative to the frame, colour (black, dark brown, same as fill), wobble (ruler-straight, slightly shaky, sketchy double lines), whether shapes are outlined at all |
| **Fill** | Flat colour, halftone, hatching, soft gradient, watercolour; highlights (a white stripe on glass) |
| **Type** | For each role (title, labels, numbers, notes): display or text, weight, case, any effect (extrusion, outline, shadow). Match it with the shipped fonts; the closest is fine, say which |
| **Layout** | Where the main object sits, where the text sits, what stays on screen all the time (a title, a progress rail), margins, how full the frame is |
| **Motion** (a video) | Pace, how things enter (drop and bounce, slide, draw on), what counts up or fills, how steps change |
| **Sound** (a video) | Silent, music, a voice. Silent stays silent unless the person asks for sound |

## 2. Map it onto the kit

- Paper and inks become the `PaperKit.create({ inks })` set: `paper`, `ink`,
  and the accents in the order of importance. Object colours (a bottle, a
  liquid, a product) are separate constants in `scenes.js`.
- Line weight and wobble: `boil` (0 for ruler-straight, 6 to 10 for
  hand-drawn), the `lw` of shapes, and the second, lighter pen pass the
  how-to kit draws (`sketch`).
- Fills: flat is `shape(pts, { fill })`; tone is `{ tone: { ink, cell, dot } }`.
  Clean references want no halftone and a light grain (`kit.finish({ grain: .3 })`).
- Type: extruded titles are `how.chunky`; labels in a marker hand are
  `Permanent Marker`; numbers and a technical voice are `Space Mono`; serif
  asides are `Instrument Serif`; condensed shouting type is `Anton`.
- Layout: copy it. If the reference keeps the object left, a card right and
  a rail below, so do you (`templates/recipe-scenes.js` is that layout).

## 3. Check side by side

After the first snapshots, put a frame of yours next to the reference at the
same size (`ffmpeg -i ref.png -i out.png -filter_complex hstack side.png`)
and look for the differences, in this order: colours, line weight, type,
layout, then details (the ice, the label, the highlight). Fix, and look
again. Say in the hand-over what you matched and what you changed on purpose.

## Do not

- Copy text, logos or a watermark from the reference into the video.
- Trace it or lift its drawings: match the style, draw your own.
- Let the look drift: a reference that is flat and clean should not come
  back with riso halftone and heavy grain because that is the kit's default.
