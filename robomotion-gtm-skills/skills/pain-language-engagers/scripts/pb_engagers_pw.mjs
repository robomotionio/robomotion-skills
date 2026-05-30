#!/usr/bin/env node
// pb_engagers_pw.mjs — Playwright degrade for pain-language-engagers (no Apify/Phantombuster).
//
// Given explicit pain-post URLs (you pick the top posts), scrapes the reactors/commenters of
// each post and emits engager rows in the new pipeline schema
// ({name, headline, profile_url, role, engagement_type, post_url, matched_pain_terms[]}).
// One-off use with a LinkedIn session cookie (LI_AT). REACTORS only — merge each post's
// AUTHOR back in as role="author" (highest intent) via extract_engagers.py's degrade plan.
// The agent then enriches + scores (score_icp.py) + dedups (dedup_history.py).
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

const HELP = `pb_engagers_pw.mjs — Playwright LinkedIn post-reactor scrape (degrade)
  --post-urls "u1,u2"   comma-separated LinkedIn post URLs   [required]
  --output <path>       output JSON (default stdout)
  --limit <n>           cap reactors per post
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
    userAgent: "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 Chrome/120 Safari/537.36",
  });
  await ctx.addCookies([{ name: "li_at", value: liAt, domain: ".linkedin.com", path: "/" }]);
  const page = await ctx.newPage();

  const seen = new Set();
  const out = [];
  for (const postUrl of posts) {
    try {
      await page.goto(postUrl, { waitUntil: "domcontentloaded", timeout: 45000 });
      await page.waitForTimeout(3000 + Math.random() * 2000);
      // Open the reactions modal if present, then read profile links.
      const reactors = await page.evaluate(() => {
        const rows = [];
        document.querySelectorAll('a[href*="/in/"]').forEach((a) => {
          const name = a.textContent.trim();
          const url = a.href.split("?")[0];
          if (name && url.includes("/in/")) rows.push({ name, linkedin_url: url });
        });
        return rows;
      });
      for (const r of reactors) {
        const k = r.linkedin_url.replace(/\/$/, "").toLowerCase();
        if (seen.has(k)) continue;
        seen.add(k);
        out.push({
          name: r.name, headline: "", profile_url: r.linkedin_url,
          role: "engager", engagement_type: "reaction", post_url: postUrl,
          matched_pain_terms: [], author_intent: false,
        });
        if (args.limit && out.length >= args.limit) break;
      }
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
