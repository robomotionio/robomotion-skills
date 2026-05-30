#!/usr/bin/env node
/**
 * review_scrape.mjs — keyless Playwright degrade for review-site-scraper.
 *
 * G2 / Capterra / Trustpilot are JS-heavy and anti-bot, so this is the fallback when no
 * APIFY_API_TOKEN is set. For g2/trustpilot it loads --url; for capterra it resolves
 * --company via Capterra search to the first product's reviews page. Extracts review
 * blocks best-effort and prints a JSON array of raw fields (the Python wrapper normalizes).
 * Expect partial results — review sites often present anti-bot interstitials.
 *
 * Requires: playwright (chromium). See SKILL.md: `npx playwright install chromium`.
 * Route through a proxy (HTTPS_PROXY / Robomotion Proxy).
 *
 * Usage:
 *   node review_scrape.mjs --platform g2 --url <reviews-url> --max 50
 *   node review_scrape.mjs --platform capterra --company "Foo App" --max 50
 */
import { chromium } from "playwright";

function arg(name, def) {
  const i = process.argv.indexOf(`--${name}`);
  return i !== -1 && process.argv[i + 1] ? process.argv[i + 1] : def;
}

const PLATFORM = arg("platform", "");
const URL_ARG = arg("url", "");
const COMPANY = arg("company", "");
const MAX = parseInt(arg("max", "50"), 10);

async function resolveCapterra(page, company) {
  const search =
    "https://www.capterra.com/search/?query=" + encodeURIComponent(company);
  await page.goto(search, { waitUntil: "domcontentloaded", timeout: 60000 });
  await page.waitForTimeout(3000);
  const href = await page.evaluate(() => {
    const a = document.querySelector('a[href*="/p/"]');
    return a ? a.getAttribute("href") : "";
  });
  if (!href) return "";
  const base = href.startsWith("http") ? href : "https://www.capterra.com" + href;
  return base.replace(/\/$/, "") + "/reviews/";
}

function extractReviews(platform) {
  // Runs in page context. Heuristic, per-platform.
  const out = [];
  const blocks = Array.from(
    document.querySelectorAll(
      '[itemprop="review"], article, [data-testid*="review"], [class*="review" i]'
    )
  ).slice(0, 200);
  for (const b of blocks) {
    const text = (b.textContent || "").replace(/\s+/g, " ").trim();
    if (text.length < 40) continue;
    // rating: look for an aria-label like "4 out of 5" or an itemprop ratingValue
    let rating = null;
    const rEl =
      b.querySelector('[itemprop="ratingValue"]') ||
      b.querySelector('[aria-label*="out of"]') ||
      b.querySelector('[class*="rating" i]');
    if (rEl) {
      const rt =
        rEl.getAttribute("content") ||
        rEl.getAttribute("aria-label") ||
        rEl.textContent ||
        "";
      const m = rt.match(/(\d(?:\.\d)?)/);
      if (m) rating = parseFloat(m[1]);
    }
    const dateEl = b.querySelector("time, [itemprop='datePublished'], [class*='date' i]");
    const date = dateEl
      ? dateEl.getAttribute("datetime") || dateEl.textContent.trim()
      : "";
    const authEl = b.querySelector("[itemprop='author'], [class*='author' i], [class*='reviewer' i]");
    const author = authEl ? authEl.textContent.replace(/\s+/g, " ").trim() : "";
    out.push({ text: text.slice(0, 4000), rating, date, author, platform });
  }
  return out;
}

async function main() {
  const browser = await chromium.launch({ headless: true });
  const ctx = await browser.newContext({
    userAgent:
      "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0 Safari/537.36",
    viewport: { width: 1280, height: 2200 },
  });
  const page = await ctx.newPage();
  try {
    let target = URL_ARG;
    if (PLATFORM === "capterra" && !target) {
      target = await resolveCapterra(page, COMPANY);
      if (!target) {
        process.stdout.write("[]");
        return;
      }
    }
    await page.goto(target, { waitUntil: "domcontentloaded", timeout: 60000 });
    await page.waitForTimeout(3500);
    for (let i = 0; i < 6; i++) {
      await page.mouse.wheel(0, 2400);
      await page.waitForTimeout(900);
    }
    const reviews = await page.evaluate(extractReviews, PLATFORM);
    // de-dup by text prefix
    const seen = new Set();
    const uniq = [];
    for (const r of reviews) {
      const k = (r.text || "").slice(0, 80);
      if (seen.has(k)) continue;
      seen.add(k);
      uniq.push(r);
      if (uniq.length >= MAX) break;
    }
    process.stdout.write(JSON.stringify(uniq));
  } finally {
    await browser.close();
  }
}

main().catch((e) => {
  process.stderr.write(String(e && e.stack ? e.stack : e) + "\n");
  process.exit(1);
});
