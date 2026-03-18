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

## Workflow
1. Install: `robomotion install canvas`
2. Connect: `robomotion canvas canvas_connect` → returns a `client-id`
3. List courses: `robomotion canvas canvas_list_courses --client-id <id>`
4. Create assignment: `robomotion canvas canvas_create_assignment --client-id <id> --course-id <course> --name <name>`
5. Grade: `robomotion canvas canvas_grade_submission --client-id <id> --course-id <course> --assignment-id <asn> --user-id <user> --grade <grade>`
6. Disconnect: `robomotion canvas canvas_disconnect --client-id <id>`

## Commands Reference
- `robomotion canvas canvas_connect`
  Connects to Canvas LMS and returns a client ID for subsequent operations
- `robomotion canvas canvas_disconnect --client-id`
  Closes the Canvas LMS connection and releases resources
- `robomotion canvas canvas_list_courses --client-id [--enrollment-type] [--state] [--50]`
  Lists courses for the authenticated user
- `robomotion canvas canvas_get_course --client-id --course-id`
  Gets details of a specific Canvas course
- `robomotion canvas canvas_list_assignments --client-id --course-id [--order-by] [--50]`
  Lists assignments in a Canvas course
- `robomotion canvas canvas_get_assignment --client-id --course-id --assignment-id`
  Gets details of a specific assignment in a Canvas course
- `robomotion canvas canvas_create_assignment --client-id --course-id --name --description [--100] [--due-date]`
  Creates a new assignment in a Canvas course
- `robomotion canvas canvas_update_assignment --client-id --course-id --assignment-id --name --description [--points-possible] [--due-date]`
  Updates an existing assignment in a Canvas course
- `robomotion canvas canvas_delete_assignment --client-id --course-id --assignment-id`
  Deletes an assignment from a Canvas course
- `robomotion canvas canvas_list_users --client-id --course-id [--enrollment-type] [--search-term] [--50]`
  Lists users enrolled in a Canvas course
- `robomotion canvas canvas_get_user --client-id --user-id`
  Gets details of a specific Canvas user
- `robomotion canvas canvas_list_enrollments --client-id --course-id [--role] [--state] [--50]`
  Lists enrollments in a Canvas course
- `robomotion canvas canvas_create_enrollment --client-id --course-id --user-id [--role]`
  Enrolls a user in a Canvas course
- `robomotion canvas canvas_delete_enrollment --client-id --course-id --enrollment-id [--action]`
  Removes a user enrollment from a Canvas course
- `robomotion canvas canvas_list_submissions --client-id --course-id --assignment-id [--50]`
  Lists submissions for an assignment in a Canvas course
- `robomotion canvas canvas_grade_submission --client-id --course-id --assignment-id --user-id --grade [--comment]`
  Grades a student submission for an assignment
- `robomotion canvas canvas_list_pages --client-id --course-id [--sort-by] [--50]`
  Lists wiki pages in a Canvas course
- `robomotion canvas canvas_create_page --client-id --course-id --title --body`
  Creates a new wiki page in a Canvas course
- `robomotion canvas canvas_update_page --client-id --course-id --page-url --title --body`
  Updates an existing wiki page in a Canvas course
- `robomotion canvas canvas_list_modules --client-id --course-id [--search-term] [--include] [--50]`
  Lists modules in a Canvas course
- `robomotion canvas canvas_create_module --client-id --course-id --name`
  Creates a new module in a Canvas course
- `robomotion canvas canvas_create_announcement --client-id --course-id --title --message`
  Creates an announcement in a Canvas course

## Environment
- ROBOMOTION_API_TOKEN (if vault credentials are needed)
