---
name: "redis"
description: "Redis — perform key-value operations on strings, hashes, lists, sets, and pub/sub channels. Supports TTL, pattern matching, and all core Redis data structures via `robomotion redis`. Do NOT use for PostgreSQL, MongoDB, Memcached, or other databases."
---

# Redis

The `robomotion redis` CLI connects to Redis for key-value and data structure operations. It supports strings (get/set with TTL), hashes (hset/hget/hgetall), lists (push/pop/range), sets (add/remove/members), key management (exists/expire/keys), and pub/sub messaging.

## When to use
- Get, set, or delete key-value pairs with optional TTL
- Work with hashes, lists, and sets (full CRUD)
- Publish messages to channels (pub/sub)
- Search keys by pattern, check existence, and manage expiration

## Prerequisites
- `robomotion` CLI installed
- Package installed: `robomotion install redis`
- Redis connection credentials configured via Robomotion vault

## IMPORTANT: Session Mode Required for Multi-Step Operations
Each CLI command runs as a **separate process** — connection IDs from `connect` do NOT persist across calls.
You MUST use `--session` on `connect` and pass `--session-id` to all subsequent commands.

## Workflow
1. Install (once): `robomotion install redis`
2. Connect with session:
   ```
   robomotion redis redis_connect --session --output json
   # → {"outClientId":"<client-id>","session_id":"<session-id>"}
   ```
3. Use the returned `client-id` and `session-id` in all subsequent commands:
   ```
   robomotion redis redis_set --client-id "<client-id>" --key <key> --value <val> --session-id "<session-id>" --output json
   ```
4. Disconnect when done:
   ```
   robomotion redis redis_disconnect --client-id "<client-id>" --session-id "<session-id>" --output json
   ```

**Always** append `--output json` to get structured JSON results.

## Commands Reference
- `robomotion redis redis_connect --session --output json`
  Connects to a Redis server and returns a client ID for subsequent operations
- `robomotion redis redis_disconnect --client-id --session-id "<session-id>" --output json`
  Closes the Redis connection and releases resources
- `robomotion redis redis_get --client-id --key --session-id "<session-id>" --output json`
  Gets the value of a key from Redis
- `robomotion redis redis_set --client-id --key --value [--0] --session-id "<session-id>" --output json`
  Sets a key-value pair in Redis with optional expiration
- `robomotion redis redis_delete --client-id --key --session-id "<session-id>" --output json`
  Deletes one or more keys from Redis
- `robomotion redis redis_hset --client-id --key --field --value --session-id "<session-id>" --output json`
  Sets a field in a Redis hash
- `robomotion redis redis_hget --client-id --key --field --session-id "<session-id>" --output json`
  Gets a field value from a Redis hash
- `robomotion redis redis_hgetall --client-id --key --session-id "<session-id>" --output json`
  Gets all fields and values from a Redis hash
- `robomotion redis redis_hdel --client-id --key --field --session-id "<session-id>" --output json`
  Deletes a field from a Redis hash
- `robomotion redis redis_lpush --client-id --key --value --session-id "<session-id>" --output json`
  Pushes a value to the left (head) of a Redis list
- `robomotion redis redis_rpush --client-id --key --value --session-id "<session-id>" --output json`
  Pushes a value to the right (tail) of a Redis list
- `robomotion redis redis_lpop --client-id --key --session-id "<session-id>" --output json`
  Pops and returns a value from the left (head) of a Redis list
- `robomotion redis redis_rpop --client-id --key --session-id "<session-id>" --output json`
  Pops and returns a value from the right (tail) of a Redis list
- `robomotion redis redis_lrange --client-id --key --0 ---1 --session-id "<session-id>" --output json`
  Gets a range of elements from a Redis list
- `robomotion redis redis_llen --client-id --key --session-id "<session-id>" --output json`
  Gets the length of a Redis list
- `robomotion redis redis_sadd --client-id --key --member --session-id "<session-id>" --output json`
  Adds a member to a Redis set
- `robomotion redis redis_smembers --client-id --key --session-id "<session-id>" --output json`
  Gets all members of a Redis set
- `robomotion redis redis_srem --client-id --key --member --session-id "<session-id>" --output json`
  Removes a member from a Redis set
- `robomotion redis redis_sismember --client-id --key --member --session-id "<session-id>" --output json`
  Checks if a value is a member of a Redis set
- `robomotion redis redis_keys --client-id --* --session-id "<session-id>" --output json`
  Gets all keys matching a pattern
- `robomotion redis redis_exists --client-id --key --session-id "<session-id>" --output json`
  Checks if a key exists in Redis
- `robomotion redis redis_expire --client-id --key --60 --session-id "<session-id>" --output json`
  Sets an expiration time on a key
- `robomotion redis redis_ttl --client-id --key --session-id "<session-id>" --output json`
  Gets the remaining time to live of a key in seconds
- `robomotion redis redis_publish --client-id --channel --message --session-id "<session-id>" --output json`
  Publishes a message to a Redis channel

## Environment
- ROBOMOTION_API_TOKEN (if vault credentials are needed)
