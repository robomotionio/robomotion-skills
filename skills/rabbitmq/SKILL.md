---
name: "rabbitmq"
description: "RabbitMQ message broker — publish and consume messages, manage queues and exchanges. Supports message routing, queue binding, and queue management via `robomotion rabbitmq`. Do NOT use for Kafka, Redis pub/sub, SQS, or other message brokers."
---

# RabbitMQ

The `robomotion rabbitmq` CLI connects to RabbitMQ for message broker operations. It publishes messages to exchanges, consumes from queues, creates and manages queues and exchanges, and handles queue binding and message routing.

## When to use
- Publish messages to RabbitMQ exchanges or queues
- Consume messages from queues
- Create, delete, and manage queues and exchanges
- Bind queues to exchanges with routing keys

## Prerequisites
- `robomotion` CLI installed
- Package installed: `robomotion install rabbitmq`
- RabbitMQ connection URI configured via Robomotion vault

## IMPORTANT: Session Mode Required for Multi-Step Operations
Each CLI command runs as a **separate process** — connection IDs from `connect` do NOT persist across calls.
You MUST use `--session` on `connect` and pass `--session-id` to all subsequent commands.

## Workflow
1. Install (once): `robomotion install rabbitmq`
2. Connect with session:
   ```
   robomotion rabbitmq rabbitmq_connect --session --output json
   # → {"outClientId":"<client-id>","session_id":"<session-id>"}
   ```
3. Use the returned `client-id` and `session-id` in all subsequent commands:
   ```
   robomotion rabbitmq rabbitmq_publish --client-id "<client-id>" --queue <queue> --message <json> --session-id "<session-id>" --output json
   ```
4. Disconnect when done:
   ```
   robomotion rabbitmq rabbitmq_disconnect --client-id "<client-id>" --session-id "<session-id>" --output json
   ```

**Always** append `--output json` to get structured JSON results.

## Commands Reference
- `robomotion rabbitmq rabbitmq_connect --session --output json`
  Connects to RabbitMQ server and returns a client ID for subsequent operations
- `robomotion rabbitmq rabbitmq_disconnect --client-id --session-id "<session-id>" --output json`
  Closes the RabbitMQ connection and releases resources
- `robomotion rabbitmq rabbitmq_publish --client-id --queue-name --exchange-name --message --routing-key [--content-type] [--delivery-mode] [--0] [--expiration] [--30] --session-id "<session-id>" --output json`
  Publishes a message to a RabbitMQ queue or exchange
- `robomotion rabbitmq rabbitmq_consume --client-id --queue-name [--auto-acknowledge] [--parse-json] --session-id "<session-id>" --output json`
  Consumes a single message from a RabbitMQ queue
- `robomotion rabbitmq rabbitmq_queue_declare --client-id --queue-name [--durable] [--auto-delete] [--exclusive] --session-id "<session-id>" --output json`
  Declares a queue on RabbitMQ server
- `robomotion rabbitmq rabbitmq_queue_delete --client-id --queue-name [--only-if-unused] [--only-if-empty] --session-id "<session-id>" --output json`
  Deletes a queue from RabbitMQ server
- `robomotion rabbitmq rabbitmq_queue_purge --client-id --queue-name --session-id "<session-id>" --output json`
  Removes all messages from a RabbitMQ queue
- `robomotion rabbitmq rabbitmq_queue_bind --client-id --queue-name --exchange-name --routing-key --session-id "<session-id>" --output json`
  Binds a queue to an exchange with a routing key
- `robomotion rabbitmq rabbitmq_exchange_declare --client-id --exchange-name [--exchange-type] [--durable] [--auto-delete] --session-id "<session-id>" --output json`
  Declares an exchange on RabbitMQ server
- `robomotion rabbitmq rabbitmq_exchange_delete --client-id --exchange-name [--only-if-unused] --session-id "<session-id>" --output json`
  Deletes an exchange from RabbitMQ server

## Environment
- ROBOMOTION_API_TOKEN (if vault credentials are needed)
