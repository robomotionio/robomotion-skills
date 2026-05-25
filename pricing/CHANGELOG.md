# Changelog

All notable changes to this skill are documented here. Format follows
[Keep a Changelog](https://keepachangelog.com/); semver tracks the
skill's `metadata.version`.

## [2.0.0] - 2026-05-25

Initial port to Robomotion from [marketingskills](https://github.com/coreyhaines31/marketingskills).

### Changed

- Kept the native agentskills.io front-matter (`name` + `description` +
  `metadata.version`) to exercise Robomotion's spec-compatibility shims;
  added `tags` for the Designer marketplace.
- Rewrote `references/` links to `${SKILL_DIR}/references/` so the model
  resolves them inside the sandbox.
- Added an Attribution section.

### Notes

- Pure-knowledge skill (no scripts) -> runs host mode.
- References the optional `.agents/product-marketing.md` context file if
  present; harmless no-op when absent.
