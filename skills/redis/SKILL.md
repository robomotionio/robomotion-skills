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

## Workflow
1. Install: `robomotion install redis`
2. Connect: `robomotion redis redis_connect` → returns a `client-id`
3. Set: `robomotion redis redis_set --client-id <id> --key <key> --value <val>`
4. Get: `robomotion redis redis_get --client-id <id> --key <key>`
5. Disconnect: `robomotion redis redis_disconnect --client-id <id>`

## Commands Reference
- `robomotion redis redis_connect`
  Connects to a Redis server and returns a client ID for subsequent operations
- `robomotion redis redis_disconnect --client-id`
  Closes the Redis connection and releases resources
- `robomotion redis redis_get --client-id --key`
  Gets the value of a key from Redis
- `robomotion redis redis_set --client-id --key --value [--0]`
  Sets a key-value pair in Redis with optional expiration
- `robomotion redis redis_delete --client-id --key`
  Deletes one or more keys from Redis
- `robomotion redis redis_hset --client-id --key --field --value`
  Sets a field in a Redis hash
- `robomotion redis redis_hget --client-id --key --field`
  Gets a field value from a Redis hash
- `robomotion redis redis_hgetall --client-id --key`
  Gets all fields and values from a Redis hash
- `robomotion redis redis_hdel --client-id --key --field`
  Deletes a field from a Redis hash
- `robomotion redis redis_lpush --client-id --key --value`
  Pushes a value to the left (head) of a Redis list
- `robomotion redis redis_rpush --client-id --key --value`
  Pushes a value to the right (tail) of a Redis list
- `robomotion redis redis_lpop --client-id --key`
  Pops and returns a value from the left (head) of a Redis list
- `robomotion redis redis_rpop --client-id --key`
  Pops and returns a value from the right (tail) of a Redis list
- `robomotion redis redis_lrange --client-id --key --0 ---1`
  Gets a range of elements from a Redis list
- `robomotion redis redis_llen --client-id --key`
  Gets the length of a Redis list
- `robomotion redis redis_sadd --client-id --key --member`
  Adds a member to a Redis set
- `robomotion redis redis_smembers --client-id --key`
  Gets all members of a Redis set
- `robomotion redis redis_srem --client-id --key --member`
  Removes a member from a Redis set
- `robomotion redis redis_sismember --client-id --key --member`
  Checks if a value is a member of a Redis set
- `robomotion redis redis_keys --client-id --*`
  Gets all keys matching a pattern
- `robomotion redis redis_exists --client-id --key`
  Checks if a key exists in Redis
- `robomotion redis redis_expire --client-id --key --60`
  Sets an expiration time on a key
- `robomotion redis redis_ttl --client-id --key`
  Gets the remaining time to live of a key in seconds
- `robomotion redis redis_publish --client-id --channel --message`
  Publishes a message to a Redis channel

## Environment
- ROBOMOTION_API_TOKEN (if vault credentials are needed)
