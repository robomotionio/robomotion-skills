# /icpg-impact — Show Blast Radius

Show the blast radius of a ReasonNode or symbol — what depends on it, what breaks if it changes.

---

## Usage

`/icpg-impact <id-or-symbol>`

- If argument looks like a UUID (contains `-`), treat as ReasonNode ID
- Otherwise, treat as symbol name and find its creating ReasonNode

---

## Steps

### 1. Resolve target

```bash
# If ReasonNode ID
icpg query blast <id>

# If symbol name
icpg query risk <symbol-name>
# Then get the creating reason from the output
icpg query blast <creating-reason-id>
```

### 2. Display results

Format the output as:

```
BLAST RADIUS: <goal>
═══════════════════════════════════

Symbols ({N}):
  function validateToken (src/auth/service.ts)
  class AuthMiddleware (src/auth/middleware.ts)
  ...

Dependent Intents ({N}):
  a1b2c3d4 — Dashboard user session management
  e5f6g7h8 — Payment authorization flow
  ...

Contracts:
  INV: file_exists("src/auth/middleware.ts")
  POST: test_exists("src/auth/__tests__/service.test.ts")

Risk: {HIGH|MEDIUM|LOW} based on dependent count + drift history
```

### 3. Recommendations

If high risk (>5 dependents or active drift):
- Suggest running full test suite before changes
- Suggest creating a new ReasonNode with MODIFIES edge
- Warn about function signatures to preserve
