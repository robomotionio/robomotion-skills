---
name: icp-identification
description: The entry point for any "find me leads / map my market / who should I sell to" request. Researches a company or idea, defines a structured Ideal Customer Profile (explicit inclusion AND exclusion criteria), then routes to the right next step (TAM mapping or direct lead finding) with a handoff context block. Keyless research; the ICP synthesis and routing are the agent's.
metadata:
  version: 1.0.1
  category: research
  type: capability
---

# ICP Identification

Research a company/idea (deterministic, keyless page fetch) then **you, the agent, define
the ICP** — inclusion + exclusion tables — validate it with the user, and emit a handoff
context block for the downstream lead/TAM skill.

## When to use

- "Find me leads", "who should I sell to", "who is my ICP?", "map my TAM".
- User provides a company URL/idea and asks for leads or market mapping.
- Sits upstream of all lead-finding and TAM-building skills.

## How to run

### Step 1 — research the company/idea (deterministic script)

```bash
python3 ${SKILL_DIR}/scripts/research_company.py \
  --url https://example.com --company "Example" \
  --max-pages 8 --output ${WORKSPACE}/company_bundle.json
```

Python 3 stdlib only. Fetches the homepage + same-domain high-signal pages (pricing,
about, product, solutions, customers, industries) into a `{url, title, headings, text}`
bundle. **Research the URL before asking the user anything answerable from the site.**

### Step 2 — research market + competitors + buyer signals (you, the agent)

With your search tool: company value prop/pricing (fill gaps the site didn't answer),
market/category + growth stage, top 3-5 competitors (`"[company] vs"`, `"[category]
competitors"`), buyer signals (titles, purchase triggers). Optionally use
`perplexity`/`tavily` only if a cited live-web market answer is needed beyond search.

### Step 3 — synthesize + validate the ICP (you, the agent)

Write a 5-10 bullet research summary; present for validation. Then define the ICP as two
explicit tables:

- **Inclusion:** titles, seniority, company size, industry, region, signals.
- **Exclusion:** titles/industries/company types/sizes/specific companies that are NOT a fit.

Keep filter values specific (avoid keyword stuffing). Iterate with the user until approved.
Exclusions are first-class — they prevent noisy downstream results.

### Step 4 — choose path + hand off (you, the agent)

Recommend TAM mapping (account-first) or lead finding (contact-first) based on ICP +
company stage. Emit the ICP context block (Include + Exclude) as JSON so the downstream
skill skips redundant intake.

## Outputs

- A validated ICP definition (inclusion table + exclusion table), a research summary, the
  chosen path, and a handoff context block carrying both criteria. Returned in-chat for
  confirmation and persisted as a workspace asset / Agent Teams attachment.

## Credentials / env

- **Required:** none. The research script is keyless; the ICP synthesis is your job as the
  agent (no LLM key in the script layer).
- **Optional:** if `PERPLEXITY_API_KEY` / `TAVILY_API_KEY` is set → cited answer-engine
  market-sizing; if not → keyless serp/fetch research the agent summarizes (default). The
  default keyless path needs no key.

## Notes & edge cases

- Every intake answer should sharpen a search/exclusion filter; probe vague answers into
  concrete filter values, not generic strategy questions.
- This skill defines, but does not execute, lead finding — the heavy lifting (Apollo,
  scraping) happens in the downstream skill it hands off to (e.g. `apollo-lead-finder`).
- `research_company.py` caps each page at 20 KB of text, fetches up to `--max-pages` deep
  pages, and backs off on HTTP 429/503.
