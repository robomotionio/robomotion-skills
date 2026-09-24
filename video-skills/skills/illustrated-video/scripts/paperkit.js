// paperkit.js: a print-ink animation kit for HyperFrames scenes.
//
// Everything is drawn on a Canvas2D with a limited set of spot inks on paper,
// halftone for tone, grain multiplied over the top and linework that "boils"
// a few times a second like hand-drawn animation. It is cheap on a CPU-only
// headless Chrome (no WebGL), so a two-minute video renders in minutes.
//
// Every frame is a pure function of time: HyperFrames seeks frames out of
// order, so nothing may carry state between frames. Use hash() for stable
// randomness and kit.jit() for boil. Never Math.random(), Date or rAF.
//
// Load it in a scene with <script src="../assets/paperkit.js"></script>
// (copy it into the project's assets/), then:
//
//   const kit = PaperKit.create({ bg: 'bg', fg: 'fg', inks: PaperKit.INKSETS.riso, bpm: 118, offset: 0.12 });
//   window.__timelines['main'] = PaperKit.timeline(12, t => { kit.frame(t); ...draw...; kit.finish(); });
//
// `t` is scene-local seconds. Pass `at` (the scene's start in the whole video)
// to create() when you want beat helpers and words to use video time.
(function (root) {
  'use strict';
  const TAU = Math.PI * 2;

  // ---------- math: small, pure, deterministic ----------
  const clamp = (v, lo = 0, hi = 1) => v < lo ? lo : v > hi ? hi : v;
  const lerp = (from, to, amount) => from * (1 - amount) + to * amount;
  const frac = v => v - Math.floor(v);
  // Integer hash (a 32-bit avalanche mix) → [0, 1). Stable per input, no state.
  function hash(n) {
    let h = Math.imul((Math.round(n * 1000) | 0) ^ 0x9E3779B9, 0x85EBCA6B);
    h ^= h >>> 13; h = Math.imul(h, 0xC2B2AE35); h ^= h >>> 16;
    return (h >>> 0) / 4294967296;
  }
  // Where t sits between a and b, as 0..1.
  const seg = (t, a, b) => b === a ? (t >= b ? 1 : 0) : clamp((t - a) / (b - a));
  // Easings (the standard curve families, written from their definitions).
  const ease = u => { u = clamp(u); return u * u * (3 - 2 * u); };                 // smoothstep
  const easeIn = u => { u = clamp(u); return u * u * u; };                        // cubic in
  const easeOut = u => { u = 1 - clamp(u); return 1 - u * u * u; };               // cubic out
  const easeInOut = u => { u = clamp(u); return u < .5 ? 4 * u * u * u : 1 - 4 * Math.pow(1 - u, 3); };
  // Overshoot then settle: the cubic-out path plus a bump that peaks ~12% past the target.
  const backOut = u => { u = clamp(u); const o = 1.6; const v = u - 1; return 1 + v * v * ((o + 1) * v + o); };
  // A decaying oscillation that ends exactly on 1.
  const elasticOut = u => { u = clamp(u); if (u === 0 || u === 1) return u; return 1 - Math.pow(2, -9 * u) * Math.cos(u * 6.5 * Math.PI); };
  const wob = (t, hz = 1, phase = 0) => Math.sin(TAU * (t * hz + phase));
  // Keyframes: kf(t, [[time, value], ...], easing). Values may be numbers or arrays.
  function kf(t, keys, e = ease) {
    const last = keys.length - 1;
    if (t <= keys[0][0]) return keys[0][1];
    if (t >= keys[last][0]) return keys[last][1];
    let i = 1; while (keys[i][0] <= t) i++;
    const [t0, v0] = keys[i - 1], [t1, v1] = keys[i], u = e((t - t0) / (t1 - t0));
    return Array.isArray(v0) ? v0.map((x, j) => lerp(x, v1[j], u)) : lerp(v0, v1, u);
  }
  // Settle after an event at t0: a damped oscillator, amplitude amp, frequency hz.
  const spring = (t, t0, amp = 1, hz = 2.2, damp = 6) => t < t0 ? 0 : amp * Math.exp(-damp * (t - t0)) * Math.sin(TAU * hz * (t - t0));
  // Seeded random stream (mulberry32).
  function mulberry(seed) { let a = seed >>> 0; return () => { a = (a + 0x6D2B79F5) >>> 0; let t = a; t = Math.imul(t ^ (t >>> 15), t | 1); t ^= t + Math.imul(t ^ (t >>> 7), t | 61); return ((t ^ (t >>> 14)) >>> 0) / 4294967296; }; }
  function hexRgb(h) { const n = parseInt(h.slice(1), 16); return [(n >> 16) & 255, (n >> 8) & 255, n & 255]; }
  function mix(a, b, k) { const A = hexRgb(a), B = hexRgb(b); return '#' + A.map((v, i) => Math.round(lerp(v, B[i], clamp(k))).toString(16).padStart(2, '0')).join(''); }
  function rgba(h, a) { const [r, g, b] = hexRgb(h); return `rgba(${r},${g},${b},${a})`; }

  // ---------- ink sets: a paper and 3-5 spot inks. Pick one per video. ----------
  const INKSETS = {
    riso:      { paper: '#EEE6D6', ink: '#27306B', a: '#F2692E', b: '#EE4E9B', c: '#F2B632', d: '#2E9C8F' }, // navy, orange, fluo pink, yellow, teal
    newsprint: { paper: '#EDE9E0', ink: '#1E1C1A', a: '#D8342B', b: '#2F5DA8', c: '#E9C54A', d: '#8E8A80' },
    blueprint: { paper: '#E9EEF2', ink: '#16324F', a: '#2F6FDE', b: '#FF6B3D', c: '#9FC3E7', d: '#F4D35E' },
    forest:    { paper: '#F1EBDD', ink: '#223127', a: '#3F7D4E', b: '#D9822B', c: '#E8C872', d: '#B04A3A' },
    candy:     { paper: '#FBF1EA', ink: '#3A2350', a: '#FF5FA2', b: '#5FB6FF', c: '#FFD23F', d: '#7ED9A6' },
    noir:      { paper: '#E8E4DA', ink: '#141414', a: '#E23B2E', b: '#6B6B6B', c: '#D9D2C3', d: '#3B5BA5' },
  };

  const FONTS = {
    hero: '"Anton", "Archivo Black", Impact, sans-serif',
    heroWide: '"Archivo Black", "Anton", sans-serif',
    serif: '"Instrument Serif", Georgia, serif',
    sans: '"DM Sans", system-ui, sans-serif',
    mono: '"Space Mono", ui-monospace, monospace',
    hand: '"Permanent Marker", "Comic Sans MS", cursive',
  };

  // ---------- HyperFrames timeline ----------
  // A paused GSAP timeline with one linear tween whose onUpdate paints the
  // frame for the tween's current time. HyperFrames seeks the timeline; the
  // canvas follows. The page registers it: window.__timelines[id] = timeline(...)
  function timeline(duration, draw) {
    const clock = { t: 0 }, tl = gsap.timeline({ paused: true });
    tl.to(clock, { t: duration, duration, ease: 'none', onUpdate: () => draw(clock.t) }, 0);
    draw(0);
    return tl;
  }

  // ---------- the kit ----------
  function create(o = {}) {
    const W = o.width || 1920, H = o.height || 1080;
    const byId = id => (typeof id === 'string' ? document.getElementById(id) : id);
    const bgC = byId(o.bg), fgC = o.fg ? byId(o.fg) : null;
    for (const c of [bgC, fgC]) if (c) { c.width = W; c.height = H; }
    const inks = Object.assign({}, INKSETS.riso, o.inks || {});
    const bpm = o.bpm || 120, BEAT = 60 / bpm, OFF = o.offset || 0, AT = o.at || 0;
    const BOIL = o.boil ?? 8;  // boil drawings per second; 0 turns the boil off
    const TEX = clamp(o.texture ?? 1, 0, 1);  // paper texture: 1 = mottled stock, 0 = clean sheet
    const words = o.words || [];  // [{w, s, e}] in video seconds, from the timing spine
    let T = 0, ctx = bgC.getContext('2d'), rnd = Math.random, boilFrame = 0;

    // Offscreen drawing surfaces. OffscreenCanvas where there is one: inside
    // the HyperFrames renderer a detached <canvas> drew as nothing.
    function surface(w, h) { if (typeof OffscreenCanvas !== 'undefined') return new OffscreenCanvas(w, h); const c = document.createElement('canvas'); c.width = w; c.height = h; return c; }
    // Paper and grain are made once per page, from a fixed seed.
    // Paper: soft mottling from a coarse value-noise field scaled up (the
    // browser's smoothing blends it), then curved fibres and a few specks.
    const paper = surface(W, H);
    (function makePaper() {
      const c = paper.getContext('2d'), r = mulberry(1103);
      c.fillStyle = inks.paper; c.fillRect(0, 0, W, H);
      const gw = 48, gh = Math.max(8, Math.round(48 * H / W)), g = surface(gw, gh);
      const gc = g.getContext('2d'), gd = gc.createImageData(gw, gh);
      for (let i = 0; i < gw * gh; i++) { const v = r(); gd.data[i * 4] = 110; gd.data[i * 4 + 1] = 92; gd.data[i * 4 + 2] = 64; gd.data[i * 4 + 3] = Math.round(v * v * 26 * TEX); }
      gc.putImageData(gd, 0, 0);
      c.imageSmoothingEnabled = true; c.imageSmoothingQuality = 'high'; c.drawImage(g, 0, 0, W, H);
      for (let i = 0; i < 1100 * TEX; i++) {
        const x = r() * W, y = r() * H, len = 6 + r() * 26, ang = r() * TAU, bend = (r() - .5) * len * .6;
        c.strokeStyle = `rgba(95,80,60,${.025 + r() * .045})`; c.lineWidth = .6 + r() * .8;
        c.beginPath(); c.moveTo(x, y);
        c.quadraticCurveTo(x + Math.cos(ang) * len / 2 - Math.sin(ang) * bend, y + Math.sin(ang) * len / 2 + Math.cos(ang) * bend, x + Math.cos(ang) * len, y + Math.sin(ang) * len); c.stroke();
      }
      for (let i = 0; i < 260 * TEX; i++) { c.fillStyle = `rgba(70,58,44,${.05 + r() * .08})`; c.fillRect(r() * W, r() * H, 1 + r() * 1.5, 1 + r() * 1.5); }
    })();
    // Grain: fine and coarse noise together, and edges that darken toward the
    // frame border (a rounded falloff), multiplied over every frame.
    const grain = surface(W, H), keep = surface(W, H);
    (function makeGrain() {
      const c = grain.getContext('2d'), r = mulberry(2027), id = c.createImageData(W, H), d = id.data;
      for (let y = 0; y < H; y++) for (let x = 0; x < W; x++) {
        const i = (y * W + x) * 4, fine = r(), coarse = hash((x >> 2) * 7919 + (y >> 2) * 104729);
        const dx = Math.max(0, Math.abs(x - W / 2) - W * .32) / (W * .18), dy = Math.max(0, Math.abs(y - H / 2) - H * .3) / (H * .2);
        const edge = Math.min(1, Math.sqrt(dx * dx + dy * dy));
        const v = 255 - fine * fine * 22 - coarse * 9 - edge * edge * 38;
        d[i] = v; d[i + 1] = v - 2; d[i + 2] = v - 6; d[i + 3] = 255;
      }
      c.putImageData(id, 0, 0);
    })();

    // Halftone patterns, cached per ink / cell / angle.
    const patCache = {};
    function halftone(col, cell = 9, dot = .42, angle = .26) {
      const key = col + cell + dot + angle;
      if (!patCache[key]) {
        const p = document.createElement('canvas'); p.width = p.height = cell;
        const c = p.getContext('2d'); c.fillStyle = col; c.beginPath(); c.arc(cell / 2, cell / 2, cell * dot, 0, TAU); c.fill();
        const pat = ctx.createPattern(p, 'repeat'); pat.setTransform(new DOMMatrix().rotate(angle * 180 / Math.PI));
        patCache[key] = { canvas: p, angle };
      }
      const pat = ctx.createPattern(patCache[key].canvas, 'repeat');
      pat.setTransform(new DOMMatrix().rotate(angle * 180 / Math.PI));
      return pat;
    }

    const K = {
      W, H, inks, fonts: FONTS, BEAT, words,
      // time
      get t() { return T; }, get vt() { return T + AT; },
      clamp, lerp, frac, hash, seg, ease, easeIn, easeOut, easeInOut, backOut, elasticOut, wob, kf, spring, mix, rgba, TAU,
      bp: vt => (vt - OFF) / BEAT,                            // beat position in video time
      beatN: (vt = T + AT) => Math.floor((vt - OFF) / BEAT),
      // Beat envelopes: 1 exactly on the beat, falling off along a power curve
      // before the next one. `k` sharpens the fall (4 soft, 10 snappy).
      pulse: (k = 6, vt = T + AT) => Math.pow(1 - frac((vt - OFF) / BEAT), k),
      pulse2: (k = 6, vt = T + AT) => Math.pow(1 - frac((vt - OFF) / BEAT * 2), k),     // on eighths
      onBeat: (n, vt = T + AT) => OFF + n * BEAT - AT,        // scene-local time of beat n
      // boil: a jitter that changes BOIL times a second. seed() restarts the
      // stream per element so one moving thing never re-boils the rest.
      seed(key = 0) { const kh = typeof key === 'string' ? [...key].reduce((a, ch) => a * 31 + ch.charCodeAt(0), 7) : key; rnd = mulberry((boilFrame * 7919 + kh * 104729) >>> 0); },
      jit: a => BOIL ? (rnd() * 2 - 1) * a : 0,
    };

    // ---------- frame lifecycle ----------
    K.frame = function (t, opts = {}) {
      T = t; CAM = null; boilFrame = BOIL ? Math.floor((t + AT) * BOIL) : 0; K.seed(0);
      ctx = bgC.getContext('2d'); ctx.setTransform(1, 0, 0, 1, 0, 0); ctx.globalAlpha = 1; ctx.globalCompositeOperation = 'source-over';
      if (opts.clear !== false) { ctx.fillStyle = inks.paper; ctx.fillRect(0, 0, W, H); ctx.drawImage(paper, 0, 0); }
      if (fgC) { const f = fgC.getContext('2d'); f.setTransform(1, 0, 0, 1, 0, 0); f.clearRect(0, 0, W, H); }
      return K;
    };
    // Switch drawing to the foreground canvas (above any generated video layer).
    K.front = () => { if (fgC) ctx = fgC.getContext('2d'); return K; };
    K.back = () => { ctx = bgC.getContext('2d'); return K; };
    Object.defineProperty(K, 'ctx', { get: () => ctx });
    K.finish = function (o2 = {}) {
      const c = bgC.getContext('2d'); c.setTransform(1, 0, 0, 1, 0, 0);
      c.globalCompositeOperation = 'multiply'; c.globalAlpha = o2.grain ?? 1; c.drawImage(grain, 0, 0);
      c.globalCompositeOperation = 'source-over'; c.globalAlpha = 1;
      // The front layer gets the same grain, multiplied into its ink only: multiply
      // fills the transparent areas too, so its own alpha is put back afterwards.
      if (fgC && o2.fgGrain !== false) {
        const f = fgC.getContext('2d'), k = keep.getContext('2d');
        k.clearRect(0, 0, W, H); k.drawImage(fgC, 0, 0);
        f.setTransform(1, 0, 0, 1, 0, 0); f.globalAlpha = 1;
        f.globalCompositeOperation = 'multiply'; f.drawImage(grain, 0, 0);
        f.globalCompositeOperation = 'destination-in'; f.drawImage(keep, 0, 0);
        f.globalCompositeOperation = 'source-over';
      }
    };

    // ---------- shapes ----------
    // Point lists with boil. Every shape is a list of [x, y].
    K.rectPts = (x, y, w, h, j = 2) => [[x + K.jit(j), y + K.jit(j)], [x + w + K.jit(j), y + K.jit(j)], [x + w + K.jit(j), y + h + K.jit(j)], [x + K.jit(j), y + h + K.jit(j)]];
    K.ellPts = (cx, cy, rx, ry, n = 40, j = 2, rot = 0) => { const p = []; for (let i = 0; i < n; i++) { const a = rot + i / n * TAU; p.push([cx + Math.cos(a) * rx + K.jit(j), cy + Math.sin(a) * ry + K.jit(j)]); } return p; };
    K.starPts = (cx, cy, r, inner = .45, n = 5, rot = -Math.PI / 2) => { const p = []; for (let i = 0; i < n * 2; i++) { const a = rot + i * Math.PI / n, q = i % 2 ? r * inner : r; p.push([cx + Math.cos(a) * q, cy + Math.sin(a) * q]); } return p; };
    K.blobPts = (cx, cy, r, lumps = 9, amp = .18, seed = 1, j = 2) => { const p = []; for (let i = 0; i < 48; i++) { const a = i / 48 * TAU, rr = r * (1 + amp * Math.sin(a * lumps + seed * 5) * (0.6 + .4 * hash(seed + i))); p.push([cx + Math.cos(a) * rr + K.jit(j), cy + Math.sin(a) * rr + K.jit(j)]); } return p; };
    function path(pts, close = true, smooth = 0) {
      ctx.beginPath();
      if (!smooth || pts.length < 3) { pts.forEach((p, i) => i ? ctx.lineTo(p[0], p[1]) : ctx.moveTo(p[0], p[1])); if (close) ctx.closePath(); return; }
      const n = pts.length, P = i => pts[(i + n) % n];
      ctx.moveTo((P(0)[0] + P(1)[0]) / 2, (P(0)[1] + P(1)[1]) / 2);
      for (let i = 1; i <= (close ? n : n - 1); i++) { const a = P(i), b = P(i + 1); ctx.quadraticCurveTo(a[0], a[1], (a[0] + b[0]) / 2, (a[1] + b[1]) / 2); }
      if (close) ctx.closePath();
    }
    K.path = path;
    // shape(pts, {fill, tone:{ink, cell, dot, angle}, line, lw, smooth, alpha, blend})
    // `fill` is a flat ink, `tone` is halftone shading on top, `line` an ink outline.
    K.shape = function (pts, s = {}) {
      ctx.save(); ctx.globalAlpha = s.alpha ?? 1; if (s.blend) ctx.globalCompositeOperation = s.blend;
      path(pts, s.close !== false, s.smooth || 0);
      if (s.fill) { ctx.fillStyle = s.fill; ctx.fill(); }
      if (s.tone) { ctx.fillStyle = halftone(s.tone.ink || inks.ink, s.tone.cell || 9, s.tone.dot ?? .38, s.tone.angle ?? .26); ctx.fill(); }
      if (s.line) { ctx.lineJoin = 'round'; ctx.lineCap = 'round'; ctx.strokeStyle = s.line; ctx.lineWidth = s.lw || 4; ctx.stroke(); }
      ctx.restore();
    };
    // A hand-inked line through points: slightly uneven weight, boiling.
    K.inkLine = function (pts, col = inks.ink, w = 4, o2 = {}) {
      ctx.save(); ctx.strokeStyle = col; ctx.lineCap = 'round'; ctx.lineJoin = 'round'; ctx.globalAlpha = o2.alpha ?? 1;
      if (o2.dash) ctx.setLineDash(o2.dash);
      for (let i = 1; i < pts.length; i++) {
        ctx.lineWidth = w * (0.8 + 0.35 * hash(i * 3.1 + (o2.seed || 0)));
        ctx.beginPath(); ctx.moveTo(pts[i - 1][0] + K.jit(1), pts[i - 1][1] + K.jit(1)); ctx.lineTo(pts[i][0] + K.jit(1), pts[i][1] + K.jit(1)); ctx.stroke();
      }
      ctx.restore();
    };
    K.fillAll = (col, alpha = 1) => { ctx.save(); ctx.setTransform(1, 0, 0, 1, 0, 0); ctx.globalAlpha = alpha; ctx.fillStyle = col; ctx.fillRect(0, 0, W, H); ctx.restore(); };
    K.toneAll = (col, cell = 7, dot = .3, alpha = 1) => { ctx.save(); ctx.setTransform(1, 0, 0, 1, 0, 0); ctx.globalAlpha = alpha; ctx.fillStyle = halftone(col, cell, dot); ctx.fillRect(0, 0, W, H); ctx.restore(); };
    // A soft ink wash (a mottled flood of one ink), for backgrounds that are not flat.
    K.wash = function (col, alpha = 1, seed = 3) {
      ctx.save(); ctx.setTransform(1, 0, 0, 1, 0, 0); ctx.globalAlpha = alpha; ctx.fillStyle = col; ctx.fillRect(0, 0, W, H);
      const r = mulberry(seed); ctx.globalCompositeOperation = 'multiply';
      for (let i = 0; i < 26; i++) { const x = r() * W, y = r() * H, rad = 200 + r() * 500, g = ctx.createRadialGradient(x, y, 0, x, y, rad); g.addColorStop(0, rgba('#000000', .05 + r() * .07)); g.addColorStop(1, 'rgba(0,0,0,0)'); ctx.fillStyle = g; ctx.fillRect(x - rad, y - rad, 2 * rad, 2 * rad); }
      ctx.restore();
    };

    // ---------- set pieces (backgrounds that carry energy) ----------
    K.sunburst = function (cx, cy, col, rays = 18, rot = 0, alt = null) {
      ctx.save(); const R = Math.hypot(W, H) * 1.2;
      if (alt) { ctx.fillStyle = alt; ctx.fillRect(0, 0, W, H); }
      ctx.fillStyle = col;
      for (let i = 0; i < rays; i++) { const a0 = rot + i / rays * TAU, a1 = a0 + TAU / rays / 2; ctx.beginPath(); ctx.moveTo(cx, cy); ctx.lineTo(cx + Math.cos(a0) * R, cy + Math.sin(a0) * R); ctx.lineTo(cx + Math.cos(a1) * R, cy + Math.sin(a1) * R); ctx.closePath(); ctx.fill(); }
      ctx.restore();
    };
    K.rings = function (cx, cy, col, gap = 90, phase = 0, width = .5) {
      ctx.save(); ctx.strokeStyle = col; ctx.lineWidth = gap * width;
      const R = Math.hypot(W, H); for (let r = (phase % 1) * gap; r < R; r += gap) { ctx.beginPath(); ctx.arc(cx, cy, Math.max(1, r), 0, TAU); ctx.stroke(); }
      ctx.restore();
    };
    K.grid = function (col = inks.ink, step = 60, alpha = .18, major = 5) {
      ctx.save(); ctx.strokeStyle = col;
      for (let x = 0, i = 0; x <= W; x += step, i++) { ctx.globalAlpha = i % major ? alpha * .5 : alpha; ctx.lineWidth = i % major ? 1 : 2; ctx.beginPath(); ctx.moveTo(x, 0); ctx.lineTo(x, H); ctx.stroke(); }
      for (let y = 0, i = 0; y <= H; y += step, i++) { ctx.globalAlpha = i % major ? alpha * .5 : alpha; ctx.lineWidth = i % major ? 1 : 2; ctx.beginPath(); ctx.moveTo(0, y); ctx.lineTo(W, y); ctx.stroke(); }
      ctx.restore();
    };
    K.ruled = function (col = inks.ink, step = 44, alpha = .22, margin = 180) {
      ctx.save(); ctx.strokeStyle = col; ctx.globalAlpha = alpha; ctx.lineWidth = 2;
      for (let y = step * 2; y < H; y += step) { ctx.beginPath(); ctx.moveTo(0, y); ctx.lineTo(W, y); ctx.stroke(); }
      ctx.strokeStyle = inks.b; ctx.globalAlpha = alpha * 1.6; ctx.beginPath(); ctx.moveTo(margin, 0); ctx.lineTo(margin, H); ctx.stroke();
      ctx.restore();
    };
    // Manga speed lines toward (cx, cy). `k` 0..1 how much of the frame they fill.
    K.speedLines = function (cx, cy, col = inks.ink, n = 90, k = 1, seed = 1) {
      ctx.save(); ctx.fillStyle = col; const R = Math.hypot(W, H);
      for (let i = 0; i < n; i++) {
        const a = (i + hash(i + seed) * .8) / n * TAU, w = .004 + .01 * hash(i * 7 + seed), r0 = R * (1 - k * (.55 + .35 * hash(i * 3 + boilFrame)));
        ctx.beginPath(); ctx.moveTo(cx + Math.cos(a) * r0, cy + Math.sin(a) * r0); ctx.lineTo(cx + Math.cos(a - w) * R, cy + Math.sin(a - w) * R); ctx.lineTo(cx + Math.cos(a + w) * R, cy + Math.sin(a + w) * R); ctx.closePath(); ctx.fill();
      }
      ctx.restore();
    };
    // Receding tunnel of frames (screens, doors, panels) for acceleration beats.
    K.tunnel = function (cx, cy, col = inks.ink, depth = 9, phase = 0, lw = 6, aspect = 16 / 9) {
      ctx.save(); ctx.strokeStyle = col; ctx.lineJoin = 'round';
      for (let i = 0; i < depth; i++) { const z = frac((i + phase) / depth), s = Math.pow(z, 2.2), w = W * 1.2 * s, h = w / aspect; if (w < 8) continue; ctx.globalAlpha = clamp(z * 1.4); ctx.lineWidth = lw * (0.3 + z); ctx.strokeRect(cx - w / 2, cy - h / 2, w, h); }
      ctx.restore();
    };
    // A line chart that draws itself: pts in data space [[x, y]], box {x, y, w, h}, k 0..1 drawn.
    K.chart = function (pts, box, k = 1, s = {}) {
      const xs = pts.map(p => p[0]), ys = pts.map(p => p[1]);
      const x0 = s.x0 ?? Math.min(...xs), x1 = s.x1 ?? Math.max(...xs), y0 = s.y0 ?? Math.min(0, ...ys), y1 = s.y1 ?? Math.max(...ys);
      const X = x => box.x + (x - x0) / (x1 - x0) * box.w, Y = y => box.y + box.h - (y - y0) / (y1 - y0) * box.h;
      ctx.save(); ctx.strokeStyle = s.axis || inks.ink; ctx.lineWidth = 3; ctx.beginPath(); ctx.moveTo(box.x, box.y); ctx.lineTo(box.x, box.y + box.h); ctx.lineTo(box.x + box.w, box.y + box.h); ctx.stroke();
      const n = Math.max(1, Math.floor(k * (pts.length - 1))), f = k * (pts.length - 1) - n, drawn = pts.slice(0, n + 1).map(p => [X(p[0]), Y(p[1])]);
      if (n < pts.length - 1 && f > 0) { const a = pts[n], b = pts[n + 1]; drawn.push([X(lerp(a[0], b[0], f)), Y(lerp(a[1], b[1], f))]); }
      if (s.area) { ctx.beginPath(); drawn.forEach((p, i) => i ? ctx.lineTo(p[0], p[1]) : ctx.moveTo(p[0], p[1])); ctx.lineTo(drawn[drawn.length - 1][0], box.y + box.h); ctx.lineTo(drawn[0][0], box.y + box.h); ctx.closePath(); ctx.fillStyle = halftone(s.area, 8, .35); ctx.fill(); }
      ctx.strokeStyle = s.line || inks.a; ctx.lineWidth = s.lw || 7; ctx.lineCap = 'round'; ctx.lineJoin = 'round';
      ctx.beginPath(); drawn.forEach((p, i) => i ? ctx.lineTo(p[0], p[1]) : ctx.moveTo(p[0], p[1])); ctx.stroke();
      const tip = drawn[drawn.length - 1]; ctx.fillStyle = s.line || inks.a; ctx.beginPath(); ctx.arc(tip[0], tip[1], (s.lw || 7) * 1.6, 0, TAU); ctx.fill();
      ctx.restore();
      return { X, Y, tip };
    };

    // ---------- images: generated characters, sets and props ----------
    // Generated art is made on flat paper colour and laid down with `multiply`:
    // the paper vanishes and only the ink stays, so no cut-out or keying is needed.
    K.image = function (img, x, y, w, h, s = {}) {
      if (!img || !img.complete || !img.naturalWidth) return;
      ctx.save(); ctx.globalAlpha = s.alpha ?? 1; ctx.globalCompositeOperation = s.blend || 'multiply';
      ctx.translate(x, y); if (s.rot) ctx.rotate(s.rot); const sx = s.flip ? -1 : 1; ctx.scale(sx * (s.sx || 1), s.sy || 1);
      const ax = s.anchor ? s.anchor[0] : .5, ay = s.anchor ? s.anchor[1] : 1;  // default anchor: bottom centre (feet)
      if (s.crop) ctx.drawImage(img, s.crop[0], s.crop[1], s.crop[2], s.crop[3], -w * ax, -h * ay, w, h);
      else ctx.drawImage(img, -w * ax, -h * ay, w, h);
      ctx.restore();
    };
    // A still that acts: a cut-out puppet that breathes, bobs on the beat and
    // squashes on hits. Swap `img` between pose variants on beats for limited animation.
    K.puppet = function (img, x, y, h, s = {}) {
      if (!img || !img.naturalWidth) return;
      const w = h * img.naturalWidth / img.naturalHeight, b = s.bob ?? 1, pl = K.pulse(5);
      const sq = (s.sq || 0) + .018 * b * pl, breathe = .006 * Math.sin((T + AT) * 2.1 + (s.seed || 0));
      K.image(img, x + (s.dx || 0), y + (s.dy || 0) - 10 * b * pl, w * (1 + sq), h * (1 - sq + breathe), { ...s, anchor: s.anchor || [.5, 1] });
    };
    // Mouth flaps from the vocal envelope: `env` is the array from envelope.py,
    // `fps` its frame rate. Returns 0..1 openness at video time vt.
    K.mouth = function (env, fps, vt = T + AT, gate = .18) { if (!env) return 0; const i = Math.floor(vt * fps); const v = env[Math.max(0, Math.min(env.length - 1, i))] || 0; return clamp((v - gate) / (1 - gate)); };
    // Recolour any image into the video's inks (posterise + ordered dither), cached per image.
    const inkCache = new WeakMap();
    K.inkify = function (img, palette = [inks.paper, inks.ink, inks.a, inks.b, inks.c]) {
      if (inkCache.has(img)) return inkCache.get(img);
      const c = document.createElement('canvas'); c.width = img.naturalWidth; c.height = img.naturalHeight;
      const x = c.getContext('2d'); x.drawImage(img, 0, 0); const id = x.getImageData(0, 0, c.width, c.height), d = id.data;
      const P = palette.map(hexRgb), B = [0, 8, 2, 10, 12, 4, 14, 6, 3, 11, 1, 9, 15, 7, 13, 5];
      for (let i = 0; i < d.length; i += 4) {
        const px = (i / 4) % c.width, py = Math.floor(i / 4 / c.width), th = (B[(py % 4) * 4 + (px % 4)] / 16 - .5) * 48;
        let best = 0, bd = 1e9; for (let k = 0; k < P.length; k++) { const dr = d[i] + th - P[k][0], dg = d[i + 1] + th - P[k][1], db = d[i + 2] + th - P[k][2], dd = dr * dr * .3 + dg * dg * .59 + db * db * .11; if (dd < bd) { bd = dd; best = k; } }
        d[i] = P[best][0]; d[i + 1] = P[best][1]; d[i + 2] = P[best][2];
      }
      x.putImageData(id, 0, 0); inkCache.set(img, c); c.naturalWidth = c.width; c.naturalHeight = c.height; c.complete = true; return c;
    };

    // ---------- camera ----------
    // cam(cx, cy, zoom, rot): world point (cx, cy) lands at the screen centre until camEnd().
    let CAM = null;
    K.cam = (cx = W / 2, cy = H / 2, zoom = 1, rot = 0) => { CAM = { cx, cy, zoom, rot }; ctx.save(); ctx.translate(W / 2, H / 2); ctx.rotate(rot); ctx.scale(zoom, zoom); ctx.translate(-cx, -cy); };
    K.camEnd = () => ctx.restore();
    // Where a world point drawn under the last cam() lands on screen. Use it to
    // put front-layer things (cursor, callout, label) on something in the world.
    K.toScreen = (x, y) => { if (!CAM) return [x, y]; const { cx, cy, zoom, rot } = CAM, dx = (x - cx) * zoom, dy = (y - cy) * zoom; return [W / 2 + dx * Math.cos(rot) - dy * Math.sin(rot), H / 2 + dx * Math.sin(rot) + dy * Math.cos(rot)]; };
    // Camera shake: a new random offset `rate` times a second, both axes independent.
    K.shake = (amt, rate = 24) => { const step = Math.floor((T + AT) * rate); return [amt * (2 * hash(step * 31 + 5) - 1), amt * (2 * hash(step * 57 + 11) - 1)]; };

    // ---------- type ----------
    function font(size, fam, weight = '') { return `${weight} ${size}px ${fam}`.trim(); }
    // Shrink `size` until `text` fits in maxW (cheap, per frame).
    K.fit = (text, size, fam, maxW, weight = '') => { ctx.font = font(size, fam, weight); const w = ctx.measureText(text).width; return w > maxW ? size * maxW / w : size; };
    // hero: the big words. o.k is 0..1 appear progress (a slam with overshoot).
    // Print look: flat ink, an offset shadow in a second ink (misregistered plate).
    K.hero = function (text, x, y, size, col = inks.b, o2 = {}) {
      const k = o2.k == null ? 1 : o2.k; if (k <= 0) return;
      const fam = o2.font || FONTS.hero, sc = o2.pop === false ? 1 : lerp(1.35, 1, backOut(k)), s2 = o2.maxW ? K.fit(text, size, fam, o2.maxW) : size;
      ctx.save(); ctx.translate(x, y); ctx.rotate(o2.rot || 0); ctx.scale(sc, sc); ctx.globalAlpha = clamp(k * 3) * (o2.alpha ?? 1);
      ctx.font = font(s2, fam, o2.weight); ctx.textAlign = o2.align || 'left'; ctx.textBaseline = o2.base || 'alphabetic';
      if (o2.upper !== false) text = text.toUpperCase();
      if (o2.outline) { ctx.lineJoin = 'round'; ctx.lineWidth = s2 * .09; ctx.strokeStyle = o2.outline; ctx.strokeText(text, 0, 0); }
      if (o2.shadow !== false) { ctx.fillStyle = o2.shadow || inks.ink; ctx.globalAlpha *= .9; ctx.fillText(text, s2 * .035, s2 * .04); ctx.globalAlpha /= .9; }
      if (o2.hollow) { ctx.lineWidth = s2 * .045; ctx.strokeStyle = col; ctx.strokeText(text, 0, 0); } else { ctx.fillStyle = col; ctx.fillText(text, 0, 0); }
      if (o2.tone) { ctx.fillStyle = halftone(o2.tone, 7, .32); ctx.fillText(text, 0, 0); }
      ctx.restore();
    };
    // heroStack: lines stacked top-down, each slamming in on its own time.
    // lines = [[text, tAppear], ...] (scene time); returns the stack's bottom y.
    K.heroStack = function (lines, x, y, size, col = inks.b, o2 = {}) {
      let yy = y; const lead = o2.lead || .92;
      for (const [txt, ta, c2] of lines) { yy += size * lead; K.hero(txt, x, yy, size, c2 || col, { ...o2, k: seg(T, ta, ta + (o2.dur || .18)) }); }
      return yy;
    };
    // wordSlam: the words of a line appear one by one on their sung/spoken times
    // (from the spine), each landing on its own line or flowing on one line.
    K.wordSlam = function (ws, x, y, size, col = inks.b, o2 = {}) {
      const vt = T + AT; let cx = x, cy = y; const sp = size * .25, maxW = o2.maxW || W - x - 60;
      ctx.font = font(size, o2.font || FONTS.hero);
      for (const w of ws) {
        const txt = (o2.upper === false ? w.w : w.w.toUpperCase()), tw = ctx.measureText(txt).width;
        if (o2.stack || cx + tw > x + maxW) { if (cx !== x) { cx = x; cy += size * (o2.lead || .95); } }
        K.hero(txt, cx, cy, size, w.col || col, { ...o2, maxW: undefined, k: seg(vt, w.s - .04, w.s + .14) });
        ctx.font = font(size, o2.font || FONTS.hero); cx += tw + sp; if (o2.stack) { cx = x; cy += size * (o2.lead || .95); }
      }
    };
    // mid: editorial serif, for asides and echoes ("in your eyes", "please").
    K.mid = function (text, x, y, size, col = inks.ink, o2 = {}) {
      const k = o2.k == null ? 1 : o2.k; if (k <= 0) return;
      ctx.save(); ctx.globalAlpha = easeOut(k) * (o2.alpha ?? 1); ctx.font = font(size, FONTS.serif, o2.italic === false ? '' : 'italic');
      ctx.textAlign = o2.align || 'left'; ctx.textBaseline = 'alphabetic'; ctx.fillStyle = col;
      const shown = o2.type ? text.slice(0, Math.ceil(text.length * clamp(k * 1.2))) : text;
      ctx.translate(x, y + (1 - easeOut(k)) * size * .2); ctx.rotate(o2.rot || 0); ctx.fillText(shown, 0, 0); ctx.restore();
    };
    K.mono = function (text, x, y, size, col = inks.ink, o2 = {}) { ctx.save(); ctx.font = font(size, FONTS.mono, o2.bold ? 'bold' : ''); ctx.textAlign = o2.align || 'left'; ctx.textBaseline = o2.base || 'alphabetic'; ctx.fillStyle = col; ctx.globalAlpha = o2.alpha ?? 1; ctx.fillText(text, x, y); ctx.restore(); };
    K.hand = function (text, x, y, size, col = inks.a, o2 = {}) { const k = o2.k == null ? 1 : o2.k; if (k <= 0) return; ctx.save(); ctx.translate(x, y); ctx.rotate((o2.rot ?? -.06) + Math.sin(k * 20) * .03 * (1 - k)); const sc = backOut(k); ctx.scale(sc, sc); ctx.font = font(size, FONTS.hand); ctx.textAlign = o2.align || 'center'; ctx.textBaseline = 'middle'; ctx.fillStyle = inks.ink; ctx.fillText(text, size * .04, size * .05); ctx.fillStyle = col; ctx.fillText(text, 0, 0); ctx.restore(); };

    // chip: the subtitle tier. A paper chip bottom-left; words fill with ink as
    // they are sung/spoken, the current word gets an underline in an accent ink.
    // `line` = {s, e, words: [{w, s, e}]} in video time (from the spine).
    K.chip = function (line, o2 = {}) {
      if (!line) return; const vt = T + AT, a = seg(vt, line.s - .12, line.s + .05) * (1 - seg(vt, line.e + .15, line.e + .3)); if (a <= 0) return;
      const size = o2.size || 34, x = o2.x ?? 72, y = o2.y ?? H - 88, pad = size * .55;
      ctx.save(); ctx.font = font(size, FONTS.sans, '600'); ctx.textBaseline = 'middle';
      const sp = ctx.measureText(' ').width, ws = line.words.map(w => ctx.measureText(w.w).width), tw = ws.reduce((p, q) => p + q, 0) + sp * (ws.length - 1);
      const rot = o2.rot ?? -.006, h = size * 1.7;
      ctx.translate(x, y + (1 - easeOut(a)) * 20); ctx.rotate(rot); ctx.globalAlpha = clamp(a * 2);
      ctx.fillStyle = rgba(inks.ink, .25); ctx.fillRect(6, -h / 2 + 7, tw + pad * 2, h);
      ctx.fillStyle = o2.bg || '#FBF8F1'; ctx.fillRect(0, -h / 2, tw + pad * 2, h);
      let cx = pad;
      line.words.forEach((w, i) => {
        const on = vt >= w.s, cur = vt >= w.s && vt < w.e + .05;
        ctx.fillStyle = on ? (o2.ink || inks.ink) : rgba(o2.ink || inks.ink, .38); ctx.fillText(w.w, cx, 1);
        if (cur) { ctx.fillStyle = o2.accent || inks.b; ctx.fillRect(cx, size * .52, ws[i] * seg(vt, w.s, Math.min(w.e, w.s + .25)), size * .12); }
        cx += ws[i] + sp;
      });
      ctx.restore();
    };
    K.lineAt = (lines, vt = T + AT) => lines.find(l => vt >= l.s - .12 && vt < l.e + .3) || null;

    // ---------- HUD and inserts: the diegetic paper layer ----------
    // A taped paper label: a live counter, a date that races forward, a metric.
    K.label = function (x, y, top, big, o2 = {}) {
      const size = o2.size || 44; ctx.save(); ctx.translate(x, y); ctx.rotate(o2.rot ?? .006);
      ctx.font = font(size, FONTS.mono, 'bold'); const w = Math.max(ctx.measureText(big).width, 120) + size * .9, h = size * 2.05;
      const ax = o2.align === 'right' ? -w : 0;
      ctx.fillStyle = rgba(inks.ink, .22); ctx.fillRect(ax + 5, 6, w, h);
      ctx.fillStyle = o2.bg || '#FBF8F1'; ctx.fillRect(ax, 0, w, h);
      if (o2.dot !== false) { ctx.fillStyle = o2.dotCol || inks.b; ctx.beginPath(); ctx.arc(ax + size * .55, size * .55, size * .15, 0, TAU); ctx.fill(); }
      ctx.font = font(size * .42, FONTS.mono); ctx.fillStyle = o2.dotCol || inks.b; ctx.textBaseline = 'middle'; ctx.fillText(top, ax + size * (o2.dot === false ? .45 : .85), size * .56);
      ctx.font = font(size, FONTS.mono, 'bold'); ctx.fillStyle = o2.col || inks.ink; ctx.fillText(big, ax + size * .45, size * 1.35);
      ctx.restore();
    };
    // A sticky note with tape; `k` 0..1 drops it in, `t0` for its landing wobble.
    K.sticky = function (x, y, w, lines, o2 = {}) {
      const k = o2.k == null ? 1 : o2.k; if (k <= 0) return; const h = o2.h || w * .62;
      ctx.save(); ctx.translate(x, y - (1 - easeOut(k)) * 60); ctx.rotate((o2.rot ?? -.05) + (o2.t0 != null ? spring(T, o2.t0, .05) : 0)); ctx.globalAlpha = clamp(k * 3);
      ctx.fillStyle = rgba(inks.ink, .25); ctx.fillRect(6, 8, w, h); ctx.fillStyle = o2.bg || inks.c; ctx.fillRect(0, 0, w, h);
      ctx.fillStyle = 'rgba(255,255,255,.55)'; ctx.fillRect(w * .35, -14, w * .3, 28);
      // First line small (a label), the rest big; each baseline moves down by its own size.
      let yy = h * .12; lines.forEach((ln, i) => { const s = i === 0 ? w * .1 : w * .2; yy += s * (i === 0 ? 1.1 : 1.05); ctx.font = font(s, FONTS.mono, i ? 'bold' : ''); ctx.fillStyle = inks.ink; ctx.fillText(ln, w * .09, yy); });
      ctx.restore();
    };
    // An evidence card: a clipping, a paper title, a headline, a spec, a quote.
    // head is small mono in an accent ink (a source line), body is serif.
    K.card = function (x, y, w, head, body, o2 = {}) {
      const k = o2.k == null ? 1 : o2.k; if (k <= 0) return;
      const bs = o2.size || 40, lines = []; ctx.font = font(bs, FONTS.serif);
      for (const para of [].concat(body)) { let cur = ''; for (const word of para.split(' ')) { const test = cur ? cur + ' ' + word : word; if (ctx.measureText(test).width > w - bs * 1.2 && cur) { lines.push(cur); cur = word; } else cur = test; } lines.push(cur); }
      const h = bs * .9 + lines.length * bs * 1.15 + bs * .9 + (head ? bs * .8 : 0);
      ctx.save(); ctx.translate(x + (1 - easeOut(k)) * (o2.from || 80), y); ctx.rotate(o2.rot ?? -.012); ctx.globalAlpha = clamp(k * 2.5);
      ctx.fillStyle = rgba(inks.ink, .22); ctx.fillRect(8, 10, w, h); ctx.fillStyle = o2.bg || '#FBF8F1'; ctx.fillRect(0, 0, w, h);
      let yy = bs * .9; if (head) { ctx.font = font(bs * .5, FONTS.mono); ctx.fillStyle = o2.headCol || inks.b; ctx.fillText(head, bs * .6, yy); yy += bs * .95; }
      ctx.font = font(bs, FONTS.serif); ctx.fillStyle = o2.col || inks.ink; for (const ln of lines) { ctx.fillText(ln, bs * .6, yy); yy += bs * 1.15; }
      ctx.restore(); return h;
    };
    // A rubber stamp: CONFIRMED, NONE ON FILE, SHIPPED. Slams at k.
    K.stamp = function (text, x, y, size, col = inks.a, o2 = {}) {
      const k = o2.k == null ? 1 : o2.k; if (k <= 0) return; const sc = lerp(1.8, 1, easeOut(k));
      ctx.save(); ctx.translate(x, y); ctx.rotate(o2.rot ?? -.12); ctx.scale(sc, sc); ctx.globalAlpha = clamp(k * 3) * .92;
      ctx.font = font(size, FONTS.heroWide); ctx.textAlign = 'center'; ctx.textBaseline = 'middle'; const w = ctx.measureText(text).width + size * .8, h = size * 1.5;
      ctx.strokeStyle = col; ctx.lineWidth = size * .09; ctx.strokeRect(-w / 2, -h / 2, w, h); ctx.fillStyle = col; ctx.fillText(text, 0, size * .04);
      ctx.globalCompositeOperation = 'destination-out'; for (let i = 0; i < 90; i++) { ctx.fillRect((hash(i) - .5) * w, (hash(i + 50) - .5) * h, 3 + hash(i + 9) * 6, 2 + hash(i + 3) * 4); }
      ctx.restore();
    };
    // A member / product card: NAME, a sub-line, a POSITION-style role line.
    K.nameCard = function (x, y, name, sub, role, o2 = {}) {
      const k = o2.k == null ? 1 : o2.k; if (k <= 0) return; const s = o2.size || 56;
      ctx.save(); ctx.translate(x - (1 - easeOut(k)) * 120, y); ctx.rotate(o2.rot ?? -.02); ctx.globalAlpha = clamp(k * 3);
      ctx.font = font(s, FONTS.heroWide); const w = Math.max(ctx.measureText(name).width, 260) + s, h = s * 2.6;
      ctx.fillStyle = rgba(inks.ink, .25); ctx.fillRect(7, 8, w, h); ctx.fillStyle = o2.bg || inks.b; ctx.fillRect(0, 0, w, h);
      ctx.fillStyle = o2.col || inks.ink; ctx.fillText(name, s * .45, s * 1.05);
      ctx.font = font(s * .36, FONTS.mono); ctx.fillText(sub || '', s * .5, s * 1.6); ctx.font = font(s * .36, FONTS.mono, 'bold'); ctx.fillText(role || '', s * .5, s * 2.15);
      ctx.restore();
    };
    // A small meter (a thermometer, a gauge) that climbs; v 0..1.
    K.meter = function (x, y, h, v, label, o2 = {}) {
      const w = o2.w || 46; ctx.save(); ctx.translate(x, y);
      ctx.fillStyle = '#FBF8F1'; ctx.strokeStyle = inks.ink; ctx.lineWidth = 4; ctx.beginPath(); ctx.roundRect(-w / 2, 0, w, h, w / 2); ctx.fill(); ctx.stroke();
      ctx.fillStyle = o2.col || inks.a; const fh = (h - 12) * clamp(v); ctx.beginPath(); ctx.roundRect(-w / 2 + 6, h - 6 - fh, w - 12, fh, (w - 12) / 2); ctx.fill();
      ctx.beginPath(); ctx.arc(0, h + w * .45, w * .75, 0, TAU); ctx.fill(); ctx.stroke();
      if (label) { ctx.font = font(24, FONTS.mono, 'bold'); ctx.textAlign = 'center'; ctx.fillStyle = inks.ink; ctx.fillText(label, 0, -16); }
      ctx.restore();
    };

    // ---------- product demos: screens, cursor, callouts ----------
    // screen(img, x, y, w, {kind, k, rot, scroll, url}): a screenshot in a drawn
    // device, printed in the video's inks. kind: 'browser' | 'phone' | 'card'.
    // `scroll` 0..1 pans a tall screenshot inside the frame; `k` 0..1 drops it in.
    K.screen = function (img, x, y, w, o2 = {}) {
      const k = o2.k == null ? 1 : o2.k; if (k <= 0) return;
      const kind = o2.kind || 'browser', phone = kind === 'phone';
      const bar = kind === 'browser' ? w * .045 : 0, pad = phone ? w * .06 : 0;
      const vw = w - pad * 2, vh = o2.h || (phone ? vw * 2.05 : vw * 9 / 16), h = vh + bar + pad * 2;
      ctx.save(); ctx.translate(x, y + (1 - easeOut(k)) * 90); ctx.rotate(o2.rot || 0); ctx.globalAlpha = clamp(k * 2.5);
      ctx.fillStyle = rgba(inks.ink, .25); ctx.beginPath(); ctx.roundRect(10, 14, w, h, phone ? w * .12 : 14); ctx.fill();
      ctx.fillStyle = phone ? inks.ink : '#FBF8F1'; ctx.strokeStyle = inks.ink; ctx.lineWidth = 5;
      ctx.beginPath(); ctx.roundRect(0, 0, w, h, phone ? w * .12 : 14); ctx.fill(); ctx.stroke();
      if (bar) {
        [inks.b, inks.c, inks.d].forEach((c, i) => { ctx.fillStyle = c; ctx.beginPath(); ctx.arc(bar * (.7 + i * .55), bar / 2, bar * .17, 0, TAU); ctx.fill(); });
        if (o2.url) { ctx.fillStyle = rgba(inks.ink, .08); ctx.beginPath(); ctx.roundRect(bar * 2.4, bar * .2, w * .5, bar * .6, bar * .3); ctx.fill(); ctx.font = font(bar * .36, FONTS.mono); ctx.fillStyle = inks.ink; ctx.textBaseline = 'middle'; ctx.fillText(o2.url, bar * 2.7, bar * .52); }
        ctx.beginPath(); ctx.moveTo(0, bar); ctx.lineTo(w, bar); ctx.stroke();
      }
      ctx.save(); ctx.beginPath(); ctx.roundRect(pad, bar + pad, vw, vh, phone ? w * .07 : [0, 0, 12, 12]); ctx.clip();
      ctx.fillStyle = inks.paper; ctx.fillRect(pad, bar + pad, vw, vh);
      if (img && img.naturalWidth) {
        const src = o2.ink === false ? img : K.inkify(img), sh = vw * src.naturalHeight / src.naturalWidth;
        ctx.drawImage(src, pad, bar + pad - Math.max(0, sh - vh) * clamp(o2.scroll || 0), vw, sh);
      }
      ctx.restore(); ctx.restore();
      return { x: x + pad, y: y + bar + pad, w: vw, h: vh };   // the viewport, for cursors and callouts
    };
    // A drawn arrow cursor at (x, y). `click` is the time of a click (scene
    // time): the cursor dips and a ring spreads from its tip.
    K.cursor = function (x, y, o2 = {}) {
      const s = o2.size || 46, dip = o2.click != null ? Math.max(0, 1 - Math.abs(T - o2.click) / .12) : 0;
      if (o2.click != null && T >= o2.click && T < o2.click + .5) { const r = seg(T, o2.click, o2.click + .5); ctx.save(); ctx.strokeStyle = o2.ring || inks.b; ctx.globalAlpha = 1 - r; ctx.lineWidth = 6 * (1 - r) + 1; ctx.beginPath(); ctx.arc(x, y, 10 + r * 60, 0, TAU); ctx.stroke(); ctx.restore(); }
      ctx.save(); ctx.translate(x, y); ctx.scale(1 - dip * .15, 1 - dip * .15);
      const P = [[0, 0], [0, s], [s * .28, s * .76], [s * .48, s * 1.12], [s * .62, s * 1.05], [s * .43, s * .7], [s * .78, s * .7]];
      ctx.fillStyle = rgba(inks.ink, .3); ctx.translate(4, 5); path(P); ctx.fill(); ctx.translate(-4, -5);
      ctx.fillStyle = o2.col || '#FBF8F1'; ctx.strokeStyle = inks.ink; ctx.lineWidth = 4; ctx.lineJoin = 'round'; path(P); ctx.fill(); ctx.stroke();
      ctx.restore();
    };
    // Cursor path: where the cursor is at scene time t, moving through
    // [[t, x, y], ...] on eased arcs (never straight lines).
    K.cursorPath = function (keys) {
      if (T <= keys[0][0]) return [keys[0][1], keys[0][2]];
      for (let i = 1; i < keys.length; i++) if (T < keys[i][0]) {
        const [t0, x0, y0] = keys[i - 1], [t1, x1, y1] = keys[i], u = easeInOut((T - t0) / (t1 - t0)), bow = Math.sin(u * Math.PI) * Math.hypot(x1 - x0, y1 - y0) * .12;
        const nx = -(y1 - y0), ny = x1 - x0, n = Math.hypot(nx, ny) || 1;
        return [lerp(x0, x1, u) + nx / n * bow, lerp(y0, y1, u) + ny / n * bow];
      }
      const l = keys[keys.length - 1]; return [l[1], l[2]];
    };
    // Callout: a hand-drawn arrow from a label to a point, drawn on over k.
    K.callout = function (fromX, fromY, toX, toY, label, o2 = {}) {
      const k = o2.k == null ? 1 : o2.k; if (k <= 0) return;
      const mx = (fromX + toX) / 2 + (toY - fromY) * .25, my = (fromY + toY) / 2 - (toX - fromX) * .25, n = 24, pts = [];
      for (let i = 0; i <= n * clamp(k * 1.4); i++) { const u = i / n; pts.push([(1 - u) * (1 - u) * fromX + 2 * (1 - u) * u * mx + u * u * toX, (1 - u) * (1 - u) * fromY + 2 * (1 - u) * u * my + u * u * toY]); }
      if (pts.length > 1) K.inkLine(pts, o2.col || inks.ink, o2.lw || 5);
      if (k * 1.4 >= 1) { const a = Math.atan2(toY - my, toX - mx), L = 26; K.inkLine([[toX - Math.cos(a - .5) * L, toY - Math.sin(a - .5) * L], [toX, toY], [toX - Math.cos(a + .5) * L, toY - Math.sin(a + .5) * L]], o2.col || inks.ink, o2.lw || 5); }
      if (label) K.hand(label, fromX, fromY - (o2.size || 54) * .7, o2.size || 54, o2.labelCol || inks.a, { k: seg(k, 0, .5), rot: o2.rot ?? -.05 });
    };

    // ---------- transitions (inside a scene, or across a cut) ----------
    // wipe(p): diagonal slats of ink sweep in (p 0 → .5), cover the cut at .5,
    // then sweep on out the far side (.5 → 1). Each slat starts a little later
    // than the one above it, so the edge reads as a hand-pulled stroke.
    K.wipe = function (p, cols = [inks.ink, inks.a], slats = 7, tilt = .18) {
      if (p <= 0 || p >= 1) return; const span = W + H * Math.abs(tilt) + 200, h = H / slats + 2;
      ctx.save(); ctx.setTransform(1, 0, 0, 1, 0, 0);
      for (let i = 0; i < slats; i++) {
        const lag = .25 * i / (slats - 1), inP = easeInOut(clamp((p * 2 - lag) / (1 - lag))), outP = easeInOut(clamp(((p - .5) * 2 - lag) / (1 - lag)));
        const lead = p < .5 ? inP : 1, tail = p < .5 ? 0 : outP, y = i * H / slats, off = (y - H / 2) * tilt;
        const x0 = -100 + span * tail + off, x1 = -100 + span * lead + off; if (x1 - x0 < 2) continue;
        ctx.fillStyle = cols[i % cols.length]; ctx.beginPath(); ctx.moveTo(x0, y); ctx.lineTo(x1, y); ctx.lineTo(x1 - h * tilt, y + h); ctx.lineTo(x0 - h * tilt, y + h); ctx.closePath(); ctx.fill();
      }
      ctx.restore();
    };
    // iris(r): everything outside a circle is ink. Shrink to close, grow to open.
    K.iris = function (cx, cy, r, col = inks.ink) { ctx.save(); ctx.setTransform(1, 0, 0, 1, 0, 0); ctx.fillStyle = col; ctx.beginPath(); ctx.rect(0, 0, W, H); ctx.arc(cx, cy, Math.max(0, r), 0, TAU, true); ctx.fill('evenodd'); ctx.restore(); };
    K.flash = (k, col = '#FFFFFF') => { if (k > .01) K.fillAll(col, clamp(k)); };
    // Paper slide: the next sheet slides over from a side, with a drop shadow.
    K.sheetEdge = function (p, col = inks.paper, dir = 1) { if (p <= 0) return; const x = dir > 0 ? W * (1 - easeInOut(p)) : -W * (1 - easeInOut(p)); ctx.save(); ctx.setTransform(1, 0, 0, 1, 0, 0); ctx.fillStyle = rgba(inks.ink, .3); ctx.fillRect(x - dir * 16, 0, W, H); ctx.fillStyle = col; ctx.fillRect(x, 0, W, H); ctx.restore(); };

    return K;
  }

  root.PaperKit = { create, timeline, INKSETS, FONTS, hash, clamp, lerp, seg, ease, easeOut, backOut };
})(typeof window !== 'undefined' ? window : globalThis);
