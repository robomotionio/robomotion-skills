---
description: TypeScript-specific conventions
paths: ["**/*.ts", "**/*.tsx", "tsconfig.json"]
---

## TypeScript Conventions

- Enable strict mode in tsconfig.json
- Prefer interfaces over type aliases for object shapes
- Use discriminated unions over type assertions
- Avoid `any` - use `unknown` with type narrowing
- Use Zod for runtime validation at boundaries
- Use ESLint with TypeScript parser
- Prefer `const` over `let`, never use `var`
