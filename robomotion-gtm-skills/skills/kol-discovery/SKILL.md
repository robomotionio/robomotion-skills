---
name: kol-discovery
description: Find Key Opinion Leaders in a domain by searching LinkedIn posts for prolific, high-engagement authors and merging them with web-researched influencers (conference speakers, newsletter authors, podcast hosts) into a ranked, scored KOL list. Use when the goal is authority/thought-leadership voices, not pain-language leads.
metadata:
  version: 1.0.1
  category: outreach
  type: capability
---

# KOL Discovery

Build a ranked KOL list by combining a **post-data half** (LinkedIn post search ->
aggregate by author -> deterministic engagement scoring) with a **web-research half**
(the agent finds conference speakers, newsletter/podcast hosts via web search). The
agent does keyword generation and web research; the bundled scripts do the post fetch
and the scoring math.

## When to use

- "Find KOLs / influencers in [industry]" / "who are the thought leaders for [domain]?"
- "Run KOL discovery for [client]" — authority voices, not complainers.
- Upstream of `linkedin-message-writer` / `linkedin-outreach` for influencer engagement.

## How it works (agent + scripts)

1. **(agent)** Intake domain, audience, seeds, exclusions, scoring thresholds. Generate
   15-25 authority/thought-leadership keywords (industry terms, "future of...", conference/
   event terms, content-creator signals) + KOL title keywords + vendor-exclusion patterns.
   **Present for approval** before running (controls Apify cost).
2. **Post search** — for each approved keyword, pull LinkedIn posts (bundled
   `post_search.py`, same as `linkedin-post-research`: Apify if `APIFY_API_TOKEN` set, else
   keyless serp degrade). Concatenate all keyword results into one posts JSON.
3. **Score** — aggregate by author and rank (bundled `score_kols.py`).
4. **(agent)** Web research — find known KOLs (top-[industry]-influencer searches, conference
   speakers, newsletter/podcast hosts). Write them as `web_kols.json`
   (`[{name, linkedin_url, source, notes}]`).
5. **Merge** — pass `--web-kols web_kols.json` to `score_kols.py`; overlaps are flagged
   `source: both` (the strongest KOLs); web-only entries appear as `source: web-research`.

## How to run

Run a post search per keyword and collect into one file, then score:

```bash
# Step 2 — collect posts (loop keywords; append into posts.json yourself, or run per batch)
python3 ${SKILL_DIR}/scripts/post_search.py \
  --keywords "future of rpa,agentic automation,intelligent automation" \
  --max-items 50 --sort-by relevance --output json > ${WORKSPACE}/posts.json

# Step 3+5 — aggregate, score, merge web-researched KOLs
python3 ${SKILL_DIR}/scripts/score_kols.py \
  --posts ${WORKSPACE}/posts.json \
  --web-kols ${WORKSPACE}/web_kols.json \
  --min-posts 2 --min-total-engagement 50 --top-n 50 --output csv
```

| `score_kols.py` flag | Default | Meaning |
|---|---|---|
| `--posts` | (required) | JSON list of posts (post_search output shape). |
| `--web-kols` | `""` | JSON list of web-researched KOLs to merge/flag. |
| `--min-posts` | `1` | Drop authors below this post count. |
| `--min-total-engagement` | `0` | Drop authors below total reactions+comments. |
| `--top-n` | `50` | Cap returned KOLs. |
| `--output` | `json` | `json` / `csv` / `summary`. |

## Outputs

Ranked KOL list: `{rank, name, linkedin_url, headline, kol_score, total_posts,
total_reactions, total_comments, avg_engagement, top_post_url, top_post_preview,
source(post-data|web-research|both)}`.

## Credentials / env

- `env.required`: **none** — the serp post-search degrade + web research backbone need no key.
- `env.optional`: `APIFY_API_TOKEN` — **if set → LinkedIn posts-search actor (accurate
  engagement metrics for the post-data scoring half); else → keyless serp** (the default; no
  engagement counts → weaker scoring, lean on web-research KOLs).

## Notes & edge cases

- Search **authority** keywords, not pain-language — the goal is voices who shape the
  conversation.
- Always run a small/test pass first (few keywords) before the full run to control Apify cost.
- Too many irrelevant authors -> tighten domain keywords + exclusions; too few -> lower
  `--min-posts` / `--min-total-engagement`. Overlaps (`source: both`) are the strongest KOLs.
