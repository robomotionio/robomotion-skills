// howto.js: drawn parts for recipe and how-to videos, on top of PaperKit.
//
// A step rail, a step card with a progress bar, extruded display type, and
// for drinks and cooking a vessel that fills (layers that mix their colour,
// items that drop in and float), a bottle that pours on a curved stream,
// level marks, a stirring spoon, a citrus twist and a celebration burst.
//
// Same contract as the kit: every part is a pure function of time t (video
// seconds), deterministic, and draws on the kit's current layer. Nothing
// here keeps state between frames.
//
//   const how = HowTo.create(kit, { ink: '#2A2626', accent: '#E0636E' });
//   const V = how.vessel({ cx: 350, top: 460, bot: 790, topW: 284, botW: 243 });
//   const P = how.pourTimes(6.0, 2.5);                       // a pour starting at 6 s
//   const st = how.drawVessel(t, V, { fills: [{ color: '#D02B45', from: P.flowStart, to: P.flowEnd, amount: 1 }] });
//   how.pour(t, { bottle: { name: 'CAMPARI', body: '#C8243A', dark: '#8E1526', liquid: '#D02B45' }, times: P, V, st });
(() => {
  const HowTo = {};

  HowTo.create = function (kit, o = {}) {
    const C = {
      ink: o.ink || '#2A2626', accent: o.accent || '#E0636E', accentDark: o.accentDark || kit.mix(o.accent || '#E0636E', '#000000', .2),
      accentLight: o.accentLight || kit.mix(o.accent || '#E0636E', '#FFFFFF', .65), muted: o.muted || '#6F6863', faint: o.faint || '#B9B4AF',
      rail: o.rail || '#E4DFD9', card: o.card || '#FFFDF9', glass: o.glass || '#DDEFF6', glassDark: o.glassDark || '#B9DCEA',
    };
    const DISPLAY = o.display || '"Archivo Black", sans-serif', HAND = o.hand || '"Permanent Marker", sans-serif';
    const { seg, ease, easeIn, easeOut, easeInOut, backOut, lerp, clamp, hash, mix, rgba, TAU } = kit;
    const frac = x => x - Math.floor(x);
    const X = () => kit.ctx;

    // ------------------------------------------------------------ drawing
    function path(pts, close = true) { const c = X(); c.beginPath(); pts.forEach((p, i) => i ? c.lineTo(p[0], p[1]) : c.moveTo(p[0], p[1])); if (close) c.closePath(); }
    // A hand-drawn outline: two slightly different passes of the pen.
    function sketch(pts, s = {}) {
      const c = X();
      if (s.fill) { path(pts, s.close !== false); c.fillStyle = s.fill; c.globalAlpha = s.alpha ?? 1; c.fill(); c.globalAlpha = 1; }
      if (s.line === null) return;
      c.strokeStyle = s.line || C.ink; c.lineJoin = 'round'; c.lineCap = 'round';
      for (let pass = 0; pass < 2; pass++) {
        c.lineWidth = (s.lw || 3.2) * (pass ? .55 : 1); c.globalAlpha = pass ? .55 : 1;
        path(pts.map(p => [p[0] + kit.jit(pass ? 1.6 : .8), p[1] + kit.jit(pass ? 1.6 : .8)]), s.close !== false); c.stroke();
      }
      c.globalAlpha = 1;
    }
    function rr(x, y, w, h, r, n = 5) {
      const p = [], q = (cx, cy, a0) => { for (let i = 0; i <= n; i++) { const a = a0 + i / n * Math.PI / 2; p.push([cx + Math.cos(a) * r, cy + Math.sin(a) * r]); } };
      q(x + w - r, y + r, -Math.PI / 2); q(x + w - r, y + h - r, 0); q(x + r, y + h - r, Math.PI / 2); q(x + r, y + r, Math.PI); return p;
    }
    function ell(cx, cy, rx, ry, n = 36) { const p = []; for (let i = 0; i <= n; i++) { const a = TAU * i / n; p.push([cx + Math.cos(a) * rx, cy + Math.sin(a) * ry]); } return p; }
    function text(s, x, y, size, fam, col, t = {}) {
      const c = X(); c.save(); c.font = `${size}px ${fam}`; c.textAlign = t.align || 'left'; c.textBaseline = t.base || 'alphabetic';
      c.globalAlpha = t.alpha ?? 1; c.fillStyle = col; c.fillText(s, x, y); c.restore();
    }
    const measure = (s, size, fam = DISPLAY) => { const c = X(); c.save(); c.font = `${size}px ${fam}`; const w = c.measureText(s).width; c.restore(); return w; };
    // Extruded display type: a face colour over a darker side, ink outline.
    function chunky(s, x, y, size, t = {}) {
      const c = X(); c.save(); c.translate(x, y); if (t.scale != null) c.scale(t.scale, t.scale);
      c.font = `${size}px ${t.family || DISPLAY}`; c.textAlign = t.align || 'center'; c.textBaseline = 'alphabetic'; c.lineJoin = 'round';
      c.globalAlpha = t.alpha ?? 1;
      const depth = Math.max(2, size * .06);
      for (let i = depth; i > 0; i -= 1) { c.fillStyle = t.side || C.accentDark; c.fillText(s, i * .9, i); }
      c.lineWidth = size * .045; c.strokeStyle = C.ink; c.strokeText(s, depth * .9, depth);
      c.fillStyle = t.face || C.accent; c.fillText(s, 0, 0);
      c.lineWidth = size * .04; c.strokeText(s, 0, 0);
      c.restore();
    }
    // A title whose letters bounce in one after another from `start`.
    function titleDrop(t, word, x, y, size, s = {}) {
      const stagger = s.stagger ?? .13, start = s.start ?? 0, w = measure(word, size, s.family);
      let cx = x - (s.align === 'left' ? 0 : w / 2);
      for (let i = 0; i < word.length; i++) {
        const cw = measure(word[i], size, s.family), k = backOut(seg(t, start + i * stagger, start + i * stagger + .32));
        if (k > 0) { kit.seed('title' + i); chunky(word[i], cx + cw / 2, y + (1 - k) * 30 + (s.bob ? Math.sin((t * 3 + i) * .9) * s.bob : 0), size, { ...s, scale: k, align: 'center' }); }
        cx += cw;
      }
    }

    // ------------------------------------------------------------ steps
    // steps: [{ name, start, done }]. The rail draws dots joined by a line
    // that fills as each step is done; the current step pulses.
    function current(t, steps) { let i = -1; steps.forEach((s, j) => { if (t >= s.start) i = j; }); return i; }
    function rail(t, steps, r = {}) {
      const a = easeOut(seg(t, r.appear ?? 0, (r.appear ?? 0) + .5)); if (a <= 0) return current(t, steps);
      const n = steps.length, gap = r.gap ?? 156, x0 = r.x ?? (kit.W - gap * (n - 1)) / 2, y = (r.y ?? kit.H - 150) + (1 - a) * 40;
      const xs = steps.map((_, i) => x0 + i * gap), c = X(), cur = current(t, steps);
      c.save(); c.globalAlpha = a;
      for (let i = 0; i < n - 1; i++) {
        const fill = easeInOut(seg(t, steps[i].done, steps[i].done + .35));
        c.strokeStyle = C.rail; c.lineWidth = 3; c.beginPath(); c.moveTo(xs[i] + 24, y); c.lineTo(xs[i + 1] - 24, y); c.stroke();
        if (fill > 0) { c.strokeStyle = C.accent; c.lineWidth = 4; c.beginPath(); c.moveTo(xs[i] + 24, y); c.lineTo(lerp(xs[i] + 24, xs[i + 1] - 24, fill), y); c.stroke(); }
      }
      steps.forEach((s, i) => {
        const done = t >= s.done, dk = backOut(seg(t, s.done, s.done + .3)), active = i === cur && !done;
        kit.seed('dot' + i);
        c.save(); c.translate(xs[i], y);
        if (done) {
          c.scale(dk, dk);
          sketch(ell(0, 0, 23, 23, 24), { fill: C.accent, lw: 2.6 });
          c.strokeStyle = '#FFFFFF'; c.lineWidth = 4.5; c.lineCap = 'round'; c.lineJoin = 'round';
          c.beginPath(); c.moveTo(-9, 1); c.lineTo(-3, 7); c.lineTo(10, -7); c.stroke();
        } else {
          const p = active ? 1 + .06 * Math.sin(t * 6) : 1; c.scale(p, p);
          sketch(ell(0, 0, 21, 21, 24), { fill: '#FFFFFF', lw: active ? 3 : 2, line: active ? C.ink : C.faint });
          text(String(i + 1), 0, 8, 24, DISPLAY, active ? C.accentDark : C.faint, { align: 'center' });
        }
        c.restore();
        text(s.name, xs[i], y + 54, r.labelSize ?? 26, HAND, active ? C.accentDark : done ? C.ink : C.faint, { align: 'center' });
      });
      c.restore();
      return cur;
    }
    // A step card that pops in at `start`: eyebrow, big amount, name, a
    // short note and an optional progress bar (progress 0..1 and its label).
    function stepCard(t, s) {
      const x = s.x, y = s.y, w = s.w ?? 384, h = s.h ?? 243, pop = backOut(seg(t, s.start, s.start + .35)), c = X();
      if (pop <= 0) return;
      c.save(); c.translate(x + w / 2, y + h / 2); c.scale(lerp(.86, 1, pop), lerp(.86, 1, pop)); c.rotate((1 - pop) * .04); c.translate(-(x + w / 2), -(y + h / 2));
      c.globalAlpha = clamp(pop * 2);
      kit.seed('card' + s.start);
      sketch(rr(x + 7, y + 9, w, h, 14), { fill: C.accentLight, line: null });
      sketch(rr(x, y, w, h, 14), { fill: C.card, lw: 3 });
      if (s.eyebrow) text(s.eyebrow, x + 26, y + 44, 26, HAND, C.accentDark);
      const bigSize = Math.min(s.bigSize ?? 64, (s.bigSize ?? 64) * (w - 60) / Math.max(1, measure(s.big, s.bigSize ?? 64)));
      chunky(s.big, x + 26, y + 116, bigSize, { align: 'left' });
      const ns = Math.min(38, 38 * (w - 50) / Math.max(1, measure(s.name, 38)));
      text(s.name, x + 26, y + 162, ns, DISPLAY, C.ink);
      if (s.sub) text(s.sub, x + 28, y + 196, Math.min(25, 25 * (w - 56) / Math.max(1, measure(s.sub, 25, HAND))), HAND, C.muted);
      if (s.progress != null) {
        const bx = x + 28, by = y + 214, bw = w - 148, bh = 14;
        sketch(rr(bx, by, bw, bh, 7), { fill: '#FFFFFF', lw: 2.2 });
        if (s.progress > 0) { c.fillStyle = C.accent; c.beginPath(); c.roundRect(bx + 2, by + 2, Math.max(10, (bw - 4) * clamp(s.progress)), bh - 4, 5); c.fill(); }
        if (s.label) text(s.label, bx + bw + 14, by + 13, 22, HAND, C.ink);
      }
      c.restore();
    }

    // ------------------------------------------------------------ vessel
    // A tapered vessel: a rocks glass, a highball (tall, narrow), a jar or a
    // mixing bowl (wide top). `unit` is how many pixels one unit of amount
    // raises the level (one ounce, one cup, one scoop).
    function vessel(v) {
      const V = { cx: v.cx, top: v.top, bot: v.bot, topW: v.topW, botW: v.botW, base: v.base ?? 45, unit: v.unit ?? 62, glass: v.glass || C.glass, rim: v.rim ?? 13 };
      V.tl = V.cx - V.topW / 2; V.tr = V.cx + V.topW / 2; V.bl = V.cx - V.botW / 2; V.br = V.cx + V.botW / 2;
      V.floor = V.bot - V.base;
      V.levelY = amount => V.floor - amount * V.unit;
      V.wallX = (y, side) => side < 0 ? lerp(V.tl, V.bl, (y - V.top) / (V.bot - V.top)) : lerp(V.tr, V.br, (y - V.top) / (V.bot - V.top));
      V.outline = (inset = 0) => [[V.tl + inset, V.top], [V.tr - inset, V.top], [V.br - inset * 1.1, V.bot - inset * .6], [V.bl + inset * 1.1, V.bot - inset * .6]];
      return V;
    }
    // The colour of what is in the vessel: each fill weighted by how much of
    // it is in and its `weight` (a clear spirit tints less than a red one).
    function mixColour(parts, fallback) {
      const tot = parts.reduce((a, p) => a + p[1], 0); if (tot < 1e-3) return fallback;
      const rgb = [0, 0, 0];
      for (const [hex, w] of parts) { const n = parseInt(hex.slice(1), 16); rgb[0] += ((n >> 16) & 255) * w; rgb[1] += ((n >> 8) & 255) * w; rgb[2] += (n & 255) * w; }
      return '#' + rgb.map(q => Math.round(q / tot).toString(16).padStart(2, '0')).join('');
    }
    // Items that drop in (ice, fruit, a scoop): a rounded square by default,
    // or your own draw(c, item, wet, liquid). Each item: { drop, x, y, rot,
    // size, float: surface offset or false }.
    function itemState(t, it, level, stirPhase, V, i) {
      const k = seg(t, it.drop - .45, it.drop); if (k <= 0) return null;
      let y = lerp(-80, it.y, easeIn(k)), rot = (it.rot || 0) + (1 - k) * 1.4 * (i % 2 ? 1 : -1);
      if (t > it.drop) y -= Math.abs(Math.exp(-(t - it.drop) * 9) * Math.sin((t - it.drop) * 30) * 10);
      if (it.float !== false && level < V.floor - 5) y = Math.min(y, level + (it.float ?? 50) + Math.sin(t * 2.2 + i * 2) * 2.5);
      let x = it.x;
      if (stirPhase != null) { x += 11 * Math.sin(stirPhase + i * 2.1); y += 4 * Math.cos(stirPhase + i * 2.1); rot += .3 * Math.sin(stirPhase * .8 + i); }
      return { ...it, i, x, y, rot, size: it.size ?? 70 };
    }
    const rot = (c, pts) => pts.map(([x, y]) => [c.x + x * Math.cos(c.rot) - y * Math.sin(c.rot), c.y + x * Math.sin(c.rot) + y * Math.cos(c.rot)]);
    function cube(it, wet, liquid) {
      const c = X(), h = it.size / 2, shape = rot(it, rr(-h, -h, it.size, it.size, it.size * .21)), edge = rot(it, [[-h + 13, -h + 15], [h - 17, -h + 15], [h - 17, h - 13]]);
      kit.seed('item' + it.i);
      if (it.draw) return it.draw(c, it, wet, liquid);
      if (!wet) {
        const g = c.createLinearGradient(it.x - h, it.y - h, it.x + h, it.y + h); g.addColorStop(0, '#FAFDFE'); g.addColorStop(1, '#D9EAF3');
        sketch(shape, { fill: g, lw: 3.2 });
        c.strokeStyle = '#8FA3AD'; c.lineWidth = 1.8; c.lineJoin = 'round'; path(edge, false); c.stroke();
      } else {
        path(shape); c.fillStyle = rgba('#FFFFFF', .2); c.fill();
        sketch(shape, { fill: null, lw: 2.6, line: rgba(mix(liquid, C.ink, .45), .7) });
        c.strokeStyle = rgba('#FFFFFF', .28); c.lineWidth = 1.8; path(edge, false); c.stroke();
      }
    }
    // Draw the vessel and what is in it. fills: [{ color, from, to, amount,
    // weight }] (amount rises over [from, to]); items: see itemState; stir:
    // [start, end]; cold: [start, end] for condensation. Returns the state
    // (amount, level, colour, per-fill progress) for marks, pours and cards.
    function drawVessel(t, V, d = {}) {
      const fills = d.fills || [], c = X(), oy = d.oy || 0;
      const prog = fills.map(f => easeInOut(seg(t, f.from, f.to)));
      const amount = fills.reduce((a, f, i) => a + prog[i] * (f.amount ?? 1), 0), level = V.levelY(amount);
      const liquid = mixColour(fills.map((f, i) => [f.color, prog[i] * (f.amount ?? 1) * (f.weight ?? 1)]), fills[0]?.color || V.glass);
      const tinted = fills.some((f, i) => (f.weight ?? 1) >= .9 && prog[i] > .02);
      const stirring = d.stir && t >= d.stir[0] && t < d.stir[1], stirPhase = stirring ? (t - d.stir[0]) * TAU * 1.6 : null;
      c.save(); c.translate(0, oy);
      kit.seed('vessel');
      sketch(V.outline(), { fill: V.glass, line: null });
      const items = (d.items || []).map((it, i) => itemState(t, it, level, stirPhase, V, i)).filter(Boolean);
      c.save(); path(V.outline(9)); c.clip();
      items.forEach(it => cube(it, false));
      if (amount > .005) {
        const wobble = stirring ? 4 : 1.5, surf = [];
        for (let i = 0; i <= 24; i++) surf.push([lerp(V.tl - 20, V.tr + 20, i / 24), level + Math.sin(t * 5 + i * .8) * wobble]);
        const body = [...surf, [V.br + 20, V.floor], [V.bl - 20, V.floor]];
        c.globalAlpha = tinted ? .9 : .5; path(body); c.fillStyle = liquid; c.fill(); c.globalAlpha = 1;
        c.save(); path(body); c.clip(); items.forEach(it => cube(it, true, liquid)); c.restore();
        const L = V.wallX(level, -1) + 9, R = V.wallX(level, 1) - 9;              // the surface, seen from slightly above
        c.fillStyle = rgba(mix(liquid, '#FFFFFF', .3), tinted ? .85 : .5);
        c.beginPath(); c.ellipse((L + R) / 2, level + 2, (R - L) / 2, 11, 0, 0, TAU); c.fill();
        c.save(); c.beginPath(); c.ellipse((L + R) / 2, level + 2, (R - L) / 2, 11, 0, 0, TAU); c.clip(); items.forEach(it => cube(it, true, liquid)); c.restore();
        c.save(); c.beginPath(); c.rect(0, 0, kit.W, level - 7); c.clip(); items.filter(it => it.y - it.size * .75 < level).forEach(it => cube(it, false)); c.restore();
      }
      c.fillStyle = mix(V.glass, '#FFFFFF', .35); c.fillRect(V.bl - 20, V.floor, V.br - V.bl + 40, V.base + 15);      // thick base
      c.fillStyle = rgba('#FFFFFF', .7); c.fillRect(V.bl + 30, V.floor + 16, 60, 5);
      c.restore();
      const cold = d.cold ? seg(t, d.cold[0], d.cold[1]) : 0;                      // condensation beads
      for (let i = 0; i < 14 && cold > 0; i++) {
        const y = lerp(V.top + 40, V.bot - 30, hash(i * 7.3)), side = hash(i * 3.1) < .5 ? -1 : 1, x = V.wallX(y, side) - side * (8 + hash(i) * 10);
        const a = clamp(cold * 1.6 - hash(i * 2.2) * .6); if (a <= 0) continue;
        c.fillStyle = rgba('#FFFFFF', .8 * a); c.strokeStyle = rgba(C.glassDark, a); c.lineWidth = 1.5;
        c.beginPath(); c.ellipse(x, y + oy + a * 6 * hash(i * 5), 3.5, 4.5, 0, 0, TAU); c.fill(); c.stroke();
      }
      c.save(); c.translate(0, oy);
      kit.seed('vesselline');
      sketch(V.outline(), { fill: null, lw: 3.4 });
      sketch(ell(V.cx, V.top, V.topW / 2, V.rim), { lw: 3 });
      sketch([[V.bl + 12, V.floor + 6], [V.br - 12, V.floor + 6]], { close: false, lw: 2, line: rgba(C.ink, .55) });
      c.strokeStyle = 'rgba(255,255,255,.9)'; c.lineWidth = 7; c.lineCap = 'round';
      c.beginPath(); c.moveTo(V.tl + 28, V.top + 50); c.lineTo(V.bl + 30, V.bot - 70); c.stroke();
      c.restore();
      return { amount, level, liquid, prog, stirPhase, oy };
    }
    // Level marks outside the right wall: [{ amount, label, show }]. A mark
    // turns the accent colour once the level reaches it; while it is the
    // next one to reach, a dashed target line crosses the vessel.
    function marks(t, V, st, list) {
      const c = X();
      list.forEach(m => {
        const show = seg(t, m.show, m.show + .3); if (show <= 0) return;
        const reached = st.amount >= m.amount - .02, y = V.levelY(m.amount) + st.oy, x = V.wallX(V.levelY(m.amount), 1) + 10, col = reached ? C.accentDark : C.faint;
        c.globalAlpha = show; c.strokeStyle = col; c.lineWidth = 3; c.lineCap = 'round';
        c.beginPath(); c.moveTo(x, y); c.lineTo(x + 24, y); c.stroke();
        text(m.label, x + 32, y + 9, 28, HAND, col);
        if (!reached && (m.until == null || t < m.until)) {
          c.setLineDash([10, 9]); c.strokeStyle = rgba(C.ink, .25); c.lineWidth = 2;
          c.beginPath(); c.moveTo(V.wallX(V.levelY(m.amount), -1) + 12, y); c.lineTo(x - 12, y); c.stroke(); c.setLineDash([]);
        }
        c.globalAlpha = 1;
      });
    }

    // ------------------------------------------------------------ pouring
    // The phases of one pour: slide in, tilt, flow, tilt back, slide out.
    function pourTimes(start, flow = 2.5, p = {}) {
      const P = { in: .5, tilt: .4, back: .4, out: .45, ...p };
      const flowStart = start + P.in + P.tilt, flowEnd = flowStart + flow;
      return { start, flowStart, flowEnd, end: flowEnd + P.back + P.out, P };
    }
    // bottle: { name, sub, body, dark, liquid, cap, stream }. Label text runs along it.
    function bottle(b, x, y, r, s = 1) {
      const c = X(); c.save(); c.translate(x, y); c.rotate(r); c.scale(s, s);
      kit.seed('bottle' + b.name);
      sketch([[-38, -40], [-38, 95], [38, 95], [38, -40], [26, -62], [13, -72], [13, -118], [-13, -118], [-13, -72], [-26, -62]], { fill: b.body, lw: 3.2 });
      c.fillStyle = rgba('#FFFFFF', .35); c.fillRect(-28, -30, 9, 110);
      sketch(rr(-15, -132, 30, 18, 4), { fill: b.cap || b.dark, lw: 2.6 });
      sketch(rr(-28, -22, 56, 100, 5), { fill: '#FBF6EC', lw: 2.4 });
      c.save(); c.translate(0, 27); c.rotate(-Math.PI / 2);
      text(b.name, 0, 2, Math.min(22, 22 * 84 / Math.max(1, measure(b.name, 22))), DISPLAY, b.dark, { align: 'center' });
      if (b.sub) text(b.sub, 0, 21, 16, HAND, C.muted, { align: 'center' });
      c.restore(); c.restore();
    }
    // One pour into V: the bottle comes in from the left, tilts, and a
    // curved stream falls from its mouth to the surface, with splash drops.
    function pour(t, d) {
      const T = d.times, b = d.bottle, V = d.V, st = d.st, oy = st.oy || 0;
      if (t < T.start || t > T.end + .05) return;
      const inK = easeOut(seg(t, T.start, T.start + T.P.in)), outK = easeIn(seg(t, T.end - T.P.out, T.end));
      const tilt = easeInOut(seg(t, T.start + T.P.in, T.flowStart)) * (1 - easeInOut(seg(t, T.flowEnd, T.flowEnd + T.P.back)));
      const rest = d.x ?? V.tl - 90, x = lerp(rest - 240, rest, inK) - outK * 260 + tilt * 12, y = (d.y ?? V.top - 160) + oy - tilt * 10 + (1 - inK) * 20;
      const r = lerp(0, d.angle ?? 2.05, tilt) + Math.sin(t * 7) * .015 * tilt;
      const target = d.targetX ?? V.cx - V.topW * .18, stream = b.stream || b.liquid, c = X();
      if (t > T.flowStart - .05 && t < T.flowEnd + .3) {
        const mx = x + Math.sin(r) * 124, my = y - Math.cos(r) * 124, surf = st.level + oy;
        const head = clamp((t - T.flowStart + .05) / .15), tail = clamp((t - T.flowEnd) / .3), pts = [];
        for (let k = 0; k <= 16; k++) {
          const u = k / 16; if (u > head || u < tail) continue;
          pts.push([mx + (target - mx) * (1 - Math.pow(1 - u, 2)) + Math.sin(t * 20 + u * 9) * 1.5, lerp(my, surf, u * u * .6 + u * .4)]);
        }
        if (pts.length > 1) {
          c.strokeStyle = stream; c.lineWidth = 8 * (1 - tail * .6); c.lineCap = 'round'; path(pts, false); c.stroke();
          c.strokeStyle = C.ink; c.lineWidth = 1.6; c.globalAlpha = .6; path(pts, false); c.stroke(); c.globalAlpha = 1;
        }
        if (head >= 1 && tail <= 0) for (let k = 0; k < 5; k++) {
          const ph = frac(t * 2.4 + hash(k * 3.7)), dx = (hash(k * 1.9) - .5) * 60;
          c.fillStyle = stream; c.beginPath(); c.arc(target + dx * ph, surf - Math.sin(ph * Math.PI) * (18 + 16 * hash(k)), 4 * (1 - ph) + 1.5, 0, TAU); c.fill();
        }
      }
      bottle(b, x, y, r);
    }

    // ------------------------------------------------------------ finishing
    // A bar spoon that dips in and circles over [start, end].
    function spoon(t, V, start, end, oy = 0) {
      const a = seg(t, start - .4, start), b = seg(t, end, end + .4); if (a <= 0 || b >= 1) return;
      const drop = (1 - easeOut(a)) * -520 + easeIn(b) * -520, ph = t > start ? (t - start) * TAU * 1.6 : 0, c = X();
      const tip = [V.cx + 46 * Math.sin(ph), V.floor - 33 + 10 * Math.cos(ph) + drop + oy], top = [V.cx + 15 + 14 * Math.sin(ph + .4), V.top - 130 + drop + oy];
      kit.seed('spoon');
      c.strokeStyle = C.ink; c.lineWidth = 7; c.lineCap = 'round'; c.beginPath(); c.moveTo(...top); c.lineTo(...tip); c.stroke();
      c.strokeStyle = '#C9CDD2'; c.lineWidth = 3.5; c.beginPath(); c.moveTo(...top); c.lineTo(...tip); c.stroke();
      for (let k = 1; k < 14; k++) { const u = k / 14, x = lerp(top[0], tip[0], u), y = lerp(top[1], tip[1], u); c.strokeStyle = rgba(C.ink, .5); c.lineWidth = 1.4; c.beginPath(); c.moveTo(x - 4, y - 3); c.lineTo(x + 4, y + 3); c.stroke(); }
      sketch(ell(top[0], top[1] - 6, 10, 10, 18), { fill: '#C9CDD2', lw: 2.6 });
      sketch(ell(tip[0], tip[1] + 8, 9, 16, 18), { fill: '#C9CDD2', lw: 2.6 });
    }
    // A citrus twist: a spritz of oil, then the peel spirals down onto the rim.
    function twist(t, x, y, start, col = '#F2A93B', dark = '#C9781B') {
      const c = X(), sp = seg(t, start + .15, start + .7);
      if (sp > 0 && sp < 1) for (let d = 0; d < 16; d++) {
        const a = -Math.PI / 2 + (hash(d * 2.3) - .5) * 1.8, r = 20 + sp * (90 + 60 * hash(d));
        c.fillStyle = rgba(col, 1 - sp); c.beginPath(); c.arc(x - 30 + Math.cos(a) * r, y - 75 + Math.sin(a) * r, 4 + 3 * hash(d * 5), 0, TAU); c.fill();
      }
      const k = seg(t, start + .5, start + 1.1); if (k <= 0) return;
      const land = t > start + 1.1 ? Math.exp(-(t - start - 1.1) * 7) * Math.sin((t - start - 1.1) * 26) : 0;
      c.save(); c.translate(x, lerp(-120, y, easeIn(k)) - land * 6); c.rotate((1 - k) * 3.2 + land * .08); c.scale(1 + land * .06, 1 - land * .06);
      const pts = []; for (let i = 0; i <= 60; i++) { const th = i / 60 * TAU * 2.6; pts.push([th * 7.5 - 16 * Math.sin(th), -16 * Math.cos(th) - th * 1.2]); }
      c.lineCap = 'round'; c.lineJoin = 'round';
      c.strokeStyle = C.ink; c.lineWidth = 15; path(pts, false); c.stroke();
      c.strokeStyle = col; c.lineWidth = 10; path(pts, false); c.stroke();
      c.strokeStyle = rgba(dark, .7); c.lineWidth = 2.5; path(pts.map(p => [p[0] + 2, p[1] + 2]), false); c.stroke();
      c.restore();
    }
    // Three rounds of short strokes fanning out above (cx, cy): the "done!" beat.
    function burst(t, cx, cy, start, r0 = 215, cols = [C.accent, '#F2A93B']) {
      if (t < start) return; const c = X();
      for (let r = 0; r < 3; r++) {
        const t0 = start + .1 + r * .9, k = seg(t, t0, t0 + .55); if (k <= 0 || k >= 1) continue;
        for (let i = 0; i < 9; i++) {
          const a = -Math.PI * .95 + i / 8 * Math.PI * .9 + (hash(i + r * 11) - .5) * .25, rr0 = r0 + easeOut(k) * 60, len = 40 * (1 - k) + 10;
          c.strokeStyle = cols[i % 3 === 0 ? 1 : 0]; c.lineWidth = 7; c.lineCap = 'round'; c.globalAlpha = 1 - k * .6;
          c.beginPath(); c.moveTo(cx + Math.cos(a) * rr0, cy + Math.sin(a) * rr0 * .9); c.lineTo(cx + Math.cos(a) * (rr0 + len), cy + Math.sin(a) * (rr0 + len) * .9); c.stroke();
        }
        c.globalAlpha = 1;
      }
    }

    return {
      C, DISPLAY, HAND, path, sketch, rr, ell, text, measure, chunky, titleDrop,
      current, rail, stepCard, vessel, drawVessel, marks, pourTimes, bottle, pour, spoon, twist, burst,
    };
  };

  (typeof window !== 'undefined' ? window : globalThis).HowTo = HowTo;
})();
