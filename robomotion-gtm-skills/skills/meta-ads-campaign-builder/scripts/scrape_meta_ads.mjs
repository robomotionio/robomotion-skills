#!/usr/bin/env node
/**
 * scrape_meta_ads.mjs — Scrape a competitor's active ads from the Meta Ad Library
 * (https://www.facebook.com/ads/library). Drives headless Chromium via Playwright,
 * because the Library is a heavy JS SPA with active anti-scraping.
 *
 * Deterministic: scrape + parse only — no LLM. The host agent does hook clustering,
 * funnel inference, and the teardown narrative (see ../SKILL.md).
 *
 * Auth: none (the Ad Library is public). Optional --proxy (Robomotion Proxy) to dodge
 * IP blocks and set the country the inventory is fetched for.
 *
 * Usage:
 *   node scrape_meta_ads.mjs --query "Notion" --country US --max-ads 60 --output meta_ads.json
 *   node scrape_meta_ads.mjs --query "Asana" --output summary
 *
 * Requires:  npx playwright install chromium
 */
import fs from "node:fs";

// Lazy so --help works before `npm install` / `npx playwright install chromium`.
async function getChromium() {
  const { chromium } = await import("playwright");
  return chromium;
}

function parseArgs(argv) {
  const a = {
    query: "",
    country: "US",
    maxAds: 60,
    output: "json",
    proxy: process.env.HTTPS_PROXY || process.env.HTTP_PROXY || "",
    timeout: 45000,
  };
  for (let i = 2; i < argv.length; i++) {
    const k = argv[i], v = argv[i + 1];
    switch (k) {
      case "--query": a.query = v; i++; break;
      case "--country": a.country = (v || "US").toUpperCase(); i++; break;
      case "--max-ads": a.maxAds = parseInt(v, 10) || 60; i++; break;
      case "--output": a.output = v; i++; break;
      case "--proxy": a.proxy = v; i++; break;
      case "--timeout": a.timeout = parseInt(v, 10) || 45000; i++; break;
      case "-h": case "--help": a.help = true; break;
    }
  }
  return a;
}

const HELP = `scrape_meta_ads.mjs — scrape active ads from the Meta Ad Library.

Options:
  --query <name>   advertiser / page name to search (required)
  --country <cc>   library country (default US); inventory is region-specific
  --max-ads <n>    cap on ads returned (default 60)
  --output <fmt>   json | summary | <path.json> (default json to stdout)
  --proxy <url>    proxy URL (else HTTPS_PROXY env); helps dodge IP blocks
  --timeout <ms>   per-navigation timeout (default 45000)
  -h, --help       this help`;

async function launch(proxy) {
  const chromium = await getChromium();
  const opts = { headless: true, args: ["--no-sandbox", "--disable-blink-features=AutomationControlled"] };
  if (proxy) opts.proxy = { server: proxy };
  return chromium.launch(opts);
}

async function dismissConsent(page) {
  // Meta shows a cookie/consent dialog; try a few common buttons.
  for (const sel of [
    '[data-cookiebanner="accept_button"]',
    '[aria-label="Allow all cookies"]',
    '[title="Allow all cookies"]',
    'button[title="Only allow essential cookies"]',
  ]) {
    try {
      const el = await page.$(sel);
      if (el) { await el.click({ timeout: 2000 }); await page.waitForTimeout(800); break; }
    } catch { /* ignore */ }
  }
}

async function scrape(page, query, country, maxAds, timeout) {
  const url =
    `https://www.facebook.com/ads/library/?active_status=active&ad_type=all` +
    `&country=${encodeURIComponent(country)}&q=${encodeURIComponent(query)}&search_type=keyword_unordered`;
  await page.goto(url, { waitUntil: "domcontentloaded", timeout });
  await page.waitForTimeout(4000);
  await dismissConsent(page);
  await page.waitForTimeout(2000);

  // Lazy-scroll to load result cards.
  let last = -1;
  for (let i = 0; i < 40; i++) {
    const n = await page.evaluate(() => {
      // Library cards contain a "Library ID" string; count those blocks.
      const blocks = Array.from(document.querySelectorAll('div')).filter((d) =>
        /Library ID/i.test(d.textContent || "") && d.querySelectorAll("div").length < 40
      );
      return blocks.length;
    });
    if (n >= maxAds || n === last) break;
    last = n;
    await page.evaluate(() => window.scrollTo(0, document.body.scrollHeight));
    await page.waitForTimeout(1600);
  }

  return page.evaluate(() => {
    const out = [];
    const seen = new Set();
    const blocks = Array.from(document.querySelectorAll("div")).filter((d) =>
      /Library ID/i.test(d.textContent || "") && d.querySelectorAll("div").length < 40
    );
    for (const b of blocks) {
      const txt = (b.textContent || "").replace(/\s+/g, " ").trim();
      const idm = txt.match(/Library ID[:\s]*([0-9]+)/i);
      const id = idm ? idm[1] : "";
      if (id && seen.has(id)) continue;
      if (id) seen.add(id);
      const startm = txt.match(/Started running on ([A-Za-z]+ \d{1,2},? \d{4})/i);
      const platformsm = txt.match(/Platforms\s*([A-Za-z, ]+)/i);
      const img = b.querySelector("img");
      const video = b.querySelector("video");
      const link = b.querySelector('a[href*="l.facebook.com"], a[href^="http"]:not([href*="facebook.com/ads"])');
      let cta = "";
      // CTA buttons in cards are typically short role=button spans.
      const btns = Array.from(b.querySelectorAll('[role="button"], a[role="button"]'))
        .map((x) => (x.textContent || "").trim())
        .filter((t) => t && t.length <= 24 && !/See ad details|See summary/i.test(t));
      if (btns.length) cta = btns[btns.length - 1];
      out.push({
        libraryId: id,
        visualType: video ? "VIDEO" : img ? "IMAGE" : "TEXT",
        adText: txt.slice(0, 800),
        cta,
        landingUrl: link ? link.href : "",
        startDate: startm ? startm[1] : "",
        platforms: platformsm ? platformsm[1].trim() : "",
        imageUrl: img ? img.src : "",
      });
    }
    return out;
  });
}

function daysRunning(startDate) {
  if (!startDate) return null;
  const t = Date.parse(startDate);
  if (isNaN(t)) return null;
  return Math.max(0, Math.round((Date.now() - t) / 86400000));
}

async function main() {
  const args = parseArgs(process.argv);
  if (args.help) { console.log(HELP); return; }
  if (!args.query) { console.error("ERROR: --query is required.\n"); console.error(HELP); process.exit(2); }

  const browser = await launch(args.proxy);
  const ctx = await browser.newContext({
    userAgent:
      "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0 Safari/537.36",
    locale: "en-US",
  });
  const page = await ctx.newPage();
  try {
    const raw = await scrape(page, args.query, args.country, args.maxAds, args.timeout);
    await browser.close();
    const ads = raw.slice(0, args.maxAds).map((a) => ({ ...a, query: args.query, daysRunning: daysRunning(a.startDate) }));
    emit(args, ads);
  } catch (err) {
    await browser.close().catch(() => {});
    console.error(`ERROR: Meta Ad Library scrape failed: ${err.message}`);
    console.error("Hint: Meta is anti-bot; retry with --proxy, randomize timing, or degrade to a site:facebook.com/ads/library web search.");
    process.exit(1);
  }
}

function emit(args, ads) {
  if (args.output === "summary") {
    if (!ads.length) { console.log(`No active Meta ads found for "${args.query}".`); return; }
    for (const a of ads) {
      const dr = a.daysRunning != null ? `${a.daysRunning}d` : "?";
      console.log(`[${a.visualType} ${dr} running] CTA:${a.cta || "-"}`);
      console.log(`        ${a.adText.slice(0, 140)}`);
      console.log(`        -> ${a.landingUrl}`);
    }
    return;
  }
  const payload = JSON.stringify(ads, null, 2);
  if (args.output && args.output !== "json") {
    fs.writeFileSync(args.output, payload + "\n");
    console.error(`${ads.length} ads -> ${args.output}`);
  } else {
    process.stdout.write(payload + "\n");
  }
}

main();
