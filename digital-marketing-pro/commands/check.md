---
description: "Run the unified pre-publish quality gate on marketing content (hallucination + brand voice + structure + claims). Use before publishing any marketing copy."
argument-hint: "<file-or-content> [--full|--compliance] [--brand <slug>] [--evidence <path>] [--schema <name>]"
allowed-tools: Read Bash Glob Grep
---

# /digital-marketing-pro:check — Pre-Publish Quality Gate

Runs the unified evaluation suite on marketing content. Wraps `scripts/eval-runner.py` and produces a single pass / warn / blocked decision with actionable issues.

This is the canonical pre-publish gate for any marketing content (blog posts, ad copy, emails, social posts, landing pages, press releases). In v3.0 and earlier, the same checks ran automatically as a global PreToolUse hook on every Write/Edit operation in every project. In v3.1 that hook was removed because it fired across all plugins and projects regardless of context. v3.2 introduces this command as the explicit replacement.

## Quick examples

```
/digital-marketing-pro:check drafts/q2-launch-blog.md
/digital-marketing-pro:check drafts/healthcare-ad.md --full --brand healthfirst --evidence facts/q2-claims.json --schema ad_copy
/digital-marketing-pro:check drafts/financial-services-landing.md --compliance --brand finadvisor
/digital-marketing-pro:check "Inline content can also be checked directly."
```

## Modes

| Flag | Mode | What it runs |
|------|------|-------------|
| (default) | `run-quick` | hallucination + content quality + readability (~2s, no external deps) |
| `--full` | `run-full` | All 6 dimensions including brand voice + claims + structure (when corresponding inputs provided) |
| `--compliance` | `run-compliance` | Compliance-focused: hallucination + claims + brand voice + structure |

## Optional inputs

| Flag | Purpose |
|------|---------|
| `--brand <slug>` | Score against named brand's voice profile. Defaults to active brand if set. |
| `--evidence <path>` | Cross-check claims against a JSON evidence file. |
| `--schema <name>` | Validate structure against a named schema (`blog_post`, `email`, `ad_copy`, `social_post`, `landing_page`, `press_release`, `content_brief`, `campaign_plan`, or `--schema list` to see all). |

## Output

The command returns a unified report with:

- Composite score (0-100) and letter grade (A+ to F)
- Per-dimension scores with weights and pass/fail status
- Issues grouped by severity (CRITICAL / WARNING)
- Each issue paired with a specific fix suggestion
- Decision: **PASS** (safe to publish), **WARN** (publish but address warnings first), or **BLOCKED** (CRITICAL issues must be fixed before publishing)

## Decision rules

- **PASS** → no CRITICAL issues, composite score above auto-reject threshold (default 40)
- **WARN** → no CRITICAL issues but at least one WARNING; user should address before publishing
- **BLOCKED** → at least one CRITICAL issue (e.g., placeholder URL, fabricated statistic in headline, missing required disclaimer for regulated industry, **missing C2PA provenance manifest on an AI-generated asset in an EU-targeted campaign**); content cannot publish until fixed

## EU AI Act Article 50 — C2PA verification (added v3.4)

For assets flagged as AI-generated (file metadata or accompanying `--evidence` JSON declares `ai_generated: true`) AND brand profile `target_markets` include any EU/EEA jurisdiction, the gate runs C2PA verification on the asset and treats a missing or invalid manifest as a CRITICAL issue. Article 50 applies from **2 Aug 2026** — penalty up to EUR 15M or 3% global turnover. To embed a manifest, use `/digital-marketing-pro:c2pa-metadata`.

## See also

- [skills/check/SKILL.md](../skills/check/SKILL.md) — full skill specification
- [scripts/eval-runner.py](../scripts/eval-runner.py) — the master orchestrator
- [skills/context-engine/eval-framework-guide.md](../skills/context-engine/eval-framework-guide.md) — eval framework documentation
- [skills/context-engine/eval-rubrics.md](../skills/context-engine/eval-rubrics.md) — per-dimension scoring rubrics
