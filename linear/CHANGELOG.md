# Changelog

All notable changes to this skill are documented here. Format follows
[Keep a Changelog](https://keepachangelog.com/); semver tracks the
`version:` field in SKILL.md.

## [1.0.0] - 2026-05-10

Initial baseline. Includes recent CLI surface fixes that shipped under
this version (would have warranted a minor bump if versioning had been
in place earlier).

### Added

- `list-issues --assignee me` resolves to the calling user's UUID via
  the `viewer` query — no manual `whoami` chain needed.
- `list-issues --status` is dual-mode: canonical workflow types
  (`triage` / `backlog` / `unstarted` / `started` / `completed` /
  `cancelled`) match `state.type` for portability across teams;
  anything else matches `state.name`.

### Fixed

- SKILL.md examples now reflect the actual CLI surface. Some prior
  examples called `search-issues` with `--assignee` and `--state`
  flags it doesn't accept; models trusted the docs and burned recovery
  tool calls.

### Capabilities

- List teams, projects, workflow states, issues
- Get one issue's full thread (description + comments)
- Free-text search across issues
- Structured filters (team / status / assignee / label)
- Create / update issues, change status, add comments
- Read and search Linear documents
