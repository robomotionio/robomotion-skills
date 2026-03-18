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

## Workflow
1. Install: `robomotion install trello`
2. Connect: `robomotion trello trello_connect` → returns a `client-id`
3. Create card: `robomotion trello trello_create_card --client-id <id> --list-id <list> --name <name>`
4. List cards: `robomotion trello trello_list_cards --client-id <id> --list-id <list>`
5. Disconnect: `robomotion trello trello_disconnect --client-id <id>`

## Commands Reference
- `robomotion trello trello_connect`
  Connects to Trello API and returns a client ID for subsequent operations
- `robomotion trello trello_disconnect --client-id`
  Closes the Trello connection and releases resources
- `robomotion trello trello_list_boards --client-id [--filter]`
  Lists all Trello boards for the authenticated user
- `robomotion trello trello_get_board --client-id --board-id`
  Gets a specific Trello board by its ID
- `robomotion trello trello_create_board --client-id --board-name --description [--default-lists] [--permission-level]`
  Creates a new Trello board
- `robomotion trello trello_get_lists --client-id --board-id [--filter]`
  Gets all lists from a Trello board
- `robomotion trello trello_create_list --client-id --board-id --list-name [--bottom]`
  Creates a new list in a Trello board
- `robomotion trello trello_list_cards --client-id --list-id --board-id [--filter]`
  Lists all cards from a Trello list or board
- `robomotion trello trello_get_card --client-id --card-id`
  Gets a specific Trello card by its ID
- `robomotion trello trello_create_card --client-id --list-id --card-name --description --due-date [--bottom]`
  Creates a new card in a Trello list
- `robomotion trello trello_update_card --client-id --card-id --new-name --new-description --due-date --due-complete`
  Updates an existing Trello card
- `robomotion trello trello_delete_card --client-id --card-id`
  Permanently deletes a Trello card
- `robomotion trello trello_move_card --client-id --card-id --target-list-id --target-board-id [--bottom]`
  Moves a Trello card to a different list
- `robomotion trello trello_archive_card --client-id --card-id [--action]`
  Archives or unarchives a Trello card
- `robomotion trello trello_add_attachment --client-id --card-id --url --file-path --attachment-name`
  Adds an attachment to a Trello card (URL or file)
- `robomotion trello trello_add_comment --client-id --card-id --comment-text`
  Adds a comment to a Trello card
- `robomotion trello trello_add_label --client-id --card-id --label-id`
  Adds an existing label to a Trello card
- `robomotion trello trello_create_checklist --client-id --card-id --checklist-name [--bottom]`
  Creates a new checklist on a Trello card
- `robomotion trello trello_add_checklist_item --client-id --checklist-id --item-name [--checked] [--bottom]`
  Adds an item to a Trello checklist
- `robomotion trello trello_list_members --client-id --board-id`
  Lists all members of a Trello board

## Environment
- ROBOMOTION_API_TOKEN (if vault credentials are needed)
