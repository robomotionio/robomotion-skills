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

## Workflow
1. Install: `robomotion install googleforms`
2. Connect: `robomotion googleforms googleforms_connect` → returns a `client-id`
3. List responses: `robomotion googleforms googleforms_list_responses --client-id <id> --form-id <form>`
4. Disconnect: `robomotion googleforms googleforms_disconnect --client-id <id>`

## Commands Reference
- `robomotion googleforms create_form --title [--type]`
  Creates a new Google Form or Quiz with the specified title
- `robomotion googleforms add_open_ended_question --form-id --question-title --1 [--type]`
  Adds a text-based question (short answer or paragraph) to a Google Form
- `robomotion googleforms add_closed_ended_question --form-id --question-title --answers --1 [--type] [--correct-answers] [--1]`
  Adds a multiple choice question (radio٫ checkbox٫ or dropdown) to a Google Form
- `robomotion googleforms get_responses --form-id`
  Retrieves all submitted responses for a Google Form
- `robomotion googleforms open_form --form-url`
  Opens an existing Google Form by URL for further operations
- `robomotion googleforms get_form --form-id`
  Retrieves the full form structure including questions and settings
- `robomotion googleforms delete_question --form-id --1`
  Deletes a question from a Google Form by its position index

## Environment
- ROBOMOTION_API_TOKEN (if vault credentials are needed)
