#!/usr/bin/env node
// detect_requests.mjs — Rendered-request tech detector (keyless detection signal #3).
//
// The most reliable modern method: load the page in a real browser, intercept EVERY
// network request, collect all third-party request hostnames, and map them to vendors
// via signatures.json (request_domains). Also evaluate known window globals
// (dataLayer, analytics, Intercom, _hsq, Munchkin, fbq, ttq, ...) for tools that load
// via a tag manager and never appear in raw HTML source.
//
// Lazy import('playwright') — degrades cleanly if not installed.
// Requires Playwright chromium:  npx playwright install chromium
//
// Usage:
//   node detect_requests.mjs --url https://example.com [--wait 5000] [--output out.json]
import { readFileSync, writeFileSync } from 'node:fs';
import { fileURLToPath } from 'node:url';
import { dirname, join } from 'node:path';

const __dirname = dirname(fileURLToPath(import.meta.url));

function parseArgs(argv) {
  const a = { url: '', wait: 5000, timeout: 45000, output: '-',
              signatures: join(__dirname, 'signatures.json') };
  for (let i = 2; i < argv.length; i++) {
    const k = argv[i];
    if (k === '--url') a.url = argv[++i];
    else if (k === '--wait') a.wait = parseInt(argv[++i], 10);
    else if (k === '--timeout') a.timeout = parseInt(argv[++i], 10);
    else if (k === '--signatures') a.signatures = argv[++i];
    else if (k === '--output') a.output = argv[++i];
    else if (k === '--help' || k === '-h') a.help = true;
  }
  return a;
}

const HELP = `detect_requests.mjs — rendered third-party-request tech detector (keyless).
  --url <u>          page URL to load (required)
  --wait <ms>        settle wait after networkidle (default 5000)
  --timeout <ms>     nav timeout (default 45000)
  --signatures <p>   signatures.json path (default: bundled)
  --output <p>       JSON output path (default stdout)
Requires: npx playwright install chromium`;

// confidence per signal, mirrors sigdb.py weights
const W = { request_domain: 0.55, global_js: 0.5, id_pattern: 0.6 };
function conf(signals) {
  let pMiss = 1.0;
  for (const s of signals) pMiss *= (1.0 - (W[s] || 0.3));
  return Math.round((1.0 - pMiss) * 100) / 100;
}

function registrableHost(h) {
  // crude eTLD+1 for first-party comparison (handles common 2-level TLDs)
  const parts = h.split('.');
  const two = new Set(['co.uk', 'com.au', 'co.jp', 'com.br', 'co.in', 'co.nz', 'com.mx']);
  if (parts.length >= 3 && two.has(parts.slice(-2).join('.'))) return parts.slice(-3).join('.');
  return parts.slice(-2).join('.');
}

async function main() {
  const a = parseArgs(process.argv);
  if (a.help || !a.url) { console.log(HELP); process.exit(a.help ? 0 : 1); }

  const techs = JSON.parse(readFileSync(a.signatures, 'utf-8')).technologies;

  // build globals index: window var -> [tech]
  const globalsIdx = {};
  for (const t of techs) {
    for (const g of (t.detection?.global_js_vars || [])) {
      (globalsIdx[g] ||= []).push(t);
    }
  }

  // build id-pattern index: tech -> {label, regexes[]} for account/pixel-ID extraction.
  // Patterns are case-SENSITIVE (IDs are case-sensitive); each has exactly one capture group.
  const idIdx = [];
  for (const t of techs) {
    const spec = t.detection?.id_pattern;
    if (!spec || !Array.isArray(spec.patterns)) continue;
    const regexes = [];
    for (const p of spec.patterns) {
      try { regexes.push(new RegExp(p, 'g')); } catch { /* skip bad regex */ }
    }
    if (regexes.length) idIdx.push({ name: t.name, label: spec.label || 'account ID', regexes });
  }

  function extractIds(corpus) {
    // returns { techName: { label, ids[] } }
    const out = {};
    for (const e of idIdx) {
      const ids = [];
      for (const rx of e.regexes) {
        rx.lastIndex = 0;
        let m;
        while ((m = rx.exec(corpus)) !== null) {
          if (m[1] && !ids.includes(m[1])) ids.push(m[1]);
          if (m.index === rx.lastIndex) rx.lastIndex++; // avoid zero-width loop
          if (ids.length >= 8) break;
        }
      }
      if (ids.length) out[e.name] = { label: e.label, ids };
    }
    return out;
  }

  let chromium;
  try {
    ({ chromium } = await import('playwright'));
  } catch {
    const out = { url: a.url, error: 'playwright not installed',
      hint: 'npx playwright install chromium && npm i playwright',
      detected: [], third_party_domains: [] };
    process.stdout.write(JSON.stringify(out, null, 2) + '\n');
    process.exit(2);
  }

  const browser = await chromium.launch({ headless: true });
  const ctx = await browser.newContext({
    userAgent: 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0 Safari/537.36',
    locale: 'en-US', viewport: { width: 1366, height: 900 },
  });
  const page = await ctx.newPage();

  const allHosts = new Set();
  const requestUrls = [];
  page.on('request', (req) => {
    try {
      const u = req.url();
      allHosts.add(new URL(u).hostname.toLowerCase());
      if (requestUrls.length < 4000) requestUrls.push(u);
    } catch { /* ignore */ }
  });

  let navError = '';
  let finalUrl = a.url;
  try {
    await page.goto(a.url, { waitUntil: 'domcontentloaded', timeout: a.timeout });
    try { await page.waitForLoadState('networkidle', { timeout: a.timeout }); } catch { /* keep going */ }
    if (a.wait > 0) await page.waitForTimeout(a.wait);
    finalUrl = page.url();
  } catch (e) {
    navError = String((e && e.message) || e);
  }

  // probe window globals
  const globalNames = Object.keys(globalsIdx);
  let presentGlobals = [];
  try {
    presentGlobals = await page.evaluate((names) => {
      const out = [];
      for (const n of names) {
        try {
          const v = window[n];
          if (typeof v !== 'undefined' && v !== null) out.push(n);
        } catch { /* cross-origin / blocked */ }
      }
      return out;
    }, globalNames);
  } catch { /* page may have failed to load */ }

  // capture rendered HTML (inline scripts carry many account/pixel IDs)
  let renderedHtml = '';
  try { renderedHtml = await page.content(); } catch { /* ignore */ }

  await browser.close();

  // account/pixel-ID extraction: rendered HTML + observed request URLs
  const idCorpus = renderedHtml + '\n' + requestUrls.join('\n');
  const idMap = extractIds(idCorpus);

  // classify first vs third party
  let firstParty = '';
  try { firstParty = registrableHost(new URL(finalUrl).hostname.toLowerCase()); } catch { /* ignore */ }
  const thirdPartyHosts = [...allHosts].filter((h) => registrableHost(h) !== firstParty).sort();

  // map request domains -> vendors
  const byName = {};
  for (const t of techs) {
    const rds = t.detection?.request_domains || [];
    if (!rds.length) continue;
    const ev = [];
    for (const rd of rds) {
      const hit = [...allHosts].find((h) => h.includes(rd.toLowerCase()));
      if (hit) ev.push(`request:${rd} (${hit})`);
    }
    if (ev.length) {
      byName[t.name] = { name: t.name, category: t.category, signals: new Set(['request_domain']),
        evidence: ev.slice(0, 6), gtm_implication: t.gtm_implication || '' };
    }
  }
  // map window globals -> vendors
  for (const g of presentGlobals) {
    for (const t of (globalsIdx[g] || [])) {
      const rec = byName[t.name] ||= { name: t.name, category: t.category,
        signals: new Set(), evidence: [], gtm_implication: t.gtm_implication || '' };
      rec.signals.add('global_js');
      if (rec.evidence.length < 6) rec.evidence.push(`window.${g}`);
    }
  }

  // an id_pattern that matched is itself strong evidence the tech is present —
  // surface those techs even if no request_domain/global signal fired.
  for (const [name, info] of Object.entries(idMap)) {
    if (!byName[name]) {
      const t = techs.find((x) => x.name === name);
      byName[name] = { name, category: t ? t.category : 'unknown',
        signals: new Set(['id_pattern']), evidence: [], gtm_implication: t ? (t.gtm_implication || '') : '' };
    }
  }

  const detected = Object.values(byName).map((r) => {
    const rec = {
      name: r.name, category: r.category, confidence: conf([...r.signals]),
      signals: [...r.signals].sort(), evidence: r.evidence, gtm_implication: r.gtm_implication,
    };
    const info = idMap[r.name];
    if (info && info.ids.length) {
      rec.account_id = info.ids[0];
      rec.account_ids = info.ids;
      rec.id_label = info.label;
      if (rec.evidence.length < 6) rec.evidence.push(`id:${info.ids[0]}`);
    }
    return rec;
  }).sort((x, y) => (y.confidence - x.confidence) || x.category.localeCompare(y.category) || x.name.localeCompare(y.name));

  const accountIds = {};
  for (const [name, info] of Object.entries(idMap)) accountIds[name] = info.ids;

  const result = {
    url: a.url, final_url: finalUrl, first_party: firstParty,
    error: navError || undefined,
    third_party_domains: thirdPartyHosts,
    window_globals_present: presentGlobals.sort(),
    account_ids: accountIds,
    detected,
    stats: { total_request_hosts: allHosts.size, third_party_hosts: thirdPartyHosts.length,
      tools_detected: detected.length },
  };
  const out = JSON.stringify(result, null, 2);
  if (a.output === '-') process.stdout.write(out + '\n');
  else { writeFileSync(a.output, out + '\n'); process.stderr.write(`rendered ${a.url} -> ${a.output} (${detected.length} detected)\n`); }
}

main().catch((e) => { console.error(e); process.exit(1); });
