#!/usr/bin/env node
// scrape_speakers_pw.mjs — Playwright degrade for conference-speaker-scraper.
//
// Renders a JS-heavy speakers page (incl. Sched/Sessionize embeds) and extracts speaker
// cards after the client app has populated the DOM. Emits the same shape as
// scrape_speakers.py's JSON. Keyless (no API key) — just a headless browser.
//
// Setup:  npx playwright install chromium
// Usage:  node scrape_speakers_pw.mjs --url https://conf.example.com/speakers \
//             --conference "ExampleConf" --output speakers.json
import { writeFileSync } from "node:fs";

function parseArgs(argv) {
  const a = {};
  for (let i = 2; i < argv.length; i++) {
    const k = argv[i];
    if (k === "--url") a.url = argv[++i];
    else if (k === "--conference") a.conference = argv[++i];
    else if (k === "--output") a.output = argv[++i];
    else if (k === "--help" || k === "-h") a.help = true;
  }
  return a;
}

const HELP = `scrape_speakers_pw.mjs — Playwright conference-speaker scrape (JS-heavy degrade)
  --url <url>            speakers-page URL                 [required]
  --conference <name>    conference name (else from host)
  --output <path>        output JSON (default stdout)
  --help                 show this
Run: npx playwright install chromium`;

async function main() {
  const args = parseArgs(process.argv);
  if (args.help || !args.url) {
    console.log(HELP);
    process.exit(args.help ? 0 : 1);
  }
  const conference = args.conference || new URL(args.url).hostname.replace(/^www\./, "");

  const { chromium } = await import("playwright");
  const browser = await chromium.launch({ headless: true });
  const ctx = await browser.newContext({
    userAgent: "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 Chrome/120 Safari/537.36",
  });
  const page = await ctx.newPage();
  await page.goto(args.url, { waitUntil: "networkidle", timeout: 60000 });
  await page.waitForTimeout(2500);

  const speakers = await page.evaluate(() => {
    const out = [];
    const sel = '[class*="speaker"],[class*="presenter"],[class*="faculty"],[class*="panelist"]';
    const cards = document.querySelectorAll(sel);
    const seen = new Set();
    cards.forEach((card) => {
      const heading = card.querySelector("h1,h2,h3,h4,h5,strong,b");
      const name = heading ? heading.textContent.trim() : "";
      if (!name || name.length > 80 || seen.has(name.toLowerCase())) return;
      seen.add(name.toLowerCase());
      const text = card.textContent.replace(/\s+/g, " ").trim().slice(0, 300);
      let title = "", company = "";
      const rest = text.replace(name, "").trim();
      if (rest.includes(",")) {
        const i = rest.indexOf(",");
        title = rest.slice(0, i).trim();
        company = rest.slice(i + 1).trim();
      } else {
        title = rest;
      }
      out.push({ name, title, company, bio: text });
    });
    return out;
  });

  await browser.close();
  for (const s of speakers) s.conference = conference;

  const payload = JSON.stringify(
    { conference, strategy: "playwright", platform: "", speakers }, null, 2);
  if (args.output) {
    writeFileSync(args.output, payload + "\n");
    console.error(`${speakers.length} speakers -> ${args.output}`);
  } else {
    process.stdout.write(payload + "\n");
  }
}

main().catch((e) => {
  console.error(e);
  process.exit(1);
});
