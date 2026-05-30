#!/usr/bin/env node
// render.mjs — Screenshot an agent-authored workflow-diagram HTML to a PNG.
// Deterministic: parse_workflow.py builds the node model; the host agent authors the
// styled HTML+SVG (node cards, arrows, branch labels) from it; this script screenshots it
// at the chosen canvas size, deviceScaleFactor 2.
//
// Requires Playwright chromium: `npx playwright install chromium` (see SKILL.md).
//
// Usage:
//   node render.mjs --html diagram.html --out diagram.png --size landscape
//   node render.mjs --html diagram.html --out diagram.png --width 1080 --height 1080

import { readFileSync } from 'node:fs';
import { pathToFileURL } from 'node:url';
import { resolve, dirname } from 'node:path';

const SIZES = {
  landscape: { width: 1920, height: 1080 },
  square:    { width: 1080, height: 1080 },
  wide:      { width: 1200, height: 630 },
};

function parseArgs(argv) {
  const a = {};
  for (let i = 0; i < argv.length; i++) {
    const k = argv[i];
    if (k === '--html') a.html = argv[++i];
    else if (k === '--out') a.out = argv[++i];
    else if (k === '--size') a.size = argv[++i];
    else if (k === '--width') a.width = parseInt(argv[++i], 10);
    else if (k === '--height') a.height = parseInt(argv[++i], 10);
    else if (k === '--wait') a.wait = parseInt(argv[++i], 10);
    else if (k === '--help' || k === '-h') a.help = true;
  }
  return a;
}

const HELP = `render.mjs — workflow-diagram HTML -> PNG (Playwright, deviceScaleFactor 2)

Required:
  --html <file>     agent-authored diagram HTML
  --out  <file.png> output PNG

Canvas size (pick one):
  --size <name>     ${Object.keys(SIZES).join(' | ')}
  --width <px> --height <px>   explicit override

Options:
  --wait <ms>       settle wait after load (default 400)
  -h, --help
`;

async function main() {
  const args = parseArgs(process.argv.slice(2));
  if (args.help) { process.stdout.write(HELP); return; }
  if (!args.html || !args.out) {
    process.stderr.write('ERROR: --html and --out are required.\n' + HELP);
    process.exit(2);
  }
  let width, height;
  if (args.size) {
    const s = SIZES[args.size];
    if (!s) { process.stderr.write(`ERROR: unknown --size "${args.size}". Allowed: ${Object.keys(SIZES).join(', ')}\n`); process.exit(2); }
    width = s.width; height = s.height;
  }
  if (args.width) width = args.width;
  if (args.height) height = args.height;
  if (!width || !height) { width = SIZES.landscape.width; height = SIZES.landscape.height; }

  const htmlPath = resolve(args.html);
  const baseURL = pathToFileURL(dirname(htmlPath) + '/').href;
  const html = readFileSync(htmlPath, 'utf8');

  // Lazy import so --help works before `npx playwright install chromium`.
  const { chromium } = await import('playwright');
  const browser = await chromium.launch();
  try {
    const page = await browser.newPage({ viewport: { width, height }, deviceScaleFactor: 2, baseURL });
    await page.setContent(html, { waitUntil: 'networkidle', baseURL });
    await page.evaluate(async () => {
      if (document.fonts && document.fonts.ready) { try { await document.fonts.ready; } catch (e) {} }
    });
    await page.waitForTimeout(args.wait ?? 400);
    await page.screenshot({ path: resolve(args.out) });
    process.stdout.write(`rendered ${width}x${height} -> ${args.out}\n`);
  } finally {
    await browser.close();
  }
}

main().catch((err) => { process.stderr.write(`ERROR: ${err.message}\n`); process.exit(1); });
