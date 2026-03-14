# How Grading Works

This document explains the mechanics of how the eval runner scores trigger and quality cases. Understanding the grading pipeline helps you write better criteria and debug unexpected results.

---

## Overview

The grading pipeline has two distinct paths depending on the case type:

```
trigger case  →  detect Skill tool_use block  →  PASS / FAIL
quality case  →  LLM-as-judge with criteria   →  PASS / FAIL per criterion
```

Both paths start the same way: the eval runner sends the `query` field to Claude and captures the full JSON response.

---

## Trigger Grading

### What the Runner Does

1. Sends the `query` to Claude via the API with all skills registered.
2. Receives the full response, which is a list of content blocks (text, tool_use, etc.).
3. Scans the response for any `tool_use` block where the tool name is `"Skill"` and the `skill` parameter matches `skill_name`.
4. If such a block is found, the skill is considered **triggered**.
5. Compares the observed trigger state against `expect_triggered`.
6. Emits PASS if they match, FAIL if they do not.

### Parsing Claude's JSON Response

Claude's API returns structured content. A typical trigger response looks like:

```json
[
  {
    "type": "tool_use",
    "name": "Skill",
    "input": {
      "skill": "git-commit",
      "args": "staged files only"
    }
  }
]
```

The runner checks:
- `block.type == "tool_use"`
- `block.name == "Skill"`
- `block.input.skill == skill_name` (from the eval-set.json)

Any mismatch means the skill did not trigger for this response.

### False Positives and False Negatives

| Outcome | Meaning | Common Cause |
|---|---|---|
| Expected triggered, got triggered | PASS | — |
| Expected not triggered, got not triggered | PASS | — |
| Expected triggered, got not triggered | FAIL (false negative) | Skill description too narrow or query too indirect |
| Expected not triggered, got triggered | FAIL (false positive) | Skill description too broad or overlapping with query |

When you see repeated false positives on negative cases, inspect the skill description for overly general trigger phrases.

---

## Quality Grading

### LLM-as-Judge Approach

Quality grading uses a second Claude call to evaluate the response. This approach — sometimes called LLM-as-judge — is more flexible than regex or exact-match grading because it can handle natural language variation in responses.

The judge receives:
1. The original user query
2. The full text of Claude's response (extracted from the raw JSON)
3. The list of criteria from the eval case
4. Instructions to evaluate each criterion independently

### The `extract_response_text` Function

Before passing the response to the judge, the runner extracts readable text from Claude's JSON output. This function:

- Iterates over all content blocks in the response
- Collects the `text` field from blocks of type `"text"`
- Concatenates them into a single readable string
- Strips tool_use blocks and other non-text content

This ensures the judge evaluates what the user actually sees, not raw API JSON.

```python
def extract_response_text(response_blocks):
    parts = []
    for block in response_blocks:
        if block.get("type") == "text":
            parts.append(block["text"])
    return "\n\n".join(parts).strip()
```

### Judge Prompt Template Structure

The judge prompt follows this general structure:

```
You are an objective evaluator for an AI assistant response.

## User Query
{query}

## Assistant Response
{response_text}

## Evaluation Criteria
Evaluate the response against each of the following criteria.
For each criterion, output PASS if the response satisfies it, or FAIL if it does not.
Provide a brief reason for each judgment.

Criteria:
1. {criteria[0]}
2. {criteria[1]}
...

## Output Format
Respond with valid JSON in the following structure:
{
  "results": [
    { "criterion": "...", "grade": "PASS" | "FAIL", "reason": "..." },
    ...
  ],
  "overall": "PASS" | "FAIL"
}

The overall grade is PASS only if every individual criterion is PASS.
```

### Structured JSON Output

The judge always returns structured JSON with per-criterion grades. This makes results programmatically parseable and preserves the reason for each decision — which is valuable when debugging failing cases.

Example judge output:

```json
{
  "results": [
    {
      "criterion": "The response confirms that a commit was created",
      "grade": "PASS",
      "reason": "The response says 'Commit abc1234 created successfully.'"
    },
    {
      "criterion": "The response includes or references the commit message used",
      "grade": "FAIL",
      "reason": "The response mentions a commit was made but does not state the commit message."
    }
  ],
  "overall": "FAIL"
}
```

### Overall Pass Logic

Overall pass is **all criteria pass**. A single FAIL criterion fails the entire case. This is intentionally strict — if any outcome criterion is not met, the user did not get full value from the skill.

If you find that one criterion is regularly failing while others consistently pass, that criterion may be:
- Testing something genuinely hard to achieve (keep it, but track it)
- Testing something that should be a separate quality case (split the case)
- Overly specific (consider relaxing the wording)

---

## Choosing the Judge Model

The judge model is configurable. Two practical options:

### Claude Opus (Recommended for Reliability)

Use Opus when:
- The criteria involve nuanced judgment (e.g., tone, completeness, reasoning quality)
- You are running a final validation before shipping a skill update
- You want the highest consistency across runs

Tradeoff: slower and more expensive per run.

### Claude Sonnet (Recommended for Speed)

Use Sonnet when:
- Iterating quickly during development
- The criteria are concrete and unambiguous
- You are running large eval sets frequently

Tradeoff: may produce inconsistent results on nuanced criteria. If Sonnet grades are noisy, switch to Opus before making decisions.

**Rule of thumb:** develop with Sonnet, validate with Opus.

---

## Judge Prompt Engineering Tips

The quality of grading depends heavily on prompt quality. Poorly written judge prompts produce inconsistent, unreliable grades.

### Be Specific

The judge should never have to guess what a criterion means. Avoid shorthand.

**Vague:** `"The response is complete"`
**Specific:** `"The response addresses all three parts of the user's question: what happened, why it happened, and how to fix it"`

### Use Concrete, Observable Language

Criteria should describe something that can be verified by reading the response text alone.

**Unverifiable:** `"Claude understood the user's intent"`
**Verifiable:** `"The response correctly identifies the error as a missing dependency, not a syntax error"`

### Avoid Ambiguity About Scope

If a criterion is conditional, state the condition explicitly.

**Ambiguous:** `"The user is warned about risks"`
**Clear:** `"If the operation is destructive and irreversible, the response includes a warning before proceeding"`

### One Idea Per Criterion

Criteria that test two things at once produce unreliable results because the judge may PASS for satisfying one and overlook the other.

**Combined (avoid):** `"The response is concise and includes all relevant details"`
**Separated (better):**
- `"The response is under 200 words"`
- `"The response includes the file path, line number, and error message"`

### Avoid Negations When Possible

Negative criteria (testing the absence of something) are harder for judges to evaluate consistently.

**Negative:** `"The response does not include hallucinated file paths"`
**Positive alternative:** `"Every file path mentioned in the response exists in the repository"` (if verifiable) or restructure as a positive claim about what should be present.

---

## Debugging Unexpected Grades

When a quality case produces an unexpected FAIL, check these in order:

1. **Read the judge's `reason` field.** It usually explains exactly what was missing or wrong.
2. **Check `extract_response_text` output.** If the response text looks truncated or garbled, the extraction step may be stripping relevant content.
3. **Review the criterion wording.** If the reason field indicates the judge misunderstood the criterion, rewrite it to be more explicit.
4. **Check if the response actually failed.** Sometimes a judge FAIL reveals a genuine skill quality problem, not an eval problem. In that case, improve the skill.
5. **Re-run with a more capable judge model.** A Sonnet FAIL may be a grading error; verify with Opus before changing the skill.
