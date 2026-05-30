#!/usr/bin/env node
// pb_engagers_pw.mjs — keyless Playwright degrade for extract_engagers.py (no Apify/PB).
//
// Given explicit LinkedIn post URLs, opens each post with a LinkedIn session cookie
// (LI_AT) and harvests the reactors/commenters it can read from the DOM. Lowest-volume
// path — use only when neither APIFY_API_TOKEN nor PHANTOMBUSTER_API_KEY is available.
//
// Emits the engine's canonical engager schema so extract_engagers.py can normalize it:
//   {name, headline, profile_url, engagement_type, comment_text?, post_url, source}
//
// Setup:  npx playwright install chromium
// Auth:   LI_AT env var = LinkedIn li_at session cookie.
// Usage:  node pb_engagers_pw.mjs --post-urls "url1,url2" [--limit N] [--output path]
import { writeFileSync } from "node:fs";

function parseArgs(argv) {
  const a = {};
  for (let i = 2; i < argv.length; i++) {
    const k = argv[i];
    if (k === "--post-urls") a.postUrls = argv[++i];
    else if (k === "--output") a.output = argv[++i];
    else if (k === "--limit") a.limit = parseInt(argv[++i], 10);
    else if (k === "--help" || k === "-h") a.help = true;
  }
  return a;
}

const HELP = `pb_engagers_pw.mjs — keyless Playwright LinkedIn engager scrape (degrade)
  --post-urls "u1,u2"   comma-separated LinkedIn post URLs   [required]
  --output <path>       output JSON (default stdout)
  --limit <n>           cap engagers across all posts
  --help                show this
Auth: LI_AT env var (li_at cookie). Run: npx playwright install chromium`;

async function main() {
  const args = parseArgs(process.argv);
  if (args.help || !args.postUrls) {
    console.log(HELP);
    process.exit(args.help ? 0 : 1);
  }
  const liAt = (process.env.LI_AT || "").trim();
  if (!liAt) {
    console.error("ERROR: LI_AT env var (LinkedIn li_at cookie) is required.");
    process.exit(1);
  }
  const posts = args.postUrls.split(",").map((s) => s.trim()).filter(Boolean);

  const { chromium } = await import("playwright");
  const browser = await chromium.launch({ headless: true });
  const ctx = await browser.newContext({
    userAgent:
      "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120 Safari/537.36",
  });
  await ctx.addCookies([{ name: "li_at", value: liAt, domain: ".linkedin.com", path: "/" }]);
  const page = await ctx.newPage();

  const seen = new Set();
  const out = [];
  for (const postUrl of posts) {
    try {
      await page.goto(postUrl, { waitUntil: "domcontentloaded", timeout: 45000 });
      await page.waitForTimeout(3000 + Math.random() * 2000);

      // Commenters (with their comment text) — strongest intent signal.
      const commenters = await page.evaluate(() => {
        const rows = [];
        document.querySelectorAll("article.comments-comment-entity, .comments-comment-item").forEach((el) => {
          const a = el.querySelector('a[href*="/in/"]');
          if (!a) return;
          const name = (el.querySelector(".comments-comment-meta__description-title")?.textContent || a.textContent || "").trim();
          const headline = (el.querySelector(".comments-comment-meta__description-subtitle")?.textContent || "").trim();
          const text = (el.querySelector(".comments-comment-item__main-content, .update-components-text")?.textContent || "").trim();
          rows.push({ name, headline, profile_url: a.href.split("?")[0], comment_text: text, type: "comment" });
        });
        return rows;
      });

      // Reactors / fallback: any /in/ profile link on the page.
      const reactors = await page.evaluate(() => {
        const rows = [];
        document.querySelectorAll('a[href*="/in/"]').forEach((a) => {
          const name = a.textContent.trim();
          const url = a.href.split("?")[0];
          if (name && url.includes("/in/")) rows.push({ name, profile_url: url, type: "reaction" });
        });
        return rows;
      });

      for (const r of [...commenters, ...reactors]) {
        const k = r.profile_url.replace(/\/$/, "").toLowerCase();
        if (seen.has(k)) continue;
        seen.add(k);
        const row = {
          name: r.name || "",
          headline: r.headline || "",
          profile_url: r.profile_url,
          engagement_type: r.type,
          post_url: postUrl,
          source: "playwright",
        };
        if (r.comment_text) row.comment_text = r.comment_text;
        out.push(row);
        if (args.limit && out.length >= args.limit) break;
      }
      if (args.limit && out.length >= args.limit) break;
    } catch (e) {
      console.error(`WARN: ${postUrl}: ${String(e).slice(0, 160)}`);
    }
  }
  await browser.close();

  const payload = JSON.stringify(out, null, 2);
  if (args.output) {
    writeFileSync(args.output, payload + "\n");
    console.error(`${out.length} engagers -> ${args.output}`);
  } else {
    process.stdout.write(payload + "\n");
  }
}

main().catch((e) => {
  console.error(e);
  process.exit(1);
});
