---
name: "wordpress"
description: "WordPress — manage posts, pages, categories, tags, media, users, and comments. Supports content publishing, media uploads, and site administration via `robomotion wordpress`. Do NOT use for Ghost, Medium, or other CMS platforms."
---

# WordPress

The `robomotion wordpress` CLI connects to WordPress sites via the REST API for content management. It creates and manages posts and pages, handles categories and tags, uploads media, and administers users and comments.

## When to use
- Create, update, list, or delete posts and pages
- Manage categories, tags, and media uploads
- Administer users and moderate comments

## Prerequisites
- `robomotion` CLI installed
- Package installed: `robomotion install wordpress`
- WordPress site URL and API credentials configured via Robomotion vault

## IMPORTANT: Session Mode Required for Multi-Step Operations
Each CLI command runs as a **separate process** — connection IDs from `connect` do NOT persist across calls.
You MUST use `--session` on `connect` and pass `--session-id` to all subsequent commands.

## Workflow
1. Install (once): `robomotion install wordpress`
2. Connect with session:
   ```
   robomotion wordpress wordpress_connect --session --output json
   # → {"outClientId":"<client-id>","session_id":"<session-id>"}
   ```
3. Use the returned `client-id` and `session-id` in all subsequent commands:
   ```
   robomotion wordpress wordpress_create_post --client-id "<client-id>" --title <title> --content <html> --status draft --session-id "<session-id>" --output json
   ```
4. Disconnect when done:
   ```
   robomotion wordpress wordpress_disconnect --client-id "<client-id>" --session-id "<session-id>" --output json
   ```

**Always** append `--output json` to get structured JSON results.

## Commands Reference
- `robomotion wordpress connect --url --session --output json`
  Connect to WordPress using Basic Auth and return a client ID for subsequent operations
- `robomotion wordpress create_post --client-id --post [--site-url] --session-id "<session-id>" --output json`
  Create a new post in WordPress with specified content and settings
- `robomotion wordpress list_posts --client-id [--site-url] [--status] [--1] [--100] --session-id "<session-id>" --output json`
  List posts from WordPress with optional filtering by status and pagination
- `robomotion wordpress create_category --client-id --category [--site-url] --session-id "<session-id>" --output json`
  Create a new category in WordPress
- `robomotion wordpress list_categories --client-id [--site-url] --session-id "<session-id>" --output json`
  List all categories from WordPress
- `robomotion wordpress create_media --client-id --file-path --file-name [--site-url] [--content-type] --session-id "<session-id>" --output json`
  Upload a media file to WordPress media library
- `robomotion wordpress disconnect --client-id --session-id "<session-id>" --output json`
  Disconnect from WordPress and release the client connection
- `robomotion wordpress delete --client-id --object-id [--site-url] [--object] --session-id "<session-id>" --output json`
  Delete a post٫ media٫ or category from WordPress
- `robomotion wordpress update --client-id --object-id --object [--site-url] [--object] --session-id "<session-id>" --output json`
  Update an existing post or category in WordPress
- `robomotion wordpress get --client-id --object-id [--site-url] [--object] --session-id "<session-id>" --output json`
  Get a single post or category from WordPress by ID
- `robomotion wordpress list_media --client-id [--site-url] --session-id "<session-id>" --output json`
  List all media files from WordPress media library

## Environment
- ROBOMOTION_API_TOKEN (if vault credentials are needed)
