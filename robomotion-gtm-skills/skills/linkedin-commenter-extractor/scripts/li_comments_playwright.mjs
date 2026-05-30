#!/usr/bin/env node
// li_comments_playwright.mjs — keyless LinkedIn post-comments scraper (session-cookie path).
//
// The keyless degrade for extract_commenters.py when APIFY_API_TOKEN is unset. Authenticates
// with an existing LinkedIn `li_at` session cookie (env LI_AT or --li-at), opens each post,
// expands/scrolls the comment thread, and emits the same shape extract_commenters.py uses.
// No LLM — just navigate, expand, extract. Lower throughput than Apify; respect LinkedIn ToS
// and route through a proxy. Requires Playwright chromium:  npx playwright install chromium
//
// Usage:
//   LI_AT=<cookie> node li_comments_playwright.mjs --post-urls "u1,u2" --max-comments 100
//   node li_comments_playwright.mjs --post-urls u1 --li-at <cookie> --output out.json
import { writeFileSync } from 'node:fs';

function parseArgs(argv) {
  const a = { postUrls: '', maxComments: 100, liAt: process.env.LI_AT || '', output: '-', timeout: 45000 };
  for (let i = 2; i < argv.length; i++) {
    const k = argv[i];
    if (k === '--post-urls') a.postUrls = argv[++i];
    else if (k === '--max-comments') a.maxComments = parseInt(argv[++i], 10);
    else if (k === '--li-at') a.liAt = argv[++i];
    else if (k === '--output') a.output = argv[++i];
    else if (k === '--timeout') a.timeout = parseInt(argv[++i], 10);
    else if (k === '--help' || k === '-h') a.help = true;
  }
  return a;
}

const HELP = `li_comments_playwright.mjs — keyless LinkedIn post-comments scraper (cookie path).
  --post-urls <u1,u2>   comma-separated LinkedIn post URLs (required)
  --max-comments <n>    cap per post (default 100)
  --li-at <cookie>      li_at session cookie (or env LI_AT)
  --output <p>          JSON output path (default stdout)
  --timeout <ms>        per-page nav timeout (default 45000)`;

function splitHeadline(headline) {
  if (!headline) return ['', ''];
  for (const sep of [' at ', ' @ ', ' | ']) {
    const idx = headline.indexOf(sep);
    if (idx !== -1) return [headline.slice(0, idx).trim(), headline.slice(idx + sep.length).trim()];
  }
  return ['', ''];
}

async function extractComments(page, url, max, timeout) {
  await page.goto(url, { waitUntil: 'domcontentloaded', timeout });
  try { await page.waitForLoadState('networkidle', { timeout: 8000 }); } catch { /* keep going */ }
  await page.waitForTimeout(3000);

  // Expand the comment thread: click "load more comments" up to a bounded number of times.
  for (let i = 0; i < 20; i++) {
    const btn = page.locator('button:has-text("more comments"), button:has-text("Load more")').first();
    if (await btn.count() === 0) break;
    try { await btn.click({ timeout: 3000 }); await page.waitForTimeout(1500); } catch { break; }
    const have = await page.locator('article.comments-comment-entity, .comments-comment-item').count();
    if (have >= max) break;
  }

  return await page.evaluate((maxN) => {
    const clean = (s) => (s || '').replace(/\s+/g, ' ').trim();
    const nodes = Array.from(document.querySelectorAll(
      'article.comments-comment-entity, .comments-comment-item, .comments-comment-entity'));
    const out = [];
    for (const n of nodes.slice(0, maxN)) {
      const name = clean((n.querySelector(
        '.comments-comment-meta__description-title, .comments-post-meta__name-text, [class*="commenter"] [aria-hidden="true"]') || {}).textContent);
      const headline = clean((n.querySelector(
        '.comments-comment-meta__description-subtitle, .comments-post-meta__headline') || {}).textContent);
      const link = n.querySelector('a[href*="/in/"]');
      const text = clean((n.querySelector(
        '.comments-comment-item__main-content, .comments-comment-entity__content, .update-components-text') || {}).textContent);
      if (!name && !link) continue;
      out.push({ name, headline, profileUrl: link ? link.href.split('?')[0] : '', text });
    }
    return out;
  }, max);
}

async function main() {
  const a = parseArgs(process.argv);
  if (a.help || !a.postUrls) { console.log(HELP); process.exit(a.help ? 0 : 1); }
  if (!a.liAt) { console.error('ERROR: no li_at session cookie (set LI_AT or --li-at).'); process.exit(2); }

  let chromium;
  try { ({ chromium } = await import('playwright')); }
  catch { console.error('ERROR: playwright not installed. Run: npx playwright install chromium && npm i playwright'); process.exit(2); }

  const urls = a.postUrls.split(',').map(s => s.trim()).filter(Boolean);
  const browser = await chromium.launch({ headless: true });
  const ctx = await browser.newContext({
    userAgent: 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0 Safari/537.36',
    locale: 'en-US', viewport: { width: 1366, height: 900 },
  });
  await ctx.addCookies([{ name: 'li_at', value: a.liAt, domain: '.linkedin.com', path: '/', httpOnly: true, secure: true }]);

  const out = [];
  for (const url of urls) {
    const page = await ctx.newPage();
    try {
      const rows = await extractComments(page, url, a.maxComments, a.timeout);
      for (const c of rows) {
        const [title, company] = splitHeadline(c.headline);
        out.push({ name: c.name, headline: c.headline, title, company,
          linkedin_url: c.profileUrl, comment_text: c.text, post_url: url, profile_image_url: '' });
      }
    } catch (e) {
      console.error(`WARN: comment scrape failed for ${url}: ${String(e && e.message || e)}`);
    } finally { await page.close(); }
  }
  await browser.close();

  const blob = JSON.stringify(out, null, 2);
  if (a.output === '-') process.stdout.write(blob + '\n');
  else { writeFileSync(a.output, blob + '\n'); process.stderr.write(`${out.length} commenter(s) -> ${a.output}\n`); }
}

main().catch((e) => { console.error(e); process.exit(1); });
