# Changelog

All notable changes to this skill are documented here. Format follows
[Keep a Changelog](https://keepachangelog.com/); semver tracks the
`version:` field in SKILL.md.

## [1.0.0] - 2026-05-25

Initial port to Robomotion from the upstream `obsidian` skill.

### Changed

- Front-matter trimmed to the Robomotion shape (`name` / `version` /
  `summary` / `tags`).
- Added an explicit note that this is a host-mode/filesystem skill.
- Declared `OBSIDIAN_VAULT_PATH` in `env.optional` (not `env.required`):
  it has a documented fallback, so the Designer offers it as a
  non-mandatory binding and the launcher injects it when bound, without
  blocking the run when it's empty.

### Capabilities

- Read, list, and search notes (filename + content)
- Create and append notes
- Targeted anchored edits
- Wikilink related notes
