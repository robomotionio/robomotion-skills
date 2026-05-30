---
name: generate-voice-guide
description: Build a structured personal voice guide for X and/or LinkedIn by scanning a person's past original posts and refining through sample-and-feedback loops. The guide (persona, dos/don'ts, banned phrases, hook patterns, format rules, annotated real examples) is consumed by create-x-content, create-linkedin-content, and social-kit. The agent authors the guide; a bundled deterministic analyzer supplies corpus stats + absence-derived banned-phrase candidates. For individual social voice, not corporate brand voice.
metadata:
  version: 1.0.1
  category: content
  type: capability
---

# Generate Voice Guide

The guide itself is **yours to write** (the agent is the model). This skill provides the
instructions plus a deterministic `analyze_corpus.py` that turns a post corpus into the
mechanical evidence you reason over.

## When to use

- "Build a voice guide for [my / someone's] LinkedIn or X."
- Whenever a sibling content skill needs a voice guide and none exists.
- NOT for corporate blog/landing-page voice (separate brand-voice skill) — this is individual.

## How to run

1. **Get the corpus.** Capture the target's recent *original* posts (exclude replies,
   retweets, quotes, reshares) per platform with text + engagement + timestamps. Acquisition
   is agent-orchestrated:
   - X / LinkedIn-at-scale → Apify user-posts actor (`APIFY_API_TOKEN`):
     `curl "https://api.apify.com/v2/acts/<actor>/run-sync-get-dataset-items?token=$APIFY_API_TOKEN" -d @input.json`
   - LinkedIn → Phantombuster (`PHANTOMBUSTER_API_KEY` + LinkedIn session cookie), or
     `web-automation` + Robomotion Proxy for one-off public profiles.
   - **Fallback:** ask the user to paste 15–25 posts as plain text — fully keyless.
2. **Analyze the corpus** (deterministic stats + banned-phrase candidates):

```bash
python3 ${SKILL_DIR}/scripts/analyze_corpus.py --input ${WORKSPACE}/posts.json --platform x \
  --output ${WORKSPACE}/x-stats.json
```

Accepts a JSON array (`[{"text","is_reply","is_retweet","engagement","created_at"}]`) or a
plain-text file (posts separated by a blank line / `---`). Emits `{post_count,
length_chars, length_words, usage_rates, top_openers, banned_phrase_candidates}`.
Banned-phrase candidates are cliches **absent** from the corpus (the "derived from absence"
rule), not a generic blocklist.

3. **Author v1 of the guide** from the stats + the raw posts: persona, the "meat" principle,
   dos/don'ts, 10–20 banned phrases (confirm the candidates), 5–8 hook patterns, format
   rules, tone calibration, 4–6 annotated **real** examples (quoted verbatim).
4. **Sample-and-feedback loop (≥5 rounds):** draft 3 samples per round on the user's own
   topics, show which guide lines drove them, collect feedback via the agent's channel,
   revise. 5 rounds is a floor — push for more.
5. **Finalize & register:** strip the iteration changelog, save the clean
   `voice-x.md` / `voice-linkedin.md` to Memory/workspace, and register the path(s) so
   `create-x-content` / `create-linkedin-content` / `social-kit` auto-discover them.

`python3 ${SKILL_DIR}/scripts/analyze_corpus.py --help` lists all flags.

## Outputs

`voice-x.md` and/or `voice-linkedin.md` (persona, "meat" principle, dos, don'ts, banned
phrases, hook patterns, CTA guidelines, format rules, tone calibration, annotated example
posts), saved to the durable store with the guide paths registered.

## Credentials / env

- **Required:** none. The agent authors the guide; the analyzer is keyless; the paste-text
  corpus path needs no key.
- **Optional:**
  - `APIFY_API_TOKEN` (paid, with a fallback) — If set → X (and LinkedIn-at-scale) corpus
    scraping via the user-posts actor (larger, automatic corpus). If not set → ask the user
    to paste 15–25 posts as plain text (the keyless default); the analyzer + guide work the
    same either way.
  - `PHANTOMBUSTER_API_KEY` (+ a LinkedIn session cookie) (paid, with a fallback) — If set →
    LinkedIn post scraping. If not → `web-automation` + paste-text fallback (the default).
  - Robomotion Proxy — recommended for `web-automation` one-off LinkedIn reads.

## Notes & edge cases

- 5 iterations is a floor, not a ceiling — guides only lock in after several rounds.
- Use the user's own topics for samples so off-key lines are easy to spot.
- Quote real posts verbatim in examples; never paraphrase.
- Flag ghost-written/assistant-authored posts before baking them into the voice.
- Exclude replies, retweets, quotes, reshares — the analyzer already filters these.
