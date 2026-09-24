#!/usr/bin/env node
// fal.mjs: run any fal.ai model from the terminal, the way a careful producer would.
//
//   node fal.mjs search "lip sync" [--category image-to-video] [--limit 10]
//   node fal.mjs schema <endpoint>                      input fields, types, enums, defaults, price
//   node fal.mjs run <endpoint> --input job.json|'{...}' --est 0.40 [--out dir] [--name shot03]
//   node fal.mjs batch jobs.json [--concurrency 4] [--out dir]
//   node fal.mjs upload <file>                          → a fal CDN URL
//   node fal.mjs spend [--project dir]                  what this project has spent
//   node fal.mjs budget <usd> [--project dir]           set the project's spending cap
//
// `run` checks the input against the model's live schema, uploads every
// local file path it finds in the input (strings, or strings in arrays) to
// fal storage, queues the job, polls it, downloads every file in the result
// into --out and appends a line to the project's spend ledger.
//
// Money: every run needs --est (your estimate in USD, from `schema`'s price
// line). A run that would take the project past its budget is refused before
// anything is sent. search and schema are free and need no key.
//
// Auth: FAL_KEY from the environment (in the sandbox it is a placeholder the
// credential proxy swaps for the real key on the way out).
import { readFileSync, writeFileSync, existsSync, mkdirSync, appendFileSync, statSync, openAsBlob } from 'node:fs';
import { basename, extname, join, resolve } from 'node:path';

const argv = process.argv.slice(2);
const cmd = argv[0];
const flags = {}, pos = [];
for (let i = 1; i < argv.length; i++) {
  const a = argv[i];
  if (a.startsWith('--')) { const [k, v] = a.slice(2).split('='); if (v !== undefined) flags[k] = v; else if (argv[i + 1] && !argv[i + 1].startsWith('--')) flags[k] = argv[++i]; else flags[k] = true; }
  else pos.push(a);
}
const PROJECT = resolve(flags.project || '.');
const LEDGER_DIR = join(PROJECT, '.fal');
const die = (msg, code = 1) => { console.error('fal: ' + msg); process.exit(code); };
const sleep = ms => new Promise(r => setTimeout(r, ms));

function authHeader() {
  const key = process.env.FAL_KEY;
  if (!key) die('FAL_KEY is not set. fal models need a fal.ai API key; the video can still be made without them (see the skill, "No fal key").', 3);
  return 'Key ' + key;
}

async function http(url, opts = {}, tries = 4) {
  for (let i = 0; ; i++) {
    let res;
    try { res = await fetch(url, opts); } catch (e) { if (i >= tries) throw e; await sleep(1500 * (i + 1)); continue; }
    if (res.ok) return res;
    if ((res.status === 429 || res.status >= 500) && i < tries) { await sleep(2000 * (i + 1)); continue; }
    const body = await res.text().catch(() => '');
    throw new Error(`${opts.method || 'GET'} ${url} → ${res.status} ${body.slice(0, 600)}`);
  }
}

// ---------- discovery (no key) ----------
async function search(q) {
  const u = new URL('https://fal.ai/api/models');
  u.searchParams.set('keywords', q); u.searchParams.set('limit', flags.limit || '12');
  if (flags.category) u.searchParams.set('categories', flags.category);
  const d = await (await http(u)).json();
  for (const m of d.items || []) {
    const price = (m.pricingInfoOverride || '').replace(/\*\*/g, '').split('. ')[0];
    console.log(`${m.id}\n   ${m.title} · ${m.category || ''} · ${m.date ? m.date.slice(0, 10) : ''}\n   ${(m.shortDescription || '').slice(0, 180)}\n   price: ${price || 'see schema'}`);
  }
}

async function openapi(endpoint) {
  const d = await (await http(`https://fal.ai/api/openapi/queue/openapi.json?endpoint_id=${encodeURIComponent(endpoint)}`)).json();
  const S = d.components?.schemas || {};
  const inName = Object.keys(S).find(k => /Input$/.test(k)) || Object.keys(S).find(k => /Input/.test(k));
  const outName = Object.keys(S).find(k => /Output$/.test(k));
  return { input: S[inName], output: S[outName], schemas: S };
}
async function priceLine(endpoint) {
  try { const d = await (await http(`https://fal.ai/api/models?keywords=${encodeURIComponent(endpoint)}&limit=5`)).json(); const m = (d.items || []).find(x => x.id === endpoint); return (m?.pricingInfoOverride || '').replace(/\*\*/g, ''); } catch { return ''; }
}
function fieldType(p, S) {
  if (!p) return '?';
  if (p.$ref) return fieldType(S[p.$ref.split('/').pop()], S);
  if (p.anyOf) return p.anyOf.map(x => fieldType(x, S)).filter(x => x !== 'null').join('|');
  if (p.enum) return 'enum(' + p.enum.join(', ') + ')';
  if (p.type === 'array') return fieldType(p.items, S) + '[]';
  return p.type || (p.properties ? 'object' : '?');
}
async function schema(endpoint) {
  const { input, schemas } = await openapi(endpoint);
  if (!input) die('no input schema found for ' + endpoint);
  const req = new Set(input.required || []);
  console.log(`${endpoint}\nprice: ${await priceLine(endpoint) || 'not listed (check fal.ai/models/' + endpoint + ')'}\ninputs:`);
  for (const [k, p] of Object.entries(input.properties || {})) {
    const lim = [p.minimum != null && `min ${p.minimum}`, p.maximum != null && `max ${p.maximum}`, p.maxItems != null && `≤${p.maxItems} items`].filter(Boolean).join(', ');
    console.log(`  ${req.has(k) ? '*' : ' '} ${k}: ${fieldType(p, schemas)}${p.default !== undefined ? ' = ' + JSON.stringify(p.default) : ''}${lim ? ' (' + lim + ')' : ''}\n      ${(p.description || '').replace(/\s+/g, ' ').slice(0, 220)}`);
  }
  console.log('(* = required)');
}

// ---------- files ----------
const MIME = { '.png': 'image/png', '.jpg': 'image/jpeg', '.jpeg': 'image/jpeg', '.webp': 'image/webp', '.gif': 'image/gif', '.mp4': 'video/mp4', '.mov': 'video/quicktime', '.webm': 'video/webm', '.mp3': 'audio/mpeg', '.wav': 'audio/wav', '.m4a': 'audio/mp4', '.ogg': 'audio/ogg', '.json': 'application/json', '.txt': 'text/plain' };
const uploaded = new Map();
async function upload(file) {
  const abs = resolve(file); if (uploaded.has(abs)) return uploaded.get(abs);
  const auth = authHeader(), type = MIME[extname(abs).toLowerCase()] || 'application/octet-stream';
  const init = await (await http('https://rest.fal.ai/storage/upload/initiate?storage_type=fal-cdn-v3', {
    method: 'POST', headers: { Authorization: auth, 'Content-Type': 'application/json' },
    body: JSON.stringify({ file_name: basename(abs), content_type: type }),
  })).json();
  await http(init.upload_url, { method: 'PUT', headers: { 'Content-Type': type }, body: await openAsBlob(abs) });
  uploaded.set(abs, init.file_url);
  return init.file_url;
}
// Replace every local file path in the input with an uploaded URL.
async function uploadLocal(v) {
  if (typeof v === 'string') { if (!/^(https?:|data:)/.test(v) && v.length < 1024 && existsSync(v) && statSync(v).isFile()) { const url = await upload(v); console.error(`  uploaded ${v} → ${url}`); return url; } return v; }
  if (Array.isArray(v)) return Promise.all(v.map(uploadLocal));
  if (v && typeof v === 'object') { const o = {}; for (const [k, x] of Object.entries(v)) o[k] = await uploadLocal(x); return o; }
  return v;
}
function mediaUrls(v, out = [], key = '') {
  if (typeof v === 'string' && /^https:\/\/[^\s]*(fal\.media|fal\.run|fal\.ai|storage\.googleapis)/.test(v) && /\.(png|jpe?g|webp|gif|mp4|mov|webm|mp3|wav|m4a|ogg|json|zip|glb)(\?|$)/i.test(v)) out.push({ url: v, key });
  else if (Array.isArray(v)) v.forEach((x, i) => mediaUrls(x, out, `${key}${i}`));
  else if (v && typeof v === 'object') for (const [k, x] of Object.entries(v)) mediaUrls(x, out, key ? `${key}_${k}` : k);
  return out;
}
async function download(url, dest) { const res = await http(url); writeFileSync(dest, Buffer.from(await res.arrayBuffer())); return dest; }

// ---------- money ----------
function ledger() { const f = join(LEDGER_DIR, 'spend.jsonl'); if (!existsSync(f)) return []; return readFileSync(f, 'utf8').trim().split('\n').filter(Boolean).map(l => JSON.parse(l)); }
function spent() { return ledger().reduce((s, r) => s + (r.est_usd || 0), 0); }
function budget() { const f = join(LEDGER_DIR, 'budget.json'); return existsSync(f) ? JSON.parse(readFileSync(f, 'utf8')).usd : null; }
function guard(est, what) {
  if (!(est >= 0)) die(`${what}: pass --est <usd> (your estimate from \`schema\`'s price line). Nothing was sent.`);
  const cap = budget(), used = spent();
  if (cap != null && used + est > cap + 1e-9) die(`${what}: $${est.toFixed(2)} would take this project to $${(used + est).toFixed(2)}, over its $${cap.toFixed(2)} budget. Nothing was sent. Ask the person before raising it (fal.mjs budget <usd>).`, 4);
}
function record(r) { mkdirSync(LEDGER_DIR, { recursive: true }); appendFileSync(join(LEDGER_DIR, 'spend.jsonl'), JSON.stringify({ at: new Date().toISOString(), ...r }) + '\n'); }

// ---------- run ----------
function readInput(s) { if (!s) die('pass --input <file.json | inline JSON>'); return s.trim().startsWith('{') ? JSON.parse(s) : JSON.parse(readFileSync(s, 'utf8')); }
async function checkInput(endpoint, input) {
  try {
    const { input: sch } = await openapi(endpoint); if (!sch) return;
    const props = sch.properties || {}, bad = Object.keys(input).filter(k => !(k in props)), miss = (sch.required || []).filter(k => !(k in input) && props[k]?.default === undefined);
    if (bad.length) die(`${endpoint} has no input field(s) ${bad.join(', ')}. Fields: ${Object.keys(props).join(', ')}. Nothing was sent.`);
    if (miss.length) die(`${endpoint} needs ${miss.join(', ')}. Nothing was sent.`);
    for (const [k, v] of Object.entries(input)) { const p = props[k]; const en = p?.enum || p?.anyOf?.find(x => x.enum)?.enum; if (en && !en.includes(v)) die(`${k}=${JSON.stringify(v)} is not one of ${en.join(', ')}. Nothing was sent.`); }
  } catch (e) { if (String(e.message).startsWith('fal:')) throw e; console.error('  (schema check skipped: ' + e.message.slice(0, 120) + ')'); }
}
async function runOne(endpoint, rawInput, o = {}) {
  const est = Number(o.est ?? flags.est), name = o.name || flags.name || endpoint.split('/').slice(-2).join('-') + '-' + Date.now().toString(36);
  const out = resolve(o.out || flags.out || join(PROJECT, 'assets', 'fal'));
  await checkInput(endpoint, rawInput);
  guard(est, name);
  const auth = authHeader();
  const input = await uploadLocal(rawInput);
  const sub = await (await http(`https://queue.fal.run/${endpoint}`, { method: 'POST', headers: { Authorization: auth, 'Content-Type': 'application/json' }, body: JSON.stringify(input) })).json();
  record({ name, endpoint, request_id: sub.request_id, est_usd: est, status: 'submitted' });
  console.error(`  ${name}: queued ${sub.request_id}`);
  const t0 = Date.now(), maxMs = (Number(o.timeout || flags.timeout) || 1800) * 1000;
  let last = '';
  for (;;) {
    await sleep(Date.now() - t0 < 30000 ? 3000 : 8000);
    const st = await (await http(sub.status_url + '?logs=1', { headers: { Authorization: auth } })).json();
    if (st.status !== last) { console.error(`  ${name}: ${st.status}${st.queue_position != null ? ' (queue ' + st.queue_position + ')' : ''}`); last = st.status; }
    if (st.status === 'COMPLETED') break;
    if (st.status === 'FAILED' || st.error) { record({ name, endpoint, request_id: sub.request_id, est_usd: 0, status: 'failed', error: String(st.error || '').slice(0, 300) }); throw new Error(`${name} failed: ${JSON.stringify(st.error || st).slice(0, 500)}`); }
    if (Date.now() - t0 > maxMs) throw new Error(`${name} still ${st.status} after ${maxMs / 1000}s; request ${sub.request_id} (fetch later with: fal.mjs result ${endpoint} ${sub.request_id})`);
  }
  const res = await (await http(sub.response_url, { headers: { Authorization: auth } })).json();
  mkdirSync(out, { recursive: true });
  const files = [];
  for (const { url, key } of mediaUrls(res)) { const ext = (url.split('?')[0].match(/\.[a-z0-9]+$/i) || ['.bin'])[0]; files.push(await download(url, join(out, `${name}${key ? '_' + key : ''}${ext}`))); }
  writeFileSync(join(out, `${name}.json`), JSON.stringify({ endpoint, request_id: sub.request_id, input: rawInput, result: res }, null, 2));
  record({ name, endpoint, request_id: sub.request_id, est_usd: 0, status: 'done', files, seconds: Math.round((Date.now() - t0) / 1000) });
  for (const f of files) console.log(f);
  return { name, files, result: res };
}
async function result(endpoint, id) {
  const auth = authHeader(), owner = endpoint.split('/').slice(0, 2).join('/');
  const res = await (await http(`https://queue.fal.run/${owner}/requests/${id}`, { headers: { Authorization: auth } })).json();
  const out = resolve(flags.out || join(PROJECT, 'assets', 'fal')); mkdirSync(out, { recursive: true });
  for (const { url, key } of mediaUrls(res)) { const ext = (url.split('?')[0].match(/\.[a-z0-9]+$/i) || ['.bin'])[0]; console.log(await download(url, join(out, `${id}${key ? '_' + key : ''}${ext}`))); }
}
// jobs.json: [{ "name": "shot03", "endpoint": "...", "input": {...}, "est": 0.4 }, ...]
async function batch(file) {
  const jobs = JSON.parse(readFileSync(file, 'utf8')), conc = Number(flags.concurrency || 4);
  const total = jobs.reduce((s, j) => s + Number(j.est), 0);
  guard(total, `batch of ${jobs.length}`);
  let next = 0; const results = [], fails = [];
  await Promise.all(Array.from({ length: Math.min(conc, jobs.length) }, async () => {
    while (next < jobs.length) { const j = jobs[next++]; try { results.push(await runOne(j.endpoint, j.input, j)); } catch (e) { fails.push({ name: j.name, error: e.message }); console.error('  ' + e.message); } }
  }));
  console.error(`batch: ${results.length} done, ${fails.length} failed`);
  if (fails.length) { writeFileSync(join(LEDGER_DIR, 'batch-failures.json'), JSON.stringify(fails, null, 2)); process.exitCode = 2; }
}

try {
  if (cmd === 'search') await search(pos.join(' '));
  else if (cmd === 'schema') await schema(pos[0]);
  else if (cmd === 'run') await runOne(pos[0], readInput(flags.input));
  else if (cmd === 'batch') await batch(pos[0]);
  else if (cmd === 'result') await result(pos[0], pos[1]);
  else if (cmd === 'upload') console.log(await upload(pos[0]));
  else if (cmd === 'spend') { const L = ledger().filter(r => r.status === 'submitted'); console.log(`${L.length} jobs, about $${spent().toFixed(2)} spent${budget() != null ? ` of a $${budget().toFixed(2)} budget` : ' (no budget set)'}`); for (const r of L) console.log(`  ${r.at.slice(0, 16)}  $${r.est_usd.toFixed(2)}  ${r.name}  ${r.endpoint}`); }
  else if (cmd === 'budget') { mkdirSync(LEDGER_DIR, { recursive: true }); writeFileSync(join(LEDGER_DIR, 'budget.json'), JSON.stringify({ usd: Number(pos[0]) })); console.log(`budget: $${Number(pos[0]).toFixed(2)} (spent so far $${spent().toFixed(2)})`); }
  else { console.log(readFileSync(new URL(import.meta.url), 'utf8').split('\n').slice(1, 24).map(l => l.replace(/^\/\/ ?/, '')).join('\n')); process.exit(cmd ? 1 : 0); }
} catch (e) { die(e.message); }
