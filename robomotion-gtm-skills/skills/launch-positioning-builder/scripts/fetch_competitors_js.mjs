#!/usr/bin/env node
/**
 * fetch_competitors_js.mjs — Playwright fallback for JS-rendered competitor marketing sites
 * and for review/ad pages that need a real browser. Renders each URL and extracts the same
 * positioning signals as fetch_competitors.py (title, meta description, hero headline/subhead,
 * CTAs, positioning phrases), plus an optional full-page screenshot for the agent to view.
 *
 * Composite glue / deterministic only — no positioning synthesis here.
 *
 * Setup (note in SKILL.md):  npx playwright install chromium
 * Run:
 *   node fetch_competitors_js.mjs --urls https://acme.com https://acme.com/pricing \
 *     --name Acme --output acme.json
 *   node fetch_competitors_js.mjs --urls https://g2.com/products/x/reviews \
 *     --name "Acme reviews" --screenshot reviews.png --output reviews.json
 */
import { writeFileSync } from "node:fs";

function parseArgs(argv) {
  const a = { urls: [], name: "", screenshot: "", output: "-", timeout: 35000 };
  for (let i = 0; i < argv.length; i++) {
    const t = argv[i];
    if (t === "--name") a.name = argv[++i];
    else if (t === "--screenshot") a.screenshot = argv[++i];
    else if (t === "--output") a.output = argv[++i];
    else if (t === "--timeout") a.timeout = parseInt(argv[++i], 10) * 1000;
    else if (t === "--help" || t === "-h") a.help = true;
    else if (t === "--urls") { while (i + 1 < argv.length && !argv[i + 1].startsWith("--")) a.urls.push(argv[++i]); }
  }
  return a;
}

const HELP = `fetch_competitors_js.mjs — render competitor/review/ad pages and extract positioning signals.

  --urls U1 U2 ...     URLs to render (homepage/pricing/about or review/ad pages) [required]
  --name NAME          label for this competitor / page set [required]
  --screenshot PATH    optional full-page screenshot of the FIRST url
  --output PATH        output JSON path (default stdout)
  --timeout SECONDS    per-page nav timeout (default 35)
  --help               this help

Requires: npx playwright install chromium`;

function extractInPage() {
  const POS = [
    /\bthe only\b[^.!?\n]{0,120}/gi,
    /\bthe #?1\b[^.!?\n]{0,120}/gi,
    /\bwe help\b[^.!?\n]{0,120}/gi,
    /\b(?:the )?(?:leading|best|fastest|easiest|most [a-z]+)\b[^.!?\n]{0,120}/gi,
    /\bplatform (?:for|to)\b[^.!?\n]{0,120}/gi,
    /\b(?:all-in-one|end-to-end|purpose-built|built for)\b[^.!?\n]{0,120}/gi,
  ];
  const metaDesc = document.querySelector("meta[name='description']")?.content
    || document.querySelector("meta[property='og:description']")?.content || "";
  const h1 = document.querySelector("h1")?.innerText?.trim() || "";
  const h2 = document.querySelector("h2")?.innerText?.trim() || "";
  const ctas = [];
  document.querySelectorAll("a,button").forEach((el) => {
    const cls = (el.className || "").toString().toLowerCase();
    const isCta = el.tagName === "BUTTON" || /btn|button|cta/.test(cls);
    const txt = (el.innerText || "").trim();
    if (isCta && txt.length >= 2 && txt.length <= 40 && !ctas.includes(txt)) ctas.push(txt);
  });
  const body = (document.body.innerText || "").replace(/\s+/g, " ");
  let raw = [];
  for (const rx of POS) {
    for (const m of body.match(rx) || []) {
      let p = m.replace(/\s+/g, " ").trim();
      if (p.length >= 118 && p.includes(" ")) p = p.slice(0, p.lastIndexOf(" ")).replace(/[,;:\-\s]+$/, "");
      if (p) raw.push(p);
    }
  }
  // dedup + drop substrings of a longer captured phrase
  raw = [...new Set(raw)].sort((a, b) => b.length - a.length);
  const phrases = [];
  for (const p of raw) {
    const pl = p.toLowerCase();
    if (!phrases.some((q) => q.toLowerCase() !== pl && q.toLowerCase().includes(pl))) phrases.push(p);
  }
  return {
    url: location.href,
    title: document.title || "",
    meta_description: metaDesc.trim(),
    hero_headline: h1,
    hero_subhead: h2,
    ctas: ctas.slice(0, 8),
    positioning_phrases: phrases.slice(0, 15),
    body_word_count: (body.match(/[A-Za-z][A-Za-z'\-]*/g) || []).length,
  };
}

async function main() {
  const args = parseArgs(process.argv.slice(2));
  if (args.help || args.urls.length === 0 || !args.name) {
    console.log(HELP);
    process.exit(args.help ? 0 : 1);
  }
  let chromium;
  try { ({ chromium } = await import("playwright")); }
  catch {
    console.error("ERROR: playwright not installed. Run: npm i playwright && npx playwright install chromium");
    process.exit(2);
  }

  const browser = await chromium.launch({ headless: true });
  const ctx = await browser.newContext({
    viewport: { width: 1440, height: 900 },
    userAgent: "robomotion-gtm-skills/launch-positioning-builder (+https://agentskills.io)",
  });
  const pages = [];
  const errors = [];
  let shotDone = false;

  for (const url of args.urls) {
    const page = await ctx.newPage();
    try {
      await page.goto(url, { waitUntil: "networkidle", timeout: args.timeout });
      await page.waitForTimeout(600);
      pages.push(await page.evaluate(extractInPage));
      if (!shotDone && args.screenshot) {
        await page.screenshot({ path: args.screenshot, fullPage: true });
        shotDone = true;
      }
    } catch (e) {
      errors.push({ url, error: String(e.message || e) });
    } finally {
      await page.close();
    }
  }
  await browser.close();

  const out = { competitors: [{ name: args.name, base_url: args.urls[0],
    screenshot: shotDone ? args.screenshot : "", pages, errors, likely_js_rendered: false }] };
  const payload = JSON.stringify(out, null, 2);
  if (args.output === "-") process.stdout.write(payload + "\n");
  else { writeFileSync(args.output, payload + "\n"); console.error(`${pages.length}/${args.urls.length} pages -> ${args.output}`); }
}

main().catch((e) => { console.error("ERROR:", e); process.exit(1); });
