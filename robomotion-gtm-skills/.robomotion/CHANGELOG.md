# Changelog — robomotion-gtm-skills

## [1.1.0] - 2026-07-27

- Added Xquik X Follower Scraper for audience exports and overlap analysis.
- Updated X mention tracking to use Xquik X Tweet Scraper.
- Replaced legacy Actor routes and token query strings with current Apify API calls.
- Added server-side charge limits and complete terminal-state handling.

## [1.0.0] — 2026-05-30
- First-party Robomotion GTM skill group: 108 skills across 9 categories
  (ads, brand, competitive-intel, content, lead-generation, monitoring,
  outreach, research, seo).
- agentskills.io `SKILL.md` frontmatter + per-skill `env.required` / `env.optional`.
- Keyless-first: every external/paid service is optional with an our-solution
  fallback (DataForSEO, Apify, Apollo, Phantombuster, CRM, etc.).
- Bundled deterministic scripts (Python stdlib + Node/Playwright); the host agent
  does all LLM reasoning.
- Added `.robomotion/post-install.sh` (Playwright/Chromium + exec bits) and a
  group `validate.sh` contract checker.
