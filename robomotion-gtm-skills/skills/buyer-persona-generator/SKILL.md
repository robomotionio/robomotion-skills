---
name: buyer-persona-generator
description: Research a company's site and synthesize 4-6 detailed, realistic buyer personas (demographics, motivations, skepticism profile, ranked decision criteria, language patterns). Use to build reusable ICP personas that downstream skills load to evaluate content, messaging, sites, and campaigns through buyer eyes. Keyless research; the agent does the synthesis.
metadata:
  version: 1.0.1
  category: research
  type: capability
---

# Buyer Persona Generator

Research a company's buyers and synthesize 4-6 grounded, specific buyer personas. The
bundled script does keyless I/O (fetch the company site into a text bundle); **you, the
agent, do all the segmentation and persona synthesis** from that bundle plus your own
search/research, then run the diversity coverage check.

## When to use

- "Build ICP personas for [company]." / "Who are our buyers really?"
- Upstream of `icp-website-audit` (it calls this when personas don't yet exist).
- Any messaging/positioning work that needs a grounded model of how buyers evaluate.

## How to run

### Step 1 — research the company site (deterministic script)

```bash
python3 ${SKILL_DIR}/scripts/research_company.py \
  --url https://example.com \
  --company "Example" \
  --max-pages 8 \
  --output ${WORKSPACE}/company_bundle.json
```

Python 3 stdlib only — no install. It fetches the homepage and discovers + fetches
same-domain high-signal pages (pricing, about, customers/case-studies, solutions,
product, "who it's for", industries) into one JSON bundle of `{url, title, headings,
text}`. For JS-heavy / auth-walled pages that come back thin, fall back to a
`web-automation` (Playwright + Robomotion Proxy) fetch, and use an `apify` review actor
only as a hostile-site fallback for G2/Capterra/TrustRadius.

### Step 2 — signal search (you, the agent)

Run searches with whatever search tool you have: `"[company] customers"`, `"case
studies"`, `"[company] reviews"` (G2/Capterra/TrustRadius), `"[company] vs"`
(comparisons reveal segments), `"[company] jobs"`. Fold the results into your context.

### Step 3 — extract, segment, synthesize (you, the agent)

From the bundle + searches, extract: problem solved, pricing/packaging (→ ACV & buyer
type), verticals, target sizes, roles/titles in case studies, GTM motion. Identify 4-6
distinct segments and write a rich synthetic persona for each per the schema below.

### Step 4 — diversity check (you, the agent)

Enforce coverage: at least one technical, one business, one skeptical, one
junior/researcher persona; cover multiple company tiers if the company serves them.
If `known_icps` were supplied, skip discovery and synthesize directly against them.

## Outputs

Write all three to `${WORKSPACE}` (and attach to the Agent Teams channel as a reusable
asset):

- `personas.json` — array; each persona: `id, name, segment, title, company_profile,
  demographics, situation, pain_points, buying_trigger, decision_criteria (ranked),
  skepticism_profile, technical_sophistication, language, evaluation_behavior`.
- `personas.md` — human-readable prose profiles.
- `segments.md` — summary table + the diversity coverage check.

Skepticism profile is the highest-value field: every persona needs a clear "what would
make them NOT buy" and a default vendor assumption.

## Credentials / env

- **Required:** none. The research script is keyless; persona synthesis is your job as
  the agent, so no LLM key is needed in the script layer.
- **Optional:** if `APIFY_API_TOKEN` is set → Apify review-site (G2/Capterra/TrustRadius)
  scraping for richer voice-of-customer input; if not → keyless direct fetch / search
  snippets (default). `PINECONE_API_KEY` / `QDRANT_URL` — if set → semantic persona dedup;
  if not → skip dedup (default). The default keyless serp/fetch path needs no key.

## Notes & edge cases

- Specificity beats abstraction ("Sarah, Sr. Demand Gen at a 50-person B2B SaaS who just
  lost her SDR team", not "Marketing Manager"). Spend real effort in research — don't
  stop at the homepage; the script already pulls deeper pages for you.
- `research_company.py` caps each page at 20 KB of text and 2 MB of HTML, fetches up to
  `--max-pages` deep pages, and backs off on HTTP 429/503.
- No paid lead/enrichment API is required — this is research + synthesis only.
