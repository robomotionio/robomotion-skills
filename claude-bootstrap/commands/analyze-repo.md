# Analyze Repository

Analyze an existing repository's structure, conventions, and guardrails.

**This command runs automatically** when `/initialize-project` detects an existing codebase without Claude setup. You can also run it standalone anytime.

**Use this command standalone when:**
- You want to re-analyze after making changes
- You want analysis without running `/initialize-project`
- Auditing code quality and guardrails on any repo
- Reviewing a codebase without adding Claude skills

**Automatic trigger:**
- `/initialize-project` on existing codebase → auto-runs this analysis first

---

## Phase 1: Repository Detection

Run these checks to understand the repo:

```bash
# Git info
echo "=== Git Status ===" && \
git remote -v 2>/dev/null && \
git branch -a 2>/dev/null | head -10 && \
git log --oneline -5 2>/dev/null

# Config files
echo "=== Config Files ===" && \
ls -la *.json *.toml *.yaml *.yml 2>/dev/null

# Directory structure (3 levels, excluding noise)
echo "=== Directory Structure ===" && \
find . -type d -maxdepth 3 \
    -not -path "*/node_modules/*" \
    -not -path "*/.git/*" \
    -not -path "*/venv/*" \
    -not -path "*/__pycache__/*" \
    -not -path "*/dist/*" \
    -not -path "*/build/*" \
    2>/dev/null | head -40
```

---

## Phase 2: Tech Stack Detection

Identify the primary technologies:

```bash
# JavaScript/TypeScript
if [ -f "package.json" ]; then
    echo "=== Package.json ===" && \
    cat package.json | head -50
fi

# Python
if [ -f "pyproject.toml" ]; then
    echo "=== pyproject.toml ===" && \
    cat pyproject.toml
fi

# Mobile
ls pubspec.yaml android/build.gradle ios/*.xcodeproj 2>/dev/null
```

Based on findings, determine:

| File | Technology |
|------|------------|
| package.json + tsconfig.json | TypeScript |
| package.json (no tsconfig) | JavaScript |
| pyproject.toml | Python |
| pubspec.yaml | Flutter (Dart) |
| android/build.gradle | Android Native |
| Cargo.toml | Rust |
| go.mod | Go |

---

## Phase 3: Repo Structure Type

Classify the repository:

```bash
# Check structure type
echo "=== Repo Structure Type ===" && \
if [ -d "packages" ] || [ -d "apps" ] || grep -q '"workspaces"' package.json 2>/dev/null; then
    echo "MONOREPO - Multiple packages/apps with shared tooling"
elif [ -d "frontend" ] && [ -d "backend" ]; then
    echo "FULL-STACK MONOLITH - Frontend + Backend in same repo"
elif [ -d "src" ] && grep -q '"react\|vue\|angular"' package.json 2>/dev/null; then
    echo "FRONTEND - Single frontend application"
elif [ -d "src" ] && grep -q '"express\|fastify\|koa"' package.json 2>/dev/null; then
    echo "BACKEND - Single backend application"
elif [ -f "pyproject.toml" ] && grep -q "fastapi\|django\|flask" pyproject.toml 2>/dev/null; then
    echo "BACKEND (Python) - Single backend application"
else
    echo "STANDARD - Single-purpose repository"
fi
```

---

## Phase 4: Guardrails Audit

Check existing code quality tools:

```bash
echo "=== Guardrails Audit ===" && \

# Pre-commit hooks
echo "Pre-commit Hooks:" && \
[ -d ".husky" ] && echo "  [x] Husky installed" || echo "  [ ] Husky NOT installed" && \
[ -f ".pre-commit-config.yaml" ] && echo "  [x] pre-commit framework" || echo "  [ ] pre-commit framework NOT installed" && \
[ -f ".git/hooks/pre-commit" ] && echo "  [x] Git hooks present" || echo "  [ ] No git hooks"

# Linting
echo "Linting:" && \
(grep -q '"eslint"' package.json 2>/dev/null && echo "  [x] ESLint") || \
(grep -q '"biome"' package.json 2>/dev/null && echo "  [x] Biome") || \
(grep -q "ruff" pyproject.toml 2>/dev/null && echo "  [x] Ruff") || \
echo "  [ ] No linter detected"

# Formatting
echo "Formatting:" && \
(grep -q '"prettier"' package.json 2>/dev/null && echo "  [x] Prettier") || \
(grep -q "black" pyproject.toml 2>/dev/null && echo "  [x] Black") || \
(grep -q "ruff" pyproject.toml 2>/dev/null && echo "  [x] Ruff (formatting)") || \
echo "  [ ] No formatter detected"

# Type checking
echo "Type Checking:" && \
([ -f "tsconfig.json" ] && echo "  [x] TypeScript") || \
(grep -q "mypy" pyproject.toml 2>/dev/null && echo "  [x] mypy") || \
(grep -q "pyright" pyproject.toml 2>/dev/null && echo "  [x] pyright") || \
echo "  [ ] No type checker detected"

# Testing
echo "Testing:" && \
(grep -q '"jest\|vitest"' package.json 2>/dev/null && echo "  [x] Jest/Vitest") || \
(grep -q "pytest" pyproject.toml 2>/dev/null && echo "  [x] pytest") || \
echo "  [ ] No test framework detected"

# Commit validation
echo "Commit Validation:" && \
([ -f "commitlint.config.js" ] && echo "  [x] commitlint") || \
(grep -q "conventional-pre-commit" .pre-commit-config.yaml 2>/dev/null && echo "  [x] conventional-pre-commit") || \
echo "  [ ] No commit validation"

# CI/CD
echo "CI/CD:" && \
[ -d ".github/workflows" ] && echo "  [x] GitHub Actions" || echo "  [ ] No GitHub Actions" && \
[ -f ".gitlab-ci.yml" ] && echo "  [x] GitLab CI" || true && \
[ -f "Jenkinsfile" ] && echo "  [x] Jenkins" || true
```

---

## Phase 5: Convention Detection

Identify existing code patterns:

```bash
echo "=== Convention Detection ===" && \

# File naming
echo "File Naming:" && \
ls src/**/*.ts 2>/dev/null | head -5 && \
ls src/**/*.py 2>/dev/null | head -5

# Import style (JS/TS)
echo "Import Style:" && \
grep -h "^import" src/**/*.ts 2>/dev/null | head -5

# Export style (JS/TS)
echo "Export Style:" && \
grep -h "^export" src/**/*.ts 2>/dev/null | head -5

# Test file location
echo "Test Location:" && \
find . -name "*.test.*" -o -name "*.spec.*" -o -name "test_*.py" 2>/dev/null | head -5
```

---

## Phase 6: Generate Report

Based on all findings, generate this report structure:

```markdown
# Repository Analysis Report

**Generated:** [timestamp]
**Repository:** [name from git remote or directory]

## Overview

| Attribute | Value |
|-----------|-------|
| Type | [Monorepo / Full-Stack / Frontend / Backend] |
| Language | [TypeScript / Python / ...] |
| Framework | [React / FastAPI / ...] |
| Package Manager | [npm / pnpm / uv / pip] |

## Directory Structure

[Simplified tree output]

## Tech Stack

| Category | Technology | Config |
|----------|------------|--------|
| Language | X | X |
| Framework | X | X |
| Testing | X | X |
| Linting | X | X |
| Formatting | X | X |

## Guardrails Status

### Present
- [x] Item 1
- [x] Item 2

### Missing (Recommended to Add)
- [ ] Item 1 - [brief reason]
- [ ] Item 2 - [brief reason]

## Conventions Observed

| Pattern | Observed Value | Example |
|---------|----------------|---------|
| Naming | camelCase / snake_case | file.ts |
| Imports | Absolute / Relative | @/components |
| Tests | Colocated / Separate | *.test.ts |
| Exports | Named / Default | export { X } |

## Recommendations

1. **High Priority**
   - [Recommendation with reason]

2. **Medium Priority**
   - [Recommendation with reason]

3. **Low Priority / Nice to Have**
   - [Recommendation with reason]

## Key Files to Review

| File | Purpose | Why Review |
|------|---------|------------|
| src/index.ts | Entry point | Understand app bootstrap |
| src/config.ts | Configuration | Understand env handling |
| tests/setup.ts | Test setup | Understand test patterns |
```

---

## Phase 7: Offer Next Steps

After generating the report, offer these options:

> **Analysis complete!** Here's what I found: [summary]
>
> What would you like to do next?
> 1. **Add missing guardrails** - Set up pre-commit hooks, linting, etc.
> 2. **Generate detailed conventions doc** - Document patterns for team
> 3. **Set up Claude integration** - Run `/initialize-project` to add Claude skills
> 4. **Start working on code** - I'll follow the conventions I detected
> 5. **Something else**

---

## Quick Analysis (One Command)

For a quick overview without the full report:

```bash
echo "=== Quick Analysis ===" && \
echo "Repo: $(basename $(pwd))" && \
echo "Type: $([ -d packages ] && echo 'Monorepo' || ([ -d frontend ] && [ -d backend ] && echo 'Full-Stack') || echo 'Standard')" && \
echo "Tech: $([ -f package.json ] && echo 'JS/TS' || ([ -f pyproject.toml ] && echo 'Python') || echo 'Other')" && \
echo "Guardrails: $([ -d .husky ] || [ -f .pre-commit-config.yaml ] && echo 'Present' || echo 'Missing')" && \
echo "CI/CD: $([ -d .github/workflows ] && echo 'GitHub Actions' || echo 'None')"
```
