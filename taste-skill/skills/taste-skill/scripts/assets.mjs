#!/usr/bin/env node
// tasteskill / assets: find real, openly licensed pictures of the subject's world, and keep their credits.
//
// A page without photographs of its own does not have to draw everything. Archives, museums and open
// collections hold the subject's city and street, its maps, its materials, its trade's history and the
// museum objects of its kind, free to use with a credit. This searches them without keys and prints what
// an agent needs to use a picture honestly: a direct image URL, the page it comes from, its size, its
// creator, its licence and a one-line credit. Then it downloads the chosen ones into the project and
// records their credits, so the page works offline and credits every picture.
//
//   node assets.mjs "<query>"                     search every source, licences safe for commercial use
//        [--source all|openverse|commons|aic|met|museums]    one or several, comma-separated
//        [--license safe|pd|all|cc0,pd,by,by-sa,...]        safe = CC0, public domain, CC BY, CC BY-SA
//        [--orientation landscape|portrait|square]  [--min-width 1000]  [--width 1920]  [--limit 5]
//        [--no-check]                              skip checking that each image loads (faster)
//        [--json]                                  machine-readable results
//   node assets.mjs --get <ref>[,<ref>...] [--to assets] [--name <file name>] [--width 1920]
//                                                  download into the project and record the credit
//   node assets.mjs --credits [--to assets]        print the credits for the footer and the report
//
// Sources: Openverse (api.openverse.org: Flickr, Wikimedia Commons, museums and libraries in one index),
// Wikimedia Commons, the Art Institute of Chicago (public-domain works over IIIF) and The Metropolitan
// Museum of Art (Open Access). Zero dependencies, no API keys. Node 18+ (built-in fetch).
import { readFileSync, writeFileSync, existsSync, mkdirSync } from 'node:fs';
import { join, resolve, relative } from 'node:path';
import { fileURLToPath } from 'node:url';

const UA = 'taste-skill-assets/2.0 (+https://github.com/Leonxlnx/taste-skill)';
const SELF = fileURLToPath(import.meta.url).split('\\').join('/');
const CMD = `node ${/\s/.test(SELF) ? `"${SELF}"` : SELF}`;
const SOURCES = {
  openverse: { name: 'Openverse', note: 'one index over Flickr, Wikimedia Commons, museums and libraries' },
  commons: { name: 'Wikimedia Commons', note: 'archival photographs, old maps, scans of prints and books, places as they look now' },
  aic: { name: 'Art Institute of Chicago', note: 'public-domain paintings, prints, photographs and textiles, served large' },
  met: { name: 'The Metropolitan Museum of Art', note: 'public-domain objects, prints, drawings and photographs (Open Access)' },
};
const SOURCE_ALIAS = { all: Object.keys(SOURCES), museums: ['aic', 'met'], wikimedia: ['commons'], artic: ['aic'], chicago: ['aic'], metmuseum: ['met'] };
const LICENCES = ['cc0', 'pd', 'by', 'by-sa', 'by-nc', 'by-nd', 'by-nc-sa', 'by-nc-nd', 'other'];
const SAFE = ['cc0', 'pd', 'by', 'by-sa'];
const LICENCE_ALIAS = { pdm: 'pd', 'public-domain': 'pd', publicdomain: 'pd', 'cc-by': 'by', 'cc-by-sa': 'by-sa', 'cc-zero': 'cc0' };
const WEB_TYPES = { 'image/jpeg': 'jpg', 'image/png': 'png', 'image/webp': 'webp', 'image/gif': 'gif', 'image/avif': 'avif', 'image/svg+xml': 'svg' };
const PROVIDERS = { flickr: 'Flickr', wikimedia: 'Wikimedia Commons', met: 'The Metropolitan Museum of Art', nypl: 'New York Public Library', rawpixel: 'rawpixel', stocksnap: 'StockSnap', clevelandmuseum: 'Cleveland Museum of Art', brooklynmuseum: 'Brooklyn Museum', sciencemuseum: 'Science Museum Group', europeana: 'Europeana', geographorguk: 'Geograph Britain and Ireland', inaturalist: 'iNaturalist', wordpress: 'WordPress Photo Directory' };
const AIC_FIELDS = ['id', 'title', 'artist_title', 'artist_display', 'date_display', 'image_id', 'thumbnail', 'medium_display', 'artwork_type_title', 'is_public_domain'];
const AIC_HEADERS = { 'AIC-User-Agent': UA };

const USAGE = `Find real, openly licensed pictures of the subject's world, download them, keep their credits.

  ${CMD} "<query>" [options]
      --source all|openverse|commons|aic|met|museums   comma-separated; default all
      --license safe|pd|all|cc0,pd,by,by-sa,...        default safe: CC0, public domain, CC BY, CC BY-SA
      --orientation landscape|portrait|square
      --min-width <px>       smallest acceptable full width, default 1000
      --width <px>           width of the image URL to use or download, default 1920
      --limit <n>            results per source, default 5 (at most 20)
      --no-check             do not check that every image loads (faster, less reliable)
      --json                 machine-readable results
  ${CMD} --get <ref>[,<ref>...] [--to assets] [--name <file name>] [--width 1920]
  ${CMD} --credits [--to assets]

Queries work best in the subject's own words and a medium: "ghent postcard", "ghent old map", "azulejo tiles",
"botanical engraving fig", "rotterdam harbour 1920", "basalt texture". The museum sources match one or two
words best ("fig", "harbour").`;

// ---------- arguments ----------
const VALUED = new Set(['source', 'sources', 'license', 'licence', 'orientation', 'min-width', 'width', 'limit', 'get', 'to', 'name']);
const FLAGS = new Set(['no-check', 'json', 'credits', 'help']);
const args = {}; const words = [];
const argv = process.argv.slice(2);
for (let i = 0; i < argv.length; i++) {
  const a = argv[i];
  if (a === '-h') { args.help = true; continue; }
  if (!a.startsWith('--')) { words.push(a); continue; }
  const eq = a.indexOf('=');
  const key = a.slice(2, eq === -1 ? undefined : eq);
  if (VALUED.has(key)) {
    const v = eq === -1 ? argv[++i] : a.slice(eq + 1);
    if (v === undefined || v === '' || (eq === -1 && v.startsWith('--'))) fail(`--${key} needs a value.`);
    args[key] = v;
  } else if (FLAGS.has(key)) args[key] = true;
  else fail(`Unknown option --${key}.`);
}
function fail(message) { console.error(`${message}\n\n${USAGE}`); process.exit(2); }
function number(key, def, min, max) {
  if (args[key] === undefined) return def;
  const n = Number(args[key]);
  if (!Number.isFinite(n) || n < min || n > max) fail(`--${key} must be a number from ${min} to ${max}.`);
  return Math.round(n);
}
function pickSources(value) {
  const out = [];
  for (const s of String(value).toLowerCase().split(',').map((x) => x.trim()).filter(Boolean)) {
    const found = SOURCE_ALIAS[s] || (SOURCES[s] ? [s] : null);
    if (!found) fail(`Unknown source "${s}". Sources: ${Object.keys(SOURCES).join(', ')}, museums (aic and met), all.`);
    for (const x of found) if (!out.includes(x)) out.push(x);
  }
  return out.length ? out : Object.keys(SOURCES);
}
function pickLicences(value) {
  const v = String(value).toLowerCase().trim();
  if (v === 'safe') return SAFE;
  if (v === 'pd') return ['cc0', 'pd'];
  if (v === 'all' || v === 'any') return LICENCES;
  const out = v.split(',').map((x) => x.trim()).filter(Boolean).map((x) => LICENCE_ALIAS[x] || x);
  const bad = out.filter((x) => !LICENCES.includes(x));
  if (bad.length || !out.length) fail(`Unknown licence "${bad.join(', ') || v}". Use safe, pd, all, or a list of: ${LICENCES.join(', ')}.`);
  return out;
}
function pickOrientation(value) {
  if (value === undefined) return null;
  const v = String(value).toLowerCase();
  const o = { landscape: 'landscape', wide: 'landscape', horizontal: 'landscape', portrait: 'portrait', tall: 'portrait', vertical: 'portrait', square: 'square' }[v];
  if (!o) fail('--orientation is landscape, portrait or square.');
  return o;
}
const o = {
  sources: pickSources(args.source ?? args.sources ?? 'all'),
  licences: pickLicences(args.license ?? args.licence ?? 'safe'),
  orientation: pickOrientation(args.orientation),
  minWidth: number('min-width', 1000, 0, 20000),
  width: number('width', 1920, 200, 4000),
  limit: number('limit', 5, 1, 20),
  check: !args['no-check'],
  to: resolve(String(args.to || 'assets')),
  toArg: args.to ? ` --to ${args.to}` : '',
};

// ---------- small helpers ----------
const sleep = (ms) => new Promise((r) => setTimeout(r, ms));
const short = (s, n) => { const t = String(s || ''); return t.length > n ? t.slice(0, n - 1).replace(/[\s,;:.-]+$/, '') + '…' : t; };
const noQuery = (u) => (u ? String(u).split('?')[0] : u);
const rel = (p) => relative(process.cwd(), p).split('\\').join('/') || '.';
const size = (bytes) => (bytes >= 1048576 ? `${(bytes / 1048576).toFixed(1)} MB` : `${Math.max(1, Math.round(bytes / 1024))} KB`);
const shape = (w, h) => (!w || !h ? null : w / h >= 1.15 ? 'landscape' : w / h <= 0.87 ? 'portrait' : 'square');
const esc = (s) => String(s ?? '').replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;').replace(/"/g, '&quot;');
function text(v) {
  if (v === undefined || v === null) return '';
  return String(v).replace(/<(style|script)\b[\s\S]*?<\/\1>/gi, ' ').replace(/<[^>]*>/g, ' ').replace(/&nbsp;/g, ' ').replace(/&quot;/g, '"').replace(/&#0?39;|&apos;/g, "'")
    .replace(/&lt;/g, '<').replace(/&gt;/g, '>').replace(/&#(\d+);/g, (_, n) => String.fromCodePoint(Number(n))).replace(/&amp;/g, '&')
    .replace(/\s+/g, ' ').trim();
}
function keyOf(u) { let s = noQuery(u) || ''; try { s = decodeURIComponent(s); } catch {} return s.toLowerCase().replace(/^https?:\/\//, '').replace(/ /g, '_'); }
function slug(s) {
  return String(s || '').normalize('NFKD').replace(/[\u0300-\u036f]/g, '').toLowerCase().replace(/[^a-z0-9]+/g, '-').replace(/^-+|-+$/g, '')
    .split('-').slice(0, 7).join('-').slice(0, 60).replace(/-+$/, '');
}
// The words of a query that carry meaning, and whether a record's own description holds them
// (all of them, or all but one of three or more). Used to keep the museum sources on the subject.
function queryWords(q) { return String(q).toLowerCase().split(/[^\p{L}\p{N}]+/u).filter((w) => w && !['the', 'a', 'an', 'of', 'in', 'on', 'at', 'and', 'or', 'for', 'with', 'from', 'to', 'by'].includes(w)); }
function onSubject(wanted, description) {
  if (!wanted.length) return true;
  const loose = (s) => String(s).toLowerCase().normalize('NFKD').replace(/[̀-ͯ]/g, '').replace(/our\b/g, 'or'); // harbour = harbor
  const hay = loose(description);
  const hits = wanted.filter((w) => { const x = loose(w); return hay.includes(x) || (x.length > 4 && hay.includes(x.replace(/(es|s)$/, ''))); }).length;
  return hits >= (wanted.length >= 3 ? wanted.length - 1 : wanted.length);
}
async function mapLimit(items, n, fn) {
  const out = new Array(items.length); let next = 0;
  await Promise.all(Array.from({ length: Math.min(n, items.length) }, async () => { while (next < items.length) { const k = next++; out[k] = await fn(items[k], k); } }));
  return out;
}
async function getJson(url, ms = 20000, headers = {}) {
  for (let attempt = 1; ; attempt++) {
    let r;
    try { r = await fetch(url, { headers: { 'User-Agent': UA, Accept: 'application/json', ...headers }, signal: AbortSignal.timeout(ms) }); }
    catch (e) {
      const timedOut = e.name === 'TimeoutError' || e.name === 'AbortError';
      if (!timedOut && attempt < 2) { await sleep(800); continue; }
      throw new Error(timedOut ? `no answer within ${Math.round(ms / 1000)} s` : `could not connect (${e.cause?.code || e.message})`);
    }
    if ([502, 503, 504].includes(r.status) && attempt < 2) { await sleep(1200); continue; }
    if (r.status === 429) throw new Error('rate limited (HTTP 429): wait a minute, or search another --source');
    if (r.status === 410) throw new Error('this API endpoint has been retired (HTTP 410); assets.mjs needs updating for it');
    if (!r.ok) throw new Error(`HTTP ${r.status}${r.status >= 500 ? ', the service is having trouble' : ''}`);
    try { return await r.json(); } catch { throw new Error('the answer was not JSON'); }
  }
}
// Width and height from the first bytes of a JPEG, PNG, GIF or WebP file.
function dims(b) {
  if (!b || b.length < 26) return {};
  if (b[0] === 0x89 && b.toString('ascii', 1, 4) === 'PNG') return { w: b.readUInt32BE(16), h: b.readUInt32BE(20) };
  if (b.toString('ascii', 0, 3) === 'GIF') return { w: b.readUInt16LE(6), h: b.readUInt16LE(8) };
  if (b.toString('ascii', 0, 4) === 'RIFF' && b.toString('ascii', 8, 12) === 'WEBP' && b.length >= 30) {
    const f = b.toString('ascii', 12, 16);
    if (f === 'VP8X') return { w: 1 + b.readUIntLE(24, 3), h: 1 + b.readUIntLE(27, 3) };
    if (f === 'VP8L') { const bits = b.readUInt32LE(21); return { w: 1 + (bits & 0x3fff), h: 1 + ((bits >>> 14) & 0x3fff) }; }
    if (f === 'VP8 ') return { w: b.readUInt16LE(26) & 0x3fff, h: b.readUInt16LE(28) & 0x3fff };
  }
  if (b[0] === 0xff && b[1] === 0xd8) {
    let i = 2;
    while (i + 9 < b.length) {
      if (b[i] !== 0xff) { i++; continue; }
      const m = b[i + 1];
      if (m === 0xff) { i++; continue; }
      if (m === 0x01 || (m >= 0xd0 && m <= 0xd8)) { i += 2; continue; }
      if (m >= 0xc0 && m <= 0xcf && m !== 0xc4 && m !== 0xc8 && m !== 0xcc) return { w: b.readUInt16BE(i + 7), h: b.readUInt16BE(i + 5) };
      i += 2 + b.readUInt16BE(i + 2);
    }
  }
  return {};
}
// The Art Institute's image server turns away scripts that do not name themselves in this header.
const imageHeaders = (url) => ({ 'User-Agent': UA, Accept: 'image/*', ...(/^https?:\/\/[^/]*artic\.edu\//.test(url) ? AIC_HEADERS : {}) });
// Does the image load, is it a web image, and how large is it? Reads only the first 128 KB.
async function probe(url, ms = 15000) {
  const ac = new AbortController(); const timer = setTimeout(() => ac.abort(), ms);
  try {
    const r = await fetch(url, { headers: { ...imageHeaders(url), Range: 'bytes=0-131071' }, signal: ac.signal, redirect: 'follow' });
    if (!r.ok) { r.body?.cancel().catch(() => {}); return { ok: false, why: `HTTP ${r.status}` }; }
    const type = (r.headers.get('content-type') || '').split(';')[0].trim().toLowerCase();
    if (!WEB_TYPES[type]) { r.body?.cancel().catch(() => {}); return { ok: false, why: type ? `not a web image (${type})` : 'no content type' }; }
    const reader = r.body.getReader(); const chunks = []; let n = 0;
    while (n < 131072) { const { done, value } = await reader.read(); if (done) break; chunks.push(value); n += value.length; }
    reader.cancel().catch(() => {});
    const bytes = r.status === 206 ? Number((r.headers.get('content-range') || '').split('/')[1]) || null : Number(r.headers.get('content-length')) || null;
    return { ok: true, type, bytes, ...dims(Buffer.concat(chunks)) };
  } catch (e) {
    return { ok: false, why: e.name === 'AbortError' ? 'timed out' : e.cause?.code || e.message };
  } finally { clearTimeout(timer); }
}

// ---------- licences and credits ----------
function licenceLabel(it) {
  if (it.licenseName) return it.licenseName; // set where the plain code would mislead: museums, informal statements, unusual licences
  if (it.license === 'cc0') return 'CC0';
  if (it.license === 'pd') return 'public domain';
  if (it.license === 'other') return 'licence on the source page';
  return `CC ${it.license.toUpperCase()}${it.licenseVersion ? ' ' + it.licenseVersion : ''}`;
}
function licenceUrl(it) {
  if (it.licenseUrl) return String(it.licenseUrl).replace(/^http:/, 'https:');
  if (it.license === 'cc0') return 'https://creativecommons.org/publicdomain/zero/1.0/';
  if (it.license === 'pd') return 'https://creativecommons.org/publicdomain/mark/1.0/';
  if (it.license.startsWith('by')) return `https://creativecommons.org/licenses/${it.license}/${it.licenseVersion || '4.0'}/`;
  return null;
}
const creditRequired = (it) => it.license !== 'cc0' && it.license !== 'pd';
function licenceNotes(it) {
  const n = [];
  if (/-sa$/.test(it.license)) n.push('Share-alike: an altered version (recoloured, combined with other pictures) must be shared under the same licence.');
  if (/-nc/.test(it.license)) n.push('Non-commercial only: not for a business, a shop or a client site.');
  if (/-nd$/.test(it.license)) n.push('No derivatives: show it whole and unaltered, no crops or treatments.');
  if (it.license === 'other') n.push('A licence outside the usual set: read the source page before using it.');
  return n;
}
function credit(it) {
  const by = it.creator && !/^(unknown|anonymous)\b/i.test(it.creator) ? ` by ${short(it.creator, 60)}` : '';
  const date = (it.source === 'aic' || it.source === 'met') && it.date ? `, ${short(it.date, 30)}` : '';
  return `"${short(it.title, 90)}"${by}${date}, ${licenceLabel(it)}, via ${it.via}`;
}
function base(source, id) {
  return { ref: `${source}:${id}`, source, via: SOURCES[source].name, title: '', creator: '', creatorUrl: null, date: null, kind: null, about: null, license: 'other', licenseVersion: null, licenseName: null, licenseUrl: null, page: null, image: null, original: null, smaller: null, width: null, height: null, imageWidth: null, imageHeight: null, bytes: null, alt: null, notes: [], hint: null };
}

// ---------- Openverse ----------
async function searchOpenverse(q, opts) {
  const lic = opts.licences.filter((l) => l !== 'other').map((l) => (l === 'pd' ? 'pdm' : l));
  if (!lic.length) return { total: 0, items: [], note: 'Openverse filters by Creative Commons licences and marks only.' };
  const call = (large) => {
    const p = new URLSearchParams({ q, license: lic.join(','), page_size: '20' });
    if (opts.orientation) p.set('aspect_ratio', { landscape: 'wide', portrait: 'tall', square: 'square' }[opts.orientation]);
    if (large) p.set('size', 'large');
    return getJson(`https://api.openverse.org/v1/images/?${p}`, 30000);
  };
  // Its default order is led by 1024px Flickr files. Ask for the large ones first, and fill up from the rest only if needed.
  const first = await call(true);
  let rows = first.results || []; let total = first.result_count ?? null;
  if (rows.filter((r) => !r.width || r.width >= opts.minWidth).length < opts.limit + 2) {
    const rest = await call(false).catch(() => null);
    if (rest) { total = rest.result_count ?? total; rows = [...rows, ...(rest.results || []).filter((r) => !rows.some((x) => x.id === r.id))]; }
  }
  const items = rows.map(fromOpenverse).filter((it) => it.image);
  await wikimediaSizes(items, opts.width);
  return { total, items };
}
function fromOpenverse(r) {
  const it = base('openverse', r.id);
  const via = r.source || r.provider;
  Object.assign(it, {
    via: PROVIDERS[via] || (String(via || '').startsWith('smithsonian') ? 'Smithsonian' : via ? String(via).replace(/_/g, ' ') : 'Openverse'),
    title: text(r.title).replace(/^File:/, '').replace(/\.(jpe?g|png|tiff?|gif|webp)$/i, '') || 'Untitled', creator: text(r.creator), creatorUrl: r.creator_url || null,
    license: r.license === 'pdm' ? 'pd' : String(r.license || 'other'), licenseVersion: r.license_version || null, licenseUrl: r.license_url || null,
    page: r.foreign_landing_url || r.detail_url, image: r.url, original: r.url,
    width: r.width || null, height: r.height || null, imageWidth: r.width || null, imageHeight: r.height || null,
  });
  if (!LICENCES.includes(it.license)) it.license = 'other';
  return it;
}
// Openverse points at Wikimedia originals, which can be 10 MB or a TIFF. Swap in a web-sized rendition.
async function wikimediaSizes(items, width) {
  const wm = items.filter((it) => /^https?:\/\/upload\.wikimedia\.org\/wikipedia\/commons\/[0-9a-f]\/[0-9a-f]{2}\//.test(it.original || ''));
  if (!wm.length) return;
  const title = (it) => { let n = noQuery(it.original).split('/').pop(); try { n = decodeURIComponent(n); } catch {} return 'File:' + n.replace(/_/g, ' '); };
  const j = await getJson(commonsApi({ titles: wm.map(title).join('|'), prop: 'imageinfo', iiprop: 'url|size|mime', iiurlwidth: String(width) })).catch(() => null);
  if (!j?.query) return;
  const normal = new Map((j.query.normalized || []).map((n) => [n.from, n.to]));
  const info = new Map((j.query.pages || []).map((pg) => [pg.title, pg.imageinfo?.[0]]));
  for (const it of wm) { const t = title(it); const ii = info.get(normal.get(t) || t); if (ii) applyThumb(it, ii); }
}

// ---------- Wikimedia Commons ----------
function commonsApi(params) { return `https://commons.wikimedia.org/w/api.php?${new URLSearchParams({ action: 'query', format: 'json', formatversion: '2', origin: '*', ...params })}`; }
function commonsInfo(width) {
  return { prop: 'imageinfo', iiprop: 'url|size|mime|extmetadata', iiurlwidth: String(width), iiextmetadatalanguage: 'en',
    iiextmetadatafilter: 'ObjectName|Artist|LicenseShortName|License|LicenseUrl|Restrictions|DateTimeOriginal|ImageDescription' };
}
async function searchCommons(q, opts) {
  let s = `${q} filetype:bitmap`;
  if (opts.minWidth > 1) s += ` filew:>${opts.minWidth - 1}`;
  const j = await getJson(commonsApi({ generator: 'search', gsrnamespace: '6', gsrsearch: s, gsrlimit: '30', ...commonsInfo(opts.width) }));
  if (j.error) throw new Error(j.error.info || 'the search failed');
  const pages = (j.query?.pages || []).sort((a, b) => (a.index ?? 0) - (b.index ?? 0));
  return { total: null, items: pages.map(fromCommons).filter(Boolean) };
}
function fromCommons(pg) {
  const ii = pg?.imageinfo?.[0]; if (!ii) return null;
  const m = (k) => text(ii.extmetadata?.[k]?.value);
  const lic = commonsLicence(m('License'), m('LicenseShortName'));
  const it = base('commons', pg.pageid);
  Object.assign(it, {
    title: m('ObjectName').replace(/\s*\b(?:title|label) QS:.*$/s, '') || pg.title.replace(/^File:/, '').replace(/\.[a-z0-9]+$/i, ''), creator: m('Artist'),
    date: m('DateTimeOriginal').replace(/\s*\bdate QS:.*$/s, '').replace(/^(\d{4}-\d{2}-\d{2})[ T]\d{2}:\d{2}.*$/, '$1') || null, about: m('ImageDescription') || null,
    license: lic.code, licenseVersion: lic.version, licenseName: lic.name, licenseUrl: m('LicenseUrl') || null, page: ii.descriptionurl,
  });
  applyThumb(it, ii);
  if (lic.informal) it.notes.push('Not a formal licence: the archive that published it states it knows of no copyright restrictions.');
  if (it.about && it.about.toLowerCase().startsWith(it.title.toLowerCase()) && it.about.length < it.title.length + 12) it.about = null;
  const restrictions = m('Restrictions');
  if (restrictions) it.notes.push(`Restrictions named on the source page (${restrictions}): personality rights, a trademark or similar. Read it before use.`);
  if (/^pd-us/i.test(m('License'))) it.notes.push('Public domain in the United States; check the source page before using it elsewhere.');
  return it;
}
function commonsLicence(license, shortName) {
  const l = String(license || '').toLowerCase(); const s = String(shortName || '').toLowerCase();
  const version = (shortName.match(/\b(\d\.\d)\b/) || l.match(/(\d\.\d)/) || [])[1] || null;
  if (/^cc0|^cc-zero/.test(l) || /^cc0/.test(s)) return { code: 'cc0', version: '1.0' };
  if (/^pd|public domain/.test(l) || /public domain/.test(s)) return { code: 'pd', version: null };
  // Flickr Commons and similar archives: no formal licence, the institution states it knows of no copyright
  if (/^no (known copyright )?restrictions/.test(s)) return { code: 'pd', version: null, name: 'no known copyright restrictions', informal: true };
  const cc = l.match(/^cc-(by(?:-nc)?(?:-sa|-nd)?)(?:-|$)/) || s.match(/^cc (by(?:-nc)?(?:-sa|-nd)?)\b/);
  if (cc) return { code: cc[1], version };
  return { code: 'other', version: null, name: shortName || license || null };
}
// Commons serves thumbnails only at standard widths (1280, 1920, 3840...); the API picks the step.
function applyThumb(it, ii) {
  it.width = ii.width || it.width; it.height = ii.height || it.height; it.original = noQuery(ii.url) || it.original;
  const tw = Number(String(ii.thumburl || '').split('?')[0].match(/(\d+)px-[^/]*$/)?.[1]) || 0;
  if (ii.thumburl && tw && ii.width && (tw < ii.width || (ii.mime && !WEB_TYPES[ii.mime]))) {
    it.image = noQuery(ii.thumburl); it.imageWidth = Math.min(tw, ii.width); it.imageHeight = ii.height ? Math.round((ii.height * it.imageWidth) / ii.width) : null;
  } else { it.image = it.original; it.imageWidth = ii.width || null; it.imageHeight = ii.height || null; }
}

// ---------- Art Institute of Chicago ----------
async function searchAic(q, opts) {
  const wanted = queryWords(q);
  const run = (match) => getJson(`https://api.artic.edu/api/v1/artworks/search?params=${encodeURIComponent(JSON.stringify({
    query: { bool: {
      // the long description field is left out on purpose: it matches almost anything
      must: [{ multi_match: { query: wanted.join(' ') || q, type: 'cross_fields', fields: ['title^3', 'subject_titles^2', 'term_titles^2', 'classification_titles', 'medium_display', 'artist_title', 'place_of_origin', 'date_display'], ...match } }],
      filter: [{ term: { is_public_domain: true } }, { exists: { field: 'image_id' } }],
    } },
    fields: AIC_FIELDS, limit: 30,
  }))}`, 20000, AIC_HEADERS);
  // every word must match; with three words or more, one may be missing. Looser than that returns noise.
  let j = await run({ operator: 'and' });
  if (!(j.data || []).length && wanted.length >= 3) j = await run({ operator: 'or', minimum_should_match: wanted.length - 1 });
  const iiif = j.config?.iiif_url || 'https://www.artic.edu/iiif/2';
  return { total: j.pagination?.total ?? null, items: (j.data || []).map((d) => fromAic(d, iiif, opts.width)).filter(Boolean) };
}
function fromAic(d, iiif, width) {
  if (!d?.image_id || d.is_public_domain === false) return null;
  const it = base('aic', d.id);
  const W = d.thumbnail?.width || null; const H = d.thumbnail?.height || null;
  const cap = W ? Math.min(W, 3000) : 3000; const w = Math.min(width, cap);
  Object.assign(it, {
    title: text(d.title) || 'Untitled', creator: text(d.artist_title) || text(String(d.artist_display || '').split('\n')[0]),
    date: text(d.date_display) || null, kind: [d.artwork_type_title, d.medium_display].filter(Boolean).map(text).join(', ') || null,
    license: 'cc0', licenseVersion: '1.0', licenseName: 'public domain (CC0)', licenseUrl: 'https://creativecommons.org/publicdomain/zero/1.0/',
    page: `https://www.artic.edu/artworks/${d.id}`, image: `${iiif}/${d.image_id}/full/${w},/0/default.jpg`, original: `${iiif}/${d.image_id}/full/${cap},/0/default.jpg`,
    width: W && H ? cap : null, height: W && H ? Math.round((H * cap) / W) : null, imageWidth: W && H ? w : null, imageHeight: W && H ? Math.round((H * w) / W) : null,
    alt: text(d.thumbnail?.alt_text) || null,
  });
  it.hint = 'Download it with --get: the museum\'s image server answers browsers and this script, and refuses plain curl or wget.';
  return it;
}

// ---------- The Met ----------
async function searchMet(q, opts) {
  const s = await getJson(`https://collectionapi.metmuseum.org/public/collection/v1.1/search?${new URLSearchParams({ q, hasImages: 'true', limit: String(Math.min(40, opts.limit * 4 + 8)), offset: '0' })}`);
  const ids = (s.objectIDs || []).slice(0, opts.limit * 4 + 8);
  const objects = await mapLimit(ids, 8, (id) => getJson(`https://collectionapi.metmuseum.org/public/collection/v1/objects/${id}`, 15000).catch(() => null));
  // The museum's search reads every field of a record, so much of what it returns is off the subject.
  // Keep the objects whose own name, material, maker, place or tags carry the words of the query.
  const wanted = queryWords(q);
  const about = (x) => [x.title, x.objectName, x.medium, x.classification, x.culture, x.period, x.artistDisplayName, x.department, x.city, x.country, x.region, x.objectDate, ...(x.tags || []).map((t) => t.term)].filter(Boolean).join(' ');
  return { total: s.total ?? null, items: objects.filter((x) => x && onSubject(wanted, about(x))).map(fromMet).filter(Boolean) };
}
function fromMet(x) {
  if (!x || !x.isPublicDomain || !x.primaryImage) return null;
  const it = base('met', x.objectID);
  const fix = (u) => (u ? encodeURI(u).replace(/%25([0-9a-f]{2})/gi, '%$1') : null);
  Object.assign(it, {
    title: text(x.title) || text(x.objectName) || 'Untitled', creator: text(x.artistDisplayName) || (x.culture ? `${text(x.culture)} maker` : ''),
    date: text(x.objectDate) || null, kind: [x.objectName || x.classification, x.medium].filter(Boolean).map(text).join(', ') || null,
    license: 'cc0', licenseVersion: '1.0', licenseName: 'public domain (CC0)', licenseUrl: 'https://creativecommons.org/publicdomain/zero/1.0/',
    page: x.objectURL || `https://www.metmuseum.org/art/collection/search/${x.objectID}`,
    image: fix(x.primaryImage), original: fix(x.primaryImage), smaller: x.primaryImageSmall && x.primaryImageSmall !== x.primaryImage ? fix(x.primaryImageSmall) : null,
  });
  return it;
}

// ---------- search ----------
function fits(it, opts, skipped) {
  const W = it.width || it.imageWidth; const H = it.height || it.imageHeight;
  if (W && W < opts.minWidth) { skipped.small++; return false; }
  if (opts.orientation && W && H && shape(W, H) !== opts.orientation) { skipped.shape++; return false; }
  return true;
}
async function search(query, opts) {
  const runners = { openverse: searchOpenverse, commons: searchCommons, aic: searchAic, met: searchMet };
  // a slow service never holds the whole search: each source gets 45 s, the image check 30 s
  const deadline = (ms, message) => new Promise((_, reject) => setTimeout(() => reject(new Error(message)), ms).unref());
  const results = await Promise.all(opts.sources.map(async (key) => {
    try { return { key, ...(await Promise.race([runners[key](query, opts), deadline(45000, 'no complete answer within 45 s; try again or search another --source')])) }; }
    catch (e) { return { key, error: e.message, items: [] }; }
  }));
  const seen = new Set();
  for (const r of results) {
    r.skipped = { licence: 0, small: 0, shape: 0, dead: 0, alike: 0 };
    const titles = new Map();
    r.items = r.items.filter((it) => {
      if (!opts.licences.includes(it.license)) { r.skipped.licence++; return false; }
      const k = keyOf(it.original || it.image); if (seen.has(k)) return false; seen.add(k);
      if (!fits(it, opts, r.skipped)) return false;
      // one scanned book can fill a whole page of results: keep two pictures per title
      const t = it.title.toLowerCase().replace(/[^a-z0-9]+/g, ' ').trim().slice(0, 32); const n = (titles.get(t) || 0) + 1; titles.set(t, n);
      if (t && n > 2) { r.skipped.alike++; return false; }
      return true;
    }).slice(0, opts.limit + 4); // a few spares for images that turn out not to load
  }
  if (opts.check) {
    await Promise.race([mapLimit(results.flatMap((r) => r.items), 8, async (it) => {
      const p = await probe(it.image, 12000); it.check = p;
      if (p.ok && p.w && p.h) {
        it.imageWidth = p.w; it.imageHeight = p.h;
        if (!it.width || it.image === it.original) { it.width = p.w; it.height = p.h; }
      }
      if (p.ok && p.bytes) it.bytes = p.bytes;
    }), new Promise((r) => setTimeout(r, 30000).unref())]);
    for (const r of results) r.items = r.items.filter((it) => (it.check?.ok ? fits(it, opts, r.skipped) : (r.skipped.dead++, (r.skipped.why = it.check?.why || 'not checked within 30 s'), false)));
  }
  for (const r of results) r.items = r.items.slice(0, opts.limit);
  const shown = results.reduce((n, r) => n + r.items.length, 0);

  if (args.json) {
    console.log(JSON.stringify({ query, options: { sources: opts.sources, licences: opts.licences, orientation: opts.orientation, minWidth: opts.minWidth, width: opts.width, limit: opts.limit, checked: opts.check },
      sources: results.map((r) => ({ source: r.key, name: SOURCES[r.key].name, total: r.total ?? null, error: r.error || null, skipped: r.skipped,
        items: r.items.map(({ check, ...it }) => ({ ...it, licenseLabel: licenceLabel(it), licenseUrl: licenceUrl(it), creditRequired: creditRequired(it), credit: credit(it), notes: [...it.notes, ...licenceNotes(it)] })) })) }, null, 1));
    return shown ? 0 : 1;
  }

  const filters = [`licences ${opts.licences.join(', ')}`, `at least ${opts.minWidth}px wide`, opts.orientation, `image URLs ${opts.width}px wide where the source can size them`, opts.check ? 'every image checked' : 'images not checked'].filter(Boolean);
  console.log(`ASSETS · "${query}" · ${filters.join(' · ')}`);
  for (const r of results) {
    const src = SOURCES[r.key];
    console.log('');
    if (r.error) { console.log(`## ${src.name}: could not search it (${r.error})`); continue; }
    const dropped = [r.skipped.small && `${r.skipped.small} narrower than ${opts.minWidth}px`, r.skipped.shape && `${r.skipped.shape} not ${opts.orientation}`, r.skipped.licence && `${r.skipped.licence} under other licences`, r.skipped.alike && `${r.skipped.alike} more with the same title`, r.skipped.dead && `${r.skipped.dead} did not load (${r.skipped.why})`].filter(Boolean);
    const count = r.total != null ? `${r.total} matches, ${r.items.length} shown` : `${r.items.length} shown`;
    console.log(`## ${src.name}: ${r.items.length ? count : 'nothing usable'}${dropped.length ? ` (dropped: ${dropped.join(', ')})` : ''}`);
    if (r.note) console.log(r.note);
    if (!r.items.length) continue;
    console.log(`${src.note}`);
    for (const it of r.items) {
      console.log('');
      console.log(`${it.ref}  ${short(it.title, 100)}${it.date ? ` (${short(it.date, 30)})` : ''}`);
      if (it.kind) console.log(`  what     ${short(it.kind, 110)}`);
      if (it.about) console.log(`  about    ${short(it.about, 150)}`);
      const pixels = it.imageWidth && it.imageHeight ? `${it.imageWidth} × ${it.imageHeight}` : 'size unknown';
      const largest = it.width && it.height && it.width !== it.imageWidth ? `; largest ${it.width} × ${it.height}` : '';
      const sh = shape(it.width || it.imageWidth, it.height || it.imageHeight);
      console.log(`  image    ${it.image}`);
      console.log(`  size     ${pixels}${it.bytes ? `, ${size(it.bytes)}` : ''}${largest}${sh ? `; ${sh}` : ''}`);
      if (it.smaller) console.log(`  smaller  ${it.smaller}`);
      console.log(`  page     ${it.page}`);
      const lu = licenceUrl(it);
      console.log(`  licence  ${licenceLabel(it)}${lu ? ` (${lu})` : ''}; ${creditRequired(it) ? 'credit required' : 'no credit required, credit anyway'}`);
      console.log(`  credit   ${credit(it)}`);
      for (const n of [...it.notes, ...licenceNotes(it), ...(it.hint ? [it.hint] : [])]) console.log(`  note     ${n}`);
    }
  }
  console.log('');
  if (results.every((r) => r.error)) {
    console.log('No source could be reached. Check the network and try again; if this machine has no internet access, draw the');
    console.log('pictures instead (references/imagery.md) and say in your report that the open collections could not be searched.');
    return 1;
  }
  if (!shown) {
    console.log('Nothing usable came back. Try fewer words; the place\'s own name for things ("azulejo", not "blue tile"); the place and a');
    console.log('medium ("ghent postcard", "ghent old map", "ghent engraving"); a decade ("rotterdam harbour 1920"); a smaller --min-width;');
    console.log('or another --source. The museum sources match one or two words best ("fig", "harbour"). If nothing honest exists, draw it.');
    return 1;
  }
  console.log('Next. Look before you choose: --get downloads into the project and records the credit; open the file to see it.');
  console.log(`  ${CMD} --get <ref>[,<ref>...]${o.toArg}`);
  console.log(`  ${CMD} --credits${o.toArg}     the footer credit line and the list for your report`);
  console.log('These pictures show the subject\'s world. Never present one as the client\'s own product, room, dish, person or team.');
  return 0;
}

// ---------- get ----------
function creditsPath(opts) { return join(opts.to, 'credits.json'); }
function readCredits(opts) { try { const j = JSON.parse(readFileSync(creditsPath(opts), 'utf8')); return Array.isArray(j) ? j : []; } catch { return []; } }
async function getOne(ref, opts) {
  const m = String(ref).match(/^(openverse|commons|aic|met):(.+)$/);
  if (!m) throw new Error('a ref looks like openverse:<id>, commons:<id>, aic:<id> or met:<id>, as a search prints it.');
  const [, src, id] = m;
  let it;
  if (src === 'openverse') { it = fromOpenverse(await getJson(`https://api.openverse.org/v1/images/${encodeURIComponent(id)}/`, 30000)); await wikimediaSizes([it], opts.width); }
  else if (src === 'commons') { const j = await getJson(commonsApi({ pageids: id, ...commonsInfo(opts.width) })); it = fromCommons(j.query?.pages?.[0]); }
  else if (src === 'aic') { const j = await getJson(`https://api.artic.edu/api/v1/artworks/${encodeURIComponent(id)}?fields=${AIC_FIELDS.join(',')}`, 20000, AIC_HEADERS); it = fromAic(j.data, j.config?.iiif_url || 'https://www.artic.edu/iiif/2', opts.width); }
  else {
    it = fromMet(await getJson(`https://collectionapi.metmuseum.org/public/collection/v1/objects/${encodeURIComponent(id)}`));
    if (it?.smaller) { const s = await probe(it.smaller); if (s.ok && s.w >= opts.width * 0.9) it.image = it.smaller; }
  }
  if (!it || !it.image) throw new Error('no usable image (not public domain, or the record has no picture).');
  if (!opts.licences.includes(it.license)) throw new Error(`its licence is ${licenceLabel(it)}, outside the ones allowed (${opts.licences.join(', ')}). Pass --license all to take it anyway, and say why in your report.`);
  let r;
  try { r = await fetch(it.image, { headers: imageHeaders(it.image), signal: AbortSignal.timeout(90000) }); }
  catch (e) { throw new Error(`the image did not download (${e.name === 'TimeoutError' ? 'timed out' : e.cause?.code || e.message}).`); }
  if (!r.ok) throw new Error(`the image did not load (HTTP ${r.status}).`);
  const type = (r.headers.get('content-type') || '').split(';')[0].trim().toLowerCase();
  const ext = WEB_TYPES[type];
  if (!ext) throw new Error(`the file is ${type || 'of no stated type'}, not a web image.`);
  const buf = Buffer.from(await r.arrayBuffer());
  if (!buf.length) throw new Error('the image was empty.');
  const d = dims(buf);
  mkdirSync(opts.to, { recursive: true });
  const credits = readCredits(opts);
  const stem = slug(args.name || it.title) || `${src}-${slug(id).slice(0, 12)}`;
  let file = join(opts.to, `${stem}.${ext}`);
  for (let k = 2; existsSync(file) && credits.find((c) => c.file === rel(file))?.ref !== it.ref; k++) file = join(opts.to, `${stem}-${k}.${ext}`);
  writeFileSync(file, buf);
  const entry = {
    file: rel(file), ref: it.ref, title: it.title, creator: it.creator || null, creatorUrl: it.creatorUrl, date: it.date,
    license: licenceLabel(it), licenseCode: it.license, licenseUrl: licenceUrl(it), creditRequired: creditRequired(it),
    page: it.page, via: it.via, image: it.image, width: d.w || it.imageWidth, height: d.h || it.imageHeight, bytes: buf.length,
    credit: credit(it), notes: [...it.notes, ...licenceNotes(it)], saved: new Date().toISOString(),
  };
  writeFileSync(creditsPath(opts), JSON.stringify([...credits.filter((c) => c.file !== entry.file), entry], null, 1));
  const alt = it.alt || it.title;
  console.log(`Saved ${entry.file}${entry.width ? ` · ${entry.width} × ${entry.height}` : ''} · ${size(buf.length)}`);
  console.log(`  page     ${it.page}`);
  console.log(`  credit   ${entry.credit}`);
  console.log(`  markup   <img src="${esc(entry.file)}"${entry.width ? ` width="${entry.width}" height="${entry.height}"` : ''} alt="${esc(short(alt, 120))}" loading="lazy" decoding="async">`);
  console.log('           (rewrite the alt to say what the picture shows; drop loading="lazy" on the hero image)');
  for (const n of entry.notes) console.log(`  note     ${n}`);
}
async function getAll(refs, opts) {
  let failed = 0;
  for (const ref of refs) {
    try { await getOne(ref, opts); } catch (e) { failed++; console.error(`Could not get ${ref}: ${e.message}`); }
    console.log('');
  }
  if (failed < refs.length) {
    console.log(`Credits are recorded in ${rel(creditsPath(opts))}. Look at each picture before using it.`);
    console.log(`Print the footer credits and the report list with: ${CMD} --credits${opts.toArg}`);
  }
  return failed ? 1 : 0;
}

// ---------- credits ----------
function printCredits(opts) {
  const list = readCredits(opts);
  const uniq = list.filter((c, i) => list.findIndex((x) => x.ref === c.ref) === i && existsSync(resolve(c.file)));
  if (!uniq.length) { console.log(`No pictures recorded in ${rel(creditsPath(opts))} yet. Download them with --get <ref> first.`); return 1; }
  const html = (c) => {
    const by = c.creator && !/^(unknown|anonymous)\b/i.test(c.creator) ? ` by ${esc(short(c.creator, 60))}` : '';
    const date = /^(aic|met):/.test(c.ref) && c.date ? `, ${esc(short(c.date, 30))}` : '';
    const lic = c.licenseUrl ? `<a href="${esc(c.licenseUrl)}">${esc(c.license)}</a>` : esc(c.license);
    return `<a href="${esc(c.page)}">“${esc(short(c.title, 90))}”</a>${by}${date}, ${lic}, via ${esc(c.via)}`;
  };
  console.log('Footer credits (HTML). Full contrast, keep the links, body size (one step smaller only on a page with plenty of');
  console.log('running text). Remove any picture the page no longer uses, here and in credits.json.\n');
  console.log(`<p class="credits">Pictures: ${uniq.map(html).join('; ')}.</p>`);
  console.log('\nFor your report:\n');
  for (const c of uniq) console.log(`- ${c.file}: ${c.credit}. ${c.page}${c.creditRequired ? '' : ' (no credit required)'}`);
  return 0;
}

// ---------- run ----------
if (args.help) { console.log(USAGE); process.exit(0); }
if (args.credits) process.exit(printCredits(o));
if (args.get) process.exit(await getAll(String(args.get).split(',').map((s) => s.trim()).filter(Boolean), o));
const query = words.join(' ').trim();
if (!query) fail('Give a search query, for example: node assets.mjs "ghent postcard"');
process.exit(await search(query, o));
