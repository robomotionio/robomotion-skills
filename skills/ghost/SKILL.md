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

## Workflow
1. Install: `robomotion install ghost`
2. Connect: `robomotion ghost ghost_connect` → returns a `client-id`
3. Create post: `robomotion ghost ghost_create_post --client-id <id> --title <title> --html <body> --status draft`
4. List members: `robomotion ghost ghost_list_members --client-id <id>`
5. Disconnect: `robomotion ghost ghost_disconnect --client-id <id>`

## Commands Reference
- `robomotion ghost ghost_connect`
  Connects to Ghost Admin API and returns a client ID
- `robomotion ghost ghost_disconnect --client-id`
  Closes the Ghost connection and releases resources
- `robomotion ghost ghost_create_post --client-id --title --html-content [--status] [--featured] [--slug] [--custom-excerpt] [--tags]`
  Creates a new post in Ghost CMS
- `robomotion ghost ghost_get_post --client-id --post-id [--include] [--content-format]`
  Gets a post by ID from Ghost CMS
- `robomotion ghost ghost_list_posts --client-id [--filter] [--15] [--1] [--order] [--include] [--content-format] [--status]`
  Lists posts from Ghost CMS with optional filtering and pagination
- `robomotion ghost ghost_update_post --client-id --post-id --title --html-content [--status] [--featured] [--slug] [--custom-excerpt] [--tags]`
  Updates an existing post in Ghost CMS
- `robomotion ghost ghost_delete_post --client-id --post-id`
  Deletes a post from Ghost CMS
- `robomotion ghost ghost_create_page --client-id --title --html-content [--status] [--featured] [--slug] [--custom-excerpt] [--tags]`
  Creates a new page in Ghost CMS
- `robomotion ghost ghost_get_page --client-id --page-id [--include] [--content-format]`
  Gets a page by ID from Ghost CMS
- `robomotion ghost ghost_list_pages --client-id [--filter] [--15] [--1] [--order] [--include] [--content-format] [--status]`
  Lists pages from Ghost CMS with optional filtering and pagination
- `robomotion ghost ghost_update_page --client-id --page-id --title --html-content [--status] [--featured] [--slug] [--custom-excerpt] [--tags]`
  Updates an existing page in Ghost CMS
- `robomotion ghost ghost_delete_page --client-id --page-id`
  Deletes a page from Ghost CMS
- `robomotion ghost ghost_create_member --client-id --email [--name] [--note] [--labels]`
  Creates a new member in Ghost CMS
- `robomotion ghost ghost_get_member --client-id --member-id`
  Gets a member by ID from Ghost CMS
- `robomotion ghost ghost_list_members --client-id [--filter] [--15] [--1] [--order] [--search]`
  Lists members from Ghost CMS with optional filtering and pagination
- `robomotion ghost ghost_update_member --client-id --member-id [--name] [--note] [--labels]`
  Updates an existing member in Ghost CMS
- `robomotion ghost ghost_delete_member --client-id --member-id`
  Deletes a member from Ghost CMS
- `robomotion ghost ghost_create_tag --client-id --name [--slug] [--description] [--accent-color]`
  Creates a new tag in Ghost CMS
- `robomotion ghost ghost_list_tags --client-id [--filter] [--15] [--1] [--order] [--include]`
  Lists tags from Ghost CMS with optional filtering and pagination
- `robomotion ghost ghost_delete_tag --client-id --tag-id`
  Deletes a tag from Ghost CMS

## Environment
- ROBOMOTION_API_TOKEN (if vault credentials are needed)
