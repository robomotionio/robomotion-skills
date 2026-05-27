# /icpg-why — Why Does This Code Exist?

Trace any symbol back to its creating ReasonNode — show the original goal, who wrote it, and whether it's still doing what it was made for.

---

## Usage

`/icpg-why <symbol-name>`

---

## Steps

### 1. Find the symbol

```bash
icpg query risk <symbol-name>
```

If not found, search more broadly:
```bash
icpg query context <likely-file-path>
```

### 2. Show the full trace

```
WHY: <symbol-name>
═══════════════════

Symbol: <type> <name> (<file-path>)
Signature: <signature>
Checksum: <checksum>

CREATING INTENT:
  ID: <reason-id>
  Goal: <goal>
  Type: <decision_type>
  Owner: <owner>
  Status: <status>
  Created: <date>

CONTRACTS:
  PRE: <preconditions>
  POST: <postconditions>
  INV: <invariants>

MODIFICATION HISTORY:
  1. <date> — <modifying-reason-goal> (by <owner>)
  2. <date> — <modifying-reason-goal> (by <owner>)

DRIFT STATUS: {CLEAN | DRIFTED}
  Dimensions: <drift-dimensions if any>
  Severity: <score>
```

### 3. If no ReasonNode found

Symbol exists but has no iCPG tracking:
```
⚠ No ReasonNode found for <symbol-name>.
This code has no tracked intent — consider creating one:
  icpg create "<inferred goal>" --scope <file>
```
