# paperkit: the drawing kit

`assets/paperkit.js` (copied in by `scaffold.sh`). A Canvas2D kit: fast on a
CPU, deterministic, and printed-looking by default.

## The contract

- A shot is `fn(t, lt, dur)`: `t` video seconds, `lt` seconds into the
  shot, `dur` the shot's length. It paints the **whole** frame.
- **Pure functions of time.** HyperFrames seeks frames in any order. No
  state carried between frames, no `Math.random()`, no `Date`, no
  `requestAnimationFrame`. `kit.hash(n)` gives a stable 0..1 per `n`;
  `kit.jit(a)` gives boil jitter that changes `boil` times a second.
- Call `kit.seed('<name>')` before each separate element that boils, so one
  moving thing does not make everything drawn after it re-boil.
- `kit.back()` draws on the world (under the performance clips),
  `kit.front()` on the type layer (over them). `draw()` in `scenes.js`
  already calls `kit.frame(t)` first (paper) and `kit.finish()` last (grain).

```js
const kit = PaperKit.create({ bg: 'bg', fg: 'fg', inks: PaperKit.INKSETS.riso,
  bpm: SPINE.bpm, offset: SPINE.offset, words: SPINE.words, boil: 8 });
```

Options: `width`/`height` (default 1920×1080; 1080×1080 or 1080×1920 for
social), `texture` (paper stock: 1 mottled print paper, 0 a clean sheet for
a crisp editorial or doodle look; pair 0 with `finish({ grain: .3 })`),
`boil` (drawings per second, 0 for none).

## Time

| | |
|---|---|
| `seg(t, a, b)` | 0..1 progress of t through [a, b] |
| `kf(t, [[t0, v0], [t1, v1], ...], ease)` | keyframes; values may be arrays (`[x, y, zoom]`) |
| `ease`, `easeIn`, `easeOut`, `easeInOut`, `backOut`, `elasticOut` | easings |
| `lerp`, `clamp`, `frac`, `wob(t, hz, phase)`, `hash(n)`, `mix(hexA, hexB, k)`, `rgba(hex, a)` | helpers |
| `spring(t, t0, amp, hz, damp)` | a settle after an event at t0 |
| `pulse(k)`, `pulse2(k)` | 1 on each beat (eighth), falling to 0 before the next |
| `beatN()`, `onBeat(n)` | current beat number; scene time of beat n |

Land things on words: `const at = w => SPINE.words.find(x => x.w.toLowerCase().startsWith(w)).s;`
then `seg(t, at('sparks') - .03, at('sparks') + .15)`.

## Shapes and sets (back layer)

| | |
|---|---|
| `rectPts`, `ellPts`, `starPts`, `blobPts` | point lists, boiling |
| `shape(pts, {fill, tone:{ink, cell, dot, angle}, line, lw, smooth, alpha, blend})` | one printed shape: flat ink, halftone tone, outline |
| `inkLine(pts, col, w)` | a hand-inked line |
| `fillAll(col)`, `toneAll(col)`, `wash(col)` | full-frame ink, halftone, mottled flood |
| `sunburst(cx, cy, col, rays, rot, alt)` | rays (a chorus, a reveal) |
| `rings(cx, cy, col, gap, phase)` | target rings (focus, hypnosis) |
| `grid(col, step)`, `ruled(col, step)` | graph paper, notebook paper |
| `speedLines(cx, cy, col, n, k)` | manga speed lines (impact, falling, speed) |
| `tunnel(cx, cy, col, depth, phase)` | receding frames (acceleration) |
| `chart(pts, {x, y, w, h}, k, {line, area})` | a line chart that draws itself to k; returns `{X, Y, tip}` |

## Pictures

| | |
|---|---|
| `image(img, x, y, w, h, {blend, rot, flip, anchor, crop})` | a still, multiplied by default, anchored at its feet |
| `puppet(img, x, y, h, {bob, sq, seed})` | a still that breathes and bobs on the beat |
| `inkify(img, palette)` | the image printed in the inks (cached) |
| `mouth(env, fps)` | 0..1 mouth openness from `envelope.py` |
| `screen(img, x, y, w, {kind, url, scroll, k, rot})` | a screenshot in a drawn browser / phone / card; returns the viewport box |
| `cursor(x, y, {click})`, `cursorPath([[t, x, y], ...])` | a drawn cursor; eased curved travel; a click ring at `click` |
| `callout(fromX, fromY, toX, toY, label, {k})` | a hand-drawn arrow with a marker label, drawn on to k |

## Camera

`cam(cx, cy, zoom, rot)` … `camEnd()`: the world point (cx, cy) at the
centre of the screen. `toScreen(x, y)` maps a world point under the last
`cam` to the screen (for putting a front-layer cursor or label on something
in the world). `shake(amount)` returns `[dx, dy]` to add on hits.

## Type (front layer)

| | |
|---|---|
| `hero(text, x, y, size, col, {k, rot, align, outline, hollow, tone, shadow, maxW})` | the big word; `k` 0..1 slams it in |
| `heroStack([[text, tAppear, col], ...], x, y, size, col)` | stacked lines, each on its time |
| `wordSlam(words, x, y, size, col, {stack, maxW})` | words from the spine, each landing on its own time |
| `mid(text, x, y, size, col, {k, type, italic})` | serif aside; `type: true` types it on |
| `mono(text, x, y, size, col)`, `hand(text, x, y, size, col, {k})` | mono line; marker lettering |
| `chip(line)`, `lineAt(lines)` | the subtitle chip for a spine line, current word underlined |
| `fit(text, size, family, maxW)` | the size at which text fits |

## Inserts (front layer)

| | |
|---|---|
| `label(x, y, top, big, {align, size})` | a taped label: LIVE + a date, a counter, a metric |
| `sticky(x, y, w, lines, {k, t0, bg})` | a sticky note that drops and settles |
| `card(x, y, w, head, body, {k, size})` | a clipping: a source line and a serif body |
| `stamp(text, x, y, size, col, {k})` | a rubber stamp that slams |
| `nameCard(x, y, name, sub, role, {k, bg})` | a member / product card |
| `meter(x, y, h, v, label)` | a gauge that fills |

## Transitions

`wipe(p, cols)` (ink slats: cover by p = .5, cut, uncover), `iris(cx, cy, r)`,
`flash(k)`, `sheetEdge(p)` (the next sheet slides over). Across a cut, run
the first half at the end of the outgoing shot and the second half at the
start of the incoming one, e.g. `kit.wipe(seg(t, cut - .3, cut + .3))` in
both.

## How-to parts (`howto.js`)

`assets/howto.js` (copied in by `scaffold.sh`) builds on the kit for recipes
and how-tos. Same contract: pure functions of time, drawn on the current
layer. `templates/recipe-scenes.js` uses all of it.

```js
const how = HowTo.create(kit, { ink: INK.ink, accent: INK.a });   // + accentDark, muted, glass, display, hand fonts
```

| | |
|---|---|
| `titleDrop(t, word, x, y, size, {start, stagger, bob})` | letters bounce in one after another |
| `chunky(text, x, y, size, {align, face, side, scale})` | extruded display type |
| `rail(t, steps, {x, y, gap, appear})` | the step rail; `steps: [{name, start, done}]`; returns the current index |
| `stepCard(t, {x, y, w, h, start, eyebrow, big, name, sub, progress, label})` | the step card, popping in at `start`, with a progress bar |
| `vessel({cx, top, bot, topW, botW, base, unit})` | a glass, jar or bowl; `unit` px per unit of amount |
| `drawVessel(t, V, {fills, items, stir, cold, oy})` | the vessel and its contents; fills rise and mix colour by `weight`; items drop and float; returns `{amount, level, liquid, prog}` |
| `marks(t, V, st, [{amount, label, show, until}])` | level marks with a dashed target line |
| `pourTimes(start, flow)`, `pour(t, {times, bottle, V, st})` | a bottle that slides in, tilts, pours on a curved stream, and leaves |
| `spoon(t, V, start, end)`, `twist(t, x, y, start)`, `burst(t, cx, cy, start)` | stir, citrus twist, the done beat |
| `sketch(pts, {fill, line, lw})`, `rr`, `ell`, `text`, `measure` | the hand-drawn outline and helpers the parts use |

## Speed

Most shots render at 20–60 ms a frame on a CPU. What costs: `inkify` of a
big image (cached after the first frame), hundreds of `speedLines`, very
large `wash`. Keep an eye on the render's frames-per-second line.
