---
description: React-specific conventions
paths: ["src/components/**", "src/pages/**", "src/app/**", "**/*.tsx", "**/*.jsx"]
---

## React Conventions

- Prefer functional components with hooks
- Use React Query / TanStack Query for server state
- Use Zustand or context for client state
- Colocate component tests (ComponentName.test.tsx)
- Extract custom hooks when logic is reused across components
- Avoid prop drilling beyond 2 levels - use context or composition
