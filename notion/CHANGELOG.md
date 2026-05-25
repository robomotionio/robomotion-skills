# Changelog

All notable changes to this skill are documented here. Format follows
[Keep a Changelog](https://keepachangelog.com/); semver tracks the
`version:` field in SKILL.md.

## [1.0.0] - 2026-05-25

Initial port to Robomotion from the upstream `notion` skill (v2.0.0).

### Changed

- Reduced to the HTTP API + `curl` path only. The upstream `ntn` CLI
  and hosted Workers sections were dropped: `ntn` is macOS/Linux-only
  with a Node 22+ requirement, and Workers need a Business/Enterprise
  plan — neither fits the sandbox port. The curl path covers all core
  read/write operations and works on every platform.
- Install/setup prose (token creation, `~/.hermes/.env`) removed from
  SKILL.md. `NOTION_API_KEY` now declares as a required credential in
  `env.required`, surfaced by the Designer's Environment tab.

### Capabilities

- Search pages and databases
- Read page metadata, Markdown rendering, and block trees
- Create pages from Markdown or typed database properties
- Patch page properties and append blocks
- Create and query databases (data sources)
- 3-step file upload and attach
