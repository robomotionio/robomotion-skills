#!/usr/bin/env node
// pb_engagers_pw.mjs — keyless Playwright degrade for KOL post engagers (no Apify/PhantomBuster).
//
// Given explicit LinkedIn post URLs (you pick the one best post per KOL), scrapes both the
// REACTORS and the COMMENTERS (with comment text) of each post and emits engager rows in the
// engine schema:  {name, headline, profile_url, engagement_type, comment_text?, post_url}.
// One-off use with a LinkedIn session cookie (LI_AT). Normally invoked by extract_engagers.py
// (--source playwright); it shells out here. The agent enriches + scores downstream.
//
// Setup:  npx playwright install chromium
// Auth:   LI_AT env var = LinkedIn li_at session cookie.
// Usage:  node pb_engagers_pw.mjs --post-urls "url1,url2" --output engagers.json
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

const HELP = `pb_engagers_pw.mjs — Playwright LinkedIn post reactors+commenters (keyless degrade)
  --post-urls "u1,u2"   comma-separated LinkedIn post URLs   [required]
  --output <path>       output JSON (default stdout)
  --limit <n>           cap engagers per post
  --help                show this
Auth: LI_AT env var (li_at cookie). Run: npx playwright install chromium`;

const norm = (u) => (u || "").split("?")[0].replace(/\/$/, "").toLowerCase();

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
    let perPost = 0;
    try {
      await page.goto(postUrl, { waitUntil: "domcontentloaded", timeout: 45000 });
      await page.waitForTimeout(3000 + Math.random() * 2000);

      // Commenters (with text) from the comments region.
      const commenters = await page.evaluate(() => {
        const rows = [];
        document
          .querySelectorAll("article.comments-comment-entity, .comments-comment-item")
          .forEach((c) => {
            const link = c.querySelector('a[href*="/in/"]');
            const nameEl = c.querySelector(
              ".comments-comment-meta__description-title, .comments-post-meta__name-text"
            );
            const headlineEl = c.querySelector(".comments-comment-meta__description-subtitle");
            const textEl = c.querySelector(
              ".comments-comment-item__main-content, .update-components-text"
            );
            const url = link ? link.href.split("?")[0] : "";
            const name = (nameEl ? nameEl.textContent : link ? link.textContent : "").trim();
            if (url && url.includes("/in/")) {
              rows.push({
                name,
                headline: headlineEl ? headlineEl.textContent.trim() : "",
                profile_url: url,
                comment_text: textEl ? textEl.textContent.trim() : "",
              });
            }
          });
        return rows;
      });
      for (const c of commenters) {
        const k = norm(c.profile_url);
        if (!k || seen.has(k)) continue;
        seen.add(k);
        out.push({
          name: c.name,
          headline: c.headline,
          profile_url: c.profile_url,
          engagement_type: "comment",
          comment_text: c.comment_text || "",
          post_url: postUrl,
        });
        if (args.limit && ++perPost >= args.limit) break;
      }

      // Reactors: any remaining /in/ profile links not already captured as commenters.
      if (!args.limit || perPost < args.limit) {
        const reactors = await page.evaluate(() => {
          const rows = [];
          document.querySelectorAll('a[href*="/in/"]').forEach((a) => {
            const name = a.textContent.trim();
            const url = a.href.split("?")[0];
            if (name && url.includes("/in/")) rows.push({ name, profile_url: url });
          });
          return rows;
        });
        for (const r of reactors) {
          const k = norm(r.profile_url);
          if (!k || seen.has(k)) continue;
          seen.add(k);
          out.push({
            name: r.name,
            headline: "",
            profile_url: r.profile_url,
            engagement_type: "reaction",
            post_url: postUrl,
          });
          if (args.limit && ++perPost >= args.limit) break;
        }
      }
    } catch (e) {
      console.error(`WARN: ${postUrl}: ${String(e).slice(0, 160)}`);
    }
  }
  await browser.close();

  const payload = JSON.stringify(out, null, 2);
  if (args.output && args.output !== "-") {
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
