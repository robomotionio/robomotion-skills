#!/usr/bin/env node
// render_page.mjs — Render a JS-heavy page with Playwright and emit structured text.
//
// Deterministic fallback for fetch_pages.py when a marketing / review / ad-library page
// renders its content client-side (G2, Capterra, SimilarWeb, Meta Ad Library, Google Ads
// Transparency Center, JS-built marketing sites). No LLM — just navigate, wait, extract.
//
// Requires Playwright chromium:  npx playwright install chromium
//
// Usage:
//   node render_page.mjs --url https://www.g2.com/products/<x>/reviews [--output out.json]
//   node render_page.mjs --url <u> --wait 5000 --selector "[itemprop='review']" --screenshot shot.png
import { writeFileSync } from 'node:fs';

function parseArgs(argv) {
  const a = { url: [], wait: 4000, selector: '', output: '-', screenshot: '', timeout: 45000 };
  for (let i = 2; i < argv.length; i++) {
    const k = argv[i];
    if (k === '--url') { while (argv[i + 1] && !argv[i + 1].startsWith('--')) a.url.push(argv[++i]); }
    else if (k === '--wait') a.wait = parseInt(argv[++i], 10);
    else if (k === '--selector') a.selector = argv[++i];
    else if (k === '--output') a.output = argv[++i];
    else if (k === '--screenshot') a.screenshot = argv[++i];
    else if (k === '--timeout') a.timeout = parseInt(argv[++i], 10);
    else if (k === '--help' || k === '-h') a.help = true;
  }
  return a;
}

const HELP = `render_page.mjs — Playwright renderer for JS-heavy pages (keyless).
  --url <u...>      one or more URLs to render (required)
  --wait <ms>       extra settle wait after networkidle (default 4000)
  --selector <css>  optional: also return outerHTML + count of matching nodes
  --screenshot <p>  optional PNG path (only for a single --url)
  --timeout <ms>    per-page nav timeout (default 45000)
  --output <p>      JSON output path (default stdout)`;

async function extractOne(page, url, a) {
  await page.goto(url, { waitUntil: 'domcontentloaded', timeout: a.timeout });
  try { await page.waitForLoadState('networkidle', { timeout: a.timeout }); } catch { /* keep going */ }
  if (a.wait > 0) await page.waitForTimeout(a.wait);

  const data = await page.evaluate((sel) => {
    const clean = (s) => (s || '').replace(/\s+/g, ' ').trim();
    const txtAll = (q) => Array.from(document.querySelectorAll(q)).map(e => clean(e.textContent)).filter(Boolean);
    const meta = (n) => { const m = document.querySelector(`meta[name='${n}'],meta[property='${n}']`); return m ? m.content : ''; };
    let selected = null;
    if (sel) {
      const nodes = Array.from(document.querySelectorAll(sel));
      selected = { count: nodes.length, text: nodes.slice(0, 80).map(e => clean(e.textContent)).filter(Boolean) };
    }
    return {
      title: document.title || '',
      meta_description: meta('description') || meta('og:description'),
      headings: txtAll('h1,h2,h3').slice(0, 80),
      paragraphs: txtAll('p').slice(0, 150),
      list_items: txtAll('li').slice(0, 200),
      body_text_chars: clean(document.body ? document.body.innerText : '').length,
      selected,
    };
  }, a.selector);

  if (a.screenshot && a.url.length === 1) {
    await page.screenshot({ path: a.screenshot, fullPage: true });
    data.screenshot = a.screenshot;
  }
  data.url = url;
  return data;
}

async function main() {
  const a = parseArgs(process.argv);
  if (a.help || a.url.length === 0) { console.log(HELP); process.exit(a.help ? 0 : 1); }

  let chromium;
  try {
    ({ chromium } = await import('playwright'));
  } catch {
    console.error("ERROR: playwright not installed. Run: npx playwright install chromium && npm i playwright");
    process.exit(2);
  }
  const browser = await chromium.launch({ headless: true });
  const ctx = await browser.newContext({
    userAgent: 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0 Safari/537.36',
    locale: 'en-US',
    viewport: { width: 1366, height: 900 },
  });
  const results = [];
  for (const url of a.url) {
    const page = await ctx.newPage();
    try {
      results.push(await extractOne(page, url, a));
    } catch (e) {
      results.push({ url, error: String(e && e.message || e), body_text_chars: 0 });
    } finally {
      await page.close();
    }
  }
  await browser.close();

  const out = JSON.stringify(results, null, 2);
  if (a.output === '-') process.stdout.write(out + '\n');
  else { writeFileSync(a.output, out + '\n'); process.stderr.write(`${results.length} page(s) -> ${a.output}\n`); }
}

main().catch((e) => { console.error(e); process.exit(1); });
