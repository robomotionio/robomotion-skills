---
name: create-x-content
description: Draft 2–5 voice-tuned X post variants from a free-form brief, each with a distinct framing (how-to, mechanism, problem-first, hype, contrarian…), and self-check each against a personal voice guide's banned phrases and format rules before returning — so posts sound like the user, not like an AI. The agent does the drafting; a bundled deterministic linter enforces banned-phrase / length / hashtag rules. Invoked standalone or by social-kit.
metadata:
  version: 1.0.1
  category: content
  type: capability
---

# Create X Content

The drafting is **yours** (the agent is the model). This skill is mostly instructions plus
a tiny deterministic linter (`lint_post.py`) that mechanically checks each variant.

## When to use

- "Write X posts about [topic/launch/build]."
- When you want several genuinely different angles on one idea.
- As the X arm of `social-kit`. Pairs with `generate-voice-guide` and `graphics-studio`.

## How to draft

1. **Resolve the voice guide**: explicit path → stored config / Memory → default location →
   else prompt to generate one (`generate-voice-guide`) or proceed with a *warned* generic
   default. Never silently skip it — generic AI tweets are the failure mode.
2. **Parse the brief; decide variant count** by richness (2 = single-angle; 5 = mechanism-rich).
3. **Draft each variant** under a distinct framing the voice guide's hook patterns support
   (simple-howto, howto-plus-mechanism, problem-first, hype, mechanism-breakdown,
   ecosystem-map, contrarian, personal-experience). Quote the brief's specifics verbatim
   (numbers, tool names, prices) — that's the "meat". For rich briefs with a field-notes
   hook pattern, include one long-form variant.
4. **Self-check each variant** with the linter, then your own voice-match judgement. Rewrite
   ≤2× or drop. Prefer fewer strong variants over many weak ones.
5. **Save one file per variant** (`variant-<letter>-<framing>.md`) with frontmatter
   (`platform: x`, `format: short|long`, `framing`, `status: draft`) and just the post text.

## Linter

```bash
python3 ${SKILL_DIR}/scripts/lint_post.py --file ${WORKSPACE}/variant-a-howto.md \
  --voice-guide ${WORKSPACE}/voice-x.md --format auto
```

| Flag | Meaning |
|---|---|
| `--file` | Post file (default stdin; frontmatter is stripped). |
| `--banned` | Comma-separated extra banned phrases (added to the built-in list). |
| `--voice-guide` | Voice-guide file; pulls its "Banned phrases" section. |
| `--format` | `short` (<280) / `long` (280–4000) / `auto`. |
| `--max-hashtags` | Hashtag ceiling (default 2). |

Emits JSON: `{format, char_count, length_ok, banned_hits, hashtag_count, hashtags_ok,
link_count, has_concrete_token, pass}`. `pass=false` (banned hit, length, or hashtags) →
rewrite or drop. `has_concrete_token=false` is your cue to check the variant has real "meat".

`python3 ${SKILL_DIR}/scripts/lint_post.py --help` lists all flags.

## Outputs

One markdown file per variant + a short summary of framings used and a suggested next step
(e.g. pair with a `graphics-studio` visual). No index file.

## Credentials / env

- **Required:** none. The agent is the drafting engine; no script needs a key.
- **Optional:** none. **No paid service is applicable** — this is pure LLM drafting with no
  external-data step. A missing voice guide degrades gracefully (prompt or warned-generic).

## Notes & edge cases

- Default to fewer variants — two strong beats five weak. Framings must genuinely differ.
- Never silently skip the voice guide.
- Mirrors `create-linkedin-content`; the difference is the platform defaults (length, no
  arrow-bullet / "why this matters" requirement here).
