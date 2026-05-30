#!/usr/bin/env node
// render_asset.mjs — Render an agent-authored HTML content asset to PNG and/or PDF.
// Deterministic: the host agent authors the styled HTML (report / landing-page / comparison
// / one-pager) with brand tokens injected; this script only screenshots/prints it.
//
// PNG  : full-page screenshot at deviceScaleFactor 2 (crisp text) at a fixed width.
// PDF  : Playwright page.pdf() — print-ready, good for multi-page reports.
//
// Requires Playwright chromium: `npx playwright install chromium` (see SKILL.md).
//
// Usage:
//   node render_asset.mjs --html report.html --png report.png --width 1200
//   node render_asset.mjs --html report.html --pdf report.pdf --pdf-format A4
//   node render_asset.mjs --html one.html --png one.png --pdf one.pdf --width 1080

import { readFileSync } from 'node:fs';
import { pathToFileURL } from 'node:url';
import { resolve, dirname } from 'node:path';

function parseArgs(argv) {
  const a = { width: 1200 };
  for (let i = 0; i < argv.length; i++) {
    const k = argv[i];
    if (k === '--html') a.html = argv[++i];
    else if (k === '--png') a.png = argv[++i];
    else if (k === '--pdf') a.pdf = argv[++i];
    else if (k === '--width') a.width = parseInt(argv[++i], 10);
    else if (k === '--pdf-format') a.pdfFormat = argv[++i];
    else if (k === '--wait') a.wait = parseInt(argv[++i], 10);
    else if (k === '--help' || k === '-h') a.help = true;
  }
  return a;
}

const HELP = `render_asset.mjs — agent-authored HTML asset -> PNG and/or PDF

Required:
  --html <file>     the HTML asset to render
  (at least one of --png / --pdf)

Output:
  --png <file>      full-page PNG screenshot (deviceScaleFactor 2)
  --pdf <file>      print-ready PDF (page.pdf)

Options:
  --width <px>      viewport width for PNG (default 1200; report 1200, one-pager 1080)
  --pdf-format <f>  PDF paper size (A4, Letter, ...) default A4
  --wait <ms>       settle wait after load (default 350)
  -h, --help
`;

async function main() {
  const args = parseArgs(process.argv.slice(2));
  if (args.help) { process.stdout.write(HELP); return; }
  if (!args.html || (!args.png && !args.pdf)) {
    process.stderr.write('ERROR: --html and at least one of --png/--pdf are required.\n' + HELP);
    process.exit(2);
  }

  const htmlPath = resolve(args.html);
  const baseURL = pathToFileURL(dirname(htmlPath) + '/').href;
  const html = readFileSync(htmlPath, 'utf8');

  // Lazy import so --help works before `npx playwright install chromium`.
  const { chromium } = await import('playwright');
  const browser = await chromium.launch();
  try {
    const page = await browser.newPage({ viewport: { width: args.width, height: 1000 }, deviceScaleFactor: 2, baseURL });
    await page.setContent(html, { waitUntil: 'networkidle', baseURL });
    await page.evaluate(async () => {
      if (document.fonts && document.fonts.ready) { try { await document.fonts.ready; } catch (e) {} }
    });
    await page.waitForTimeout(args.wait ?? 350);

    if (args.png) {
      await page.screenshot({ path: resolve(args.png), fullPage: true });
      process.stdout.write(`PNG  -> ${args.png}\n`);
    }
    if (args.pdf) {
      await page.emulateMedia({ media: 'print' });
      await page.pdf({ path: resolve(args.pdf), format: args.pdfFormat ?? 'A4', printBackground: true });
      process.stdout.write(`PDF  -> ${args.pdf}\n`);
    }
  } finally {
    await browser.close();
  }
}

main().catch((err) => { process.stderr.write(`ERROR: ${err.message}\n`); process.exit(1); });
