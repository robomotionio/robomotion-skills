---
description: Security rules enforced on all code
---

## Security Rules

- No secrets in code - use environment variables
- No secrets in client-exposed env vars (VITE_*, NEXT_PUBLIC_*, REACT_APP_*)
- `.env` files always in `.gitignore`
- Parameterized queries only - no string concatenation for SQL
- Hash passwords with bcrypt (12+ rounds) or argon2
- Validate all input at API boundaries (Zod/Pydantic)
- `.env.example` with all required vars (no values)
