---
name: "jira"
description: "Jira project management — create, update, search, transition, and comment on issues. Supports JQL search, issue lifecycle, and project management via `robomotion jira`. Do NOT use for Trello, ClickUp, Asana, or other PM tools."
---

# Jira

The `robomotion jira` CLI connects to Jira for issue and project management. It creates, reads, updates, and transitions issues; searches with JQL; adds comments; manages projects and issue types — covering the full issue lifecycle.

## When to use
- Create, update, or transition Jira issues through workflow states
- Search issues using JQL queries
- Add comments and manage issue details
- List projects and issue types

## Prerequisites
- `robomotion` CLI installed
- Package installed: `robomotion install jira`
- Jira URL and API token (or OAuth) configured via Robomotion vault

## IMPORTANT: Session Mode Required for Multi-Step Operations
Each CLI command runs as a **separate process** — connection IDs from `connect` do NOT persist across calls.
You MUST use `--session` on `connect` and pass `--session-id` to all subsequent commands.

## Workflow
1. Install (once): `robomotion install jira`
2. Connect with session:
   ```
   robomotion jira connect --session --output json
   # → {"outClientId":"<client-id>","session_id":"<session-id>"}
   ```
3. Use the returned `client-id` and `session-id` in all subsequent commands:
   ```
   robomotion jira create_issue --client-id "<client-id>" --project <proj> --summary <text> --issue-type <type> --session-id "<session-id>" --output json
   ```
4. Disconnect when done:
   ```
   robomotion jira disconnect --client-id "<client-id>" --session-id "<session-id>" --output json
   ```

**Always** append `--output json` to get structured JSON results.

## Commands Reference
- `robomotion jira jira_connect --session --output json`
  Connects to Jira Cloud and returns a client ID for subsequent operations
- `robomotion jira jira_disconnect --client-id --session-id "<session-id>" --output json`
  Closes the Jira connection and releases resources
- `robomotion jira jira_create_issue --client-id --project-key --summary --issue-type --description --assignee-account-id --priority --labels --session-id "<session-id>" --output json`
  Creates a new issue in Jira
- `robomotion jira jira_get_issue --client-id --issue-key --session-id "<session-id>" --output json`
  Gets an issue by its key or ID from Jira
- `robomotion jira jira_update_issue --client-id --issue-key --summary --description --assignee-account-id --priority --labels --session-id "<session-id>" --output json`
  Updates an existing issue in Jira
- `robomotion jira jira_delete_issue --client-id --issue-key --session-id "<session-id>" --output json`
  Deletes an issue from Jira
- `robomotion jira jira_search_issues --client-id --jql-query [--50] [--0] --session-id "<session-id>" --output json`
  Searches for issues using JQL (Jira Query Language)
- `robomotion jira jira_get_transitions --client-id --issue-key --session-id "<session-id>" --output json`
  Gets available transitions for an issue based on its current status
- `robomotion jira jira_do_transition --client-id --issue-key --transition-id --comment --session-id "<session-id>" --output json`
  Executes a transition to change an issue's status
- `robomotion jira jira_add_comment --client-id --issue-key --comment-body --session-id "<session-id>" --output json`
  Adds a comment to an issue
- `robomotion jira jira_list_comments --client-id --issue-key [--order-by] [--50] --session-id "<session-id>" --output json`
  Lists all comments on an issue
- `robomotion jira jira_list_projects --client-id --session-id "<session-id>" --output json`
  Lists all projects accessible to the user
- `robomotion jira jira_get_project --client-id --project-key --session-id "<session-id>" --output json`
  Gets detailed information about a project
- `robomotion jira jira_add_attachment --client-id --issue-key --file-path --session-id "<session-id>" --output json`
  Adds a file attachment to an issue

## Environment
- ROBOMOTION_API_TOKEN (if vault credentials are needed)
