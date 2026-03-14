# Skill Eval Tool — Usage Guide

A minimal evaluation tool for testing whether Claude Code SKILL.md files trigger correctly and produce quality output.

## Prerequisites

- **Python 3.10+** — no external packages required
- **Claude CLI** — `claude` must be on your PATH and authenticated
- **SKILL.md skills** — each skill directory must contain an `eval-set.json` file

Verify your setup:

```bash
python3 --version        # 3.10+
claude --version         # Claude CLI installed
claude auth status       # Authenticated (for quality evals that invoke tools)
```

---

## Quick Start

```bash
# Run all evals for a skill
python3 run_eval.py /path/to/skills/yeet/

# Run only trigger precision tests
python3 run_eval.py /path/to/skills/yeet/ --type trigger

# Run only output quality tests
python3 run_eval.py /path/to/skills/yeet/ --type quality

# Run a single test case by ID
python3 run_eval.py /path/to/skills/yeet/ --case trigger-pos-1

# Full debug output
python3 run_eval.py /path/to/skills/yeet/ --verbose
```

---

## CLI Reference

```
python3 run_eval.py <skill_path> [options]
```

| Argument | Description |
|----------|-------------|
| `skill_path` | Path to skill directory containing `eval-set.json` (required) |
| `--type trigger\|quality` | Run only trigger or quality evals |
| `--case <id>` | Run only the case with this ID |
| `--model <model>` | Model for running queries (default: `sonnet`) |
| `--judge-model <model>` | Model for LLM-as-judge quality grading (default: `sonnet`) |
| `--verbose` | Print full JSON responses from Claude |

### Exit Codes

| Code | Meaning |
|------|---------|
| `0` | All cases passed |
| `1` | One or more cases failed |
| `2` | Setup error (e.g., `claude` CLI not found) |

---

## What It Tests

### 1. Trigger Precision

Does Claude invoke the skill for the right queries — and *not* for the wrong ones?

Each trigger case sends a query to Claude and checks whether a `Skill` tool_use block with the matching `skill_name` appears in the JSON output. This is a **deterministic, code-based** check — no LLM judging involved.

- **Positive cases** (`expect_triggered: true`): queries that *should* activate the skill
- **Negative cases** (`expect_triggered: false`): queries that should *not* activate the skill

Example output:
```
[trigger-pos-1] PASS
[trigger-pos-2] PASS
[trigger-neg-1] FAIL   Expected skill 'yeet' NOT to trigger but it DID
```

### 2. Output Quality

When the skill *does* activate, does it produce good results?

Each quality case sends a query to Claude, captures the full response (text + tool calls), then sends it to a **judge model** along with a list of criteria. The judge grades each criterion as PASS/FAIL and returns structured JSON.

- **Overall pass** = all criteria pass
- Criteria should be **outcome-based** ("creates a branch with codex/ prefix") not process-based ("calls git checkout -b")

Example output:
```
[quality-1] PASS
[quality-2] FAIL   2/4 criteria passed
```

---

## eval-set.json Format

Every skill that you want to evaluate needs an `eval-set.json` file in its directory, alongside the `SKILL.md`:

```
skills/yeet/
  SKILL.md
  eval-set.json
```

### Schema

```json
{
  "skill_name": "yeet",
  "cases": [
    {
      "id": "trigger-pos-1",
      "type": "trigger",
      "query": "yeet this change",
      "expect_triggered": true
    },
    {
      "id": "trigger-neg-1",
      "type": "trigger",
      "query": "write a git helper script",
      "expect_triggered": false
    },
    {
      "id": "quality-1",
      "type": "quality",
      "query": "yeet this with description 'fix login bug'",
      "criteria": [
        "Checks gh auth status before proceeding",
        "Creates a branch with codex/ prefix",
        "Opens a draft PR with gh pr create"
      ]
    }
  ]
}
```

### Field Reference

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `skill_name` | string | yes | Must match the `name` field in SKILL.md frontmatter |
| `cases` | array | yes | List of test cases |
| `cases[].id` | string | yes | Unique identifier (used with `--case` flag) |
| `cases[].type` | string | yes | `"trigger"` or `"quality"` |
| `cases[].query` | string | yes | The user message sent to Claude |
| `cases[].expect_triggered` | boolean | trigger only | Whether the skill should activate |
| `cases[].criteria` | string[] | quality only | List of outcome-based criteria for the judge |

---

## Writing Good Test Cases

### Trigger Cases

Aim for **4-6 positive** and **4-6 negative** trigger cases per skill. Focus on boundary cases — queries that are *close* to triggering but shouldn't:

| Category | Example for `yeet` | Expected |
|----------|-------------------|----------|
| Exact keyword | "yeet this change" | trigger |
| Natural paraphrase | "push my changes and create a PR" | trigger |
| Partial overlap | "commit this change" | no trigger |
| Unrelated | "explain how PRs work" | no trigger |
| Adjacent tool | "create a new branch" | no trigger |

### Quality Criteria

Write criteria that check **outcomes**, not **exact tool sequences**:

| Good (outcome-based) | Bad (process-based) |
|----------------------|---------------------|
| "Creates a branch with codex/ prefix" | "Runs `git checkout -b codex/...`" |
| "Opens a draft PR" | "Calls `gh pr create --draft --fill`" |
| "Installs missing dependencies" | "Runs `uv pip install reportlab`" |

### How Many Cases?

Start with **8-13 cases per skill**:
- 4-6 trigger positive
- 4-6 trigger negative
- 2-3 quality

Add more when you find edge cases that fail.

---

## Understanding the Output

### Summary Table

After all cases run, you get a summary:

```
ID                        Type       Result   Details
--------------------------------------------------------------------------------
trigger-pos-1             trigger    PASS     expected=trigger
trigger-pos-2             trigger    PASS     expected=trigger
trigger-neg-1             trigger    PASS     expected=no trigger
trigger-neg-2             trigger    FAIL     Expected skill 'yeet' NOT to trigger but it DID
quality-1                 quality    PASS     3/3 criteria passed
quality-2                 quality    FAIL     2/4 criteria passed

5/6 passed
```

### Results File

After each run, results are saved to `eval-results.json` in the skill directory:

```json
{
  "skill_name": "yeet",
  "results": [
    {
      "id": "trigger-pos-1",
      "type": "trigger",
      "passed": true,
      "expected": true,
      "actual": true,
      "reason": ""
    },
    {
      "id": "quality-1",
      "type": "quality",
      "passed": true,
      "grades": [
        {"criterion": "Checks gh auth status", "passed": true, "reason": "..."},
        {"criterion": "Creates codex/ branch", "passed": true, "reason": "..."}
      ]
    }
  ]
}
```

### Verbose Mode

Use `--verbose` to see the raw JSON response from Claude for each case. Useful for debugging why a trigger check failed or why the judge graded a criterion as FAIL:

```bash
python3 run_eval.py ./skills/yeet/ --case trigger-neg-2 --verbose
```

This prints the first 2000 characters of Claude's JSON response for each case.

---

## Using in CI

The tool is designed to be CI-friendly out of the box:

```yaml
# GitHub Actions example
- name: Run skill evals
  run: |
    python3 run_eval.py ./skills/yeet/ --type trigger
    python3 run_eval.py ./skills/pdf/ --type trigger
```

Key behaviors for CI:
- **Exit code 0** when all cases pass, **exit code 1** on any failure
- Deterministic trigger checks (no LLM judging, no flakiness)
- Quality evals use LLM-as-judge and may have some variance — consider running trigger-only in CI and quality evals on-demand
- Results file (`eval-results.json`) can be uploaded as a build artifact

### CI Strategy

| Pipeline | What to run | Why |
|----------|-------------|-----|
| PR checks | `--type trigger` only | Fast, deterministic, catches description regressions |
| Nightly | All cases | Catches quality drift, LLM-as-judge variance |
| After description changes | All cases for changed skill | Validates the change didn't break anything |

---

## Model Selection

### Query Model (`--model`)

The model that receives the user query and decides whether to invoke the skill.

| Model | Speed | Trigger accuracy | Cost |
|-------|-------|-----------------|------|
| `haiku` | Fast | Lower | Cheapest |
| `sonnet` (default) | Medium | Good | Moderate |
| `opus` | Slow | Highest | Most expensive |

Use `sonnet` for day-to-day iteration. Use `opus` when you need highest-fidelity trigger testing or your description changes are subtle.

### Judge Model (`--judge-model`)

The model that grades quality eval responses against criteria.

| Model | Reliability | Speed | When to use |
|-------|-------------|-------|-------------|
| `sonnet` (default) | Good | Fast | Day-to-day quality checks |
| `opus` | Highest | Slow | Final validation, ambiguous criteria |

---

## Workflow: Optimizing a Skill Description

The primary feedback loop for improving skills:

1. **Write initial test cases** in `eval-set.json`
2. **Run trigger evals**: `python3 run_eval.py ./skills/foo/ --type trigger`
3. **Identify failures**: which positive cases didn't trigger? Which negatives did?
4. **Refine the SKILL.md description** based on failures
5. **Re-run trigger evals** to verify improvement
6. **Run quality evals** once triggers are stable: `python3 run_eval.py ./skills/foo/ --type quality`
7. **Adjust criteria or skill workflow** based on quality failures
8. **Repeat** until pass rate is acceptable

### Description Tuning Tips

If too many **false negatives** (skill should trigger but doesn't):
- Make the description more inclusive of natural phrasings
- Add trigger synonyms or example scenarios

If too many **false positives** (skill triggers when it shouldn't):
- Add explicit exclusion language: "do NOT use for..."
- Narrow the scope: replace broad terms with specific ones
- Use the `negative space` technique: define what the skill is *not* for

---

## Existing Eval Sets

| Skill | Path | Cases |
|-------|------|-------|
| yeet | `skills/yeet/eval-set.json` | 4 trigger+, 5 trigger-, 2 quality |
| pdf | `skills/pdf/eval-set.json` | 4 trigger+, 4 trigger-, 2 quality |

---

## Troubleshooting

### "claude CLI not found" (exit code 2)

The `claude` command is not on your PATH. Install Claude Code:
```bash
npm install -g @anthropic-ai/claude-code
```

### Trigger eval times out

Default timeout is 300 seconds per case. If Claude is slow to respond, check your network or try a faster model:
```bash
python3 run_eval.py ./skills/yeet/ --model haiku --type trigger
```

### Quality judge returns invalid JSON

The judge model sometimes wraps its response in markdown fences. The tool strips these automatically, but if it still fails, try `--judge-model opus` for more reliable structured output.

### All trigger cases fail

- Verify `skill_name` in `eval-set.json` matches the `name` field in `SKILL.md` exactly
- Verify the skill is registered (check `skills-index.json` or equivalent manifest)
- Run a single case with `--verbose` to inspect the raw response

### Results look nondeterministic

LLM outputs are inherently variable. Trigger evals may occasionally flip, especially for boundary cases. If a case flips frequently:
- It's a genuine ambiguity — refine the skill description
- Or the query is too close to the decision boundary — rephrase it to be more clearly in/out of scope

---

## Project Structure

```
/home/faik/skills/
  run_eval.py              # Eval runner (this tool)
  USAGE.md                 # This file
  docs/
    01-eval-concepts.md    # What evals are, why they matter
    02-browsecomp.md       # Eval awareness & BrowseComp research
    03-skill-anatomy.md    # SKILL.md format reference
    04-eval-tool-usage.md  # CLI reference (detailed)
    05-writing-eval-sets.md # How to write test cases
    06-grading.md          # Trigger grading & LLM-as-judge
    07-best-practices.md   # Industry best practices
    08-references.md       # Links to source material
```

Each skill with evals:
```
skills/<skill-name>/
  SKILL.md               # The skill definition
  eval-set.json          # Test cases
  eval-results.json      # Auto-generated after running evals
```

---

## Further Reading

See the `docs/` directory for in-depth documentation:

- **New to evals?** Start with [01-eval-concepts.md](docs/01-eval-concepts.md)
- **Writing test cases?** Read [05-writing-eval-sets.md](docs/05-writing-eval-sets.md)
- **Tuning a skill description?** See [03-skill-anatomy.md](docs/03-skill-anatomy.md) and [07-best-practices.md](docs/07-best-practices.md)
- **Understanding grading?** Check [06-grading.md](docs/06-grading.md)
- **Worried about eval gaming?** Read [02-browsecomp.md](docs/02-browsecomp.md)
