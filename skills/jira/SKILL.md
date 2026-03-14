---
name: "jira"
description: "Use when the user wants to call the Robomotion Jira package to create, update, or search issues via the `robomotion jira` CLI. Do NOT use for Linear, Trello, or other project management tools."
---

# Jira Skill

## When to use
- Create or update Jira issues
- Search for Jira issues using JQL
- Manage Jira projects and boards
- Transition Jira issue statuses

## Prerequisites
- `robomotion` CLI installed
- Package installed: `robomotion install jira`
- Credentials configured via Robomotion vault or environment variables

## Workflow
1. Install the package: `robomotion install jira`
2. Run commands: `robomotion jira <command> [flags]`

## Commands Reference
- `robomotion jira jira_connect`
  Connects to Jira Cloud and returns a client ID for subsequent operations
- `robomotion jira jira_disconnect --client-id`
  Closes the Jira connection and releases resources
- `robomotion jira jira_create_issue --client-id --project-key --summary --issue-type --description --assignee-account-id --priority --labels`
  Creates a new issue in Jira
- `robomotion jira jira_get_issue --client-id --issue-key`
  Gets an issue by its key or ID from Jira
- `robomotion jira jira_update_issue --client-id --issue-key --summary --description --assignee-account-id --priority --labels`
  Updates an existing issue in Jira
- `robomotion jira jira_delete_issue --client-id --issue-key`
  Deletes an issue from Jira
- `robomotion jira jira_search_issues --client-id --jql-query [--50] [--0]`
  Searches for issues using JQL (Jira Query Language)
- `robomotion jira jira_get_transitions --client-id --issue-key`
  Gets available transitions for an issue based on its current status
- `robomotion jira jira_do_transition --client-id --issue-key --transition-id --comment`
  Executes a transition to change an issue's status
- `robomotion jira jira_add_comment --client-id --issue-key --comment-body`
  Adds a comment to an issue
- `robomotion jira jira_list_comments --client-id --issue-key [--order-by] [--50]`
  Lists all comments on an issue
- `robomotion jira jira_list_projects --client-id`
  Lists all projects accessible to the user
- `robomotion jira jira_get_project --client-id --project-key`
  Gets detailed information about a project
- `robomotion jira jira_add_attachment --client-id --issue-key --file-path`
  Adds a file attachment to an issue

## Environment
- ROBOMOTION_API_TOKEN (if vault credentials are needed)
