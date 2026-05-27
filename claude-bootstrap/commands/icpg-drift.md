# /icpg-drift — Show All Drift

Run a full drift scan and display all unresolved drift events, grouped by dimension and sorted by severity.

---

## Usage

`/icpg-drift`

---

## Steps

### 1. Run drift scan

```bash
icpg drift check
```

### 2. Also show existing unresolved drift

```bash
icpg status
```

### 3. Display results

```
DRIFT REPORT
═══════════════

{N} unresolved drift events across {M} symbols

BY SEVERITY:
  [0.85] spec(0.9) + decision(0.8) — validateToken drifted from "JWT auth"
  [0.60] ownership(0.7) + test(0.5) — UserService has 4 owners, tests stale
  ...

BY DIMENSION:
  Spec drift:       {count} events
  Decision drift:   {count} events
  Ownership drift:  {count} events
  Test drift:       {count} events
  Usage drift:      {count} events
  Dependency drift: {count} events

TOP ACTIONS:
  1. Fix spec drift in validateToken — checksum changed without MODIFIES edge
  2. Add tests for UserService — VALIDATED_BY tests are missing
  3. Assign single owner to PaymentProcessor — 5 different owners
```

### 4. Offer resolution

For each event, suggest:
- `icpg drift resolve <id>` to mark resolved
- Create a new MODIFIES ReasonNode if the change was intentional
- Write missing tests if test drift detected
