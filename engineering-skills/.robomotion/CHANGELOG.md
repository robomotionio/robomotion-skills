# Changelog — engineering-skills

All notable Robomotion-side changes to the vendored `engineering-skills/` mirror.

The format roughly follows [Keep a Changelog](https://keepachangelog.com/).
**This is not upstream's changelog** — see
[`addyosmani/agent-skills`](https://github.com/addyosmani/agent-skills)
for the upstream history. This file tracks only what *we* shipped: vendoring
events, version pins, and Robomotion-side additions inside `.robomotion/`.

## [1.0.0] — 2026-05-26

### Added
- Vendored from `addyosmani/agent-skills@2a62238` — 23 production-grade
  engineering skills covering the full SDLC: define (interview-me,
  idea-refine, spec-driven-development), plan (planning-and-task-breakdown),
  build (incremental-implementation, test-driven-development,
  context-engineering, source-driven-development, doubt-driven-development,
  frontend-ui-engineering, api-and-interface-design), verify
  (browser-testing-with-devtools, debugging-and-error-recovery), review
  (code-review-and-quality, code-simplification, security-and-hardening,
  performance-optimization), ship (git-workflow-and-versioning,
  ci-cd-and-automation, deprecation-and-migration, documentation-and-adrs,
  shipping-and-launch), and the using-agent-skills meta-skill.
- `.robomotion/skill.yaml` — group metadata (name, version, author, source_url,
  license, summary, tags).
- `.robomotion/LICENSE` — verbatim copy of upstream MIT for stable discovery.
