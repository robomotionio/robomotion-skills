# SKILL.md Format & Structure

## Overview

A skill is a self-contained unit of capability that Claude can invoke to handle a specific class of user request. Each skill lives in its own directory and is defined primarily by a `SKILL.md` file. This file serves two distinct purposes simultaneously:

1. **As an instruction document** — it tells Claude what to do when the skill is activated.
2. **As a routing signal** — its description field tells the skill-loading system when to activate the skill at all.

Understanding the distinction between these two roles is essential to writing skills that work well in practice.

---

## YAML Frontmatter

Every `SKILL.md` file begins with a YAML frontmatter block delimited by `---`. The frontmatter contains metadata that the skills system reads to register and route the skill.

```yaml
---
name: skill-name
description: "A precise description of when this skill should be used."
---
```

### `name`

The `name` field is a short, machine-readable identifier for the skill. It should:

- Use lowercase letters and hyphens (kebab-case)
- Be unique across all skills in the index
- Match the directory name containing the skill
- Be stable — changing it may break references in the skills index

### `description`

The `description` field is the most important field in the frontmatter. It is the primary signal the routing system uses to decide whether to load a skill for a given user request. See the section on "The Description as a Learnable Hyperparameter" below for detailed guidance.

---

## Markdown Body

After the frontmatter, the `SKILL.md` body contains the skill's instructions in plain markdown. The body is what Claude reads and follows once the skill has been activated. A well-structured skill body typically includes the following sections, though not all are required for every skill.

### Prerequisites

List any tools, packages, CLI utilities, or environment requirements the skill depends on. This section helps Claude verify that the execution environment is suitable before attempting to run the skill.

Example:
```
## Prerequisites
- `gh` CLI installed and authenticated
- Git repository initialized with a remote
- Python 3.8+ with `reportlab` installed
```

### Workflow

The workflow section describes the sequence of steps Claude should follow to complete the task. It should be written as a numbered list or structured prose that makes the order of operations unambiguous.

A good workflow section:
- States the first action Claude should take before any decision-making
- Handles the common case first, then edge cases
- Specifies what to do when something goes wrong
- Does not leave ambiguous gaps that Claude must fill with guesswork

### Conventions

The conventions section documents any style, format, or behavioral rules that apply to outputs produced by this skill. Examples include:

- Commit message format
- File naming conventions
- Output verbosity expectations
- Which tools to prefer when multiple tools could accomplish the same task

---

## The Description as a Learnable Hyperparameter

The `description` field is not documentation — it is a **routing decision function written in natural language**. Its job is to be interpreted by a language model that is deciding, in real time, whether this skill is the right tool for the current user request.

This framing has a concrete implication: the description can be tuned. If a skill is over-triggering (activating when it should not), the description should be made more restrictive. If a skill is under-triggering (failing to activate when it should), the description should be broadened or made more explicit about the cases it covers.

Think of the description as a hyperparameter that can be adjusted based on eval results. A trigger precision eval tells you how well the current description is working. A failing eval case is a signal that the description needs to be revised.

---

## Three Principles for Writing Descriptions

### 1. Imperative Voice

Descriptions should begin with a verb phrase that directly tells the routing model what to do. This makes the trigger condition explicit rather than implicit.

- **Weak:** "This skill helps with git operations involving commits and pushes."
- **Strong:** "Use only when the user explicitly asks to stage, commit, push, and open a GitHub pull request in one flow using the GitHub CLI (`gh`)."

The imperative form ("Use when...", "Use only when...", "Use for...") signals to the routing model that this is an activation rule, not a description of capabilities.

### 2. Concrete Examples

Abstract descriptions are ambiguous. Concrete descriptions — those that name specific tools, specific workflows, or specific user phrasings — leave less room for incorrect routing.

Compare:

- **Abstract:** "Use when the user wants to work with documents."
- **Concrete:** "Use when tasks involve reading, creating, or reviewing PDF files where rendering and layout matter; prefer visual checks by rendering pages (Poppler) and use Python tools such as `reportlab`, `pdfplumber`, and `pypdf` for generation and extraction."

The concrete version names specific tools (`reportlab`, `pdfplumber`, `pypdf`, `Poppler`) and specifies a particular concern (`rendering and layout matter`). This precision helps the routing model distinguish between a request that should trigger this skill and a superficially similar request that should not.

### 3. Negative Space

Negative space refers to the implicit boundary created by what the description does not include. A well-written description naturally excludes cases that look similar but should be handled differently.

More explicitly, consider adding "Use only when..." or "Do not use for..." clauses when there is a meaningful risk of false positives. The yeet skill description uses "Use only when" to signal that its trigger condition is narrow — the user must explicitly request all four actions (stage, commit, push, and open a PR) together. A request to just commit, or just push, should not trigger the yeet skill.

---

## Reference: Canonical Skill Descriptions

Two skills serve as reference examples for well-written descriptions:

### yeet

```
Use only when the user explicitly asks to stage, commit, push, and open a GitHub pull request in one flow using the GitHub CLI (`gh`).
```

This description demonstrates:
- Imperative voice ("Use only when")
- Restrictive scoping ("only when", "explicitly asks")
- Enumeration of all required conditions (stage AND commit AND push AND open a PR)
- Tool specificity ("GitHub CLI (`gh`)")

The word "explicitly" is load-bearing: it prevents the skill from triggering when the user mentions these actions in passing rather than requesting them as a combined operation. The enumeration of all four actions (stage, commit, push, PR) prevents the skill from triggering when only a subset is requested.

### pdf

```
Use when tasks involve reading, creating, or reviewing PDF files where rendering and layout matter; prefer visual checks by rendering pages (Poppler) and use Python tools such as `reportlab`, `pdfplumber`, and `pypdf` for generation and extraction.
```

This description demonstrates:
- Imperative voice ("Use when")
- Scope definition via medium ("PDF files") and concern ("rendering and layout matter")
- Tool guidance embedded in the description (`reportlab`, `pdfplumber`, `pypdf`, `Poppler`)
- A secondary instruction about preferred approach ("prefer visual checks")

Note that the description does double duty: it is both a routing signal (when to activate) and a brief instruction (how to approach the task once activated). This is acceptable and often useful when the most important aspect of "how" is closely tied to "when."

---

## skills-index.json Manifest Format

All skills registered in the system are listed in a central manifest file called `skills-index.json`. This file is the authoritative registry of available skills and is read by the skills-loading system at startup.

The manifest is a JSON array of skill objects. Each object contains at minimum:

```json
[
  {
    "name": "skill-name",
    "path": "relative/path/to/skill/directory",
    "description": "The full description string from the skill's frontmatter."
  }
]
```

### Fields

- **`name`** — Must match the `name` field in the skill's `SKILL.md` frontmatter exactly.
- **`path`** — Path to the skill directory, relative to the skills repository root. Used to locate the `SKILL.md` file and any associated resources (evals, scripts, etc.).
- **`description`** — The description string used for routing. Should be kept in sync with the `description` field in the skill's frontmatter. When these diverge, the manifest value takes precedence for routing decisions.

### Keeping the Manifest in Sync

When a skill's description is updated in its `SKILL.md` frontmatter, the corresponding entry in `skills-index.json` must also be updated. An automated check or pre-commit hook should enforce this constraint, since a stale manifest entry will cause routing to use the old description even after the skill's instructions have changed.

When adding a new skill:
1. Create the skill directory and write the `SKILL.md` file.
2. Add an entry to `skills-index.json` with the correct name, path, and description.
3. Run trigger evals to verify that the routing decision matches expectations.
