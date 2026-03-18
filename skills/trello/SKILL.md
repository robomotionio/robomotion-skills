---
name: "trello"
description: "Trello — manage boards, lists, cards, labels, checklists, and members for visual project management. Supports full card lifecycle including attachments, comments, and checklist items via `robomotion trello`. Do NOT use for Jira, ClickUp, Asana, or other PM tools."
---

# Trello

The `robomotion trello` CLI connects to Trello for visual project management. It manages boards, lists, and cards with full lifecycle support — creating, moving, archiving cards; adding labels, checklists, and attachments; managing members; and handling comments.

## When to use
- Create, update, move, or archive cards across lists and boards
- Manage labels, checklists, and checklist items on cards
- Add attachments and comments to cards
- List and manage boards, lists, and members

## Prerequisites
- `robomotion` CLI installed
- Package installed: `robomotion install trello`
- Trello API key and token configured via Robomotion vault

## IMPORTANT: Session Mode Required for Multi-Step Operations
Each CLI command runs as a **separate process** — connection IDs from `connect` do NOT persist across calls.
You MUST use `--session` on `connect` and pass `--session-id` to all subsequent commands.

## Workflow
1. Install (once): `robomotion install trello`
2. Connect with session:
   ```
   robomotion trello trello_connect --session --output json
   # → {"outClientId":"<client-id>","session_id":"<session-id>"}
   ```
3. Use the returned `client-id` and `session-id` in all subsequent commands:
   ```
   robomotion trello trello_create_card --client-id "<client-id>" --list-id <list> --name <name> --session-id "<session-id>" --output json
   ```
4. Disconnect when done:
   ```
   robomotion trello trello_disconnect --client-id "<client-id>" --session-id "<session-id>" --output json
   ```

**Always** append `--output json` to get structured JSON results.

## Commands Reference
- `robomotion trello trello_connect --session --output json`
  Connects to Trello API and returns a client ID for subsequent operations
- `robomotion trello trello_disconnect --client-id --session-id "<session-id>" --output json`
  Closes the Trello connection and releases resources
- `robomotion trello trello_list_boards --client-id [--filter] --session-id "<session-id>" --output json`
  Lists all Trello boards for the authenticated user
- `robomotion trello trello_get_board --client-id --board-id --session-id "<session-id>" --output json`
  Gets a specific Trello board by its ID
- `robomotion trello trello_create_board --client-id --board-name --description [--default-lists] [--permission-level] --session-id "<session-id>" --output json`
  Creates a new Trello board
- `robomotion trello trello_get_lists --client-id --board-id [--filter] --session-id "<session-id>" --output json`
  Gets all lists from a Trello board
- `robomotion trello trello_create_list --client-id --board-id --list-name [--bottom] --session-id "<session-id>" --output json`
  Creates a new list in a Trello board
- `robomotion trello trello_list_cards --client-id --list-id --board-id [--filter] --session-id "<session-id>" --output json`
  Lists all cards from a Trello list or board
- `robomotion trello trello_get_card --client-id --card-id --session-id "<session-id>" --output json`
  Gets a specific Trello card by its ID
- `robomotion trello trello_create_card --client-id --list-id --card-name --description --due-date [--bottom] --session-id "<session-id>" --output json`
  Creates a new card in a Trello list
- `robomotion trello trello_update_card --client-id --card-id --new-name --new-description --due-date --due-complete --session-id "<session-id>" --output json`
  Updates an existing Trello card
- `robomotion trello trello_delete_card --client-id --card-id --session-id "<session-id>" --output json`
  Permanently deletes a Trello card
- `robomotion trello trello_move_card --client-id --card-id --target-list-id --target-board-id [--bottom] --session-id "<session-id>" --output json`
  Moves a Trello card to a different list
- `robomotion trello trello_archive_card --client-id --card-id [--action] --session-id "<session-id>" --output json`
  Archives or unarchives a Trello card
- `robomotion trello trello_add_attachment --client-id --card-id --url --file-path --attachment-name --session-id "<session-id>" --output json`
  Adds an attachment to a Trello card (URL or file)
- `robomotion trello trello_add_comment --client-id --card-id --comment-text --session-id "<session-id>" --output json`
  Adds a comment to a Trello card
- `robomotion trello trello_add_label --client-id --card-id --label-id --session-id "<session-id>" --output json`
  Adds an existing label to a Trello card
- `robomotion trello trello_create_checklist --client-id --card-id --checklist-name [--bottom] --session-id "<session-id>" --output json`
  Creates a new checklist on a Trello card
- `robomotion trello trello_add_checklist_item --client-id --checklist-id --item-name [--checked] [--bottom] --session-id "<session-id>" --output json`
  Adds an item to a Trello checklist
- `robomotion trello trello_list_members --client-id --board-id --session-id "<session-id>" --output json`
  Lists all members of a Trello board

## Environment
- ROBOMOTION_API_TOKEN (if vault credentials are needed)
