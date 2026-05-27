# Changelog - hermes-skills

All notable Robomotion-side changes to the vendored `hermes-skills/` mirror.

The format roughly follows [Keep a Changelog](https://keepachangelog.com/).
**This is not upstream's changelog** - see
[`NousResearch/hermes-agent`](https://github.com/NousResearch/hermes-agent)
for the upstream history. This file tracks only what *we* shipped: vendoring
events, version pins, and Robomotion-side additions inside `.robomotion/`.

## [0.14.0] - 2026-05-27

### Added
- Vendored `skills/` from `NousResearch/hermes-agent` at commit `5deb384` (pyproject `version = "0.14.0"`).
  90 skills across 22 active categories - software development, MLOps,
  research, productivity, creative, devops, platform automation (Apple, GitHub,
  smart home).
- `.robomotion/skill.yaml` - group metadata pinning version `0.14.0`.
- `.robomotion/LICENSE` - copy of upstream MIT.
- `env.required` / `env.optional` files written per `§3.5b` for inner skills
  that ship `scripts/`. See per-skill diffs.

### Tooling
- Extended `build-index.py` to discover `SKILL.md` recursively under
  `<group>/skills/`. Hermes uses 1-3 levels of nesting (e.g.
  `skills/yuanbao/SKILL.md`, `skills/apple/macos-computer-use/SKILL.md`,
  `skills/mlops/research/dspy/SKILL.md`). Existing one-level groups
  (marketing-skills, engineering-skills, etc.) still index identically -
  the walker stops at the first `SKILL.md` per branch.
