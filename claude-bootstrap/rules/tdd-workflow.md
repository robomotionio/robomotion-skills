---
description: TDD workflow enforced for all implementation tasks
---

## TDD Workflow

Every feature and bug fix follows RED-GREEN-VALIDATE:

1. **RED** - Write tests based on acceptance criteria. Run them. All must FAIL.
2. **GREEN** - Write minimum code to pass tests. Run them. All must PASS.
3. **VALIDATE** - Run linter, type checker, full test suite with coverage >= 80%.

Tests must fail first to prove they validate the requirement. No code ships without a test that failed first.

For bugs: identify test gap, write failing test that reproduces bug, then fix.
