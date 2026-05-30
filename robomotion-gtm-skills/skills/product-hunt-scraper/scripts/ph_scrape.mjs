#!/usr/bin/env node
/**
 * ph_scrape.mjs — keyless Product Hunt leaderboard scraper (degrade path).
 *
 * Product Hunt is JS-heavy and anti-bot, so the keyless path uses Playwright to load the
 * leaderboard for the chosen period and extract product cards. Prints a JSON array of
 * { name, tagline, url, upvotes } to stdout. Lower reliability than the Apify path.
 *
 * Requires: playwright (chromium). See SKILL.md: `npx playwright install chromium`.
 * Route through a proxy (HTTPS_PROXY / Robomotion Proxy) when running volume.
 *
 * Usage: node ph_scrape.mjs --period weekly --max 50
 */
import { chromium } from "playwright";

function arg(name, def) {
  const i = process.argv.indexOf(`--${name}`);
  return i !== -1 && process.argv[i + 1] ? process.argv[i + 1] : def;
}

const PERIOD = (arg("period", "weekly")).toLowerCase();
const MAX = parseInt(arg("max", "50"), 10);
const PATHS = { daily: "daily", weekly: "weekly", monthly: "monthly" };
const url = `https://www.producthunt.com/leaderboard/${PATHS[PERIOD] || "weekly"}`;

async function main() {
  const browser = await chromium.launch({ headless: true });
  const ctx = await browser.newContext({
    userAgent:
      "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0 Safari/537.36",
    viewport: { width: 1280, height: 1800 },
  });
  const page = await ctx.newPage();
  try {
    await page.goto(url, { waitUntil: "networkidle", timeout: 60000 });
    // Scroll to load lazy cards.
    for (let i = 0; i < 6; i++) {
      await page.mouse.wheel(0, 2400);
      await page.waitForTimeout(800);
    }
    const items = await page.evaluate(() => {
      const out = [];
      const seen = new Set();
      const links = Array.from(document.querySelectorAll('a[href^="/posts/"]'));
      for (const a of links) {
        const href = a.getAttribute("href") || "";
        if (!href.startsWith("/posts/")) continue;
        const slug = href.split("?")[0];
        if (seen.has(slug)) continue;
        const card =
          a.closest('[data-test^="post-item"]') ||
          a.closest("section") ||
          a.parentElement?.parentElement;
        if (!card) continue;
        const name = (a.textContent || "").trim();
        if (!name) continue;
        seen.add(slug);
        const text = (card.textContent || "").replace(/\s+/g, " ").trim();
        // upvotes: leading integer often the vote count button text
        const voteMatch = text.match(/(\d[\d,]*)\s*$/) || text.match(/^(\d[\d,]*)/);
        const upvotes = voteMatch ? parseInt(voteMatch[1].replace(/,/g, ""), 10) : 0;
        // tagline: text after the name, trimmed
        let tagline = text.replace(name, "").trim().slice(0, 200);
        out.push({
          name,
          tagline,
          url: "https://www.producthunt.com" + slug,
          upvotes: Number.isFinite(upvotes) ? upvotes : 0,
        });
      }
      return out;
    });
    process.stdout.write(JSON.stringify(items.slice(0, MAX)));
  } finally {
    await browser.close();
  }
}

main().catch((e) => {
  process.stderr.write(String(e && e.stack ? e.stack : e) + "\n");
  process.exit(1);
});
