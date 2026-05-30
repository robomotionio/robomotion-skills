#!/usr/bin/env node
/**
 * x_scrape.mjs — keyless X search scraper (best-effort degrade path).
 *
 * X is login-walled and aggressively anti-bot, so this path is unreliable by design — it
 * is the fallback when no APIFY_API_TOKEN is set. Loads the live-search results page and
 * extracts whatever tweet articles render before the login wall. Prints a JSON array of
 * { id, text, likeCount, retweetCount, replyCount, createdAt, author, url }.
 *
 * Requires: playwright (chromium). See SKILL.md: `npx playwright install chromium`.
 * Route through a proxy (HTTPS_PROXY / Robomotion Proxy) and expect partial/empty results.
 *
 * Usage: node x_scrape.mjs --term '"robomotion" since:2025-01-01' --max 30
 */
import { chromium } from "playwright";

function arg(name, def) {
  const i = process.argv.indexOf(`--${name}`);
  return i !== -1 && process.argv[i + 1] ? process.argv[i + 1] : def;
}

const TERM = arg("term", "");
const MAX = parseInt(arg("max", "50"), 10);
const url =
  "https://x.com/search?f=live&q=" + encodeURIComponent(TERM);

async function main() {
  const browser = await chromium.launch({ headless: true });
  const ctx = await browser.newContext({
    userAgent:
      "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0 Safari/537.36",
    viewport: { width: 1280, height: 2000 },
  });
  const page = await ctx.newPage();
  const collected = new Map();
  try {
    await page.goto(url, { waitUntil: "domcontentloaded", timeout: 60000 });
    await page.waitForTimeout(4000);
    for (let i = 0; i < 8 && collected.size < MAX; i++) {
      const batch = await page.evaluate(() => {
        const arts = Array.from(document.querySelectorAll("article"));
        return arts.map((art) => {
          const link = art.querySelector('a[href*="/status/"]');
          const href = link ? link.getAttribute("href") : "";
          const m = href ? href.match(/\/([^/]+)\/status\/(\d+)/) : null;
          const textEl = art.querySelector('[data-testid="tweetText"]');
          const text = textEl ? textEl.textContent || "" : "";
          const timeEl = art.querySelector("time");
          return {
            id: m ? m[2] : "",
            userName: m ? m[1] : "",
            text,
            createdAt: timeEl ? timeEl.getAttribute("datetime") || "" : "",
            url: href ? "https://x.com" + href.split("?")[0] : "",
          };
        });
      });
      for (const t of batch) {
        if (t.id && !collected.has(t.id)) {
          collected.set(t.id, {
            id: t.id,
            text: t.text,
            fullText: t.text,
            likeCount: 0,
            retweetCount: 0,
            replyCount: 0,
            viewCount: 0,
            createdAt: t.createdAt,
            author: { userName: t.userName, name: "" },
            url: t.url,
          });
        }
      }
      await page.mouse.wheel(0, 2400);
      await page.waitForTimeout(1500);
    }
    process.stdout.write(JSON.stringify(Array.from(collected.values()).slice(0, MAX)));
  } finally {
    await browser.close();
  }
}

main().catch((e) => {
  process.stderr.write(String(e && e.stack ? e.stack : e) + "\n");
  process.exit(1);
});
