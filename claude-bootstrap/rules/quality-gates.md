---
description: Code quality constraints enforced on all files
---

## Quality Gates

| Constraint | Limit |
|------------|-------|
| Lines per function | 20 max |
| Parameters per function | 3 max |
| Nesting depth | 2 levels max |
| Lines per file | 200 max |
| Functions per file | 10 max |
| Test coverage | 80% minimum |

Before completing any file: count lines, count functions, check parameter counts. If limits exceeded, split or decompose immediately.
