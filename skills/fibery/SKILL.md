---
name: "fibery"
description: "Fibery workspace platform — manage entities, databases, documents, and spaces. Supports CRUD on any entity type with filtering and search via `robomotion fibery`. Do NOT use for Notion, ClickUp, Monday.com, or other productivity platforms."
---

# Fibery

The `robomotion fibery` CLI connects to Fibery for workspace and entity management. It creates, reads, updates, and deletes entities in any Fibery database, lists available types/spaces, and supports filtered queries.

## When to use
- Create, update, or delete entities in Fibery databases
- List and search entities with filters
- Browse available entity types and database schemas

## Prerequisites
- `robomotion` CLI installed
- Package installed: `robomotion install fibery`
- Fibery API token and workspace URL configured via Robomotion vault

## Workflow
1. Install: `robomotion install fibery`
2. Connect: `robomotion fibery fibery_connect` → returns a `client-id`
3. List entities: `robomotion fibery fibery_list_entities --client-id <id> --type <type>`
4. Create entity: `robomotion fibery fibery_create_entity --client-id <id> --type <type> --fields <json>`
5. Disconnect: `robomotion fibery fibery_disconnect --client-id <id>`

## Commands Reference
- `robomotion fibery fibery_connect`
  Connects to Fibery API and returns a client ID for subsequent operations
- `robomotion fibery fibery_disconnect --client-id`
  Closes the Fibery connection and releases resources
- `robomotion fibery fibery_query_schema --client-id [--60]`
  Retrieves the Fibery workspace schema including all types، fields، and their properties
- `robomotion fibery fibery_query_entities --client-id --entity-type --select-fields --where --order-by [--100] [--0] [--60]`
  Queries and retrieves entities from a Fibery database with optional filtering، sorting، and pagination
- `robomotion fibery fibery_create_entity --client-id --entity-type --fields --entity-id [--60]`
  Creates a new entity in a Fibery database with the specified fields
- `robomotion fibery fibery_update_entity --client-id --entity-type --entity-id --fields [--60]`
  Updates an existing entity in a Fibery database with new field values
- `robomotion fibery fibery_delete_entity --client-id --entity-type --entity-id [--60]`
  Deletes an entity from a Fibery database

## Environment
- ROBOMOTION_API_TOKEN (if vault credentials are needed)
