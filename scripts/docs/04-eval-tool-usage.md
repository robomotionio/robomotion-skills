# Using run_eval.py

## Overview

`run_eval.py` is the command-line tool for running evals against skills in this repository. It discovers eval cases defined alongside a skill, executes each case against Claude, applies the appropriate grader, and reports results.

The tool is designed to be simple to run locally during development and straightforward to integrate into CI pipelines.

---

## Installation

No installation is required beyond what you already have:

- **Python 3** (any recent version — 3.8 or later recommended)
- **`claude` CLI** installed and authenticated

There are no additional Python package dependencies to install. The tool uses only the standard library and subprocess calls to the `claude` CLI.

To verify your environment is ready:

```bash
python3 --version
claude --version
```

If the `claude` CLI is not installed or not authenticated, eval runs will fail with an error before any cases are executed.

---

## CLI Reference

All invocations follow the pattern:

```
python run_eval.py <skill_path> [options]
```

Where `<skill_path>` is the path to the skill directory containing the `SKILL.md` file and `evals/` subdirectory.

### Run All Evals

```bash
python run_eval.py path/to/skill
```

Runs all eval cases defined for the skill — both trigger evals and quality evals. Results are printed to stdout and written to `eval-results.json` in the skill directory.

### Run Trigger Evals Only

```bash
python run_eval.py path/to/skill --type trigger
```

Runs only the trigger precision eval cases. Useful when iterating on the skill's description field to improve routing without re-running the full (slower) quality eval suite.

### Run Quality Evals Only

```bash
python run_eval.py path/to/skill --type quality
```

Runs only the output quality eval cases. Useful when the routing behavior is correct and you are iterating on the skill's instructions or workflow.

### Run a Single Eval Case

```bash
python run_eval.py path/to/skill --case <id>
```

Runs a single eval case identified by its case ID. Case IDs are defined in the eval case files. Use this for rapid iteration on a specific failing case without waiting for the full suite to complete.

Example:
```bash
python run_eval.py skills/yeet --case trigger-explicit-pr-flow
```

### Verbose Output

```bash
python run_eval.py path/to/skill --verbose
```

Prints full JSON output for each eval case, including:
- The input message sent to Claude
- The complete model response
- The grader's verdict and reasoning
- All tool calls made during the turn

Without `--verbose`, the tool prints a compact summary line per case (PASS or FAIL with the case ID). With `--verbose`, the full detail is available for debugging unexpected results.

### Override the Subject Model

```bash
python run_eval.py path/to/skill --model <model>
```

Overrides the model used to run the skill being evaluated. By default, the tool uses the model configured in the `claude` CLI. Use this flag to test a skill against a specific model version.

Example:
```bash
python run_eval.py skills/pdf --model claude-opus-4-5
```

### Override the Judge Model

```bash
python run_eval.py path/to/skill --judge-model <model>
```

Overrides the model used as the LLM-as-judge grader for quality evals. By default, the judge uses the same model as the subject. Specifying a different judge model is useful when you want to use a more capable model for judgment than for execution, or when you want to keep the judge model stable while testing different subject models.

Example:
```bash
python run_eval.py skills/pdf --model claude-haiku-4-5 --judge-model claude-opus-4-5
```

---

## Running Trigger Evals

Trigger evals verify that the skill activates (or does not activate) correctly for a given input message.

Each trigger eval case specifies:
- An input message
- Whether the skill **should** or **should not** trigger

The grader checks whether the skill was actually invoked in Claude's response and compares this to the expected behavior.

**Typical workflow when iterating on a description:**

1. Run trigger evals to establish a baseline:
   ```bash
   python run_eval.py skills/yeet --type trigger
   ```
2. Identify failing cases (false positives or false negatives).
3. Edit the `description` field in `SKILL.md` and update `skills-index.json`.
4. Re-run trigger evals to verify the change improved results.
5. Confirm no previously passing cases regressed.

---

## Running Quality Evals

Quality evals verify that the skill produces correct, complete, and appropriately formatted output given that it has been triggered.

Each quality eval case specifies:
- An input message (typically one that should trigger the skill)
- A rubric or expected output description used by the judge
- Optionally, specific assertions that the code-based grader checks

**Typical workflow when iterating on skill instructions:**

1. Run quality evals to establish a baseline:
   ```bash
   python run_eval.py skills/pdf --type quality
   ```
2. Use `--verbose` to inspect the full output of failing cases:
   ```bash
   python run_eval.py skills/pdf --type quality --verbose
   ```
3. Identify whether the failure is in the model's reasoning, missing steps, format violations, or incorrect tool usage.
4. Edit the `SKILL.md` workflow or conventions sections.
5. Re-run to verify improvement.

---

## Understanding Output

### Per-Case Lines

For each eval case, the tool prints a single summary line:

```
PASS  trigger-explicit-pr-flow
FAIL  trigger-ambiguous-commit
PASS  quality-basic-pdf-creation
```

The case ID follows the PASS/FAIL verdict. Case IDs are defined in the eval case files and should be descriptive enough to identify what is being tested at a glance.

### Summary Table

After all cases have run, the tool prints a summary table:

```
Results: 7 passed, 1 failed, 0 errored (8 total)

Type       Cases   Passed  Failed
trigger    5       4       1
quality    3       3       0
```

The table breaks down results by eval type, making it easy to see whether failures are concentrated in routing or output quality.

### Exit Codes

The tool exits with one of two codes:

- **`0`** — All eval cases passed. Use this to gate CI workflows.
- **`1`** — One or more eval cases failed (or an error prevented execution).

In CI, check the exit code to determine whether to block a merge:

```bash
python run_eval.py skills/yeet
if [ $? -ne 0 ]; then
  echo "Eval failures detected — blocking merge"
  exit 1
fi
```

### Error Cases

If a case could not be executed (for example, due to a `claude` CLI error, a timeout, or a malformed eval case definition), it is reported as `ERROR` rather than `PASS` or `FAIL`. Error cases count toward the non-zero exit code.

---

## Using in CI Pipelines

`run_eval.py` is designed to integrate cleanly into CI pipelines (GitHub Actions, GitLab CI, etc.).

### Basic GitHub Actions Step

```yaml
- name: Run skill evals
  run: python run_eval.py skills/yeet
  env:
    ANTHROPIC_API_KEY: ${{ secrets.ANTHROPIC_API_KEY }}
```

### Running Evals for All Skills

To run evals for every skill in the repository, iterate over skill directories:

```yaml
- name: Run all skill evals
  run: |
    for skill_dir in skills/*/; do
      if [ -d "$skill_dir/evals" ]; then
        python run_eval.py "$skill_dir" || exit 1
      fi
    done
  env:
    ANTHROPIC_API_KEY: ${{ secrets.ANTHROPIC_API_KEY }}
```

### Recommended CI Strategy

- Run **trigger evals** on every PR — they are fast and cheap.
- Run **quality evals** on PRs that modify skill instructions or the model version, and on a nightly schedule.
- Run **all evals** before any release or model upgrade.

This tiered approach balances coverage against cost and CI run time.

---

## Verbose Mode for Debugging

When a case fails unexpectedly, `--verbose` combined with `--case` provides the most targeted view:

```bash
python run_eval.py skills/pdf --case quality-extract-table --verbose
```

The verbose output for a failing quality eval includes:

- **Input message** — exactly what was sent to Claude
- **Full model response** — including all tool calls and their results
- **Judge prompt** — the full prompt sent to the judge model
- **Judge response** — the judge's verdict and reasoning
- **Grader verdict** — PASS or FAIL with the deciding criterion

This information is usually sufficient to diagnose whether the failure is in:
- The skill's instructions (Claude is not following them correctly)
- The eval case's rubric (the judge is applying the wrong criteria)
- The subject model's capabilities (the model cannot perform the task regardless of instructions)

---

## Results File: eval-results.json

After every run, `run_eval.py` writes a `eval-results.json` file to the skill directory. This file contains the full structured results for all cases run in the most recent invocation.

File location:
```
path/to/skill/eval-results.json
```

### Structure

```json
{
  "skill": "skill-name",
  "timestamp": "2026-03-14T10:22:00Z",
  "model": "claude-sonnet-4-6",
  "judge_model": "claude-sonnet-4-6",
  "summary": {
    "total": 8,
    "passed": 7,
    "failed": 1,
    "errored": 0
  },
  "cases": [
    {
      "id": "trigger-explicit-pr-flow",
      "type": "trigger",
      "status": "pass",
      "input": "stage everything, commit with message 'fix: typo', push, and open a PR",
      "expected_trigger": true,
      "actual_trigger": true,
      "duration_ms": 1240
    },
    {
      "id": "trigger-ambiguous-commit",
      "type": "trigger",
      "status": "fail",
      "input": "commit my changes",
      "expected_trigger": false,
      "actual_trigger": true,
      "duration_ms": 980,
      "failure_reason": "Skill triggered on a bare commit request that should not invoke the full yeet flow"
    }
  ]
}
```

### Uses

- **Trend analysis.** Compare `eval-results.json` across commits to track whether pass rates are improving or degrading.
- **CI artifacts.** Upload `eval-results.json` as a CI artifact to preserve the eval record for each run.
- **Debugging.** The `failure_reason` field (populated when `--verbose` is used or when the judge provides reasoning) records why a case failed, providing a persistent record for follow-up.

The results file is always overwritten by the most recent run. It is not a log of historical runs — use version control or CI artifact storage for historical records.
