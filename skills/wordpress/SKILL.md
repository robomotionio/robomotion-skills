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

## Workflow
1. Install: `robomotion install wordpress`
2. Connect: `robomotion wordpress wordpress_connect` → returns a `client-id`
3. Create post: `robomotion wordpress wordpress_create_post --client-id <id> --title <title> --content <html> --status draft`
4. List posts: `robomotion wordpress wordpress_list_posts --client-id <id>`
5. Disconnect: `robomotion wordpress wordpress_disconnect --client-id <id>`

## Commands Reference
- `robomotion wordpress connect --url`
  Connect to WordPress using Basic Auth and return a client ID for subsequent operations
- `robomotion wordpress create_post --client-id --post [--site-url]`
  Create a new post in WordPress with specified content and settings
- `robomotion wordpress list_posts --client-id [--site-url] [--status] [--1] [--100]`
  List posts from WordPress with optional filtering by status and pagination
- `robomotion wordpress create_category --client-id --category [--site-url]`
  Create a new category in WordPress
- `robomotion wordpress list_categories --client-id [--site-url]`
  List all categories from WordPress
- `robomotion wordpress create_media --client-id --file-path --file-name [--site-url] [--content-type]`
  Upload a media file to WordPress media library
- `robomotion wordpress disconnect --client-id`
  Disconnect from WordPress and release the client connection
- `robomotion wordpress delete --client-id --object-id [--site-url] [--object]`
  Delete a post٫ media٫ or category from WordPress
- `robomotion wordpress update --client-id --object-id --object [--site-url] [--object]`
  Update an existing post or category in WordPress
- `robomotion wordpress get --client-id --object-id [--site-url] [--object]`
  Get a single post or category from WordPress by ID
- `robomotion wordpress list_media --client-id [--site-url]`
  List all media files from WordPress media library

## Environment
- ROBOMOTION_API_TOKEN (if vault credentials are needed)
