# Writing Test Cases for Skill Evals

This guide explains how to write effective eval sets for Claude Code skills. A well-designed eval set gives you confidence that your skill triggers at the right times and produces high-quality outputs.

---

## The eval-set.json Schema

Each skill's eval set lives in a file named `eval-set.json` alongside the skill. The top-level structure is:

```json
{
  "skill_name": "string",
  "cases": [
    {
      "id": "string",
      "type": "trigger|quality",
      "query": "string",
      "expect_triggered": true,
      "criteria": ["string array (quality type only)"]
    }
  ]
}
```

### Field Reference

| Field | Type | Required | Description |
|---|---|---|---|
| `skill_name` | string | Yes | Must exactly match the skill's registered name |
| `cases` | array | Yes | List of test case objects |
| `cases[].id` | string | Yes | Unique identifier, e.g. `"trigger-positive-01"` |
| `cases[].type` | `"trigger"` or `"quality"` | Yes | Determines how the case is evaluated |
| `cases[].query` | string | Yes | The user message sent to Claude |
| `cases[].expect_triggered` | boolean | Trigger only | Whether the skill should activate for this query |
| `cases[].criteria` | string[] | Quality only | Outcome criteria the response must satisfy |

The `expect_triggered` field is only meaningful for `trigger` type cases. The `criteria` field is only meaningful for `quality` type cases. Including neither field in the wrong case type is a common source of confusion — keep them separated.

---

## Trigger Cases

Trigger cases verify that the skill activates when it should and stays silent when it should not. Every skill needs both positive (should trigger) and negative (should not trigger) trigger cases.

### Positive Trigger Cases

Positive cases confirm the skill activates for genuine, in-scope requests.

**Guidelines:**
- Use the most direct, unambiguous phrasing a real user would use
- Include at least one query that uses the exact wording from the skill description
- Include paraphrases that convey the same intent with different vocabulary
- Include queries that are clearly in scope but phrased informally

**Example** (for a `git-commit` skill):
```json
{ "id": "trigger-positive-01", "type": "trigger", "query": "commit my changes", "expect_triggered": true },
{ "id": "trigger-positive-02", "type": "trigger", "query": "save my work to git", "expect_triggered": true },
{ "id": "trigger-positive-03", "type": "trigger", "query": "create a git commit with a good message", "expect_triggered": true }
```

### Negative Trigger Cases

Negative cases confirm the skill does not fire on unrelated or adjacent requests.

**Guidelines:**
- Include queries that share vocabulary but have different intent (e.g., asking *about* git, not asking Claude *to* commit)
- Include queries for adjacent workflows that have their own skill (if any)
- Include queries that a user might plausibly ask in the same session but that are clearly out of scope

**Example:**
```json
{ "id": "trigger-negative-01", "type": "trigger", "query": "what is git?", "expect_triggered": false },
{ "id": "trigger-negative-02", "type": "trigger", "query": "push my changes to the remote", "expect_triggered": false },
{ "id": "trigger-negative-03", "type": "trigger", "query": "show me the git log", "expect_triggered": false }
```

### Boundary Cases

Boundary cases sit at the edge of the skill's scope and are the most valuable for refining the skill description.

**Guidelines:**
- Identify the ambiguous zone around your skill's intent
- Write queries that a reasonable person might expect the skill to handle — but that you have consciously decided are in or out of scope
- Mark them clearly in the `id` so you can spot them in results (e.g., `trigger-boundary-01`)

**Example:**
```json
{ "id": "trigger-boundary-01", "type": "trigger", "query": "commit and push my changes", "expect_triggered": false }
```

If this boundary case fails (skill triggers when it shouldn't), you know the skill description needs tightening.

---

## Quality Cases

Quality cases verify the output of the skill meets real standards. They run the full skill and evaluate the response against a set of criteria using an LLM judge.

### Writing Good Criteria

Criteria should be **outcome-based**, not **process-based**. They describe what the final response must accomplish — not how Claude should go about it.

**Good criteria (outcome-based):**
- `"The commit message follows the Conventional Commits format"`
- `"The response includes a summary of which files were staged"`
- `"The user is informed if there are no staged changes"`

**Bad criteria (process-based):**
- `"Claude calls git_status before git_commit"` — tests tool sequence, not outcome
- `"Claude uses the Bash tool"` — implementation detail, not user value
- `"The response is helpful"` — unmeasurable and subjective

### Criteria Writing Checklist

Before adding a criterion, ask:

1. Can a judge determine pass/fail by reading only the final response text?
2. Is the criterion specific enough that two judges would agree?
3. Does passing this criterion mean the user got something valuable?
4. Would the criterion still be valid if Claude used a completely different internal approach?

If any answer is no, revise the criterion.

### Example Quality Case

```json
{
  "id": "quality-basic-commit",
  "type": "quality",
  "query": "commit my staged changes",
  "criteria": [
    "The response confirms that a commit was created",
    "The response includes or references the commit message that was used",
    "If no files are staged, the response informs the user rather than proceeding silently"
  ]
}
```

---

## How Many Cases to Write

A practical eval set for a single skill contains **8 to 13 cases** total, distributed roughly as follows:

| Category | Count | Notes |
|---|---|---|
| Positive trigger | 3–4 | Cover direct, paraphrase, and informal phrasings |
| Negative trigger | 3–4 | Cover vocabulary overlap, adjacent intents, out-of-scope |
| Boundary trigger | 1–2 | The edge cases unique to your skill |
| Quality | 2–3 | Cover the core happy path and at least one edge/error path |

**Why not more?** Larger sets are valuable for statistical confidence but require more maintenance. For initial development, 8–13 cases give you fast iteration. Once the skill is stable, consider expanding to 20+ using a framework like promptfoo.

**Why not fewer?** Fewer than 8 cases, especially with only 1–2 negative triggers, leaves major blind spots. A skill with only positive trigger tests can pass all cases while triggering on everything.

---

## Common Query Patterns

### Exact Match Queries

Use the most direct formulation of the request. These should almost always pass and serve as a sanity check.

```
"commit my changes"
"run the eval"
"create a pull request"
```

### Paraphrase Queries

Rephrase the same intent. Tests that the skill is robust to natural language variation.

```
"save my work in a commit"       # paraphrase of "commit my changes"
"evaluate this skill"            # paraphrase of "run the eval"
"open a PR for this branch"      # paraphrase of "create a pull request"
```

### Adversarial / Boundary Queries

Queries designed to probe the edges. Either clearly adjacent-but-out-of-scope, or ambiguous enough to require a deliberate decision.

```
"commit and then push"           # two-step; likely out of scope for a commit-only skill
"what should my commit message say?" # asking for advice, not asking Claude to commit
"git add and commit"             # might include staging, which may or may not be in scope
```

---

## Anti-Patterns to Avoid

### Overfitting to Specific Wording

Writing trigger cases that only use the exact phrasing from the skill description creates a false sense of coverage. The skill may fail on natural user queries.

**Bad:** Only testing `"please make a git commit"` because the description says "makes a git commit".
**Better:** Also test `"save my changes"`, `"checkpoint my work"`, `"commit everything staged"`.

### Testing Tool Sequences Instead of Outcomes

Quality criteria that check whether Claude called a specific tool in a specific order are fragile. Claude's internal strategy may change without affecting the quality of the result.

**Bad criterion:** `"Claude calls git_diff before git_commit"`
**Better criterion:** `"The response summarizes what changes are included in the commit"`

### Vague Criteria

Criteria that cannot be objectively evaluated lead to inconsistent judge results and noisy eval scores.

**Bad:** `"The response is good"`, `"Claude behaves appropriately"`, `"The output is useful"`
**Better:** `"The response states the name of the branch the commit was added to"`, `"The response includes the short commit hash"`

### Missing Negative Trigger Cases

An eval set with only positive trigger cases will pass even if the skill triggers on every possible query. Negative cases are essential for detecting over-triggering.

### Duplicating Cases Without Purpose

Having five nearly identical positive trigger cases that vary only by punctuation wastes eval budget and doesn't improve coverage. Each case should test something meaningfully different.

---

## Naming Convention for Case IDs

Use a consistent naming scheme so results are easy to scan:

```
trigger-positive-01
trigger-positive-02
trigger-negative-01
trigger-negative-02
trigger-boundary-01
quality-happy-path-01
quality-edge-case-01
```

The `id` field appears in eval output. Descriptive IDs let you immediately see which cases are failing without reading the full query.
