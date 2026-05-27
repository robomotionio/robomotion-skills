# Phase 10: Integration Testing + Documentation

**Status:** pending
**Priority:** P1 — validates the full system works together
**Effort:** Large
**Dependencies:** All phases (1-9) — this is the integration phase

---

## Scope

End-to-end integration testing across all Maggy components. Validate that PiAdapter, model routing, Mnemos multi-model, CIKG, dashboard, process intelligence, and MCP Forge work together as a coherent system. Update all documentation to reflect the v5 architecture.

## What Gets Built

1. **Integration test suite** (`tests/integration/`)
   - `test_full_task_flow.py` — Ticket → routing → container → execution → reward update
   - `test_model_fallback.py` — Quota hit → checkpoint → model switch → task continues
   - `test_process_loop.py` — CI failure → signal collection → pattern detection → pre-fix
   - `test_dashboard_live.py` — All dashboard panels render with live data
   - `test_multi_project.py` — Multiple projects with different configs run simultaneously

2. **Behavioral evals** (`evals/`)
   - Extend existing eval framework for v5 scenarios
   - Eval: "Does routing select the right model for blast 8 auth task?"
   - Eval: "Does model switch preserve task context?"
   - Eval: "Does process intelligence reduce review rounds?"

3. **Documentation updates**
   - `docs/architecture-v5.md` — Final review and consistency check
   - `docs/getting-started.md` — New setup guide for v5
   - `docs/api-reference.md` — All REST endpoints documented
   - `maggy/README.md` — Updated with v5 features and setup
   - `CHANGELOG.md` — v5.0 release notes

4. **CI pipeline**
   - GitHub Actions workflow for integration tests
   - Run on PR to main: unit tests + lint + type check + integration tests
   - Nightly: full eval suite

## Deliverables

- [ ] `tests/integration/` — Integration test suite (5+ test files)
- [ ] `evals/` — Extended behavioral eval scenarios
- [ ] `docs/getting-started.md` — v5 setup guide
- [ ] `docs/api-reference.md` — REST API reference
- [ ] Updated `maggy/README.md`
- [ ] Updated `CHANGELOG.md`
- [ ] `.github/workflows/integration.yml` — CI pipeline
- [ ] All integration tests passing

## Success Criteria

- [ ] Full task flow (ticket → deploy) completes without manual intervention
- [ ] Model fallback chain works end-to-end (checkpoint → switch → continue)
- [ ] Dashboard shows accurate real-time data from all components
- [ ] Documentation is complete enough for a new developer to set up Maggy v5
- [ ] CI pipeline catches regressions before merge
- [ ] Integration test coverage >= 70% of critical paths

## Risks

- Integration tests require all components running — may need Docker Compose setup
- Flaky tests from network calls (GitHub API, model APIs) — mock external services
- Documentation can lag behind implementation — enforce docs update in PR checklist
