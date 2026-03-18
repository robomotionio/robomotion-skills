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

## Workflow
1. Install: `robomotion install rabbitmq`
2. Connect: `robomotion rabbitmq rabbitmq_connect` → returns a `client-id`
3. Publish: `robomotion rabbitmq rabbitmq_publish --client-id <id> --queue <queue> --message <json>`
4. Consume: `robomotion rabbitmq rabbitmq_consume --client-id <id> --queue <queue>`
5. Disconnect: `robomotion rabbitmq rabbitmq_disconnect --client-id <id>`

## Commands Reference
- `robomotion rabbitmq rabbitmq_connect`
  Connects to RabbitMQ server and returns a client ID for subsequent operations
- `robomotion rabbitmq rabbitmq_disconnect --client-id`
  Closes the RabbitMQ connection and releases resources
- `robomotion rabbitmq rabbitmq_publish --client-id --queue-name --exchange-name --message --routing-key [--content-type] [--delivery-mode] [--0] [--expiration] [--30]`
  Publishes a message to a RabbitMQ queue or exchange
- `robomotion rabbitmq rabbitmq_consume --client-id --queue-name [--auto-acknowledge] [--parse-json]`
  Consumes a single message from a RabbitMQ queue
- `robomotion rabbitmq rabbitmq_queue_declare --client-id --queue-name [--durable] [--auto-delete] [--exclusive]`
  Declares a queue on RabbitMQ server
- `robomotion rabbitmq rabbitmq_queue_delete --client-id --queue-name [--only-if-unused] [--only-if-empty]`
  Deletes a queue from RabbitMQ server
- `robomotion rabbitmq rabbitmq_queue_purge --client-id --queue-name`
  Removes all messages from a RabbitMQ queue
- `robomotion rabbitmq rabbitmq_queue_bind --client-id --queue-name --exchange-name --routing-key`
  Binds a queue to an exchange with a routing key
- `robomotion rabbitmq rabbitmq_exchange_declare --client-id --exchange-name [--exchange-type] [--durable] [--auto-delete]`
  Declares an exchange on RabbitMQ server
- `robomotion rabbitmq rabbitmq_exchange_delete --client-id --exchange-name [--only-if-unused]`
  Deletes an exchange from RabbitMQ server

## Environment
- ROBOMOTION_API_TOKEN (if vault credentials are needed)
