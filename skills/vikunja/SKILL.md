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

## Workflow
1. Install: `robomotion install vikunja`
2. Connect: `robomotion vikunja vikunja_connect` → returns a `client-id`
3. List tasks: `robomotion vikunja vikunja_list_tasks --client-id <id> --project-id <proj>`
4. Create task: `robomotion vikunja vikunja_create_task --client-id <id> --project-id <proj> --title <title>`
5. Disconnect: `robomotion vikunja vikunja_disconnect --client-id <id>`

## Commands Reference
- `robomotion vikunja vikunja_connect`
  Connects to Vikunja and returns a reusable client ID
- `robomotion vikunja vikunja_disconnect --client-id`
  Closes the Vikunja connection and releases resources
- `robomotion vikunja vikunja_create_task --client-id --project-id --task-title --description --due-date --priority --color [--30]`
  Creates a new task in a Vikunja project
- `robomotion vikunja vikunja_get_task --client-id --task-id [--30]`
  Retrieves a single task by ID
- `robomotion vikunja vikunja_list_tasks --client-id --project-id [--1] [--50] [--30]`
  Lists all tasks in a project
- `robomotion vikunja vikunja_update_task --client-id --task-id --task-title --description --done --due-date --priority --color [--30]`
  Updates an existing task
- `robomotion vikunja vikunja_delete_task --client-id --task-id [--30]`
  Deletes a task by ID
- `robomotion vikunja vikunja_add_comment --client-id --task-id --comment [--30]`
  Adds a comment to a task
- `robomotion vikunja vikunja_list_comments --client-id --task-id [--30]`
  Lists all comments on a task
- `robomotion vikunja vikunja_create_project --client-id --project-title --description --parent-project-id --identifier --color [--30]`
  Creates a new project in Vikunja
- `robomotion vikunja vikunja_get_project --client-id --project-id [--30]`
  Retrieves a single project by ID
- `robomotion vikunja vikunja_list_projects --client-id [--1] [--50] [--30]`
  Lists all accessible projects
- `robomotion vikunja vikunja_update_project --client-id --project-id --project-title --description --archived --identifier --color [--30]`
  Updates an existing project
- `robomotion vikunja vikunja_delete_project --client-id --project-id [--30]`
  Deletes a project by ID
- `robomotion vikunja vikunja_create_label --client-id --label-title --description --color [--30]`
  Creates a new label in Vikunja
- `robomotion vikunja vikunja_list_labels --client-id [--1] [--50] [--30]`
  Lists all labels
- `robomotion vikunja vikunja_delete_label --client-id --label-id [--30]`
  Deletes a label by ID

## Environment
- ROBOMOTION_API_TOKEN (if vault credentials are needed)
