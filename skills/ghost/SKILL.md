---
name: "ghost"
description: "Ghost CMS — manage posts, pages, tags, members, tiers, newsletters, and offers on Ghost-powered sites. Supports content publishing, membership management, and newsletter configuration via `robomotion ghost`. Do NOT use for WordPress, Medium, or other CMS platforms."
---

# Ghost

The `robomotion ghost` CLI connects to Ghost CMS for content and membership management. It handles creating/updating/deleting posts and pages, managing tags, administering members and tiers, configuring newsletters, and managing offers — covering both content publishing and subscription operations.

## When to use
- Create, update, publish, or delete blog posts and pages
- Manage tags, members, tiers, and subscription offers
- Configure and manage Ghost newsletters
- List and search content, members, and site resources

## Prerequisites
- `robomotion` CLI installed
- Package installed: `robomotion install ghost`
- Ghost Admin API key configured via Robomotion vault

## IMPORTANT: Session Mode Required for Multi-Step Operations
Each CLI command runs as a **separate process** — connection IDs from `connect` do NOT persist across calls.
You MUST use `--session` on `connect` and pass `--session-id` to all subsequent commands.

## Workflow
1. Install (once): `robomotion install ghost`
2. Connect with session:
   ```
   robomotion ghost ghost_connect --session --output json
   # → {"outClientId":"<client-id>","session_id":"<session-id>"}
   ```
3. Use the returned `client-id` and `session-id` in all subsequent commands:
   ```
   robomotion ghost ghost_create_post --client-id "<client-id>" --title <title> --html <body> --status draft --session-id "<session-id>" --output json
   ```
4. Disconnect when done:
   ```
   robomotion ghost ghost_disconnect --client-id "<client-id>" --session-id "<session-id>" --output json
   ```

**Always** append `--output json` to get structured JSON results.

## Commands Reference
- `robomotion ghost ghost_connect --session --output json`
  Connects to Ghost Admin API and returns a client ID
- `robomotion ghost ghost_disconnect --client-id --session-id "<session-id>" --output json`
  Closes the Ghost connection and releases resources
- `robomotion ghost ghost_create_post --client-id --title --html-content [--status] [--featured] [--slug] [--custom-excerpt] [--tags] --session-id "<session-id>" --output json`
  Creates a new post in Ghost CMS
- `robomotion ghost ghost_get_post --client-id --post-id [--include] [--content-format] --session-id "<session-id>" --output json`
  Gets a post by ID from Ghost CMS
- `robomotion ghost ghost_list_posts --client-id [--filter] [--15] [--1] [--order] [--include] [--content-format] [--status] --session-id "<session-id>" --output json`
  Lists posts from Ghost CMS with optional filtering and pagination
- `robomotion ghost ghost_update_post --client-id --post-id --title --html-content [--status] [--featured] [--slug] [--custom-excerpt] [--tags] --session-id "<session-id>" --output json`
  Updates an existing post in Ghost CMS
- `robomotion ghost ghost_delete_post --client-id --post-id --session-id "<session-id>" --output json`
  Deletes a post from Ghost CMS
- `robomotion ghost ghost_create_page --client-id --title --html-content [--status] [--featured] [--slug] [--custom-excerpt] [--tags] --session-id "<session-id>" --output json`
  Creates a new page in Ghost CMS
- `robomotion ghost ghost_get_page --client-id --page-id [--include] [--content-format] --session-id "<session-id>" --output json`
  Gets a page by ID from Ghost CMS
- `robomotion ghost ghost_list_pages --client-id [--filter] [--15] [--1] [--order] [--include] [--content-format] [--status] --session-id "<session-id>" --output json`
  Lists pages from Ghost CMS with optional filtering and pagination
- `robomotion ghost ghost_update_page --client-id --page-id --title --html-content [--status] [--featured] [--slug] [--custom-excerpt] [--tags] --session-id "<session-id>" --output json`
  Updates an existing page in Ghost CMS
- `robomotion ghost ghost_delete_page --client-id --page-id --session-id "<session-id>" --output json`
  Deletes a page from Ghost CMS
- `robomotion ghost ghost_create_member --client-id --email [--name] [--note] [--labels] --session-id "<session-id>" --output json`
  Creates a new member in Ghost CMS
- `robomotion ghost ghost_get_member --client-id --member-id --session-id "<session-id>" --output json`
  Gets a member by ID from Ghost CMS
- `robomotion ghost ghost_list_members --client-id [--filter] [--15] [--1] [--order] [--search] --session-id "<session-id>" --output json`
  Lists members from Ghost CMS with optional filtering and pagination
- `robomotion ghost ghost_update_member --client-id --member-id [--name] [--note] [--labels] --session-id "<session-id>" --output json`
  Updates an existing member in Ghost CMS
- `robomotion ghost ghost_delete_member --client-id --member-id --session-id "<session-id>" --output json`
  Deletes a member from Ghost CMS
- `robomotion ghost ghost_create_tag --client-id --name [--slug] [--description] [--accent-color] --session-id "<session-id>" --output json`
  Creates a new tag in Ghost CMS
- `robomotion ghost ghost_list_tags --client-id [--filter] [--15] [--1] [--order] [--include] --session-id "<session-id>" --output json`
  Lists tags from Ghost CMS with optional filtering and pagination
- `robomotion ghost ghost_delete_tag --client-id --tag-id --session-id "<session-id>" --output json`
  Deletes a tag from Ghost CMS

## Environment
- ROBOMOTION_API_TOKEN (if vault credentials are needed)
