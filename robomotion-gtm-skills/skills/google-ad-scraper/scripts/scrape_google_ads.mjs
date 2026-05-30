#!/usr/bin/env node
/**
 * scrape_google_ads.mjs — Scrape a competitor's active Google ads from the
 * Google Ads Transparency Center (https://adstransparency.google.com).
 *
 * The Transparency Center is a JS single-page app, so this drives a headless
 * Chromium via Playwright. Deterministic: it scrapes + parses only — no LLM.
 * Implements the robomotion-gtm-skills `google-ad-scraper` contract.
 *
 * Auth: none. Google Ads Transparency Center is public.
 * Optional: a proxy via --proxy (or HTTPS_PROXY env) to dodge IP blocks / set geo.
 *
 * Usage:
 *   node scrape_google_ads.mjs --domain hubspot.com --max-ads 50 --country US
 *   node scrape_google_ads.mjs --company "HubSpot" --output ads.json
 *   node scrape_google_ads.mjs --domain stripe.com --output summary
 *
 * Requires Playwright chromium:  npx playwright install chromium
 */
import fs from "node:fs";

// Lazy so --help works before `npm install` / `npx playwright install chromium`.
async function getChromium() {
  const { chromium } = await import("playwright");
  return chromium;
}

function parseArgs(argv) {
  const a = {
    domain: "",
    company: "",
    maxAds: 50,
    country: "US",
    output: "json",
    proxy: process.env.HTTPS_PROXY || process.env.HTTP_PROXY || "",
    timeout: 45000,
  };
  for (let i = 2; i < argv.length; i++) {
    const k = argv[i];
    const v = argv[i + 1];
    switch (k) {
      case "--domain": a.domain = v; i++; break;
      case "--company": a.company = v; i++; break;
      case "--max-ads": a.maxAds = parseInt(v, 10) || 50; i++; break;
      case "--country": a.country = (v || "US").toUpperCase(); i++; break;
      case "--output": a.output = v; i++; break;
      case "--proxy": a.proxy = v; i++; break;
      case "--timeout": a.timeout = parseInt(v, 10) || 45000; i++; break;
      case "-h":
      case "--help": a.help = true; break;
    }
  }
  return a;
}

const HELP = `scrape_google_ads.mjs — scrape active Google ads from the Transparency Center.

Options:
  --domain <d>     target domain (e.g. hubspot.com). Recommended path.
  --company <name> company name; resolved to an advertiser when no domain given.
  --max-ads <n>    cap on ads returned (default 50)
  --country <cc>   geo / library region (default US)
  --output <fmt>   json | summary | <path.json> (default json to stdout)
  --proxy <url>    proxy URL (else HTTPS_PROXY env); helps dodge IP blocks
  --timeout <ms>   per-navigation timeout (default 45000)
  -h, --help       this help

At least one of --domain / --company is required.`;

async function launch(proxy) {
  const chromium = await getChromium();
  const opts = { headless: true, args: ["--no-sandbox", "--disable-blink-features=AutomationControlled"] };
  if (proxy) opts.proxy = { server: proxy };
  return chromium.launch(opts);
}

// Resolve a company name to a Transparency-Center advertiser id via the search page.
async function resolveAdvertiser(page, company, country, timeout) {
  const url = `https://adstransparency.google.com/?region=${encodeURIComponent(country)}&search_text=${encodeURIComponent(company)}`;
  await page.goto(url, { waitUntil: "domcontentloaded", timeout });
  await page.waitForTimeout(3500);
  // Advertiser cards link to /advertiser/<id>. Collect candidates.
  const cands = await page.evaluate(() => {
    const out = [];
    document.querySelectorAll('a[href*="/advertiser/"]').forEach((a) => {
      const m = a.getAttribute("href").match(/\/advertiser\/([A-Za-z0-9]+)/);
      if (m) out.push({ advertiserId: m[1], advertiserName: (a.textContent || "").trim() });
    });
    return out;
  });
  // dedup by id
  const seen = new Set();
  return cands.filter((c) => (seen.has(c.advertiserId) ? false : (seen.add(c.advertiserId), true)));
}

// Scrape ad creatives for an advertiser/domain query. Returns raw card records.
async function scrapeAds(page, query, country, maxAds, timeout) {
  const url = `https://adstransparency.google.com/?region=${encodeURIComponent(country)}&search_text=${encodeURIComponent(query)}`;
  await page.goto(url, { waitUntil: "domcontentloaded", timeout });
  await page.waitForTimeout(3500);

  // Scroll to lazy-load more creatives until we have enough or the page stops growing.
  let lastCount = -1;
  for (let i = 0; i < 30; i++) {
    const count = await page.evaluate(() =>
      document.querySelectorAll('creative-preview, [data-creative-id], a[href*="/creative/"]').length
    );
    if (count >= maxAds || count === lastCount) break;
    lastCount = count;
    await page.evaluate(() => window.scrollTo(0, document.body.scrollHeight));
    await page.waitForTimeout(1500);
  }

  // Extract structured creative records from the DOM.
  return page.evaluate(() => {
    const recs = [];
    const cards = document.querySelectorAll('creative-preview, [data-creative-id], a[href*="/creative/"]');
    cards.forEach((card) => {
      const href =
        card.getAttribute && card.getAttribute("href")
          ? card.getAttribute("href")
          : (card.querySelector && card.querySelector('a[href*="/creative/"]')?.getAttribute("href")) || "";
      const cm = (href || "").match(/\/creative\/([A-Za-z0-9]+)/);
      const am = (href || "").match(/\/advertiser\/([A-Za-z0-9]+)/);
      const img = card.querySelector ? card.querySelector("img") : null;
      const iframe = card.querySelector ? card.querySelector("iframe") : null;
      const video = card.querySelector ? card.querySelector("video") : null;
      let fmt = "TEXT";
      if (video) fmt = "VIDEO";
      else if (img) fmt = "IMAGE";
      const text = (card.textContent || "").replace(/\s+/g, " ").trim().slice(0, 600);
      recs.push({
        creativeId: cm ? cm[1] : "",
        advertiserId: am ? am[1] : "",
        originalUrl: href ? new URL(href, location.origin).href : "",
        imageUrl: img ? img.src : "",
        variantFormat: fmt,
        variantContent: text,
        _hasFrame: !!iframe,
      });
    });
    return recs;
  });
}

function normalize(recs, advertiserName, maxAds) {
  // dedup by creativeId, group variants by creative
  const byId = new Map();
  for (const r of recs) {
    if (!r.creativeId && !r.variantContent) continue;
    const key = r.creativeId || r.originalUrl || r.variantContent.slice(0, 60);
    if (!byId.has(key)) {
      byId.set(key, {
        advertiserId: r.advertiserId,
        advertiserName: advertiserName || "",
        creativeId: r.creativeId,
        originalUrl: r.originalUrl,
        imageUrl: r.imageUrl,
        variantFormat: r.variantFormat,
        variantContent: r.variantContent,
        variants: [],
        variantCount: 1,
        startDate: "",
      });
    } else {
      const e = byId.get(key);
      if (r.variantContent && r.variantContent !== e.variantContent) {
        e.variants.push({ format: r.variantFormat, content: r.variantContent, imageUrl: r.imageUrl });
        e.variantCount = e.variants.length + 1;
      }
    }
  }
  return Array.from(byId.values()).slice(0, maxAds);
}

async function main() {
  const args = parseArgs(process.argv);
  if (args.help) {
    console.log(HELP);
    return;
  }
  if (!args.domain && !args.company) {
    console.error("ERROR: at least one of --domain or --company is required.\n");
    console.error(HELP);
    process.exit(2);
  }

  const browser = await launch(args.proxy);
  const ctx = await browser.newContext({
    userAgent:
      "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0 Safari/537.36",
    locale: "en-US",
  });
  const page = await ctx.newPage();

  let advertiserName = "";
  let query = args.domain;
  try {
    if (!args.domain && args.company) {
      const cands = await resolveAdvertiser(page, args.company, args.country, args.timeout);
      if (cands.length === 0) {
        // Could not resolve — emit empty + candidate note rather than error.
        await browser.close();
        const empty = { advertiser_candidates: [], ads: [], note: "no advertiser resolved for company" };
        emit(args, empty.ads, empty);
        return;
      }
      if (cands.length > 1) {
        // Ambiguous — return candidate list for the caller to disambiguate.
        await browser.close();
        emit(args, [], { advertiser_candidates: cands, ads: [], note: "ambiguous company; pass --domain or rerun with a resolved advertiser" });
        return;
      }
      advertiserName = cands[0].advertiserName;
      query = cands[0].advertiserName || args.company;
    }

    const raw = await scrapeAds(page, query, args.country, args.maxAds, args.timeout);
    const ads = normalize(raw, advertiserName, args.maxAds);
    await browser.close();
    emit(args, ads, { ads });
  } catch (err) {
    await browser.close().catch(() => {});
    console.error(`ERROR: scrape failed: ${err.message}`);
    console.error("Hint: Transparency Center is anti-bot; retry with --proxy or fall back to an Apify Google-ads actor (APIFY_API_TOKEN).");
    process.exit(1);
  }
}

function emit(args, ads, full) {
  if (args.output === "summary") {
    if (!ads.length) {
      console.log("No Google ads found (advertiser may be unverified or inactive in this region).");
      return;
    }
    for (const a of ads) {
      console.log(`[${a.variantFormat} ${a.variantCount}v] ${a.advertiserName || a.advertiserId}`);
      console.log(`        ${a.variantContent.slice(0, 140)}`);
      console.log(`        ${a.originalUrl}`);
    }
    return;
  }
  const payload = JSON.stringify(full.advertiser_candidates !== undefined ? full : ads, null, 2);
  if (args.output && args.output !== "json") {
    fs.writeFileSync(args.output, payload + "\n");
    console.error(`${ads.length} ads -> ${args.output}`);
  } else {
    process.stdout.write(payload + "\n");
  }
}

main();
