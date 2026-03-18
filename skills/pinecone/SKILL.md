---
name: "pinecone"
description: "Pinecone vector database — upsert, query, and manage vector embeddings in Pinecone indexes. Supports similarity search, namespace management, and index operations via `robomotion pinecone`. Do NOT use for Qdrant, Weaviate, ChromaDB, or other vector databases."
---

# Pinecone

The `robomotion pinecone` CLI connects to Pinecone for vector database operations. It upserts, queries, fetches, and deletes vectors; manages indexes and namespaces; and performs similarity searches with metadata filtering.

## When to use
- Upsert vector embeddings into Pinecone indexes
- Query for similar vectors with top-K and metadata filtering
- Manage Pinecone indexes — create, describe, list, delete
- Fetch vectors by ID and manage namespaces

## Prerequisites
- `robomotion` CLI installed
- Package installed: `robomotion install pinecone`
- Pinecone API key configured via Robomotion vault

## IMPORTANT: Session Mode Required for Multi-Step Operations
Each CLI command runs as a **separate process** — connection IDs from `connect` do NOT persist across calls.
You MUST use `--session` on `connect` and pass `--session-id` to all subsequent commands.

## Workflow
1. Install (once): `robomotion install pinecone`
2. Connect with session:
   ```
   robomotion pinecone pinecone_connect --session --output json
   # → {"outClientId":"<client-id>","session_id":"<session-id>"}
   ```
3. Use the returned `client-id` and `session-id` in all subsequent commands:
   ```
   robomotion pinecone pinecone_upsert --client-id "<client-id>" --index <idx> --vectors <json> --session-id "<session-id>" --output json
   ```
4. Disconnect when done:
   ```
   robomotion pinecone pinecone_disconnect --client-id "<client-id>" --session-id "<session-id>" --output json
   ```

**Always** append `--output json` to get structured JSON results.

## Commands Reference
- `robomotion pinecone connect --session --output json`
  Connect to Pinecone vector database and create a client session
- `robomotion pinecone create_index --connection-id --environment --name --dimension [--metric] [--1] [--1] [--p-1] [--source-collection] --session-id "<session-id>" --output json`
  Create a new Pinecone index with specified configuration
- `robomotion pinecone upsert --connection-id --host-url --ids --values [--metadatas] [--name-space] --session-id "<session-id>" --output json`
  Insert or update vectors in a Pinecone index
- `robomotion pinecone query --connection-id --host-url --10 [--name-space] [--vector] [--id] [--filter] --session-id "<session-id>" --output json`
  Query vectors by similarity using a vector or ID
- `robomotion pinecone describe_index_stats --connection-id --host-url [--filter] --session-id "<session-id>" --output json`
  Get statistics about a Pinecone index including vector count and dimension
- `robomotion pinecone fetch --connection-id --host-url --ids --session-id "<session-id>" --output json`
  Fetch vectors by ID from a Pinecone index
- `robomotion pinecone delete --connection-id --host-url [--ids] [--filter] [--name-space] --session-id "<session-id>" --output json`
  Delete vectors from a Pinecone index by ID٫ filter٫ or all
- `robomotion pinecone list_or_describe_indexes --connection-id --environment --index-name [--method] --session-id "<session-id>" --output json`
  List all indexes or get details of a specific index
- `robomotion pinecone delete_index --connection-id --environment --index-name --session-id "<session-id>" --output json`
  Delete a Pinecone index permanently
- `robomotion pinecone update --connection-id --host-url --id --values [--metadata] [--name-space] --session-id "<session-id>" --output json`
  Update a vector's values or metadata in a Pinecone index

## Environment
- ROBOMOTION_API_TOKEN (if vault credentials are needed)
