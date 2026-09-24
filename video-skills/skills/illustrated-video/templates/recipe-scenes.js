// recipe-scenes.js: a recipe or how-to, step by step, in one continuous shot.
// Copy it over scenes.js (scaffold.sh leaves an existing scenes.js alone).
//
// Edit RECIPE and the colours; the rest follows from them. A vessel on the
// left fills as each step happens, a card on the right says what the step is
// and how far along it is, and a rail below ticks the steps off. Step kinds:
//   items  drop things in (ice, fruit, a scoop): count, size
//   pour   a bottle pours an amount: bottle, color, amount, weight, flow
//   stir   a spoon circles for dur seconds: seconds (the number counted down)
//   twist  a citrus twist lands on the rim
//   note   nothing drawn in the vessel; the card and rail carry it
// Every `at` is in video seconds. Space the steps so each one is readable:
// a pour needs about 4.5 s, a drop of items 2 s, a stir 4 s.
(() => {
  const W = 1920, H = 1080;
  // The stage (vessel, card, rail) is laid out at 1080p scale and enlarged by
  // STAGE around (W / 2, STAGE_Y); the title stays at its own size.
  const STAGE = 1.25, STAGE_Y = 600;
  const INK = { paper: '#FAF7F2', ink: '#2A2626', a: '#E0636E', b: '#D02B45', c: '#F2A93B', d: '#DDEFF6' };
  const RECIPE = {
    title: 'NEGRONI', intro: 'a 30 second recipe', tagline: 'equal parts  ·  stirred  ·  on the rocks',
    unit: 'oz',
    vessel: { cx: 700, top: 440, bot: 780, topW: 290, botW: 248, unit: 62 },
    steps: [
      { kind: 'items', name: 'ICE', big: 'FILL', title: 'ICE', sub: 'big cubes · rocks glass', at: 3.7, count: 3 },
      { kind: 'pour', name: 'GIN', big: '1 OZ', title: 'GIN', sub: 'London dry · 30 ml', at: 6.0, amount: 1, color: '#EAF3F6', weight: .35, stream: '#9CC7D8',
        bottle: { name: 'GIN', sub: 'london dry', body: '#CFE6EF', dark: '#8FB9CB', cap: '#7A9CAB' } },
      { kind: 'pour', name: 'CAMPARI', big: '1 OZ', title: 'CAMPARI', sub: 'the bitter one · 30 ml', at: 10.7, amount: 1, color: '#D02B45',
        bottle: { name: 'CAMPARI', sub: 'bitter', body: '#C8243A', dark: '#8E1526', cap: '#6E1020' } },
      { kind: 'pour', name: 'VERMOUTH', big: '1 OZ', title: 'SWEET VERMOUTH', sub: 'vermouth rosso · 30 ml', at: 15.4, amount: 1, color: '#5E0B1C',
        bottle: { name: 'ROSSO', sub: 'vermouth', body: '#5A1420', dark: '#34080F', cap: '#2A0509' } },
      { kind: 'stir', name: 'STIR', big: '20 SEC', title: 'STIR', sub: 'until nice and cold', at: 20.3, dur: 3.7, seconds: 20 },
      { kind: 'twist', name: 'PEEL', big: '1', title: 'ORANGE PEEL', sub: 'express the oils, drop it in', at: 24.4 },
    ],
    done: { at: 26.9, eyebrow: "THAT'S A NEGRONI", big: 'CIN CIN!', title: '1 : 1 : 1', sub: 'gin · Campari · sweet vermouth' },
  };

  const kit = PaperKit.create({ bg: 'bg', fg: 'fg', width: W, height: H, inks: INK, boil: 8 });
  const how = HowTo.create(kit, { ink: INK.ink, accent: INK.a });
  const { seg, easeInOut, easeOut, backOut, lerp, clamp, TAU, rgba } = kit;
  const V = how.vessel(RECIPE.vessel);
  const S = RECIPE.steps, N = S.length;

  // ---------------------------------------------------------------- timing
  // Where each step's action happens, when it counts as done, and what goes in.
  let poured = 0;
  S.forEach((s, i) => {
    if (s.kind === 'pour') {
      s.times = how.pourTimes(s.at, s.flow ?? 2.5);
      s.done = s.times.flowEnd + .1;
      poured += s.amount ?? 1; s.mark = poured;
    } else if (s.kind === 'items') {
      s.drops = Array.from({ length: s.count ?? 3 }, (_, k) => s.at + .55 + k * .5);
      s.done = s.drops[s.drops.length - 1] + .45;
    } else if (s.kind === 'stir') s.done = s.at + .4 + s.dur;
    else if (s.kind === 'twist') s.done = s.at + 1.6;
    else s.done = s.at + (s.dur ?? 2);
    s.start = s.at;
  });
  const fills = S.filter(s => s.kind === 'pour').map(s => ({ color: s.color, from: s.times.flowStart, to: s.times.flowEnd, amount: s.amount ?? 1, weight: s.weight ?? 1 }));
  const items = S.filter(s => s.kind === 'items').flatMap(s => s.drops.map((drop, k) => ({
    drop, x: V.cx + (k - ((s.count ?? 3) - 1) / 2) * 68, y: V.floor - 37 - (k % 2) * 56, rot: [-.3, .22, .1, -.15][k % 4], size: s.size ?? 70, float: [60, 34, 64, 44][k % 4],
  })));
  const stir = S.find(s => s.kind === 'stir'), twist = S.find(s => s.kind === 'twist');
  const TITLE_UP = Math.max(1.6, S[0].at - 1.1), GLASS_IN = Math.max(.8, S[0].at - .7), RAIL_IN = Math.max(1, S[0].at - .3);

  // ---------------------------------------------------------------- frame
  function draw(t) {
    kit.frame(t);
    const c = kit.ctx;
    // Title: letters bounce in centre screen, then the title rises to the top.
    const up = easeInOut(seg(t, TITLE_UP, TITLE_UP + .7));
    how.titleDrop(t, RECIPE.title, W / 2, lerp(H / 2, 128, up), lerp(170, 88, up), { start: .15, bob: (1 - up) * 4 });
    how.text(RECIPE.intro, W / 2, H / 2 + 90, 40, how.HAND, how.C.muted, { align: 'center', alpha: seg(t, 1.2, 1.6) * (1 - seg(t, TITLE_UP, TITLE_UP + .25)) });
    const a2 = seg(t, TITLE_UP + .55, TITLE_UP + .95);
    if (a2 > 0) how.text(RECIPE.tagline, W / 2, 192 + (1 - easeOut(a2)) * 12, 36, how.HAND, how.C.muted, { align: 'center', alpha: a2 });

    c.save(); c.translate(W / 2, STAGE_Y); c.scale(STAGE, STAGE); c.translate(-W / 2, -STAGE_Y);
    const done = t >= RECIPE.done.at;
    const oy = (1 - backOut(seg(t, GLASS_IN, GLASS_IN + .6))) * 560 + (done ? Math.sin((t - RECIPE.done.at) * 5) * 3 : 0);
    let st = { amount: 0, level: V.floor, prog: [], oy };
    if (t > GLASS_IN) {
      c.fillStyle = rgba(INK.ink, .06); c.beginPath(); c.ellipse(V.cx, V.bot + 14 + oy, V.topW * .53, 16, 0, 0, TAU); c.fill();
      st = how.drawVessel(t, V, { fills, items, oy, stir: stir && [stir.at + .4, stir.done], cold: stir && [stir.at + .8, stir.done - .2] });
      how.marks(t, V, st, S.filter(s => s.kind === 'pour').map(s => ({ amount: s.mark, label: `${+s.mark.toFixed(2)} ${RECIPE.unit}`, show: s.at + .6, until: s.times.flowEnd })));
      if (stir) how.spoon(t, V, stir.at + .4, stir.done, oy);
      if (twist) how.twist(t, V.cx + V.topW * .35, V.top - 5 + oy, twist.at);
      how.burst(t, V.cx, V.bot - (V.bot - V.top) * .55 + oy, RECIPE.done.at);
      S.forEach(s => { if (s.kind === 'pour') how.pour(t, { times: s.times, bottle: { ...s.bottle, liquid: s.color, stream: s.stream }, V, st }); });
    }

    // Card: the current step, with how far along it is.
    const cur = how.current(t, S);
    const cx = V.cx + V.topW / 2 + 160, cy = V.top + 50;
    if (done) {
      const d = RECIPE.done; how.stepCard(t, { x: cx, y: cy, start: d.at, eyebrow: d.eyebrow, big: d.big, name: d.title, sub: d.sub, bigSize: 70 });
    } else if (cur >= 0) {
      const s = S[cur]; let k = 0, label = '';
      if (s.kind === 'items') { const n = s.drops.filter(d => t >= d).length; k = n / s.drops.length; label = `${n} / ${s.drops.length}`; }
      else if (s.kind === 'pour') { const f = fills.findIndex(f => f.from === s.times.flowStart); k = st.prog[f] ?? 0; label = `${(k * (s.amount ?? 1)).toFixed(1)} / ${s.amount ?? 1} ${RECIPE.unit}`; }
      else if (s.kind === 'stir') { k = seg(t, s.at + .4, s.done); label = `${Math.ceil((s.seconds ?? 20) * (1 - k))} s`; }
      else if (s.kind === 'twist') { k = seg(t, s.at + .2, s.at + 1.1); label = k >= 1 ? 'done!' : 'twist...'; }
      else { k = seg(t, s.at, s.done); }
      how.stepCard(t, { x: cx, y: cy, start: s.at, eyebrow: `STEP ${cur + 1} OF ${N}`, big: s.big, name: s.title, sub: s.sub, progress: k, label });
    }
    how.rail(t, S, { y: H - 190, appear: RAIL_IN });
    c.restore();
    kit.finish({ grain: .3 });
  }

  window.SCENES_READY = document.fonts.ready.then(() => draw);
})();
