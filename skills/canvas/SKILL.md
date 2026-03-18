---
name: "canvas"
description: "Canvas LMS — manage courses, assignments, users, enrollments, submissions, pages, modules, and announcements. Supports grading, enrollment management, and course content creation via `robomotion canvas`. Do NOT use for Moodle, Google Classroom, Blackboard, or other LMS platforms."
---

# Canvas LMS

The `robomotion canvas` CLI connects to Canvas LMS for education management. It manages courses, assignments (create/update/delete/grade), user enrollments, wiki pages, modules, and announcements — covering the full lifecycle of course content and student interaction.

## When to use
- Create, update, or delete assignments and grade submissions
- Manage course enrollments — enroll or remove students
- Create wiki pages, modules, and announcements in courses
- List courses, users, assignments, and submissions with filters

## Prerequisites
- `robomotion` CLI installed
- Package installed: `robomotion install canvas`
- Canvas LMS API access token configured via Robomotion vault

## IMPORTANT: Session Mode Required for Multi-Step Operations
Each CLI command runs as a **separate process** — connection IDs from `connect` do NOT persist across calls.
You MUST use `--session` on `connect` and pass `--session-id` to all subsequent commands.

## Workflow
1. Install (once): `robomotion install canvas`
2. Connect with session:
   ```
   robomotion canvas canvas_connect --session --output json
   # → {"outClientId":"<client-id>","session_id":"<session-id>"}
   ```
3. Use the returned `client-id` and `session-id` in all subsequent commands:
   ```
   robomotion canvas canvas_list_courses --client-id "<client-id>" --session-id "<session-id>" --output json
   ```
4. Disconnect when done:
   ```
   robomotion canvas canvas_disconnect --client-id "<client-id>" --session-id "<session-id>" --output json
   ```

**Always** append `--output json` to get structured JSON results.

## Commands Reference
- `robomotion canvas canvas_connect --session --output json`
  Connects to Canvas LMS and returns a client ID for subsequent operations
- `robomotion canvas canvas_disconnect --client-id --session-id "<session-id>" --output json`
  Closes the Canvas LMS connection and releases resources
- `robomotion canvas canvas_list_courses --client-id [--enrollment-type] [--state] [--50] --session-id "<session-id>" --output json`
  Lists courses for the authenticated user
- `robomotion canvas canvas_get_course --client-id --course-id --session-id "<session-id>" --output json`
  Gets details of a specific Canvas course
- `robomotion canvas canvas_list_assignments --client-id --course-id [--order-by] [--50] --session-id "<session-id>" --output json`
  Lists assignments in a Canvas course
- `robomotion canvas canvas_get_assignment --client-id --course-id --assignment-id --session-id "<session-id>" --output json`
  Gets details of a specific assignment in a Canvas course
- `robomotion canvas canvas_create_assignment --client-id --course-id --name --description [--100] [--due-date] --session-id "<session-id>" --output json`
  Creates a new assignment in a Canvas course
- `robomotion canvas canvas_update_assignment --client-id --course-id --assignment-id --name --description [--points-possible] [--due-date] --session-id "<session-id>" --output json`
  Updates an existing assignment in a Canvas course
- `robomotion canvas canvas_delete_assignment --client-id --course-id --assignment-id --session-id "<session-id>" --output json`
  Deletes an assignment from a Canvas course
- `robomotion canvas canvas_list_users --client-id --course-id [--enrollment-type] [--search-term] [--50] --session-id "<session-id>" --output json`
  Lists users enrolled in a Canvas course
- `robomotion canvas canvas_get_user --client-id --user-id --session-id "<session-id>" --output json`
  Gets details of a specific Canvas user
- `robomotion canvas canvas_list_enrollments --client-id --course-id [--role] [--state] [--50] --session-id "<session-id>" --output json`
  Lists enrollments in a Canvas course
- `robomotion canvas canvas_create_enrollment --client-id --course-id --user-id [--role] --session-id "<session-id>" --output json`
  Enrolls a user in a Canvas course
- `robomotion canvas canvas_delete_enrollment --client-id --course-id --enrollment-id [--action] --session-id "<session-id>" --output json`
  Removes a user enrollment from a Canvas course
- `robomotion canvas canvas_list_submissions --client-id --course-id --assignment-id [--50] --session-id "<session-id>" --output json`
  Lists submissions for an assignment in a Canvas course
- `robomotion canvas canvas_grade_submission --client-id --course-id --assignment-id --user-id --grade [--comment] --session-id "<session-id>" --output json`
  Grades a student submission for an assignment
- `robomotion canvas canvas_list_pages --client-id --course-id [--sort-by] [--50] --session-id "<session-id>" --output json`
  Lists wiki pages in a Canvas course
- `robomotion canvas canvas_create_page --client-id --course-id --title --body --session-id "<session-id>" --output json`
  Creates a new wiki page in a Canvas course
- `robomotion canvas canvas_update_page --client-id --course-id --page-url --title --body --session-id "<session-id>" --output json`
  Updates an existing wiki page in a Canvas course
- `robomotion canvas canvas_list_modules --client-id --course-id [--search-term] [--include] [--50] --session-id "<session-id>" --output json`
  Lists modules in a Canvas course
- `robomotion canvas canvas_create_module --client-id --course-id --name --session-id "<session-id>" --output json`
  Creates a new module in a Canvas course
- `robomotion canvas canvas_create_announcement --client-id --course-id --title --message --session-id "<session-id>" --output json`
  Creates an announcement in a Canvas course

## Environment
- ROBOMOTION_API_TOKEN (if vault credentials are needed)
