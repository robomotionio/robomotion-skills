---
name: "mongodb"
description: "Use when the user wants to call the Robomotion MongoDB package to query, insert, or manage documents in MongoDB via the `robomotion mongodb` CLI. Do NOT use for SQL databases like PostgreSQL or MySQL."
---

# Mongodb Skill

## When to use
- Query documents in MongoDB collections
- Insert or update MongoDB documents
- Aggregate data in MongoDB

## Prerequisites
- `robomotion` CLI installed
- Package installed: `robomotion install mongodb`
- Credentials configured via Robomotion vault or environment variables

## Workflow
1. Install the package: `robomotion install mongodb`
2. Run commands: `robomotion mongodb <command> [flags]`

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
