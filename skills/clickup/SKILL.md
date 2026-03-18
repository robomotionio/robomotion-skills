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

## Workflow
1. Install: `robomotion install clickup`
2. Connect: `robomotion clickup clickup_connect` → returns a `client-id`
3. List tasks: `robomotion clickup clickup_get_tasks --client-id <id> --list-id <list>`
4. Create task: `robomotion clickup clickup_create_task --client-id <id> --list-id <list> --name <name>`
5. Disconnect: `robomotion clickup clickup_disconnect --client-id <id>`

## Commands Reference
- `robomotion clickup clickup_connect`
  Connects to ClickUp API and returns a client ID
- `robomotion clickup clickup_disconnect --client-id`
  Closes the ClickUp connection and releases resources
- `robomotion clickup get_workspaces --client-id`
  Gets all authorized ClickUp workspaces (teams)
- `robomotion clickup create_space --client-id --team-id --name`
  Creates a new space in a ClickUp workspace
- `robomotion clickup get_space --client-id --space-id`
  Gets a single space by ID
- `robomotion clickup list_spaces --client-id --team-id`
  Lists all spaces in a ClickUp workspace
- `robomotion clickup update_space --client-id --space-id --name`
  Updates an existing space
- `robomotion clickup delete_space --client-id --space-id`
  Deletes a space from ClickUp
- `robomotion clickup create_folder --client-id --space-id --name`
  Creates a new folder in a ClickUp space
- `robomotion clickup get_folder --client-id --folder-id`
  Gets a single folder by ID
- `robomotion clickup list_folders --client-id --space-id`
  Lists all folders in a ClickUp space
- `robomotion clickup update_folder --client-id --folder-id --name`
  Updates an existing folder
- `robomotion clickup delete_folder --client-id --folder-id`
  Deletes a folder from ClickUp
- `robomotion clickup create_list --client-id --folder-id --space-id --name --content`
  Creates a new list in a ClickUp folder or space (folderless)
- `robomotion clickup get_list --client-id --list-id`
  Gets a single list by ID
- `robomotion clickup list_lists --client-id --folder-id --space-id`
  Lists all lists in a folder or space (folderless)
- `robomotion clickup update_list --client-id --list-id --name --content`
  Updates an existing list
- `robomotion clickup delete_list --client-id --list-id`
  Deletes a list from ClickUp
- `robomotion clickup create_task --client-id --list-id --name --description --status --due-date --assignees --tags [--priority]`
  Creates a new task in a ClickUp list
- `robomotion clickup get_task --client-id --task-id`
  Gets a single task by ID
- `robomotion clickup list_tasks --client-id --list-id [--0] [--order-by]`
  Lists tasks in a ClickUp list with optional filters
- `robomotion clickup update_task --client-id --task-id --name --description --status --due-date [--priority]`
  Updates an existing task
- `robomotion clickup delete_task --client-id --task-id`
  Deletes a task from ClickUp
- `robomotion clickup create_comment --client-id --target-id --comment-text [--comment-on]`
  Creates a comment on a task，list，or view
- `robomotion clickup list_comments --client-id --target-id [--comment-on]`
  Lists comments on a task，list，or view
- `robomotion clickup update_comment --client-id --comment-id --comment-text [--resolved]`
  Updates an existing comment
- `robomotion clickup delete_comment --client-id --comment-id`
  Deletes a comment from ClickUp

## Environment
- ROBOMOTION_API_TOKEN (if vault credentials are needed)
