#!/usr/bin/env node
// render.mjs — Render agent-authored HTML to high-res PNG(s) via Playwright.
//
// Deterministic: it does NOT author copy or HTML (the host agent does that). It loads a
// single HTML file OR a directory of per-slide HTML files, locks the viewport to a
// named/explicit canvas size, AWAITS document.fonts.ready + every <img> decode + a settle
// delay, and writes PNG(s) at deviceScaleFactor 2. Optional combined --pdf.
//
// Canvas sizes are looked up from formats.json (single source of truth) with --width/
// --height override. --help works before Playwright is installed (lazy import).
//
// Requires Playwright chromium: `npx playwright install chromium` (see SKILL.md).
//
// Usage:
//   node render.mjs --html slide.html --out slide.png --format carousel
//   node render.mjs --dir slides/ --out-dir out/ --format slides          # directory mode
//   node render.mjs --html tall.html --out tall.png --format infographic  # full-page auto
//   node render.mjs --html card.html --out card.png --width 1080 --height 1080
//   node render.mjs --dir slides/ --out-dir out/ --format carousel --pdf deck.pdf

import { readFileSync, readdirSync, mkdirSync, existsSync } from 'node:fs';
import { pathToFileURL } from 'node:url';
import { resolve, dirname, join, basename, extname } from 'node:path';
import { fileURLToPath } from 'node:url';

const __dirname = dirname(fileURLToPath(import.meta.url));

function loadFormats() {
  try {
    const raw = readFileSync(join(__dirname, 'formats.json'), 'utf8');
    const j = JSON.parse(raw);
    const out = {};
    for (const [k, v] of Object.entries(j.formats || {})) {
      out[k] = {
        width: v.canvas?.w,
        height: v.canvas?.h,
        fullPage: !!v.full_page,
        multi: !!v.multi_slide,
      };
    }
    return out;
  } catch {
    // Fallback so --help and explicit --width/--height still work if JSON is missing.
    return {
      carousel: { width: 1080, height: 1350, multi: true },
      story: { width: 1080, height: 1920 },
      infographic: { width: 1080, height: 2400, fullPage: true },
      slides: { width: 1920, height: 1080, multi: true },
      poster: { width: 1080, height: 1350 },
      chart: { width: 1080, height: 1080 },
      tweet: { width: 1080, height: 1080 },
    };
  }
}

const FORMATS = loadFormats();

function parseArgs(argv) {
  const a = { fullPage: false };
  for (let i = 0; i < argv.length; i++) {
    const k = argv[i];
    if (k === '--html') a.html = argv[++i];
    else if (k === '--dir') a.dir = argv[++i];
    else if (k === '--out') a.out = argv[++i];
    else if (k === '--out-dir') a.outDir = argv[++i];
    else if (k === '--format') a.format = argv[++i];
    else if (k === '--width') a.width = parseInt(argv[++i], 10);
    else if (k === '--height') a.height = parseInt(argv[++i], 10);
    else if (k === '--full-page') a.fullPage = true;
    else if (k === '--wait') a.wait = parseInt(argv[++i], 10);
    else if (k === '--pdf') a.pdf = argv[++i];
    else if (k === '--help' || k === '-h') a.help = true;
  }
  return a;
}

const HELP = `render.mjs — agent-authored HTML -> high-res PNG(s) (Playwright, deviceScaleFactor 2)

Single file:
  --html <file>     one HTML file to render
  --out  <file.png> output PNG path

Directory (multi-slide carousel/slides — every *.html -> a PNG):
  --dir     <dir>   folder of per-slide HTML files (sorted by name)
  --out-dir <dir>   folder to write PNGs into (named after each HTML file)

Canvas size:
  --format <name>   one of: ${Object.keys(FORMATS).join(', ')} (size from formats.json)
  --width <px> --height <px>   explicit size (overrides --format size)

Options:
  --full-page       capture full scroll height (auto for infographic)
  --wait <ms>       extra settle wait after fonts+images (default 400)
  --pdf <file.pdf>  also emit a combined PDF of all rendered slides (A-Z order)
  -h, --help
`;

function resolveSize(args) {
  let width, height, fullPage = args.fullPage;
  if (args.format) {
    const f = FORMATS[args.format];
    if (!f) {
      process.stderr.write(`ERROR: unknown --format "${args.format}". Allowed: ${Object.keys(FORMATS).join(', ')}\n`);
      process.exit(2);
    }
    width = f.width; height = f.height;
    if (f.fullPage) fullPage = true;
  }
  if (args.width) width = args.width;
  if (args.height) height = args.height;
  if (!width || !height) {
    process.stderr.write('ERROR: provide --format or both --width and --height.\n');
    process.exit(2);
  }
  return { width, height, fullPage };
}

async function main() {
  const args = parseArgs(process.argv.slice(2));
  if (args.help) { process.stdout.write(HELP); return; }

  const dirMode = !!args.dir;
  if (!dirMode && (!args.html || !args.out)) {
    process.stderr.write('ERROR: --html and --out required (or --dir + --out-dir).\n' + HELP);
    process.exit(2);
  }
  if (dirMode && !args.outDir) {
    process.stderr.write('ERROR: --dir requires --out-dir.\n');
    process.exit(2);
  }

  const { width, height, fullPage } = resolveSize(args);

  // Build the work list.
  let jobs = [];
  if (dirMode) {
    if (!existsSync(args.dir)) { process.stderr.write(`ERROR: dir not found: ${args.dir}\n`); process.exit(2); }
    mkdirSync(args.outDir, { recursive: true });
    const files = readdirSync(args.dir).filter((f) => /\.html?$/i.test(f)).sort();
    if (!files.length) { process.stderr.write(`ERROR: no .html files in ${args.dir}\n`); process.exit(2); }
    jobs = files.map((f) => ({
      html: join(args.dir, f),
      out: join(args.outDir, basename(f, extname(f)) + '.png'),
    }));
  } else {
    jobs = [{ html: args.html, out: args.out }];
  }

  // Lazy import so --help works before `npx playwright install chromium`.
  const { chromium } = await import('playwright');
  const browser = await chromium.launch();
  const renderedPng = [];
  try {
    for (const job of jobs) {
      const baseURL = pathToFileURL(dirname(resolve(job.html)) + '/').href;
      const htmlContent = readFileSync(job.html, 'utf8');
      const page = await browser.newPage({ viewport: { width, height }, deviceScaleFactor: 2, baseURL });
      try {
        await page.setContent(htmlContent, { waitUntil: 'networkidle', baseURL });
        await page.evaluate(async () => {
          if (document.fonts && document.fonts.ready) { try { await document.fonts.ready; } catch (e) {} }
          const imgs = Array.from(document.images || []);
          await Promise.all(imgs.map((img) => {
            if (img.complete && img.naturalWidth > 0) return (img.decode ? img.decode().catch(() => {}) : Promise.resolve());
            return new Promise((res) => {
              img.addEventListener('load', () => res(), { once: true });
              img.addEventListener('error', () => res(), { once: true });
            });
          }));
        });
        await page.waitForTimeout(args.wait ?? 400);
        await page.screenshot({ path: resolve(job.out), fullPage });
        renderedPng.push(job.out);
        process.stdout.write(`rendered ${width}x${height}${fullPage ? ' (full-page)' : ''} -> ${job.out}\n`);
      } finally {
        await page.close();
      }
    }

    if (args.pdf) {
      // All slides stacked into one multi-page PDF at the exact canvas size.
      await writeCombinedPdf(args.pdf, jobs, width, height, browser, args.wait);
      process.stdout.write(`pdf -> ${args.pdf}\n`);
    }
  } finally {
    await browser.close();
  }
}

// Combined PDF: render every slide HTML to its own page in ONE Chromium pdf by stacking
// them in a single document. We build a wrapper HTML that @page-sizes each slide and
// page-breaks between them, preserving exact canvas dimensions.
async function writeCombinedPdf(pdfPath, jobs, width, height, browser, waitMs) {
  const sections = jobs.map((job) => {
    const html = readFileSync(job.html, 'utf8');
    // extract <body> inner if present, else use whole doc
    const m = html.match(/<body[^>]*>([\s\S]*?)<\/body>/i);
    const head = (html.match(/<head[^>]*>([\s\S]*?)<\/head>/i) || [,''])[1];
    return { head, body: m ? m[1] : html };
  });
  const headMerged = sections.length ? sections[0].head : '';
  const wrapper = `<!doctype html><html><head>${headMerged}
<style>@page { size: ${width}px ${height}px; margin: 0; }
.gg-page { width:${width}px; height:${height}px; overflow:hidden; page-break-after: always; }
.gg-page:last-child { page-break-after: auto; }</style></head>
<body>${sections.map((s) => `<div class="gg-page">${s.body}</div>`).join('')}</body></html>`;
  const page = await browser.newPage({ viewport: { width, height }, deviceScaleFactor: 2 });
  try {
    await page.setContent(wrapper, { waitUntil: 'networkidle' });
    await page.evaluate(async () => {
      if (document.fonts && document.fonts.ready) { try { await document.fonts.ready; } catch (e) {} }
    });
    await page.waitForTimeout(waitMs ?? 400);
    await page.pdf({ path: resolve(pdfPath), width: `${width}px`, height: `${height}px`, printBackground: true, pageRanges: '' });
  } finally {
    await page.close();
  }
}

main().catch((err) => { process.stderr.write(`ERROR: ${err.message}\n`); process.exit(1); });
