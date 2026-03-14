# Evaluation Fundamentals

## What Are AI Evals and Why They Matter

AI evaluations (evals) are structured tests that measure whether a model or system behaves correctly across a defined set of inputs. Unlike traditional software tests, which verify deterministic outputs, AI evals operate probabilistically — a given input may produce slightly different outputs across runs, so evals are designed to assess intent, coverage, and quality rather than byte-for-byte correctness.

Evals serve several critical functions:

- **Regression prevention.** As models are updated or skills are modified, evals catch regressions before they reach users. A skill that worked last week may break after a prompt change or a model update.
- **Capability verification.** Before shipping a new skill, evals confirm that the system actually performs the task it claims to perform.
- **Comparative benchmarking.** When choosing between two skill descriptions or two prompt strategies, evals provide quantitative signal about which is better.
- **Documentation as tests.** A well-written eval suite doubles as living documentation — it makes explicit what the system is expected to do and not do.

Without evals, quality assessment is purely anecdotal. A developer might manually test a few cases and declare success, while systematic failure modes go undetected. Evals enforce discipline.

---

## The Two Dimensions We Test

Every skill eval targets one of two orthogonal dimensions:

### 1. Trigger Precision

Trigger precision measures whether a skill activates at the right times — and only at those times. This is a routing problem: given a user message, does the system correctly decide to invoke this skill?

Two failure modes exist:

- **False positives (over-triggering).** The skill fires when it should not. A commit skill that activates when the user merely mentions the word "commit" in a sentence, rather than when they explicitly request a commit operation, is over-triggering. This wastes tokens, confuses users, and may take unwanted actions.
- **False negatives (under-triggering).** The skill fails to fire when it should. A PDF skill that doesn't activate when the user says "convert this to a PDF" is under-triggering. The user's request goes unhandled.

Trigger evals test both failure modes by providing positive examples (should trigger) and negative examples (should not trigger) and checking the model's routing decision.

### 2. Output Quality

Output quality measures whether, given that the skill has been triggered, the resulting output meets the desired standard. This includes:

- **Correctness.** Does the output fulfill the user's request accurately?
- **Completeness.** Are all required steps or components present?
- **Format compliance.** Does the output follow any structural conventions (e.g., valid JSON, correct markdown, proper CLI flags)?
- **Safety and scope.** Does the output stay within appropriate boundaries, avoiding destructive or unauthorized actions?

Output quality evals are typically harder to automate than trigger evals because the criteria are more nuanced. They often require an LLM-as-judge rather than a simple pattern match.

---

## Capability Evals vs. Regression Evals

Anthropic's research distinguishes two complementary eval paradigms that together provide comprehensive coverage:

### Capability Evals

Capability evals ask: *Can the system do this at all?* They probe the outer boundary of what the skill or model is able to accomplish. These evals are run:

- When a skill is first developed, to confirm it works as intended
- When extending a skill to cover new use cases
- When validating that a model upgrade preserves or improves existing behavior

Capability evals tend to use carefully constructed, sometimes challenging examples. A capability eval for a PDF skill might test whether it can extract structured data from a scanned document with irregular formatting — a hard case that confirms the skill's upper bound.

### Regression Evals

Regression evals ask: *Does the system still do what it used to do?* They guard against changes — to prompts, to models, to dependencies — breaking previously working behavior. These evals are run:

- On every pull request or skill update
- After model version upgrades
- After changes to the skills index or routing logic

Regression evals prioritize breadth over depth. They cover the common cases that users actually encounter, not exotic edge cases. A regression suite for a commit skill would include the standard "stage, commit, and push" flow that accounts for 90% of usage, not unusual repository states.

In practice, a mature skill has both: a regression suite that runs in CI and a capability suite that runs on demand when the skill is being developed or extended.

---

## Three Grader Types

A grader is the mechanism that decides whether a given eval case passed or failed. There are three primary grader types:

### 1. Code-Based Graders

Code-based graders are deterministic functions written in Python (or another language) that inspect the model's output programmatically.

**Examples:**
- Check whether a specific file was created
- Verify that a git command was issued with the correct flags
- Parse JSON output and assert that a field has the expected value
- Confirm that a URL was opened or a CLI tool was called

**Strengths:**
- Fast — no additional model calls required
- Perfectly reproducible — same input always produces same verdict
- Cheap — no API costs beyond the skill invocation itself

**Weaknesses:**
- Brittle — minor surface-level variation in output format can cause false failures
- Limited scope — cannot assess prose quality, tone, or nuanced correctness
- Requires anticipating exact output format in advance

**Best for:** Trigger decisions (did the skill fire?), action verification (was a specific tool called?), structured output validation (is this valid JSON?).

### 2. Model-Based Graders (LLM-as-Judge)

Model-based graders use a second LLM call to evaluate the output of the first. A judge prompt describes the evaluation criteria and the judge model returns a pass/fail verdict (often with reasoning).

**Examples:**
- "Does this response correctly summarize the document without adding false information?"
- "Does this commit message accurately describe the diff and follow conventional commits format?"
- "Does this skill activation decision match what a reasonable user would expect?"

**Strengths:**
- Flexible — can evaluate open-ended, subjective, or complex criteria
- Robust to surface variation — understands semantic equivalence
- Can provide reasoning that aids debugging

**Weaknesses:**
- Slower and more expensive — requires an additional model call per eval case
- Non-deterministic — different runs may produce different verdicts
- Judge model may have its own biases or blind spots
- Requires careful judge prompt engineering

**Best for:** Output quality on prose tasks, nuanced correctness where exact matching fails, multi-step reasoning quality.

### 3. Human Graders

Human graders involve a person reviewing the output and making a judgment.

**Examples:**
- A developer reviewing generated code for correctness before merging
- A domain expert assessing whether a summarization is accurate
- A UX reviewer checking whether a response is appropriately helpful

**Strengths:**
- Highest quality — humans can apply full contextual understanding
- Catches failure modes that automated graders miss
- Necessary for tasks where no automated criterion exists yet

**Weaknesses:**
- Slow — does not scale to large eval suites
- Expensive — requires human time
- Inconsistent — different reviewers may reach different conclusions
- Cannot run in CI

**Best for:** Initial development of a new skill (before automated evals exist), auditing a sample of production outputs, calibrating automated graders.

---

## When to Use Each Type

| Scenario | Recommended Grader |
|---|---|
| Did the skill trigger on this message? | Code-based |
| Was a specific file created or tool called? | Code-based |
| Is this JSON output structurally valid? | Code-based |
| Is this commit message descriptive and accurate? | Model-based |
| Does this summary capture the key points? | Model-based |
| Is this response safe and appropriately scoped? | Model-based |
| Is this novel generated output high quality? | Human (initially), then model-based |
| Does this behavior match user expectations? | Human |

In practice, most eval suites use a mix. Trigger evals use code-based graders because the decision is binary and checkable. Quality evals use model-based graders for prose and human graders for initial calibration.

---

## How This Applies to SKILL.md Testing

Skills in this repository are tested along both dimensions described above. Each skill directory may contain an `evals/` subdirectory with eval cases defined as structured data. The `run_eval.py` script runs these cases and applies the appropriate grader.

For trigger evals, the grader checks whether the skill was invoked (or not invoked) by running the target message through Claude and inspecting the tool calls made. This is effectively a code-based grader — it checks for the presence or absence of a specific action.

For quality evals, the grader typically uses a judge model with a skill-specific rubric. The rubric is defined alongside the eval case and describes what a correct output looks like in terms the judge can apply.

This design means that writing good evals is as important as writing good skills. A skill with no evals is unverified. A skill with weak evals may pass while still failing users. The goal is evals that are strict enough to catch real problems and flexible enough not to flag correct behavior as failures.
