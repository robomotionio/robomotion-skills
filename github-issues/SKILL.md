---
name: github-issues
summary: Read, file, comment, label, and close GitHub issues via the gh CLI.
---

# GitHub issues

Manage GitHub issues using GitHub's official `gh` CLI. The CLI handles auth, pagination, and rate-limit retry, which is why we prefer it over raw `curl` against the REST API for issue work.

## Capabilities

- List issues with filters (assignee, label, state, milestone, author)
- View one issue's full thread (description + every comment)
- File a new issue with body, labels, assignees
- Comment on existing issues
- Close, reopen, lock, transfer issues across repos
- Bulk label / assign via shell loops
- Drop down to `gh api` for anything `gh issue` doesn't cover (custom fields, project boards)

## Usage

```sh
gh issue list --repo owner/repo --state open --label bug --limit 50
gh issue view 1234 --repo owner/repo --comments
gh issue create --repo owner/repo --title "Deploy failed" --body "$(cat /workspace/log.txt)" --label bug
gh issue comment 1234 --repo owner/repo --body "Reproduced; PR #1235 has the fix."
gh issue close 1234 --repo owner/repo --reason completed

# Anything else: gh api
gh api repos/owner/repo/issues/1234 --jq '.assignees[].login'
gh api graphql -f query='query { viewer { login } }'
```

## When to use

- "What's the oldest open issue assigned to me on `myorg/myrepo`?"
- "File a bug for the deploy failure with logs attached"
- "Triage these 12 issues — read each one, label severity, assign to a person"
- "Comment on every issue tagged `needs-info` asking for a repro"

## When NOT to use

- For code review (use a `github-pr-workflow` skill)
- For repository administration like settings/branches (use `gh api` directly or a `github-repo-management` skill)
- Across many orgs at scale — the CLI auth is one-token-per-host; for multi-org workflows, set `GH_HOST` per command

## Operating notes

- `gh` reads `$GH_TOKEN` AND `$GITHUB_TOKEN`; we set `GITHUB_TOKEN` via env binding. Exit code is 0 on success, 1 on usage error, 4 on auth error — surface auth failures clearly to the user (almost always a missing/expired token).
- Pagination: `gh issue list` defaults to 30 results. Use `--limit N` (max 1000 per call); for more, paginate via `gh api --paginate`.
- Issue numbers are repo-scoped. Cross-repo references must include the `owner/repo#N` form.
- When filing issues programmatically, prefer body templates from `/workspace` files over inline shell strings — multi-line bodies are easier to maintain in files.
- Don't post duplicate comments. Before commenting, view recent comments to check the bot didn't already say something.
- Rate limits: 5000 requests/hour for authenticated users. `gh api rate_limit` shows current state.
