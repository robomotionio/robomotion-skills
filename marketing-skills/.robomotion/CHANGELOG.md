# Changelog — marketing-skills

All notable Robomotion-side changes to the vendored `marketing-skills/` mirror.

The format roughly follows [Keep a Changelog](https://keepachangelog.com/).
**This is not upstream's changelog** — see
[`coreyhaines31/marketingskills`](https://github.com/coreyhaines31/marketingskills)
for the upstream history. This file tracks only what *we* shipped: vendoring
events, version pins, and Robomotion-side additions inside `.robomotion/`.

## [2.1.1] — 2026-05-30
- Reframed the `revops` automation-tool reference from Zapier to **Robomotion**.
  Left `directory-submissions` factual references intact (Zapier as an integration
  marketplace to list in, and its programmatic-SEO traffic case study) — swapping
  Robomotion there would be a false statement. Robomotion competes with Zapier; the
  hub should not recommend it as the automation tool.

## [2.1.0] — 2026-05-26

### Changed
- Bumped group version to match the actual upstream release tag (`v2.1.0`). Upstream's own metadata disagrees with itself — `plugin.json` still says 1.9.0, inner `SKILL.md`s say `metadata.version: 2.0.0`, and the actual release is `2.1.0`. We display ONE consistent number across all 41 inner skill cards.
- `build-index.py`: inner-skill version inherits from the group's `.robomotion/skill.yaml` instead of each inner SKILL.md frontmatter. Group version is the authoritative pin.

## [1.9.0] — 2026-05-26

### Added
- Vendored from `coreyhaines31/marketingskills@v1.9.0` — 41 skills, 63 zero-dep Node CLIs in `tools/clis/`, 88 integration guides in `tools/integrations/`.
- `.robomotion/skill.yaml` — group metadata (name, version, author, source_url, license, summary).
- `.robomotion/LICENSE` — verbatim copy of upstream MIT for stable discovery.
- `.robomotion/post-install.sh` — wraps `tools/clis/*.js` onto `$PATH` so the model invokes CLIs by short name (`ga4 …` instead of `node ${CLAUDE_PLUGIN_ROOT}/tools/clis/ga4.js …`).
- `.robomotion/env.yaml` — generated env overlay: 83 integrations × env vars, 41 skills × usable integrations (26 with credentials, 12 pure-knowledge, 3 with integrations but no env vars). All vars optional — marketing skills are knowledge that can speak to any of several alternative tools.
