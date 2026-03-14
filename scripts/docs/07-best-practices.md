# Best Practices & Pitfalls

This guide consolidates lessons from building and iterating on Claude Code skill evals. It draws on Anthropic's published guidance on evaluation design and practical experience from the eval loop.

---

## The 8-Step Roadmap from Anthropic's "Demystifying Evals"

Anthropic's research on building evals for AI agents identifies a progression that applies directly to skill development:

1. **Define the task clearly.** Write down what the skill does and does not do before writing a single test case. Ambiguity in the skill definition produces unreliable evals.

2. **Identify the success criteria.** What does a good response look like? What does a bad response look like? Be concrete before opening an editor.

3. **Start with human judgment.** Before building automated evals, manually test the skill on 5–10 queries and grade the results yourself. This calibrates your intuition.

4. **Write a small eval set first.** 8–13 cases is enough to get started. Resist the urge to write 50 cases before running anything.

5. **Run evals and analyze failures.** Look for patterns in failures — do they cluster around a specific type of query, a specific criterion, or a specific edge case?

6. **Iterate on the skill or the description.** Most failures in early evals indicate a skill description problem, not a model problem. Refine the description before changing the eval cases.

7. **Add cases for discovered failure modes.** After each iteration, add eval cases that cover the failure modes you found. This prevents regression.

8. **Graduate to larger-scale testing when stable.** Once the small eval set passes consistently, expand to more cases or a dedicated eval framework for statistical confidence.

---

## The Eval Loop

The core development cycle for any skill looks like this:

```
write skill description
        ↓
write eval-set.json (8–13 cases)
        ↓
run trigger evals
        ↓
identify failures → refine skill description
        ↓
run quality evals
        ↓
identify failures → refine criteria or skill behavior
        ↓
re-run full eval set
        ↓
iterate until stable
```

This loop should be tight and fast. Each iteration should take minutes, not hours. If it takes longer, the eval set is probably too large or the cases are too complex.

### Description Optimization Cycle

Trigger eval failures almost always trace back to the skill description. The description is what Claude reads to decide whether to activate a skill. When trigger evals fail:

1. Run all trigger cases and collect failures.
2. Read each failing query carefully. Ask: "Given the current description, why would Claude make this mistake?"
3. Find the phrase in the description that caused the over-trigger or under-trigger.
4. Rewrite that phrase. Make it more specific to reduce over-triggering. Make it broader or add examples to reduce under-triggering.
5. Re-run trigger evals immediately. Do not wait to run quality evals.
6. Repeat until all trigger cases pass, then move to quality evals.

---

## Clean Test Environments

Eval results are only reliable if the environment is consistent between runs.

**Run from the skill directory.** The eval runner resolves paths relative to the current directory. Running from a different directory can cause skills or eval files to not be found.

**No prior conversation context.** Each eval case is a fresh, independent conversation. If your eval runner is reusing a conversation session, results may be contaminated by prior context.

**Pin the model version when possible.** If you are tracking quality over time, model updates can change results in ways unrelated to your skill. Pin to a specific model version for reproducibility.

**Avoid running evals while editing the skill.** If you change the skill file between cases in a run, the results will be inconsistent.

---

## Common Pitfalls

### Vague Skill Descriptions That Trigger Too Broadly

A skill description like "helps with git" will cause the skill to activate for any git-related query, including ones handled by other skills or by Claude's general capabilities.

**Signs of this problem:** Many false positives in trigger evals, especially on negative cases involving adjacent workflows.

**Fix:** Make the description action-specific. Describe exactly what the user must be asking for to activate the skill. Use the form: "Activate when the user wants to [specific action]."

### Brittle Criteria That Test Tool Sequences Instead of Outcomes

Criteria like "Claude calls git_status before proceeding" are testing implementation details. Claude may find a better internal approach that still produces a correct result — and your eval will incorrectly fail it.

**Signs of this problem:** Quality evals fail even when the user-visible response is correct. The judge's reason cites something the user never sees.

**Fix:** Rewrite every criterion as a statement about the response text or the user's achieved outcome. If you cannot verify the criterion by reading the response, it is the wrong criterion.

### Too Few Negative Trigger Cases

An eval set with three positive trigger cases and one negative trigger case will give you false confidence. The skill could be triggering on every query and still pass most cases.

**Signs of this problem:** Eval pass rate is high, but users report unexpected skill activations in real use.

**Fix:** Aim for at least three negative trigger cases per skill. Include vocabulary-overlap cases (queries that use the same words as your skill but have different intent) and adjacent-workflow cases.

### Not Rotating Test Cases (Eval Awareness Risk)

If the same eval set is run repeatedly during development, there is a risk that the skill description becomes optimized specifically for those queries rather than for the general task. This is the skill-level equivalent of eval awareness — the concern documented in Anthropic's BrowseComp research where models may have been trained on eval benchmarks.

**Signs of this problem:** Eval pass rates are high but real-world performance is mediocre. The skill works well on eval queries but struggles on slight paraphrases.

**Fix:** Periodically add new cases written by someone unfamiliar with the current eval set. Reserve a holdout set of cases that you only run at milestone checkpoints, not during iteration.

### Criteria That Are Subjective or Unmeasurable

Criteria like "the response is helpful" or "Claude handles this gracefully" cannot be reliably graded because they depend on the judge's interpretation of vague terms.

**Signs of this problem:** The same case produces different grades on different runs. Judge reasons are inconsistent.

**Fix:** Replace subjective criteria with observable ones. "Helpful" becomes "the response provides at least one actionable next step." "Graceful" becomes "the response acknowledges the error without blaming the user."

### Treating Eval Pass as a Guarantee

A passing eval set is evidence of quality, not proof of it. Evals only cover the cases you wrote. New user query patterns, edge cases, and model updates can all introduce regressions not covered by the existing set.

**Fix:** Treat evals as a living artifact. Add cases whenever a real-world failure is reported. Run evals after every skill update, not just during initial development.

---

## When to Graduate to promptfoo or Braintrust

The lightweight eval runner built into the skills framework is designed for fast iteration on small case sets. At a certain point, you will need more infrastructure. Consider graduating to a dedicated eval framework when:

**You need statistical significance.** When you want to compare two versions of a skill description with confidence that the difference is real and not noise, you need enough cases and enough runs to compute meaningful statistics. Frameworks like promptfoo support this natively.

**You need A/B testing across model versions or skill variants.** If you want to compare Sonnet vs. Opus as the execution model, or compare two different skill descriptions systematically, dedicated frameworks provide the experiment management tooling.

**Your case set has grown beyond ~30 cases.** Managing a large eval set in a hand-written JSON file becomes error-prone. Frameworks provide better organization, tagging, filtering, and result storage.

**You need persistent result history.** The built-in runner does not store historical results. Braintrust and LangSmith provide result storage, trend visualization, and regression detection across time.

**You want to evaluate at the dataset level, not just case level.** Some quality properties (e.g., consistency, coverage of a topic domain) can only be evaluated by looking at many responses together, not one at a time.

The recommendation: start with the built-in runner and the 8–13 case pattern. Move to a framework when the limitations become a bottleneck, not before.
