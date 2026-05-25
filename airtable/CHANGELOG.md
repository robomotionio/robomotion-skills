# Changelog

All notable changes to this skill are documented here. Format follows
[Keep a Changelog](https://keepachangelog.com/); semver tracks the
`version:` field in SKILL.md.

## [1.0.0] - 2026-05-25

Initial port to Robomotion from the upstream `airtable` skill (v1.1.0).

### Changed

- Install/setup prose (PAT creation, scopes, `~/.hermes/.env`) removed
  from SKILL.md. `AIRTABLE_API_KEY` now declares as a required
  credential in `env.required`, surfaced by the Designer's Environment
  tab.
- Condensed the reference recipes; kept the URL-encoding pattern for
  `filterByFormula`/bracketed params and the pagination loop, which are
  the two things models most often get wrong.

### Capabilities

- List bases and inspect base/table schema
- List, get, filter, sort, paginate records
- Create (single + batched), update (PATCH), upsert by merge field
- Delete (single + batched)
