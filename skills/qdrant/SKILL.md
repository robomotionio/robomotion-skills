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

## IMPORTANT: Session Mode Required for Multi-Step Operations
Each CLI command runs as a **separate process** — connection IDs from `connect` do NOT persist across calls.
You MUST use `--session` on `connect` and pass `--session-id` to all subsequent commands.

## Workflow
1. Install (once): `robomotion install qdrant`
2. Connect with session:
   ```
   robomotion qdrant qdrant_connect --session --output json
   # → {"outClientId":"<client-id>","session_id":"<session-id>"}
   ```
3. Use the returned `client-id` and `session-id` in all subsequent commands:
   ```
   robomotion qdrant qdrant_upsert_points --client-id "<client-id>" --collection <col> --points <json> --session-id "<session-id>" --output json
   ```
4. Disconnect when done:
   ```
   robomotion qdrant qdrant_disconnect --client-id "<client-id>" --session-id "<session-id>" --output json
   ```

**Always** append `--output json` to get structured JSON results.

## Commands Reference
- `robomotion qdrant qdrant_connect --localhost --6334 [--30] --session --output json`
  Connects to Qdrant vector database and returns a client ID for subsequent operations
- `robomotion qdrant qdrant_disconnect --client-id --session-id "<session-id>" --output json`
  Closes the Qdrant connection and releases resources
- `robomotion qdrant qdrant_create_collection --client-id --collection-name --vector-size [--localhost] [--6334] [--distance-metric] [--60] --session-id "<session-id>" --output json`
  Creates a new collection in Qdrant for storing vectors
- `robomotion qdrant qdrant_list_collections --client-id [--localhost] [--6334] [--30] --session-id "<session-id>" --output json`
  Lists all collections in Qdrant
- `robomotion qdrant qdrant_get_collection --client-id --collection-name [--localhost] [--6334] [--30] --session-id "<session-id>" --output json`
  Gets detailed information about a specific collection
- `robomotion qdrant qdrant_delete_collection --client-id --collection-name [--localhost] [--6334] [--60] --session-id "<session-id>" --output json`
  Deletes a collection and all its data from Qdrant
- `robomotion qdrant qdrant_collection_exists --client-id --collection-name [--localhost] [--6334] [--30] --session-id "<session-id>" --output json`
  Checks if a collection exists in Qdrant
- `robomotion qdrant qdrant_upsert_points --client-id --collection-name --points [--localhost] [--6334] [--60] --session-id "<session-id>" --output json`
  Inserts or updates points (vectors with payload) in a collection
- `robomotion qdrant qdrant_get_points --client-id --collection-name --point-ids [--localhost] [--6334] [--30] --session-id "<session-id>" --output json`
  Retrieves points by their IDs from a collection
- `robomotion qdrant qdrant_delete_points --client-id --collection-name --point-ids [--localhost] [--6334] [--60] --session-id "<session-id>" --output json`
  Deletes points from a collection by IDs or filter
- `robomotion qdrant qdrant_scroll_points --client-id --collection-name --offset [--localhost] [--6334] [--100] [--30] --session-id "<session-id>" --output json`
  Iterates through all points in a collection with optional filtering
- `robomotion qdrant qdrant_count_points --client-id --collection-name [--localhost] [--6334] [--30] --session-id "<session-id>" --output json`
  Counts points in a collection with optional filtering
- `robomotion qdrant qdrant_query_points --client-id --collection-name --vector [--localhost] [--6334] [--10] [--score-threshold] [--30] --session-id "<session-id>" --output json`
  Searches for similar vectors in a collection using vector similarity
- `robomotion qdrant qdrant_set_payload --client-id --collection-name --point-ids --payload [--localhost] [--6334] [--60] --session-id "<session-id>" --output json`
  Sets or updates payload fields for specified points
- `robomotion qdrant qdrant_delete_payload --client-id --collection-name --point-ids --keys [--localhost] [--6334] [--60] --session-id "<session-id>" --output json`
  Deletes specific payload fields from points
- `robomotion qdrant qdrant_clear_payload --client-id --collection-name --point-ids [--localhost] [--6334] [--60] --session-id "<session-id>" --output json`
  Removes all payload fields from specified points

## Environment
- ROBOMOTION_API_TOKEN (if vault credentials are needed)
