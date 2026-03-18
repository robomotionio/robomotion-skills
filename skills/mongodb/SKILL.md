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

## Workflow
1. Install: `robomotion install mongodb`
2. Connect: `robomotion mongodb connect` → returns a `conn-id`
3. Find: `robomotion mongodb find --conn-id <id> --collection <col> --filter <json>`
4. Insert: `robomotion mongodb insert_one --conn-id <id> --collection <col> --document <json>`
5. Disconnect: `robomotion mongodb disconnect --conn-id <id>`

## Commands Reference
- `robomotion mongodb drop_database --client-id --database-name`
  Delete an entire MongoDB database and all its collections
- `robomotion mongodb list_databases --client-id`
  List all databases available on the MongoDB server
- `robomotion mongodb connect`
  Connect to a MongoDB database server using credentials
- `robomotion mongodb create_database --client-id --database-name`
  Create a new MongoDB database
- `robomotion mongodb create_collection --client-id --database-name --collection-name`
  Create a new collection in a MongoDB database
- `robomotion mongodb drop_collection --client-id --database-name --collection-name`
  Delete a collection and all its documents from a MongoDB database
- `robomotion mongodb insert_document --client-id --database-name --collection-name`
  Insert one or more documents into a MongoDB collection
- `robomotion mongodb delete_document --client-id --database-name --collection-name`
  Delete documents from a MongoDB collection that match the specified query filter
- `robomotion mongodb disconnect --client-id`
  Disconnect from a MongoDB database server and release the client connection
- `robomotion mongodb update_document --client-id --database-name --collection-name`
  Update documents in a MongoDB collection that match the specified filter
- `robomotion mongodb read_document --client-id --database-name --collection-name`
  Query and read documents from a MongoDB collection using a filter
- `robomotion mongodb read_all --client-id --database-name --collection-name`
  Read all documents from a MongoDB collection
- `robomotion mongodb show_collections --client-id --database-name`
  List all collections in a MongoDB database

## Environment
- ROBOMOTION_API_TOKEN (if vault credentials are needed)
