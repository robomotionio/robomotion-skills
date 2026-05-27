# Phase 8: Process Intelligence (Env Discovery + Signal Collection)

**Status:** pending
**Priority:** P1 — enables Maggy to learn from the full SDLC
**Effort:** Large
**Dependencies:** Phase 5 (Maggy v2 UI for displaying insights), GitHub API access

---

## Scope

Maggy doesn't just optimize code output — it optimizes the entire development process. Process Intelligence observes what happens to code after it's written: PR reviews, CI results, CodeRabbit findings, reviewer feedback, merge patterns, and post-deploy incidents. It learns patterns and preemptively fixes recurring issues.

## What Gets Built

1. **Environment discovery** (`maggy/maggy/process/discovery.py`)
   - Auto-detect on first run per project (no configuration):
     - Ticketing: GitHub Issues, Asana, Linear, Jira
     - GitHub integrations: CodeRabbit, Dependabot, Renovate, Vercel
     - CI/CD: GitHub Actions, Jenkins, CircleCI, GitLab CI
     - Code quality: ESLint, ruff, mypy, pre-commit, coverage tools
     - Review process: required reviewers, CODEOWNERS, branch protection
   - Output: `~/.maggy/environments/{project}.yaml`

2. **Signal collectors** (`maggy/maggy/process/signals/`)
   - `ci.py` — Parse GitHub Actions run results, extract failure patterns
   - `review.py` — Parse PR review comments, identify recurring themes
   - `coderabbit.py` — Parse CodeRabbit findings, track resolution rate
   - `merge.py` — Track PR merge patterns: rounds, time, reviewer
   - Each collector writes to `~/.maggy/signals/{project}/signals.jsonl`

3. **Pattern engine** (`maggy/maggy/process/patterns.py`)
   - Correlate signals: `(code_pattern, review_feedback)` pairs
   - Identify recurring reviewer complaints: "always flags missing error handling"
   - Track CI failure modes: "tests fail when touching auth module"
   - Generate pre-emptive fixes: add error handling before PR creation

4. **Process health dashboard**
   - CI pass rate trend (daily, weekly)
   - Review rounds trend (target: < 1.5 rounds)
   - CodeRabbit findings trend (target: decreasing)
   - Top recurring issues with auto-fix status

5. **L2/L3 integration**
   - L2 daily: CI pass rate drop > 10% → alert + disable causing model
   - L3 weekly: Pattern analysis → skill file patches, workflow adjustments
   - Compound metric: "Review rounds dropped from 2.8 to 1.1"

## Deliverables

- [ ] `maggy/maggy/process/discovery.py` — Environment auto-discovery
- [ ] `maggy/maggy/process/signals/ci.py` — CI signal collector
- [ ] `maggy/maggy/process/signals/review.py` — Review signal collector
- [ ] `maggy/maggy/process/signals/coderabbit.py` — CodeRabbit collector
- [ ] `maggy/maggy/process/signals/merge.py` — Merge pattern collector
- [ ] `maggy/maggy/process/patterns.py` — Pattern correlation engine
- [ ] `maggy/maggy/api/routes_process.py` — Process health endpoints
- [ ] `tests/test_discovery.py` — Environment detection tests
- [ ] `tests/test_signals.py` — Signal collection tests
- [ ] `tests/test_patterns.py` — Pattern correlation tests
- [ ] Dashboard process health panel

## Success Criteria

- [ ] Environment discovery detects CI/CD, ticketing, and review tools automatically
- [ ] Signal collectors capture CI failures, review comments, and merge patterns
- [ ] Pattern engine identifies top 5 recurring issues per project
- [ ] Pre-emptive fixes reduce review rounds by >= 30% after 4 weeks
- [ ] CI pass rate improves by >= 10% after pattern-based pre-checks
- [ ] All tests pass, coverage >= 80%

## Risks

- GitHub API rate limits for signal collection — batch requests, cache aggressively
- Pattern correlation may produce false positives — require minimum sample size (10+)
- Review comment parsing requires NLP — start with keyword matching, upgrade to LLM classification later
