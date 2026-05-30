#!/usr/bin/env node
/**
 * fetch_content_js.mjs — Playwright fallback for JS-rendered / auth-walled blogs that
 * fetch_content.py returns thin text for. Renders each page, strips chrome via DOM
 * evaluation, and emits the SAME corpus JSON shape as fetch_content.py (minus the
 * Python-side readability metrics, which the agent can recompute or which fetch_content.py
 * supplies for the non-JS pages).
 *
 * Deterministic tool only — no voice synthesis here.
 *
 * Setup (note in SKILL.md):  npx playwright install chromium
 * Run:
 *   node fetch_content_js.mjs --company "Acme" --urls https://a https://b --output corpus.json
 */
import { writeFileSync } from "node:fs";

function parseArgs(argv) {
  const a = { company: "", urls: [], numPages: 15, output: "-", timeout: 30000 };
  for (let i = 0; i < argv.length; i++) {
    const t = argv[i];
    if (t === "--company") a.company = argv[++i];
    else if (t === "--num-pages") a.numPages = parseInt(argv[++i], 10);
    else if (t === "--output") a.output = argv[++i];
    else if (t === "--timeout") a.timeout = parseInt(argv[++i], 10) * 1000;
    else if (t === "--help" || t === "-h") a.help = true;
    else if (t === "--urls") { while (i + 1 < argv.length && !argv[i + 1].startsWith("--")) a.urls.push(argv[++i]); }
  }
  return a;
}

const HELP = `fetch_content_js.mjs — Playwright render + clean-text extraction (JS blogs).

  --company NAME       company name (for labeling) [required]
  --urls U1 U2 ...     page URLs to render and extract [required]
  --num-pages N        cap on pages (default 15)
  --timeout SECONDS    per-page nav timeout (default 30)
  --output PATH        output JSON path (default stdout)
  --help               this help

Requires: npx playwright install chromium`;

async function main() {
  const args = parseArgs(process.argv.slice(2));
  if (args.help || !args.company || args.urls.length === 0) {
    console.log(HELP);
    process.exit(args.help ? 0 : 1);
  }

  let chromium;
  try {
    ({ chromium } = await import("playwright"));
  } catch {
    console.error("ERROR: playwright not installed. Run: npm i playwright && npx playwright install chromium");
    process.exit(2);
  }

  const urls = [...new Set(args.urls.map((u) => u.trim()).filter(Boolean))].slice(0, args.numPages);
  const browser = await chromium.launch({ headless: true });
  const ctx = await browser.newContext({
    userAgent: "robomotion-gtm-skills/brand-voice-extractor (+https://agentskills.io)",
  });
  const pages = [];
  const errors = [];

  for (const url of urls) {
    const page = await ctx.newPage();
    try {
      await page.goto(url, { waitUntil: "networkidle", timeout: args.timeout });
      const data = await page.evaluate(() => {
        const SKIP = new Set(["SCRIPT", "STYLE", "NAV", "FOOTER", "HEADER", "ASIDE",
          "FORM", "NOSCRIPT", "SVG", "BUTTON", "SELECT", "IFRAME"]);
        const counts = { h: 0, li: 0, ul_ol: 0, strong_em: 0, blockquote: 0, a: 0, img: 0 };
        const root = document.querySelector("main, article") || document.body;
        const walk = (node, out) => {
          if (node.nodeType === 3) { const t = node.textContent.trim(); if (t) out.push(t); return; }
          if (node.nodeType !== 1 || SKIP.has(node.tagName)) return;
          const tag = node.tagName;
          if (/^H[1-6]$/.test(tag)) counts.h++;
          else if (tag === "LI") counts.li++;
          else if (tag === "UL" || tag === "OL") counts.ul_ol++;
          else if (["STRONG", "B", "EM", "I"].includes(tag)) counts.strong_em++;
          else if (tag === "BLOCKQUOTE") counts.blockquote++;
          else if (tag === "A") counts.a++;
          else if (tag === "IMG") counts.img++;
          const block = ["P", "DIV", "SECTION", "ARTICLE", "LI", "BR", "TR", "BLOCKQUOTE",
            "H1", "H2", "H3", "H4", "H5", "H6"].includes(tag);
          if (block) out.push("\n");
          for (const c of node.childNodes) walk(c, out);
          if (block) out.push("\n");
        };
        const out = [];
        walk(root, out);
        const text = out.join(" ").split("\n").map((l) => l.replace(/[ \t]+/g, " ").trim())
          .filter(Boolean).join("\n");
        return { title: document.title || "", text, counts };
      });
      const wc = (data.text.match(/[A-Za-z][A-Za-z'\-]*/g) || []).length;
      pages.push({ url, title: data.title.trim(), word_count: wc, text: data.text,
        metrics: { word_count: wc, ...data.counts } });
    } catch (e) {
      errors.push({ url, error: String(e.message || e) });
    } finally {
      await page.close();
    }
  }

  await browser.close();
  const out = {
    company: args.company,
    pages_requested: urls.length,
    pages_fetched: pages.length,
    corpus_metrics: { total_words: pages.reduce((s, p) => s + p.word_count, 0) },
    pages,
    errors,
    note: "JS-rendered fetch: readability metrics not computed here; agent recomputes if needed.",
  };
  const payload = JSON.stringify(out, null, 2);
  if (args.output === "-") process.stdout.write(payload + "\n");
  else { writeFileSync(args.output, payload + "\n"); console.error(`${pages.length}/${urls.length} pages -> ${args.output}`); }
}

main().catch((e) => { console.error("ERROR:", e); process.exit(1); });
