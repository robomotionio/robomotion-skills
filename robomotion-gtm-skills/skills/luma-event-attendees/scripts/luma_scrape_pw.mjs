#!/usr/bin/env node
// luma_scrape_pw.mjs — direct (free) Luma event-page scrape via Playwright.
//
// Direct-scrape mode: given a single Luma event URL, render the JS app and extract event
// metadata + hosts (+ any publicly embedded guests). Keyless. For full registered-guest
// profiles use the Apify search mode (luma_search.py) instead.
//
// Luma embeds structured data in a Next.js __NEXT_DATA__ script tag; we read that first and
// fall back to DOM scraping. Emits normalized people records.
//
// Setup:  npx playwright install chromium
// Usage:  node luma_scrape_pw.mjs --event-url https://lu.ma/abc123 --output people.json
import { writeFileSync } from "node:fs";

function parseArgs(argv) {
  const a = {};
  for (let i = 2; i < argv.length; i++) {
    const k = argv[i];
    if (k === "--event-url") a.eventUrl = argv[++i];
    else if (k === "--output") a.output = argv[++i];
    else if (k === "--help" || k === "-h") a.help = true;
  }
  return a;
}

const HELP = `luma_scrape_pw.mjs — direct Luma event-page scrape (hosts + metadata, keyless)
  --event-url <url>   a single Luma event URL   [required]
  --output <path>     output JSON (default stdout)
  --help              show this
Run: npx playwright install chromium`;

function pushPerson(out, seen, p) {
  const url = (p.linkedin_url || p.x || p.website || p.name || "").toLowerCase();
  if (!p.name || seen.has(url)) return;
  seen.add(url);
  out.push(p);
}

async function main() {
  const args = parseArgs(process.argv);
  if (args.help || !args.eventUrl) {
    console.log(HELP);
    process.exit(args.help ? 0 : 1);
  }

  const { chromium } = await import("playwright");
  const browser = await chromium.launch({ headless: true });
  const ctx = await browser.newContext({
    userAgent: "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 Chrome/120 Safari/537.36",
  });
  const page = await ctx.newPage();
  await page.goto(args.eventUrl, { waitUntil: "networkidle", timeout: 60000 });
  await page.waitForTimeout(2000);

  const nextData = await page.evaluate(() => {
    const el = document.getElementById("__NEXT_DATA__");
    if (!el) return null;
    try { return JSON.parse(el.textContent); } catch { return null; }
  });

  const out = [];
  const seen = new Set();
  let eventName = "", eventDate = "";

  if (nextData) {
    const blob = JSON.stringify(nextData);
    // best-effort: pull event name/date from common Luma keys
    const nameM = blob.match(/"name":"([^"]{3,120})"/);
    if (nameM) eventName = nameM[1];
    const dateM = blob.match(/"start_at":"([^"]+)"/);
    if (dateM) eventDate = dateM[1];
    // hosts: Luma stores host objects with name + social handles
    const hostMatches = blob.matchAll(
      /"name":"([^"]{2,80})"[^}]*?(?:"twitter_handle":"([^"]*)")?[^}]*?(?:"linkedin_handle":"([^"]*)")?/g);
    for (const m of hostMatches) {
      pushPerson(out, seen, {
        name: m[1],
        bio: "",
        linkedin_url: m[3] ? `https://linkedin.com/in/${m[3]}` : "",
        x: m[2] ? `https://x.com/${m[2]}` : "",
        instagram: "", website: "", company: "",
        event_date: eventDate, role: "host",
      });
      if (out.length >= 50) break;
    }
  }

  if (out.length === 0) {
    // DOM fallback: host/organizer cards
    const dom = await page.evaluate(() => {
      const rows = [];
      document.querySelectorAll('a[href*="/user/"], [class*="host"], [class*="organizer"]').forEach((el) => {
        const name = el.textContent.trim();
        if (name && name.length < 80) rows.push({ name });
      });
      return rows;
    });
    for (const r of dom) {
      pushPerson(out, seen, {
        name: r.name, bio: "", linkedin_url: "", x: "", instagram: "",
        website: "", company: "", event_date: eventDate, role: "host",
      });
    }
  }

  await browser.close();

  const payload = JSON.stringify(
    { event_name: eventName, event_url: args.eventUrl, event_date: eventDate,
      mode: "direct-scrape", people: out }, null, 2);
  if (args.output) {
    writeFileSync(args.output, payload + "\n");
    console.error(`${out.length} people (direct-scrape: hosts/metadata only) -> ${args.output}`);
  } else {
    process.stdout.write(payload + "\n");
  }
}

main().catch((e) => {
  console.error(e);
  process.exit(1);
});
