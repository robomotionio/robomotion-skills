#!/usr/bin/env node
// pb_profiles_pw.mjs — Playwright degrade for champion-tracker (no Phantombuster key).
//
// Scrapes each champion's LinkedIn profile for current company + title, one-off, using a
// LinkedIn session cookie (LI_AT env var). Emits the same {linkedin_url, name, company,
// title} rows as pb_profiles.py so the agent's baseline/diff logic is identical.
//
// Deterministic I/O only — the agent does ICP scoring and baseline diff (use pb_profiles.py
// --mode track logic, or diff in-agent).
//
// Setup:  npx playwright install chromium
// Auth:   LI_AT env var = your LinkedIn `li_at` session cookie value.
// Usage:  node pb_profiles_pw.mjs --urls champions.csv --output snapshot.json
//         (then feed snapshot.json to your baseline/diff step)
import { readFileSync, writeFileSync } from "node:fs";

function parseArgs(argv) {
  const a = {};
  for (let i = 2; i < argv.length; i++) {
    const k = argv[i];
    if (k === "--urls") a.urls = argv[++i];
    else if (k === "--output") a.output = argv[++i];
    else if (k === "--limit") a.limit = parseInt(argv[++i], 10);
    else if (k === "--help" || k === "-h") a.help = true;
  }
  return a;
}

const HELP = `pb_profiles_pw.mjs — Playwright LinkedIn profile scrape (champion-tracker degrade)
  --urls <csv>     CSV with a linkedin_url column (name optional)   [required]
  --output <path>  output JSON (default stdout)
  --limit <n>      cap profiles scraped
  --help           show this
Auth: LI_AT env var (LinkedIn li_at session cookie). Run: npx playwright install chromium`;

function loadUrls(path) {
  const text = readFileSync(path, "utf-8").trim();
  const lines = text.split(/\r?\n/);
  const header = lines.shift().split(",").map((s) => s.trim().toLowerCase());
  const urlIdx = header.findIndex((h) => ["linkedin_url", "linkedin", "url", "linkedinurl"].includes(h));
  const nameIdx = header.findIndex((h) => h === "name");
  const rows = [];
  for (const ln of lines) {
    if (!ln.trim()) continue;
    const cols = ln.split(",");
    const url = (cols[urlIdx] || "").trim();
    if (url) rows.push({ linkedin_url: url, name: nameIdx >= 0 ? (cols[nameIdx] || "").trim() : "" });
  }
  return rows;
}

async function main() {
  const args = parseArgs(process.argv);
  if (args.help || !args.urls) {
    console.log(HELP);
    process.exit(args.help ? 0 : 1);
  }
  const liAt = (process.env.LI_AT || "").trim();
  if (!liAt) {
    console.error("ERROR: LI_AT env var (LinkedIn li_at session cookie) is required.");
    process.exit(1);
  }
  let rows = loadUrls(args.urls);
  if (args.limit) rows = rows.slice(0, args.limit);

  const { chromium } = await import("playwright");
  const browser = await chromium.launch({ headless: true });
  const ctx = await browser.newContext({
    userAgent: "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 Chrome/120 Safari/537.36",
  });
  await ctx.addCookies([{ name: "li_at", value: liAt, domain: ".linkedin.com", path: "/" }]);
  const page = await ctx.newPage();

  const out = [];
  for (const r of rows) {
    try {
      await page.goto(r.linkedin_url, { waitUntil: "domcontentloaded", timeout: 45000 });
      await page.waitForTimeout(2500 + Math.random() * 2000); // throttle / anti-bot
      const data = await page.evaluate(() => {
        const txt = (sel) => document.querySelector(sel)?.textContent?.trim() || "";
        const name = txt("h1");
        const headline = txt(".text-body-medium");
        // current experience block (best-effort; LinkedIn DOM shifts often)
        let company = "";
        const exp = document.querySelector('[data-view-name="profile-component-entity"] span[aria-hidden="true"]');
        if (exp) company = exp.textContent.trim();
        return { name, headline, company };
      });
      out.push({
        linkedin_url: r.linkedin_url,
        name: data.name || r.name,
        company: data.company,
        title: data.headline,
      });
    } catch (e) {
      out.push({ linkedin_url: r.linkedin_url, name: r.name, company: "", title: "", error: String(e).slice(0, 200) });
    }
  }
  await browser.close();

  const payload = JSON.stringify(out, null, 2);
  if (args.output) {
    writeFileSync(args.output, payload + "\n");
    console.error(`${out.length} profiles -> ${args.output}`);
  } else {
    process.stdout.write(payload + "\n");
  }
}

main().catch((e) => {
  console.error(e);
  process.exit(1);
});
