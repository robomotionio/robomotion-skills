---
name: linear
version: 1.0.0
summary: Read and modify Linear issues, projects, and cycles via GraphQL. Ships a stdlib Python CLI.
tags: ["linear", "issues", "project-management"]
---

# Linear

Manage Linear issues, projects, teams, and documents through Linear's GraphQL API. The skill ships `scripts/linear_api.py`, a stdlib-only Python CLI that wraps the most-used queries — useful for one-liners that don't need hand-written GraphQL.

## Capabilities

- List teams, projects, workflow states, issues
- Get one issue's full thread (description + comments)
- Search issues with free-text queries
- Filter issues by team / status / assignee / label
- Create / update issues, change status, add comments
- Read and search Linear documents
- Drop down to raw GraphQL when the wrapper doesn't cover something

## Two list verbs — pick the right one

The wrapper has two distinct issue-listing commands. Choosing wrong wastes calls:

- **`list-issues`** — structured filters (team / status / assignee / label / limit). Use this when the user asks for "issues in state X" or "issues assigned to Y" or "the latest N issues."
- **`search-issues`** — free-text fuzzy search across title and description. Takes a positional `query`, no filters. Use this when the user describes the issue by *content* ("the deploy failure ticket from last week").

## Usage

```sh
# List recent issues, no filter — returns most-recently-updated.
python3 ${SKILL_DIR}/scripts/linear_api.py list-issues --limit 10

# Structured filters: team / status / assignee / label.
python3 ${SKILL_DIR}/scripts/linear_api.py list-issues --team ENG --status started --limit 20
python3 ${SKILL_DIR}/scripts/linear_api.py list-issues --assignee me --status started
python3 ${SKILL_DIR}/scripts/linear_api.py list-issues --label bug --limit 50

# Free-text search (positional query, fuzzy match).
python3 ${SKILL_DIR}/scripts/linear_api.py search-issues "deploy failed" --limit 10

# Single issue with full thread.
python3 ${SKILL_DIR}/scripts/linear_api.py get-issue ENG-42

# Identity / metadata.
python3 ${SKILL_DIR}/scripts/linear_api.py whoami
python3 ${SKILL_DIR}/scripts/linear_api.py list-teams
python3 ${SKILL_DIR}/scripts/linear_api.py list-states --team ENG

# Mutations.
python3 ${SKILL_DIR}/scripts/linear_api.py create-issue --team ENG --title "Deploy failed" --description "$(cat /workspace/log.txt)"
python3 ${SKILL_DIR}/scripts/linear_api.py update-status ENG-42 "In Progress"
python3 ${SKILL_DIR}/scripts/linear_api.py add-comment ENG-42 "Reproduced; PR #1234 has the fix."

# Raw GraphQL escape hatch.
python3 ${SKILL_DIR}/scripts/linear_api.py raw 'query { viewer { name } }'
```

Run any subcommand with `--help` if you need its full flag list.

## When to use

- "What issues are assigned to me this cycle?"
- "Open a bug on the Backend team for the failed deployment"
- "Add a comment to ENG-1234 saying the fix is in review"
- "List all P1 issues without an assignee"

## When NOT to use

- Anything outside Linear (use `github-issues` for code work, `slack` for messaging)
- Analytics dashboards spanning many tools — export Linear data, then aggregate

## Operating notes

- **Identifiers** are typed prefixes (`ENG-1234`, `OPS-42`). Surface those, not raw UUIDs, in user-facing output.
- **`--assignee me`** resolves to the calling user via the viewer query under the hood — no need to call `whoami` first to get a UUID. Only call `whoami` when the user's identity is itself the answer (e.g., "who am I logged in as?") or when you need their name/email for output. Don't call it when "me" appears as a filter target (`--assignee me` handles it) or as conversational filler ("show *me* the issues…").
- **`--status` is dual-mode.** Canonical workflow types (`triage` / `backlog` / `unstarted` / `started` / `completed` / `cancelled`) match `state.type` and are portable across teams. Anything else matches `state.name`, which is team-customizable. Prefer types when semantics matter ("in progress" → `--status started`); use exact names only when the user named a specific custom state.
- **Auth header** is `Authorization: $LINEAR_API_KEY` with **no** `Bearer` prefix. This trips up scripts that copy generic OAuth patterns.
- Issue descriptions are markdown; preserve formatting when copying snippets in or out.
- The API rate-limits aggressively. Coalesce list operations and prefer pagination over re-fetching.

## Attribution

The bundled `linear_api.py` is adapted from the [Nous Hermes Agent](https://github.com/NousResearch/hermes-agent) skill of the same name (MIT).
