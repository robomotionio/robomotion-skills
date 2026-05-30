---
name: create-linkedin-content
description: Draft 2–5 voice-tuned LinkedIn post variants from a free-form brief, each with a distinct framing, applying LinkedIn-native conventions (arrow bullets, a "why this matters" beat, 150–500 words, 0–2 hashtags) and self-checking against a personal voice guide before returning. The agent does the drafting; a bundled deterministic linter enforces banned-phrase / length / arrow-bullet / "why this matters" rules. Invoked standalone or by social-kit.
metadata:
  version: 1.0.1
  category: content
  type: capability
---

# Create LinkedIn Content

The drafting is **yours** (the agent is the model). This skill is mostly instructions plus
a tiny deterministic linter (`lint_post.py`) enforcing the LinkedIn format conventions.

## When to use

- "Write LinkedIn posts about [topic/launch]."
- After a build/launch/insight when you want several framings to choose from.
- As the LinkedIn arm of `social-kit`. Pairs with `generate-voice-guide` and `graphics-studio`.

## How to draft

1. **Resolve the voice guide**: explicit path → stored config / Memory → default location →
   else prompt to generate one (`generate-voice-guide`) or proceed with a *warned* generic
   default. Never silently skip it — generic, AI-sounding posts are the failure mode.
2. **Parse the brief; decide variant count** by richness (LinkedIn skews toward 3).
3. **Draft each variant** under a distinct framing (builder-story, product-launch,
   problem-first, ecosystem-map, contrarian-insight, workflow-tutorial), applying LinkedIn
   defaults: 150–500 words, `→` arrow bullets for any list, a "why this matters" beat,
   0–2 hashtags, a "link in comments"-style CTA. Quote the brief's specifics verbatim.
   Avoid "I'm humbled" / "Grateful for…" performative openers.
4. **Self-check each variant** with the linter, then your own voice-match + press-release-tone
   judgement. Rewrite ≤2× or drop.
5. **Save one file per variant** (`linkedin-<letter>-<framing>.md`) with frontmatter
   (`platform: linkedin`, `framing`, `status: draft`) and the post body.

## Linter

```bash
python3 ${SKILL_DIR}/scripts/lint_post.py --file ${WORKSPACE}/linkedin-a-builder-story.md \
  --voice-guide ${WORKSPACE}/voice-linkedin.md
```

| Flag | Meaning |
|---|---|
| `--file` | Post file (default stdin; frontmatter is stripped). |
| `--banned` | Comma-separated extra banned phrases. |
| `--voice-guide` | Voice-guide file; pulls its "Banned phrases" section. |
| `--word-min` / `--word-max` | LinkedIn word band (default 150 / 500). |
| `--max-hashtags` | Hashtag ceiling (default 2). |

Emits JSON: `{word_count, length_ok, banned_hits, has_arrow_bullets,
has_why_this_matters, hashtag_count, hashtags_ok, has_concrete_token, pass}`. `pass`
requires no banned hits, in-band length, a "why this matters" beat, and ≤2 hashtags →
otherwise rewrite or drop. `has_arrow_bullets=false` is a nudge to use `→` for any list.

`python3 ${SKILL_DIR}/scripts/lint_post.py --help` lists all flags.

## Outputs

One markdown file per variant + a short summary of the framings used.

## Credentials / env

- **Required:** none. The agent is the drafting engine; no script needs a key.
- **Optional:** none. **No paid service is applicable** — this is pure LLM drafting with no
  external-data step. A missing voice guide degrades gracefully (prompt or warned-generic).

## Notes & edge cases

- Arrow bullets are a LinkedIn signal; prefer them for any list.
- Quote the brief's specifics verbatim (numbers, tool names, prices) — paraphrasing kills it.
- Prefer fewer strong variants over many watered-down ones.
- Mirrors `create-x-content`; the difference is the LinkedIn defaults above.
