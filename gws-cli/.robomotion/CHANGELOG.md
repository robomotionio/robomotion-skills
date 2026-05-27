# Changelog — gws-cli

## [1.0.0] — 2026-05-27
- Vendored from googleworkspace/cli@main verbatim (95 SKILL.md files:
  17 service skills, 50 action sub-skills, 28 recipe workflows).
- License: Apache 2.0.
- No per-skill scripts — skills wrap the upstream `gws` CLI binary,
  which is expected on `$PATH`. The launcher will need to ship `gws`
  in the container image (post-install concern, not yet wired here).
