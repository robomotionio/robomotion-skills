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
- Added `skills/research-keywords/env.optional` — `SERPAPI_KEY`, the only env var any
  bundled script reads (`scripts/keyword-explorer.mjs`, `scripts/serp-analyzer.mjs`,
  both `process.env.SERPAPI_KEY || ""` → optional, free mode without it). No
  `env.required` anywhere; every other skill is pure-knowledge or runs a zero-config
  Node script (`audit-website-aeo/scripts/aeo-audit.mjs`).
