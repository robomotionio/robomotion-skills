#!/usr/bin/env node
// fetch_page.mjs — KEYLESS default path: render a JS/anti-bot review page with Playwright
// and dump its visible text (no API key). Expect partial coverage and possible blocks on
// the most hostile sites; set APIFY_API_TOKEN and use scrape_reviews.py for full, reliable
// extraction (the optional paid upgrade).
//
// Deterministic I/O only — no LLM. The host agent parses the dumped text for review themes.
//
// Setup:  cd ${SKILL_DIR}/scripts && npm install && npx playwright install chromium
// Run:    node fetch_page.mjs --url "https://www.g2.com/products/x/reviews" [--out page.txt]
//         optional: --proxy "http://user:pass@host:port"  (Robomotion Proxy / residential)

import { chromium } from "playwright";
import { writeFileSync } from "node:fs";

function arg(name, def = undefined) {
  const i = process.argv.indexOf(`--${name}`);
  return i !== -1 && i + 1 < process.argv.length ? process.argv[i + 1] : def;
}

const url = arg("url");
if (!url) {
  console.error("ERROR: --url is required");
  process.exit(2);
}
const out = arg("out");
const proxy = arg("proxy");

const launchOpts = { headless: true };
if (proxy) launchOpts.proxy = { server: proxy };

const browser = await chromium.launch(launchOpts);
try {
  const ctx = await browser.newContext({
    userAgent:
      "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120 Safari/537.36",
  });
  const page = await ctx.newPage();
  await page.goto(url, { waitUntil: "networkidle", timeout: 60000 });
  // scroll to trigger lazy-loaded reviews
  for (let i = 0; i < 6; i++) {
    await page.mouse.wheel(0, 4000);
    await page.waitForTimeout(800);
  }
  const text = await page.evaluate(() => {
    for (const el of document.querySelectorAll("script,style,noscript")) el.remove();
    return document.body ? document.body.innerText : "";
  });
  const cleaned = text.replace(/\n{3,}/g, "\n\n").trim();
  if (out) {
    writeFileSync(out, cleaned + "\n");
    console.error(`${cleaned.length} chars -> ${out}`);
  } else {
    process.stdout.write(cleaned + "\n");
  }
} catch (e) {
  console.error(`ERROR: ${e.message}`);
  process.exitCode = 1;
} finally {
  await browser.close();
}
