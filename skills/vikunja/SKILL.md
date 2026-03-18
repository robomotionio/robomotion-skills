---
name: "vikunja"
description: "Vikunja — manage projects, tasks, labels, teams, and task assignments in self-hosted Vikunja instances. Supports full task lifecycle including comments, attachments, and team management via `robomotion vikunja`. Do NOT use for Jira, Trello, ClickUp, or other PM tools."
---

# Vikunja

The `robomotion vikunja` CLI connects to Vikunja (open-source task management) for project and task operations. It manages projects, tasks with due dates and priorities, labels, teams, task comments, and attachments — supporting the full task lifecycle.

## When to use
- Create, update, or delete tasks with due dates and priorities
- Manage projects, labels, and team members
- Add comments and attachments to tasks
- List and filter tasks across projects

## Prerequisites
- `robomotion` CLI installed
- Package installed: `robomotion install vikunja`
- Vikunja instance URL and API token configured via Robomotion vault

## IMPORTANT: Session Mode Required for Multi-Step Operations
Each CLI command runs as a **separate process** — connection IDs from `connect` do NOT persist across calls.
You MUST use `--session` on `connect` and pass `--session-id` to all subsequent commands.

## Workflow
1. Install (once): `robomotion install vikunja`
2. Connect with session:
   ```
   robomotion vikunja vikunja_connect --session --output json
   # → {"outClientId":"<client-id>","session_id":"<session-id>"}
   ```
3. Use the returned `client-id` and `session-id` in all subsequent commands:
   ```
   robomotion vikunja vikunja_list_tasks --client-id "<client-id>" --project-id <proj> --session-id "<session-id>" --output json
   ```
4. Disconnect when done:
   ```
   robomotion vikunja vikunja_disconnect --client-id "<client-id>" --session-id "<session-id>" --output json
   ```

**Always** append `--output json` to get structured JSON results.

## Commands Reference
- `robomotion vikunja vikunja_connect --session --output json`
  Connects to Vikunja and returns a reusable client ID
- `robomotion vikunja vikunja_disconnect --client-id --session-id "<session-id>" --output json`
  Closes the Vikunja connection and releases resources
- `robomotion vikunja vikunja_create_task --client-id --project-id --task-title --description --due-date --priority --color [--30] --session-id "<session-id>" --output json`
  Creates a new task in a Vikunja project
- `robomotion vikunja vikunja_get_task --client-id --task-id [--30] --session-id "<session-id>" --output json`
  Retrieves a single task by ID
- `robomotion vikunja vikunja_list_tasks --client-id --project-id [--1] [--50] [--30] --session-id "<session-id>" --output json`
  Lists all tasks in a project
- `robomotion vikunja vikunja_update_task --client-id --task-id --task-title --description --done --due-date --priority --color [--30] --session-id "<session-id>" --output json`
  Updates an existing task
- `robomotion vikunja vikunja_delete_task --client-id --task-id [--30] --session-id "<session-id>" --output json`
  Deletes a task by ID
- `robomotion vikunja vikunja_add_comment --client-id --task-id --comment [--30] --session-id "<session-id>" --output json`
  Adds a comment to a task
- `robomotion vikunja vikunja_list_comments --client-id --task-id [--30] --session-id "<session-id>" --output json`
  Lists all comments on a task
- `robomotion vikunja vikunja_create_project --client-id --project-title --description --parent-project-id --identifier --color [--30] --session-id "<session-id>" --output json`
  Creates a new project in Vikunja
- `robomotion vikunja vikunja_get_project --client-id --project-id [--30] --session-id "<session-id>" --output json`
  Retrieves a single project by ID
- `robomotion vikunja vikunja_list_projects --client-id [--1] [--50] [--30] --session-id "<session-id>" --output json`
  Lists all accessible projects
- `robomotion vikunja vikunja_update_project --client-id --project-id --project-title --description --archived --identifier --color [--30] --session-id "<session-id>" --output json`
  Updates an existing project
- `robomotion vikunja vikunja_delete_project --client-id --project-id [--30] --session-id "<session-id>" --output json`
  Deletes a project by ID
- `robomotion vikunja vikunja_create_label --client-id --label-title --description --color [--30] --session-id "<session-id>" --output json`
  Creates a new label in Vikunja
- `robomotion vikunja vikunja_list_labels --client-id [--1] [--50] [--30] --session-id "<session-id>" --output json`
  Lists all labels
- `robomotion vikunja vikunja_delete_label --client-id --label-id [--30] --session-id "<session-id>" --output json`
  Deletes a label by ID

## Environment
- ROBOMOTION_API_TOKEN (if vault credentials are needed)
