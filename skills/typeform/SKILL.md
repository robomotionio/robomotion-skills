---
name: "typeform"
description: "Typeform — manage forms, collect responses, and analyze submission data. Supports form listing, response retrieval, and form management via `robomotion typeform`. Do NOT use for Google Forms, SurveyMonkey, or other form builders."
---

# Typeform

The `robomotion typeform` CLI connects to Typeform for form and survey management. It lists forms, retrieves responses with filtering, manages form settings, and handles form lifecycle operations.

## When to use
- List forms and retrieve form details
- Collect and filter form responses/submissions
- Manage form settings and configuration

## Prerequisites
- `robomotion` CLI installed
- Package installed: `robomotion install typeform`
- Typeform API token configured via Robomotion vault

## Workflow
1. Install: `robomotion install typeform`
2. Connect: `robomotion typeform typeform_connect` → returns a `client-id`
3. List forms: `robomotion typeform typeform_list_forms --client-id <id>`
4. Get responses: `robomotion typeform typeform_list_responses --client-id <id> --form-id <form>`
5. Disconnect: `robomotion typeform typeform_disconnect --client-id <id>`

## Commands Reference
- `robomotion typeform typeform_connect`
  Connects to Typeform API and returns a client ID
- `robomotion typeform typeform_disconnect --client-id`
  Closes the Typeform connection and releases resources
- `robomotion typeform typeform_list_forms --client-id [--search] [--10] [--1] [--workspace-id]`
  Lists forms in your Typeform account
- `robomotion typeform typeform_get_form --client-id --form-id`
  Retrieves a single form with all its details and fields
- `robomotion typeform typeform_create_form --client-id --title [--workspace-url]`
  Creates a new Typeform form
- `robomotion typeform typeform_delete_form --client-id --form-id`
  Deletes a Typeform form and all its responses
- `robomotion typeform typeform_list_responses --client-id --form-id [--25] [--since] [--until] [--query] [--response-type]`
  Retrieves responses for a Typeform form
- `robomotion typeform typeform_delete_responses --client-id --form-id --response-i-ds`
  Deletes specific responses from a Typeform form

## Environment
- ROBOMOTION_API_TOKEN (if vault credentials are needed)
