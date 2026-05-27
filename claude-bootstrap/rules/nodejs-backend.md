---
description: Node.js backend conventions
paths: ["src/api/**", "src/routes/**", "src/server/**", "src/middleware/**", "server/**", "api/**"]
---

## Node.js Backend Conventions

- Use Express or Fastify with typed route handlers
- Repository pattern for data access
- Validate request bodies with Zod at the route level
- Use proper HTTP status codes (201 for creation, 404 for missing, etc.)
- Add rate limiting to auth endpoints
- Use structured logging (pino/winston)
- Handle async errors with middleware, not try/catch in every route
