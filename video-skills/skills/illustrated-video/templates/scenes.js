// scenes.js: the video, shot by shot. Each shot is a pure function of time.
//
// shot(start, end, fn) registers a shot in video seconds; fn(t, lt, dur) gets
// the video time t, the time in the shot lt and the shot's length, and paints
// the WHOLE frame. The kit clears the canvases, lays the paper and finishes
// with grain for you. Cuts land on each shot's start.
//
// Draw on kit.back() for the world, on kit.front() for type and HUD (it sits
// above the performance clips). Put hits on beats: kit.pulse(), kit.beatN(),
// or a word's own time from SPINE.words.
(() => {
  const INKS = PaperKit.INKSETS.riso;          // one ink set for the whole video
  const kit = PaperKit.create({
    bg: 'bg', fg: 'fg', inks: INKS,
    bpm: SPINE.bpm || 120, offset: SPINE.offset || 0,
    words: SPINE.words, boil: 8,
  });
  const { seg, kf, ease, easeOut, backOut, lerp, clamp, hash } = kit;
  const W = 1920, H = 1080;

  // Generated stills (characters, sets, props), made on flat paper colour.
  // Every image a shot draws must be listed here, so it is decoded before the first seek.
  const IMG = {};
  const SRC = {
    // hero: 'assets/gen/hero-front.png',
    // heroOpen: 'assets/gen/hero-mouth-open.png',
  };

  // Words of a line, and the line playing now, from the spine.
  const lineAt = t => SPINE.lines.find(l => t >= l.s - .12 && t < l.e + .3);
  const wordsIn = (a, b) => SPINE.words.filter(w => w.s >= a && w.s < b);

  const SHOTS = [];
  const shot = (s, e, fn) => SHOTS.push({ s, e, fn });

  // ---------------------------------------------------------------- shots
  shot(0, __DURATION__, (t, lt, dur) => {
    kit.back();
    kit.sunburst(W * .7, H * .5, kit.mix(INKS.paper, INKS.b, .35), 20, lt * .15);
    kit.front();
    kit.chip(lineAt(t));
  });
  // ---------------------------------------------------------------- end shots

  function draw(t) {
    kit.frame(t);
    const i = SHOTS.findIndex(s => t >= s.s && t < s.e);
    const S = SHOTS[i >= 0 ? i : SHOTS.length - 1];
    if (S) S.fn(t, t - S.s, S.e - S.s);
    kit.back(); kit.finish();
  }

  window.SCENES_READY = Promise.all([
    document.fonts.ready,
    ...Object.entries(SRC).map(([k, src]) => new Promise(ok => { const im = new Image(); im.onload = im.onerror = () => ok(); im.src = src; IMG[k] = im; }).then(() => IMG[k].decode?.().catch(() => {}))),
  ]).then(() => draw);
})();
