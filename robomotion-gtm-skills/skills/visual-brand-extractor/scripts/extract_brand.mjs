#!/usr/bin/env node
/**
 * extract_brand.mjs — Render a site with Playwright and harvest its raw visual-identity
 * signals: CSS custom properties, color declarations (hex/rgb/hsl), font-family names,
 * Google Fonts / Fontshare / @font-face links, theme-color meta tags, Tailwind utility
 * classes, and basic layout/visual-pattern signals (border-radius, gradients, shadows).
 * Also captures a hero (above-the-fold) screenshot for downstream color sampling and the
 * agent's vision cross-check.
 *
 * Deterministic tool only. It does NOT classify color roles, pick fonts, or write the
 * vibe — the host agent does all of that from this JSON + the screenshot.
 *
 * Setup (note in SKILL.md):  npx playwright install chromium
 * Run:
 *   node extract_brand.mjs --url https://acme.com --client Acme \
 *     --screenshot hero.png --output signals.json
 */
import { writeFileSync } from "node:fs";

function parseArgs(argv) {
  const a = { url: "", pages: [], client: "", screenshot: "", output: "-", timeout: 30000 };
  for (let i = 0; i < argv.length; i++) {
    const t = argv[i];
    if (t === "--url") a.url = argv[++i];
    else if (t === "--client") a.client = argv[++i];
    else if (t === "--screenshot") a.screenshot = argv[++i];
    else if (t === "--output") a.output = argv[++i];
    else if (t === "--timeout") a.timeout = parseInt(argv[++i], 10) * 1000;
    else if (t === "--help" || t === "-h") a.help = true;
    else if (t === "--pages") { while (i + 1 < argv.length && !argv[i + 1].startsWith("--")) a.pages.push(argv[++i]); }
  }
  return a;
}

const HELP = `extract_brand.mjs — render a site and harvest visual-identity signals + hero screenshot.

  --url URL            homepage / landing page to extract [required]
  --client NAME        client name (for labeling) [required]
  --pages U1 U2 ...    up to 2 extra pages (product/blog/about) for richer extraction
  --screenshot PATH    write a hero (above-the-fold) PNG here (recommended)
  --output PATH        signals JSON path (default stdout)
  --timeout SECONDS    per-page nav timeout (default 30)
  --help               this help

Requires: npx playwright install chromium`;

// Runs in the page context: harvest CSS/font/color/meta/tailwind/layout signals.
function harvestInPage() {
  const colorRx = /#[0-9a-fA-F]{3,8}\b|rgba?\([^)]*\)|hsla?\([^)]*\)/g;
  const customProps = {};
  const colorFreq = {};
  const fonts = new Set();
  const tailwind = new Set();
  const fontLinks = [];
  const meta = {};
  const layout = { borderRadius: new Set(), gradients: 0, shadows: 0, animations: new Set() };

  // 1. CSS custom properties from :root computed style
  const rootStyle = getComputedStyle(document.documentElement);
  for (let i = 0; i < rootStyle.length; i++) {
    const name = rootStyle[i];
    if (name.startsWith("--")) {
      const val = rootStyle.getPropertyValue(name).trim();
      if (val) customProps[name] = val;
    }
  }

  // 2. meta tags
  document.querySelectorAll("meta[name='theme-color'], meta[name='msapplication-TileColor']")
    .forEach((m) => { meta[m.getAttribute("name")] = m.getAttribute("content"); });

  // 3. font + stylesheet links
  document.querySelectorAll("link[rel='stylesheet'], link[as='font'], link[href]").forEach((l) => {
    const href = l.getAttribute("href") || "";
    if (/fonts\.googleapis|fonts\.gstatic|fontshare|typekit|use\.typekit|fonts\.bunny/.test(href)) {
      fontLinks.push(href);
      const fam = href.match(/family=([^&:?]+)/i);
      if (fam) fam[1].split("|").forEach((f) => fonts.add(decodeURIComponent(f.replace(/\+/g, " "))));
    }
  });

  // 4. @font-face from stylesheets
  for (const sheet of document.styleSheets) {
    let rules;
    try { rules = sheet.cssRules; } catch { continue; }
    if (!rules) continue;
    for (const rule of rules) {
      if (rule.type === CSSRule.FONT_FACE_RULE) {
        const f = rule.style.getPropertyValue("font-family").replace(/['"]/g, "").trim();
        if (f) fonts.add(f);
      }
    }
  }

  // 5. Walk visible elements: colors, fonts, tailwind classes, layout signals.
  const els = document.querySelectorAll("body *");
  let scanned = 0;
  for (const el of els) {
    if (scanned++ > 4000) break;
    const cs = getComputedStyle(el);
    for (const prop of ["color", "backgroundColor", "borderColor", "fill", "stroke"]) {
      const v = cs[prop];
      if (v && v !== "rgba(0, 0, 0, 0)" && v !== "transparent") {
        (v.match(colorRx) || [v]).forEach((c) => { colorFreq[c] = (colorFreq[c] || 0) + 1; });
      }
    }
    const ff = cs.fontFamily;
    if (ff) ff.split(",")[0].replace(/['"]/g, "").trim() && fonts.add(ff.split(",")[0].replace(/['"]/g, "").trim());
    const br = cs.borderRadius;
    if (br && br !== "0px") layout.borderRadius.add(br);
    if (cs.backgroundImage && cs.backgroundImage.includes("gradient")) {
      layout.gradients++;
      (cs.backgroundImage.match(colorRx) || []).forEach((c) => { colorFreq[c] = (colorFreq[c] || 0) + 1; });
    }
    if (cs.boxShadow && cs.boxShadow !== "none") layout.shadows++;
    if (cs.animationName && cs.animationName !== "none") layout.animations.add(cs.animationName);
    const cls = el.getAttribute && el.getAttribute("class");
    if (cls && typeof cls === "string") {
      cls.split(/\s+/).forEach((c) => {
        if (/^(bg|text|border|from|via|to|fill|ring|shadow|rounded)-/.test(c)) tailwind.add(c);
      });
    }
  }

  // 6. inlined tailwind.config (rare but valuable)
  let tailwindConfig = "";
  document.querySelectorAll("script").forEach((s) => {
    const txt = s.textContent || "";
    if (/tailwind\.config\s*=/.test(txt)) tailwindConfig += txt.slice(0, 4000);
  });

  // rank colors by frequency
  const colors = Object.entries(colorFreq).sort((a, b) => b[1] - a[1])
    .slice(0, 40).map(([value, count]) => ({ value, count }));

  return {
    url: location.href,
    title: document.title,
    custom_properties: customProps,
    meta_colors: meta,
    colors_ranked: colors,
    fonts: [...fonts].slice(0, 25),
    font_links: [...new Set(fontLinks)],
    tailwind_classes: [...tailwind].slice(0, 120),
    tailwind_config_snippet: tailwindConfig,
    layout: {
      border_radius: [...layout.borderRadius].slice(0, 10),
      gradient_count: layout.gradients,
      shadow_count: layout.shadows,
      animations: [...layout.animations].slice(0, 10),
    },
  };
}

async function main() {
  const args = parseArgs(process.argv.slice(2));
  if (args.help || !args.url || !args.client) {
    console.log(HELP);
    process.exit(args.help ? 0 : 1);
  }

  let chromium;
  try { ({ chromium } = await import("playwright")); }
  catch {
    console.error("ERROR: playwright not installed. Run: npm i playwright && npx playwright install chromium");
    process.exit(2);
  }

  const browser = await chromium.launch({ headless: true });
  const ctx = await browser.newContext({
    viewport: { width: 1440, height: 900 },
    userAgent: "robomotion-gtm-skills/visual-brand-extractor (+https://agentskills.io)",
  });

  const targets = [args.url, ...args.pages].slice(0, 3);
  const pages = [];
  const errors = [];
  let firstScreenshotDone = false;

  for (const url of targets) {
    const page = await ctx.newPage();
    try {
      await page.goto(url, { waitUntil: "networkidle", timeout: args.timeout });
      await page.waitForTimeout(800); // let webfonts/CSS settle
      const signals = await page.evaluate(harvestInPage);
      pages.push(signals);
      if (!firstScreenshotDone && args.screenshot) {
        await page.screenshot({ path: args.screenshot, clip: { x: 0, y: 0, width: 1440, height: 900 } });
        firstScreenshotDone = true;
      }
    } catch (e) {
      errors.push({ url, error: String(e.message || e) });
    } finally {
      await page.close();
    }
  }

  await browser.close();
  const out = {
    client: args.client,
    primary_url: args.url,
    screenshot: firstScreenshotDone ? args.screenshot : "",
    pages,
    errors,
  };
  const payload = JSON.stringify(out, null, 2);
  if (args.output === "-") process.stdout.write(payload + "\n");
  else { writeFileSync(args.output, payload + "\n"); console.error(`${pages.length}/${targets.length} pages -> ${args.output}${firstScreenshotDone ? `  (screenshot: ${args.screenshot})` : ""}`); }
}

main().catch((e) => { console.error("ERROR:", e); process.exit(1); });
