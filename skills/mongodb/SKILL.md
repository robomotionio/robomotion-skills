---
name: "mongodb"
description: "MongoDB — query, insert, update, delete, and aggregate documents in MongoDB collections. Supports CRUD operations, aggregation pipelines, and collection management via `robomotion mongodb`. Do NOT use for PostgreSQL, MySQL, Redis, or other databases."
---

# MongoDB

The `robomotion mongodb` CLI connects to MongoDB for document database operations. It supports finding, inserting, updating, and deleting documents; running aggregation pipelines; and managing collections.

## When to use
- Query documents with filters and projections
- Insert, update, or delete documents in collections
- Run aggregation pipelines for data analysis
- Manage MongoDB connections and collections

## Prerequisites
- `robomotion` CLI installed
- Package installed: `robomotion install mongodb`
- MongoDB connection URI configured via Robomotion vault

## IMPORTANT: Session Mode Required for Multi-Step Operations
Each CLI command runs as a **separate process** — connection IDs from `connect` do NOT persist across calls.
You MUST use `--session` on `connect` and pass `--session-id` to all subsequent commands.

## Workflow
1. Install (once): `robomotion install mongodb`
2. Connect with session:
   ```
   robomotion mongodb connect --session --output json
   # → {"outConnectionId":"<conn-id>","session_id":"<session-id>"}
   ```
3. Use the returned `conn-id` and `session-id` in all subsequent commands:
   ```
   robomotion mongodb find --conn-id "<conn-id>" --collection <col> --filter <json> --session-id "<session-id>" --output json
   ```
4. Disconnect when done:
   ```
   robomotion mongodb disconnect --conn-id "<conn-id>" --session-id "<session-id>" --output json
   ```

**Always** append `--output json` to get structured JSON results.

## Commands Reference
- `robomotion mongodb drop_database --client-id --database-name --session-id "<session-id>" --output json`
  Delete an entire MongoDB database and all its collections
- `robomotion mongodb list_databases --client-id --session-id "<session-id>" --output json`
  List all databases available on the MongoDB server
- `robomotion mongodb connect --session --output json`
  Connect to a MongoDB database server using credentials
- `robomotion mongodb create_database --client-id --database-name --session-id "<session-id>" --output json`
  Create a new MongoDB database
- `robomotion mongodb create_collection --client-id --database-name --collection-name --session-id "<session-id>" --output json`
  Create a new collection in a MongoDB database
- `robomotion mongodb drop_collection --client-id --database-name --collection-name --session-id "<session-id>" --output json`
  Delete a collection and all its documents from a MongoDB database
- `robomotion mongodb insert_document --client-id --database-name --collection-name --session-id "<session-id>" --output json`
  Insert one or more documents into a MongoDB collection
- `robomotion mongodb delete_document --client-id --database-name --collection-name --session-id "<session-id>" --output json`
  Delete documents from a MongoDB collection that match the specified query filter
- `robomotion mongodb disconnect --client-id --session-id "<session-id>" --output json`
  Disconnect from a MongoDB database server and release the client connection
- `robomotion mongodb update_document --client-id --database-name --collection-name --session-id "<session-id>" --output json`
  Update documents in a MongoDB collection that match the specified filter
- `robomotion mongodb read_document --client-id --database-name --collection-name --session-id "<session-id>" --output json`
  Query and read documents from a MongoDB collection using a filter
- `robomotion mongodb read_all --client-id --database-name --collection-name --session-id "<session-id>" --output json`
  Read all documents from a MongoDB collection
- `robomotion mongodb show_collections --client-id --database-name --session-id "<session-id>" --output json`
  List all collections in a MongoDB database

## Environment
- ROBOMOTION_API_TOKEN (if vault credentials are needed)
