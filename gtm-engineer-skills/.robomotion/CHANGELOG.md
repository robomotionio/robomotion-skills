# Changelog — gtm-engineer-skills

## [1.0.0] — 2026-05-30
- Vendored from onvoyage-ai/gtm-engineer-skills@25ee0df (12 skills: research-brand,
  research-keywords, reddit-opportunity-research, geo-content-research,
  geo-content-planning, write-seo-geo-content, create-geo-charts, audit-content,
  build-backlinks, build-resource-pages, audit-website-aeo, improve-aeo-geo).
- **Structural adaptation (content verbatim):** upstream ships each skill folder at
  the repo root; our group discovery contract (`build-index.py` → `discover_inner_skills`)
  only walks `<group>/skills/<name>/`. The 12 skill folders were relocated under
  `skills/` **with their contents byte-for-byte unchanged**. Shared upstream files
  (`README.md`, `AGENT.md`, `CONTRIBUTING.md`, `TESTING.md`, `package.json`, `evals/`,
  `assets/`) stay at the group root. A bump re-applies the same root→`skills/` move.
- Added `.robomotion/skill.yaml`, `.robomotion/LICENSE` (verbatim MIT copy),
  this changelog.
- Added `skills/research-keywords/env.required` — `SERPAPI_KEY`. Classified by tracing
  the downstream gate, not the access idiom: both scripts read `process.env.SERPAPI_KEY
  || ""`, but `scripts/serp-analyzer.mjs` then does `if (!SERPAPI_KEY) process.exit(1)`
  (docstring: "Requires SERPAPI_KEY") → required. `scripts/keyword-explorer.mjs` has a
  genuine free-autocomplete fallback, so partial keyword research works without it, but
  the SERP-competition half of the skill is dead → the var is REQUIRED at skill level.
  Every other skill is pure-knowledge or runs a zero-config Node script
  (`audit-website-aeo/scripts/aeo-audit.mjs`).
