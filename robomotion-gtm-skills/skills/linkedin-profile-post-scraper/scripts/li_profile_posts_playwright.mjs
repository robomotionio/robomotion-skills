#!/usr/bin/env node
// li_profile_posts_playwright.mjs — keyless LinkedIn profile-posts scraper (session-cookie path).
//
// The keyless degrade for profile_posts.py when APIFY_API_TOKEN is unset. Authenticates with
// an existing LinkedIn `li_at` session cookie (env LI_AT or --li-at), opens each profile's
// recent-activity feed, scrolls to load posts, and emits the raw actor-style shape that
// profile_posts.normalize() consumes. No LLM. Lower throughput than Apify; respect LinkedIn
// ToS and route through a proxy. Requires Playwright chromium: npx playwright install chromium
//
// Usage:
//   LI_AT=<cookie> node li_profile_posts_playwright.mjs --profiles "u1,u2" --max-posts 20
//   node li_profile_posts_playwright.mjs --profiles u1 --li-at <cookie> --output out.json
import { writeFileSync } from 'node:fs';

function parseArgs(argv) {
  const a = { profiles: '', maxPosts: 20, liAt: process.env.LI_AT || '', output: '-', timeout: 45000 };
  for (let i = 2; i < argv.length; i++) {
    const k = argv[i];
    if (k === '--profiles') a.profiles = argv[++i];
    else if (k === '--max-posts') a.maxPosts = parseInt(argv[++i], 10);
    else if (k === '--li-at') a.liAt = argv[++i];
    else if (k === '--output') a.output = argv[++i];
    else if (k === '--timeout') a.timeout = parseInt(argv[++i], 10);
    else if (k === '--help' || k === '-h') a.help = true;
  }
  return a;
}

const HELP = `li_profile_posts_playwright.mjs — keyless LinkedIn profile-posts scraper (cookie path).
  --profiles <u1,u2>    comma-separated canonical /in/<user> profile URLs (required)
  --max-posts <n>       cap per profile (default 20)
  --li-at <cookie>      li_at session cookie (or env LI_AT)
  --output <p>          JSON output path (default stdout)
  --timeout <ms>        per-page nav timeout (default 45000)`;

function activityUrl(profileUrl) {
  const base = profileUrl.replace(/\/+$/, '');
  return `${base}/recent-activity/all/`;
}

async function extractPosts(page, profileUrl, max, timeout) {
  await page.goto(activityUrl(profileUrl), { waitUntil: 'domcontentloaded', timeout });
  try { await page.waitForLoadState('networkidle', { timeout: 8000 }); } catch { /* keep going */ }
  await page.waitForTimeout(3000);

  // Scroll to lazy-load posts up to a bounded number of passes.
  for (let i = 0; i < 25; i++) {
    const have = await page.locator('div.feed-shared-update-v2, li.profile-creator-shared-feed-update__container').count();
    if (have >= max) break;
    await page.evaluate(() => window.scrollBy(0, window.innerHeight * 2));
    await page.waitForTimeout(1200);
  }

  return await page.evaluate((maxN) => {
    const clean = (s) => (s || '').replace(/\s+/g, ' ').trim();
    const num = (s) => {
      const m = clean(s).match(/([\d,.]+)\s*([KkMm]?)/);
      if (!m) return 0;
      let v = parseFloat(m[1].replace(/,/g, '')) || 0;
      if (/k/i.test(m[2])) v *= 1000; else if (/m/i.test(m[2])) v *= 1e6;
      return Math.round(v);
    };
    const nodes = Array.from(document.querySelectorAll(
      'div.feed-shared-update-v2, li.profile-creator-shared-feed-update__container'));
    const out = [];
    for (const n of nodes.slice(0, maxN)) {
      const text = clean((n.querySelector(
        '.update-components-text, .feed-shared-update-v2__description, .feed-shared-text') || {}).textContent);
      const reactEl = n.querySelector('.social-details-social-counts__reactions-count, [aria-label*="reaction"]');
      const cmtEl = n.querySelector('[aria-label*="comment"], .social-details-social-counts__comments');
      const linkEl = n.querySelector('a[href*="/feed/update/"], a[href*="activity-"]');
      if (!text && !linkEl) continue;
      out.push({
        text,
        numLikes: reactEl ? num(reactEl.textContent || reactEl.getAttribute('aria-label')) : 0,
        numComments: cmtEl ? num(cmtEl.textContent || cmtEl.getAttribute('aria-label')) : 0,
        url: linkEl ? linkEl.href.split('?')[0] : '',
        postedAtISO: '',
      });
    }
    return out;
  }, max);
}

async function main() {
  const a = parseArgs(process.argv);
  if (a.help || !a.profiles) { console.log(HELP); process.exit(a.help ? 0 : 1); }
  if (!a.liAt) { console.error('ERROR: no li_at session cookie (set LI_AT or --li-at).'); process.exit(2); }

  let chromium;
  try { ({ chromium } = await import('playwright')); }
  catch { console.error('ERROR: playwright not installed. Run: npx playwright install chromium && npm i playwright'); process.exit(2); }

  const profiles = a.profiles.split(',').map(s => s.trim()).filter(Boolean);
  const browser = await chromium.launch({ headless: true });
  const ctx = await browser.newContext({
    userAgent: 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0 Safari/537.36',
    locale: 'en-US', viewport: { width: 1366, height: 900 },
  });
  await ctx.addCookies([{ name: 'li_at', value: a.liAt, domain: '.linkedin.com', path: '/', httpOnly: true, secure: true }]);

  const out = [];
  for (const prof of profiles) {
    const page = await ctx.newPage();
    try {
      const posts = await extractPosts(page, prof, a.maxPosts, a.timeout);
      for (const p of posts) out.push({ ...p, authorName: '', author: prof, _profile: prof });
    } catch (e) {
      console.error(`WARN: profile scrape failed for ${prof}: ${String(e && e.message || e)}`);
    } finally { await page.close(); }
  }
  await browser.close();

  const blob = JSON.stringify(out, null, 2);
  if (a.output === '-') process.stdout.write(blob + '\n');
  else { writeFileSync(a.output, blob + '\n'); process.stderr.write(`${out.length} post(s) -> ${a.output}\n`); }
}

main().catch((e) => { console.error(e); process.exit(1); });
