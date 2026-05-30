---
name: tech-stack-teardown
description: Reverse-engineer a company's sales/marketing/outbound tech stack from public signals only — no login, keyless-first. Detects 200+ technologies (CRMs & marketing automation, ad pixels, CDP/ABM, analytics, A/B-testing, chat/support, CMS, ecommerce, payments, consent/CMP, email-capture, reviews, scheduling, forms, video, heatmaps) by fusing FOUR independent signals: HTML source, HTTP headers/cookies, rendered third-party network requests (Playwright), and DNS (MX/SPF/DKIM/DMARC/TXT). Also EXTRACTS account/pixel IDs (GA4 G-, GTM-, Meta Pixel, HubSpot portal, UA-, LinkedIn partner, Marketo Munchkin, Segment, +20 more) into an attribution fingerprint so two teardowns sharing an ID can be linked to the same owner/agency. Merges into one confidence-ranked profile, infers the go-to-market MOTION, assesses email-auth deliverability, supports change-tracking via snapshot/diff. Single company or batch. Optional Apify/BuiltWith key for enrichment only.
metadata:
  version: 2.1.0
  category: competitive-intel
  type: capability
---

# Tech Stack Teardown

Detect a company's GTM stack from public signals — **keyless-first, four independent
detection signals**, merged into one profile. No single layer sees everything: raw HTML
misses tag-manager-injected tools, headers reveal CDN/platform/cookies that HTML hides,
the rendered browser sees every third-party request and `window` global, and **DNS doesn't
lie** about who sends a company's mail. The scripts collect and merge deterministically;
**you, the agent, write the narrative report** from the unified profile + motion inference.

## The four detection signals

| # | Signal | Script | What it catches that others miss |
|---|--------|--------|----------------------------------|
| 1 | **HTML source** | `source_inspect.py` | script-src URLs, meta generator, inline globals, cookie names — keyless, instant |
| 2 | **HTTP headers + cookies** | `fetch_headers.py` | CDN/hosting (Cloudflare/Vercel/Netlify/Fastly/CloudFront/Akamai), platform (`x-shopify-stage`), session cookies (`__hstc`, `_mkto_trk`, `intercom-id`), security posture |
| 3 | **Rendered requests** (most reliable) | `detect_requests.mjs` | the **modern method** — loads the page in Chromium, collects every third-party request hostname + probes `window` globals (`dataLayer`, `fbq`, `_hsq`, `Munchkin`, `Intercom`, `ttq`…); catches everything a tag manager injects |
| 4 | **DNS** (highest-signal email layer) | `dns_scan.py` | MX→email provider, SPF includes→senders, DKIM selectors→which tools sign mail, DMARC policy+rua, TXT verification tokens→vendors |

## Account/pixel-ID extraction & attribution fingerprint (v2.1.0)

Detecting the **vendor** is table stakes; the high-value move is pulling the **specific
account/pixel ID** a vendor's snippet exposes. ~29 high-value technologies now carry an
`id_pattern` (a capture-group regex run against raw + rendered HTML and request URLs). Every
extracted ID is collected into an **attribution fingerprint** in the JSON and a dedicated
markdown section.

Why it matters — **cross-company attribution**: IDs are stable and often shared.
- Two domains loading the **same `GTM-XXXX` container** or **`G-XXXX` GA4 stream** are
  almost certainly the same owner, agency, or parent company (one team manages both tags).
- A shared **Meta Pixel ID** links a brand's microsites / landing-page domains / shadow funnels.
- A **HubSpot portal ID** ties together every property a single HubSpot account powers.
- Run a teardown on each domain, then `grep` the `attribution_fingerprint.flat` lists for an
  intersection — any shared `tech=value` is a strong ownership link.

An `id_pattern` hit is itself strong evidence the tech is present, so an ID match alone
promotes the tech into the detected stack (even if no request-domain/global signal fired).

```bash
# extract IDs (keyless, source layer only):
python3 ${SKILL_DIR}/scripts/source_inspect.py --domain example.com | jq '.account_ids'

# full teardown surfaces the fingerprint in JSON (.attribution_fingerprint) and the .md report:
python3 ${SKILL_DIR}/scripts/teardown.py --domain example.com --no-render --md ${WORKSPACE}/ex.md
jq -r '.attribution_fingerprint.flat[]' ${WORKSPACE}/ex.json   # compare across domains
```

### Account/pixel-ID format cheat-sheet
| Tech | ID format | Example | Where it lives |
|---|---|---|---|
| Google Analytics 4 | `G-[A-Z0-9]{6,}` | `G-ABC1234XYZ` | `gtag('config',…)` / gtag src |
| Universal Analytics | `UA-\d+-\d+` | `UA-11757081-1` | inline `ga()` / gtag |
| Google Tag Manager | `GTM-[A-Z0-9]{4,}` | `GTM-N5LT88` | `gtm.js?id=` |
| Google Ads | `AW-\d+` | `AW-123456789` | gtag conversion |
| Meta/Facebook Pixel | `\d{6,}` | `1234567890` | `fbq('init',…)` / `facebook.com/tr?id=` |
| HubSpot (portal/hub) | `\d{4,}` | `2345678` | `js.hs-scripts.com/<id>.js` |
| LinkedIn Insight | `\d{4,}` | `987654` | `_linkedin_partner_id = "…"` |
| Marketo Munchkin | `\d{3}-[A-Z]{3}-\d{3}` | `123-ABC-456` | `Munchkin.init('…')` |
| Hotjar | `\d{5,}` | `1234567` | `hjid:` / `hotjar-<id>.js` |
| Intercom | `[a-z0-9]{6,10}` | `abcd1234` | `app_id:` / `widget.intercom.io/widget/<id>` |
| Segment | write key | `AbCdEf…` | `analytics.load('…')` / `cdn.segment.com/analytics.js/v1/<key>/` |
| Mixpanel | 32-hex / token | `…` | `mixpanel.init('…')` |
| Amplitude | `[0-9a-f]{32}` | `…` | `amplitude…init('…')` |
| TikTok Pixel | `[A-Z0-9]{16,24}` | `C…` | `ttq.load('…')` / `sdkid=` |
| X Pixel | `[a-z0-9]{4,8}` | `o1abc` | `twq('config','…')` |
| Pinterest Tag | `\d{10,}` | `2612345678901` | `pintrk('load','…')` / `tid=` |
| Klaviyo | 6-char company ID | `Ab3Xyz` | `klaviyo.com/onsite/js/<id>` |
| Optimizely | numeric project | `5113954737848320` | `cdn.optimizely.com/js/<id>.js` |
| Drift | embed/app id | `…` | `drift.load('…')` / `js.driftt.com/include/…/<id>.js` |
| Stripe | `pk_live_\w+` (publishable only) | `pk_live_51…` | inline (LIVE publishable key only — never secret) |
| Crazy Egg | account id | `…` | `script.crazyegg.com/pages/scripts/<id>/…` |
| FullStory | org id | `…` | `_fs_org = '…'` |
| Microsoft Clarity | `[a-z0-9]{8,12}` | `…` | `clarity.ms/tag/<id>` |
| VWO | numeric account | `…` | `account_id=` / `_vwo_code` |
| Heap | app/env id | `…` | `heap.load('…')` |
| Pendo | API key (uuid) | `…` | `cdn.pendo.io/agent/static/<key>/pendo.js` |
| PostHog | `phc_\w+` | `phc_AbCd…` | `posthog.init('…')` |

> Only **public, client-side** IDs are extracted (e.g. Stripe **publishable** `pk_live_`, never
> a secret key). These are values any visitor's browser already sees.

## When to use

- "What tools does [company] use?" / "Tear down [company]'s sales & marketing stack."
- "Are these two domains run by the same company/agency?" — compare attribution fingerprints.
- "What's [company]'s GTM motion?" — the motion-inference layer answers this from the stack.
- "Is [company]'s email sending compliant?" (SPF/DKIM/DMARC + blacklist assessment).
- Competitive/prospect recon, deliverability assessment, batch profiling, change-tracking a target.

## How to run

### One-shot (recommended): the orchestrator

`teardown.py` runs all four signals, merges them, infers the GTM motion, and emits JSON + markdown.

```bash
# keyless, full (DNS + source + headers + rendered). Rendered layer auto-skips if Playwright absent.
npx playwright install chromium     # one-time, enables signal #3
python3 ${SKILL_DIR}/scripts/teardown.py --domain example.com \
  --json ${WORKSPACE}/example.json --md ${WORKSPACE}/example.md

# fastest keyless mode (skip the browser layer):
python3 ${SKILL_DIR}/scripts/teardown.py --domain example.com --no-render \
  --json ${WORKSPACE}/example.json
```

Flags: `--no-render` (skip Playwright), `--no-dns`, `--no-blacklist`, `--render-wait <ms>`.
For a **batch**, loop per domain and have the agent build the comparison table.

### Change tracking (snapshot / diff)

```bash
# week 1 — save a snapshot:
python3 ${SKILL_DIR}/scripts/teardown.py --domain example.com --no-render \
  --snapshot ${WORKSPACE}/example_w1.json --json -

# week 2 — diff against it (added/removed tools + motion shifts):
python3 ${SKILL_DIR}/scripts/teardown.py --domain example.com --no-render \
  --diff ${WORKSPACE}/example_w1.json --json ${WORKSPACE}/example_w2.json
```

### Run a single signal (for targeted recon)

```bash
python3 ${SKILL_DIR}/scripts/source_inspect.py --domain example.com   # signal 1
python3 ${SKILL_DIR}/scripts/fetch_headers.py  --url    example.com   # signal 2
node    ${SKILL_DIR}/scripts/detect_requests.mjs --url https://example.com --wait 5000  # signal 3
python3 ${SKILL_DIR}/scripts/dns_scan.py --domain example.com         # signal 4
```

All four read the bundled `${SKILL_DIR}/scripts/signatures.json` (200+ technologies). Pass
`--signatures <path>` to override.

### GTM motion inference

`teardown.py` reads the merged stack and infers the go-to-market motion(s), each with
matched tools + a confidence score:

| Motion | Trigger pattern (examples) |
|--------|----------------------------|
| **Enterprise ABM / sales-led** | Marketo/Eloqua/Pardot + Salesforce + 6sense/Demandbase + LinkedIn/Bing + OneTrust |
| **Inbound / PLG sales-assist** | HubSpot + Calendly/Chili Piper + Drift/Intercom + Koala/Warmly |
| **Product-led growth (PLG)** | Amplitude/Mixpanel/PostHog + LaunchDarkly/Statsig + Stripe/Paddle + Segment |
| **DTC / ecommerce lifecycle** | Shopify/Woo + Klaviyo + Recharge + Yotpo/Okendo + Meta/TikTok pixel |
| **Outbound SDR / cold-email** | Salesloft/Outreach + Apollo/ZoomInfo/RB2B/Clearbit + Smartlead/Instantly |
| **Content / creator-led** | Ghost/WordPress + Substack/Beehiiv/ConvertKit + Outbrain/Taboola |
| **CRO / paid-acquisition** | Optimizely/VWO + Hotjar/FullStory + Unbounce/Instapage + AdRoll/Criteo |

### Optional enrichment (paid — not required)

The four keyless signals already produce a strong profile (and the 202-sig DB + ID extraction
cover the high-value GTM stack). For **long-tail breadth** — obscure / dynamically-loaded tech
the bundled DB may miss — an optional Wappalyzer-style **Apify** actor can be layered in when
`APIFY_API_TOKEN` is set. **Enrichment only**; keyless-first is always primary and the skill
never depends on it.

```bash
# bundled helper — gated on APIFY_API_TOKEN; prints a clean "skipped" record (exit 0) without it.
# Uses a PUBLIC Apify Store technology-profiler actor (override with --actor user/actor-name):
APIFY_API_TOKEN=... python3 ${SKILL_DIR}/scripts/apify_profiler.py --url example.com \
  --output ${WORKSPACE}/example_apify.json

# or fold it straight into the orchestrator (adds Apify-only techs as a low-confidence layer):
APIFY_API_TOKEN=... python3 ${SKILL_DIR}/scripts/teardown.py --domain example.com --apify \
  --json ${WORKSPACE}/example.json
```

`apify_profiler.py` normalizes the actor's varied output shapes into `{detected:[{name,
category}]}`. The default actor is a public Store profiler; pick any public technology-profiler
actor you trust via `--actor` or `APIFY_TECH_ACTOR`. A **BuiltWith** lookup
(`BUILTWITH_API_KEY`) is an alternate profiler you can layer in the same way.

### Report (you, the agent)

`teardown.py --md` writes a structured markdown teardown (motion inference → detected stack
by category with evidence/confidence → email-auth & deliverability → collection notes). For
a single domain that's often enough; **enrich it** with: public complaint/stack-mention web
search (`"[domain]" spam OR blacklist`, `"[company]" + tool names`), and for batches a
comparative summary table across domains.

## Outputs

- `${WORKSPACE}/*.json` — the unified profile (detected stack with per-tech `account_id`/
  `account_ids`, by-category, motion inference, `attribution_fingerprint`, raw per-signal data)
  and any per-signal JSON.
- `${WORKSPACE}/*.md` — the markdown teardown (orchestrator-generated; agent enriches).
- `${WORKSPACE}/*_snap.json` — saved snapshots for `--diff` change tracking.

## Credentials / env

- **Required:** none. All four signals are keyless. `dig` (bind/dnsutils) must be on PATH for
  the DNS layer; Playwright chromium (`npx playwright install chromium`) enables signal #3 —
  if absent, the rendered layer auto-skips and the other three still run.
- **Optional:** `APIFY_API_TOKEN` / `BUILTWITH_API_KEY` — enrichment-only technology profiler.
  Free mode already yields a strong report.

## Cheat-sheet reference tables

### Common SPF includes → sender
| include: | tool |
|---|---|
| `_spf.google.com` | Google Workspace |
| `spf.protection.outlook.com` | Microsoft 365 |
| `amazonses.com` | Amazon SES |
| `sendgrid.net` | SendGrid |
| `mailgun.org` | Mailgun |
| `spf.mandrillapp.com` | Mandrill (Mailchimp Transactional) |
| `servers.mcsv.net` | Mailchimp |
| `mktomail.com` / `mktdns.com` | Marketo |
| `_spf.hubspot.com` / `spf.hubspotemail.net` | HubSpot |
| `et._spf.pardot.com` | Pardot (Salesforce) |
| `_spf.salesloft.com` | Salesloft |
| `spf.sleadtrack.com` | Smartlead |
| `_spf.instantly.ai` | Instantly |
| `_spf.klaviyo.com` / `klaviyomail.com` | Klaviyo |
| `spf.mtasv.net` | Postmark |
| `pphosted.com` | Proofpoint |
| `mimecast.com` | Mimecast |

### Common DKIM selectors → tool
| selector | tool |
|---|---|
| `google` | Google Workspace |
| `selector1` / `selector2` | Microsoft 365 |
| `k1` | Mailchimp / Klaviyo |
| `klaviyo` | Klaviyo |
| `pm` / `pm-bounces` | Postmark |
| `scph0` / `scph1` | SparkPost |
| `hs1` / `hs2` | HubSpot |
| `sendgrid` / `sg` | SendGrid |
| `mandrill` | Mandrill |
| `mte1` / `mte2` | Marketo |
| `createsend` / `cm` | Campaign Monitor |
| `zoho` | Zoho Mail |
| `intercom` | Intercom |

### High-value vendor request-domains (rendered layer)
| request domain | tool |
|---|---|
| `googletagmanager.com` | Google Tag Manager |
| `connect.facebook.net` / `facebook.com/tr` | Meta Pixel |
| `px.ads.linkedin.com` / `snap.licdn.com` | LinkedIn Insight |
| `js.hs-scripts.com` / `hsforms.net` | HubSpot |
| `munchkin.marketo.net` | Marketo |
| `6sc.co` | 6sense |
| `company-target.com` | Demandbase |
| `widget.intercom.io` | Intercom |
| `js.driftt.com` | Drift |
| `cdn.segment.com` | Segment |
| `cdn.amplitude.com` | Amplitude |
| `static.klaviyo.com` | Klaviyo |
| `cdn.shopify.com` | Shopify |
| `js.stripe.com` | Stripe |
| `assets.calendly.com` | Calendly |
| `cdn.cookielaw.org` | OneTrust |

## Notes & edge cases

- **DNS is the highest-signal email layer** — SPF/DKIM "don't lie." Lead detection from it.
- **Wildcard `_domainkey`:** some domains answer *every* DKIM selector. `dns_scan.py` probes a
  random selector first; if it resolves, it sets `dkim_wildcard:true` and suppresses the
  (meaningless) per-selector tool map. Trust SPF/MX/TXT instead for those domains.
- **"SPF shows Google only but they use Smartlead/Instantly"** is normal — those relay through
  Google Workspace via SMTP. Confirm via `open.sleadtrack.com` in TXT/source or a separate
  cold-outbound domain (`dns_scan.py` probes `get[brand].com`/`try[brand].com`-style variants).
- **Confidence:** combines independent signals; multi-layer corroboration (e.g. rendered+source)
  bumps it. `request_domain`/`global_js`/`meta_generator` are strong; bare `html` substrings are weak.
- **"No tools detected"** can mean early-stage or tools that leave no public trace (Sales Nav,
  Clay, Apollo-for-prospecting) — say so rather than implying none exist.
- **Parked/for-sale domains** (wildcard DNS, Afternic redirect) — try `.co`/`.com`/`.io` variants.
- The rendered layer needs Chromium; for batches > ~10 domains it dominates runtime — use
  `--no-render` for a fast keyless pass, then re-render only the domains that warrant it.
