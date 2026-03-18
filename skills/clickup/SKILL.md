---
name: "clickup"
description: "ClickUp project management — manage workspaces, spaces, folders, lists, tasks, and comments. Supports full task lifecycle including creation, updates, assignments, and commenting via `robomotion clickup`. Do NOT use for Jira, Trello, Asana, or other PM tools."
---

# ClickUp

The `robomotion clickup` CLI connects to ClickUp for project and task management. It covers the full workspace hierarchy (teams → spaces → folders → lists → tasks) and supports task CRUD, comment management, member listing, and organizational operations.

## When to use
- Create, update, or delete tasks with assignees, due dates, and priorities
- List and manage workspaces, spaces, folders, and lists
- Add, update, or delete comments on tasks
- Browse team members and task details

## Prerequisites
- `robomotion` CLI installed
- Package installed: `robomotion install clickup`
- ClickUp API token configured via Robomotion vault

## IMPORTANT: Session Mode Required for Multi-Step Operations
Each CLI command runs as a **separate process** — connection IDs from `connect` do NOT persist across calls.
You MUST use `--session` on `connect` and pass `--session-id` to all subsequent commands.

## Workflow
1. Install (once): `robomotion install clickup`
2. Connect with session:
   ```
   robomotion clickup clickup_connect --session --output json
   # → {"outClientId":"<client-id>","session_id":"<session-id>"}
   ```
3. Use the returned `client-id` and `session-id` in all subsequent commands:
   ```
   robomotion clickup clickup_get_tasks --client-id "<client-id>" --list-id <list> --session-id "<session-id>" --output json
   ```
4. Disconnect when done:
   ```
   robomotion clickup clickup_disconnect --client-id "<client-id>" --session-id "<session-id>" --output json
   ```

**Always** append `--output json` to get structured JSON results.

## Commands Reference
- `robomotion clickup clickup_connect --session --output json`
  Connects to ClickUp API and returns a client ID
- `robomotion clickup clickup_disconnect --client-id --session-id "<session-id>" --output json`
  Closes the ClickUp connection and releases resources
- `robomotion clickup get_workspaces --client-id --session-id "<session-id>" --output json`
  Gets all authorized ClickUp workspaces (teams)
- `robomotion clickup create_space --client-id --team-id --name --session-id "<session-id>" --output json`
  Creates a new space in a ClickUp workspace
- `robomotion clickup get_space --client-id --space-id --session-id "<session-id>" --output json`
  Gets a single space by ID
- `robomotion clickup list_spaces --client-id --team-id --session-id "<session-id>" --output json`
  Lists all spaces in a ClickUp workspace
- `robomotion clickup update_space --client-id --space-id --name --session-id "<session-id>" --output json`
  Updates an existing space
- `robomotion clickup delete_space --client-id --space-id --session-id "<session-id>" --output json`
  Deletes a space from ClickUp
- `robomotion clickup create_folder --client-id --space-id --name --session-id "<session-id>" --output json`
  Creates a new folder in a ClickUp space
- `robomotion clickup get_folder --client-id --folder-id --session-id "<session-id>" --output json`
  Gets a single folder by ID
- `robomotion clickup list_folders --client-id --space-id --session-id "<session-id>" --output json`
  Lists all folders in a ClickUp space
- `robomotion clickup update_folder --client-id --folder-id --name --session-id "<session-id>" --output json`
  Updates an existing folder
- `robomotion clickup delete_folder --client-id --folder-id --session-id "<session-id>" --output json`
  Deletes a folder from ClickUp
- `robomotion clickup create_list --client-id --folder-id --space-id --name --content --session-id "<session-id>" --output json`
  Creates a new list in a ClickUp folder or space (folderless)
- `robomotion clickup get_list --client-id --list-id --session-id "<session-id>" --output json`
  Gets a single list by ID
- `robomotion clickup list_lists --client-id --folder-id --space-id --session-id "<session-id>" --output json`
  Lists all lists in a folder or space (folderless)
- `robomotion clickup update_list --client-id --list-id --name --content --session-id "<session-id>" --output json`
  Updates an existing list
- `robomotion clickup delete_list --client-id --list-id --session-id "<session-id>" --output json`
  Deletes a list from ClickUp
- `robomotion clickup create_task --client-id --list-id --name --description --status --due-date --assignees --tags [--priority] --session-id "<session-id>" --output json`
  Creates a new task in a ClickUp list
- `robomotion clickup get_task --client-id --task-id --session-id "<session-id>" --output json`
  Gets a single task by ID
- `robomotion clickup list_tasks --client-id --list-id [--0] [--order-by] --session-id "<session-id>" --output json`
  Lists tasks in a ClickUp list with optional filters
- `robomotion clickup update_task --client-id --task-id --name --description --status --due-date [--priority] --session-id "<session-id>" --output json`
  Updates an existing task
- `robomotion clickup delete_task --client-id --task-id --session-id "<session-id>" --output json`
  Deletes a task from ClickUp
- `robomotion clickup create_comment --client-id --target-id --comment-text [--comment-on] --session-id "<session-id>" --output json`
  Creates a comment on a task，list，or view
- `robomotion clickup list_comments --client-id --target-id [--comment-on] --session-id "<session-id>" --output json`
  Lists comments on a task，list，or view
- `robomotion clickup update_comment --client-id --comment-id --comment-text [--resolved] --session-id "<session-id>" --output json`
  Updates an existing comment
- `robomotion clickup delete_comment --client-id --comment-id --session-id "<session-id>" --output json`
  Deletes a comment from ClickUp

## Environment
- ROBOMOTION_API_TOKEN (if vault credentials are needed)
