---
name: linear
summary: Read and modify Linear issues, projects, and cycles via GraphQL. Ships a stdlib Python CLI.
tags: ["linear", "issues", "project-management"]
---

# Linear

Manage Linear issues, projects, teams, and documents through Linear's GraphQL API. The skill ships `scripts/linear_api.py`, a stdlib-only Python CLI that wraps the most-used queries — useful for one-liners that don't need hand-written GraphQL.

## Capabilities

- List teams, projects, workflow states, issues
- Get one issue's full thread (description + comments)
- Search issues with filters (assignee, label, state, team)
- Create / update issues, change status, add comments
- Read and search Linear documents
- Drop down to raw GraphQL when the wrapper doesn't cover something

## Usage

```sh
python3 ${SKILL_DIR}/scripts/linear_api.py whoami
python3 ${SKILL_DIR}/scripts/linear_api.py list-teams
python3 ${SKILL_DIR}/scripts/linear_api.py get-issue ENG-42
python3 ${SKILL_DIR}/scripts/linear_api.py search-issues --assignee me --state started
python3 ${SKILL_DIR}/scripts/linear_api.py create-issue --team ENG --title "Deploy failed" --description "$(cat /workspace/log.txt)"
python3 ${SKILL_DIR}/scripts/linear_api.py add-comment ENG-42 --body "Reproduced; PR #1234 has the fix."
python3 ${SKILL_DIR}/scripts/linear_api.py raw 'query { viewer { name } }'
```

Run any subcommand with `--help` to see flags. For raw GraphQL not covered by the wrapper:

```sh
curl -s -X POST https://api.linear.app/graphql \
  -H "Authorization: $LINEAR_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{"query": "{ viewer { id name } }"}' | python3 -m json.tool
```

## When to use

- "What issues are assigned to me this cycle?"
- "Open a bug on the Backend team for the failed deployment"
- "Add a comment to ENG-1234 saying the fix is in review"
- "List all P1 issues without an assignee"

## When NOT to use

- Anything outside Linear (use `github-issues` for code work, `slack` for messaging)
- Analytics dashboards spanning many tools — export Linear data, then aggregate

## Operating notes

- Identifiers are typed prefixes (`ENG-1234`, `OPS-42`). Surface those, not raw UUIDs, in user-facing output.
- "Me" → call `whoami` first; never assume the bot user is the operator.
- Workflow states have a `type` field (`triage`, `backlog`, `unstarted`, `started`, `completed`, `cancelled`). Filter by type when "in progress" / "done" semantics matter — the `name` is team-customizable.
- Auth header is `Authorization: $LINEAR_API_KEY` with **no** `Bearer` prefix. This trips up scripts that copy generic OAuth patterns.
- Issue descriptions are markdown; preserve formatting when copying snippets in or out.
- The API rate-limits aggressively. Coalesce list operations and prefer pagination over re-fetching.

## Attribution

The bundled `linear_api.py` is adapted from the [Nous Hermes Agent](https://github.com/NousResearch/hermes-agent) skill of the same name (MIT).
