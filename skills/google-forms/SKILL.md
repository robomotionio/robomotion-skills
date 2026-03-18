---
name: "google-forms"
description: "Google Forms — create forms, manage questions, and retrieve responses. Supports form creation, question management, and response collection via `robomotion googleforms`. Do NOT use for Typeform, SurveyMonkey, or other form builders."
---

# Google Forms

The `robomotion googleforms` CLI connects to Google Forms API for form and response management. It creates forms, adds and manages questions, retrieves form submissions, and lists available forms.

## When to use
- Create new Google Forms with custom questions
- Retrieve and list form responses/submissions
- Manage form questions and settings

## Prerequisites
- `robomotion` CLI installed
- Package installed: `robomotion install googleforms`
- Google Forms OAuth2 or Service Account credentials configured via Robomotion vault

## IMPORTANT: Session Mode Required for Multi-Step Operations
Each CLI command runs as a **separate process** — connection IDs from `connect` do NOT persist across calls.
You MUST use `--session` on `connect` and pass `--session-id` to all subsequent commands.

## Workflow
1. Install (once): `robomotion install googleforms`
2. Connect with session:
   ```
   robomotion googleforms googleforms_connect --session --output json
   # → {"outClientId":"<client-id>","session_id":"<session-id>"}
   ```
3. Use the returned `client-id` and `session-id` in all subsequent commands:
   ```
   robomotion googleforms googleforms_list_responses --client-id "<client-id>" --form-id <form> --session-id "<session-id>" --output json
   ```
4. Disconnect when done:
   ```
   robomotion googleforms googleforms_disconnect --client-id "<client-id>" --session-id "<session-id>" --output json
   ```

**Always** append `--output json` to get structured JSON results.

## Commands Reference
- `robomotion googleforms create_form --title [--type] --output json`
  Creates a new Google Form or Quiz with the specified title
- `robomotion googleforms add_open_ended_question --form-id --question-title --1 [--type] --output json`
  Adds a text-based question (short answer or paragraph) to a Google Form
- `robomotion googleforms add_closed_ended_question --form-id --question-title --answers --1 [--type] [--correct-answers] [--1] --output json`
  Adds a multiple choice question (radio٫ checkbox٫ or dropdown) to a Google Form
- `robomotion googleforms get_responses --form-id --output json`
  Retrieves all submitted responses for a Google Form
- `robomotion googleforms open_form --form-url --output json`
  Opens an existing Google Form by URL for further operations
- `robomotion googleforms get_form --form-id --output json`
  Retrieves the full form structure including questions and settings
- `robomotion googleforms delete_question --form-id --1 --output json`
  Deletes a question from a Google Form by its position index

## Environment
- ROBOMOTION_API_TOKEN (if vault credentials are needed)
