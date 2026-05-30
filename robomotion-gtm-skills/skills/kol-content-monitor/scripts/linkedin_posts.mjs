#!/usr/bin/env node
/**
 * linkedin_posts.mjs — keyless LinkedIn profile recent-posts scraper (degrade path).
 *
 * LinkedIn is auth-walled and anti-bot. The reliable path is PhantomBuster
 * (PHANTOMBUSTER_API_KEY + LinkedIn session cookie); this Playwright fallback is best-effort
 * and one-off. It loads a public profile's /recent-activity/all/ page and extracts whatever
 * post cards render. Supply a logged-in session via LINKEDIN_COOKIE (the li_at value) for
 * better results — without it LinkedIn shows a wall and yields little.
 *
 * Prints a JSON array: { kol, url, text, engagement, comments, platform:"linkedin" }.
 *
 * Requires: playwright (chromium). See SKILL.md: `npx playwright install chromium`.
 * Route through a proxy (HTTPS_PROXY / Robomotion Proxy).
 *
 * Usage: node linkedin_posts.mjs --profile https://www.linkedin.com/in/foo --name "Foo" --max 20
 */
import { chromium } from "playwright";

function arg(name, def) {
  const i = process.argv.indexOf(`--${name}`);
  return i !== -1 && process.argv[i + 1] ? process.argv[i + 1] : def;
}

const PROFILE = arg("profile", "");
const NAME = arg("name", "");
const MAX = parseInt(arg("max", "20"), 10);

function actUrl(profile) {
  const base = profile.replace(/\/$/, "");
  return base + "/recent-activity/all/";
}

function parseCount(s) {
  if (!s) return 0;
  const m = String(s).replace(/,/g, "").match(/([\d\.]+)\s*([KkMm]?)/);
  if (!m) return 0;
  let n = parseFloat(m[1]);
  if (/k/i.test(m[2])) n *= 1000;
  else if (/m/i.test(m[2])) n *= 1000000;
  return Math.round(n);
}

async function main() {
  if (!PROFILE) {
    process.stderr.write("ERROR: --profile is required\n");
    process.exit(2);
  }
  const browser = await chromium.launch({ headless: true });
  const ctx = await browser.newContext({
    userAgent:
      "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0 Safari/537.36",
    viewport: { width: 1280, height: 2400 },
  });
  if (process.env.LINKEDIN_COOKIE) {
    await ctx.addCookies([
      {
        name: "li_at",
        value: process.env.LINKEDIN_COOKIE,
        domain: ".linkedin.com",
        path: "/",
        httpOnly: true,
        secure: true,
      },
    ]);
  }
  const page = await ctx.newPage();
  try {
    await page.goto(actUrl(PROFILE), { waitUntil: "domcontentloaded", timeout: 60000 });
    await page.waitForTimeout(4000);
    for (let i = 0; i < 6; i++) {
      await page.mouse.wheel(0, 2600);
      await page.waitForTimeout(1200);
    }
    const raw = await page.evaluate(() => {
      const out = [];
      const cards = Array.from(
        document.querySelectorAll('div.feed-shared-update-v2, [data-urn*="activity"], article')
      ).slice(0, 60);
      for (const c of cards) {
        const textEl = c.querySelector(
          '.feed-shared-update-v2__description, .update-components-text, [class*="commentary" i]'
        );
        const text = textEl ? (textEl.textContent || "").replace(/\s+/g, " ").trim() : "";
        if (!text) continue;
        const social = (c.textContent || "").replace(/\s+/g, " ");
        const reactM = social.match(/([\d,\.]+[KkMm]?)\s*(?:reactions|likes)/);
        const commM = social.match(/([\d,\.]+[KkMm]?)\s*comments?/);
        const linkEl = c.querySelector('a[href*="/feed/update/"], a[href*="activity"]');
        out.push({
          text: text.slice(0, 1200),
          reactions: reactM ? reactM[1] : "0",
          comments: commM ? commM[1] : "0",
          url: linkEl ? linkEl.href : "",
        });
      }
      return out;
    });
    const items = raw.slice(0, MAX).map((r) => ({
      kol: NAME || PROFILE,
      url: r.url,
      text: r.text,
      engagement: parseCount(r.reactions),
      comments: parseCount(r.comments),
      platform: "linkedin",
    }));
    process.stdout.write(JSON.stringify(items));
  } finally {
    await browser.close();
  }
}

main().catch((e) => {
  process.stderr.write(String(e && e.stack ? e.stack : e) + "\n");
  process.exit(1);
});
