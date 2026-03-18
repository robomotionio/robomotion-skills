---
name: "qdrant"
description: "Qdrant vector database — upsert, search, and manage vector embeddings with payload filtering. Supports collection management, similarity search, batch operations, and scroll queries via `robomotion qdrant`. Do NOT use for Pinecone, Weaviate, ChromaDB, or other vector databases."
---

# Qdrant

The `robomotion qdrant` CLI connects to Qdrant for vector database operations. It upserts, searches, scrolls, and deletes points; manages collections with configurable distance metrics; supports batch operations; and performs filtered similarity searches with payload conditions.

## When to use
- Upsert vectors with payloads into Qdrant collections
- Search for similar vectors with filtering and scoring
- Manage collections — create, delete, get info
- Scroll through points and retrieve by ID

## Prerequisites
- `robomotion` CLI installed
- Package installed: `robomotion install qdrant`
- Qdrant instance URL and API key (if secured) configured via Robomotion vault

## Workflow
1. Install: `robomotion install qdrant`
2. Connect: `robomotion qdrant qdrant_connect` → returns a `client-id`
3. Upsert: `robomotion qdrant qdrant_upsert_points --client-id <id> --collection <col> --points <json>`
4. Search: `robomotion qdrant qdrant_search --client-id <id> --collection <col> --vector <vec> --limit 10`
5. Disconnect: `robomotion qdrant qdrant_disconnect --client-id <id>`

## Commands Reference
- `robomotion qdrant qdrant_connect --localhost --6334 [--30]`
  Connects to Qdrant vector database and returns a client ID for subsequent operations
- `robomotion qdrant qdrant_disconnect --client-id`
  Closes the Qdrant connection and releases resources
- `robomotion qdrant qdrant_create_collection --client-id --collection-name --vector-size [--localhost] [--6334] [--distance-metric] [--60]`
  Creates a new collection in Qdrant for storing vectors
- `robomotion qdrant qdrant_list_collections --client-id [--localhost] [--6334] [--30]`
  Lists all collections in Qdrant
- `robomotion qdrant qdrant_get_collection --client-id --collection-name [--localhost] [--6334] [--30]`
  Gets detailed information about a specific collection
- `robomotion qdrant qdrant_delete_collection --client-id --collection-name [--localhost] [--6334] [--60]`
  Deletes a collection and all its data from Qdrant
- `robomotion qdrant qdrant_collection_exists --client-id --collection-name [--localhost] [--6334] [--30]`
  Checks if a collection exists in Qdrant
- `robomotion qdrant qdrant_upsert_points --client-id --collection-name --points [--localhost] [--6334] [--60]`
  Inserts or updates points (vectors with payload) in a collection
- `robomotion qdrant qdrant_get_points --client-id --collection-name --point-ids [--localhost] [--6334] [--30]`
  Retrieves points by their IDs from a collection
- `robomotion qdrant qdrant_delete_points --client-id --collection-name --point-ids [--localhost] [--6334] [--60]`
  Deletes points from a collection by IDs or filter
- `robomotion qdrant qdrant_scroll_points --client-id --collection-name --offset [--localhost] [--6334] [--100] [--30]`
  Iterates through all points in a collection with optional filtering
- `robomotion qdrant qdrant_count_points --client-id --collection-name [--localhost] [--6334] [--30]`
  Counts points in a collection with optional filtering
- `robomotion qdrant qdrant_query_points --client-id --collection-name --vector [--localhost] [--6334] [--10] [--score-threshold] [--30]`
  Searches for similar vectors in a collection using vector similarity
- `robomotion qdrant qdrant_set_payload --client-id --collection-name --point-ids --payload [--localhost] [--6334] [--60]`
  Sets or updates payload fields for specified points
- `robomotion qdrant qdrant_delete_payload --client-id --collection-name --point-ids --keys [--localhost] [--6334] [--60]`
  Deletes specific payload fields from points
- `robomotion qdrant qdrant_clear_payload --client-id --collection-name --point-ids [--localhost] [--6334] [--60]`
  Removes all payload fields from specified points

## Environment
- ROBOMOTION_API_TOKEN (if vault credentials are needed)
