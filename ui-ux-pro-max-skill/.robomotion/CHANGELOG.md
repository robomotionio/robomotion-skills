# Changelog — ui-ux-pro-max-skill

## [2.5.0] — 2026-05-27
- Vendored from nextlevelbuilder/ui-ux-pro-max-skill@main (7 inner skills: ui-ux-pro-max + 6 claudekit siblings — banner-design, brand, design, design-system, slides, ui-styling).
- Upstream uses `.claude/skills/<name>/SKILL.md` (Claude Code plugin layout) — indexer extended to discover it.
- Version pinned to 2.5.0 (matches `skill.json`); upstream's older `plugin.json` (2.2.1) ignored per group-version-wins policy.
- No `post-install.sh` and no `env.yaml` — pure knowledge skills, no env vars, no CLIs needed (upstream `cli/` is an installer for other AI platforms and is left on disk but unused).
