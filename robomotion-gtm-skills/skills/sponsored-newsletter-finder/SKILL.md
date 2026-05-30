---
name: sponsored-newsletter-finder
description: Discover newsletters a target ICP reads, evaluate each for audience fit / reach / CPM, and produce a ranked, tiered sponsorship shortlist with budget allocation and outreach templates. Use to test paid newsletter distribution faster and cheaper than building your own audience. Keyless discovery; the host agent does scoring and ranking.
metadata:
  version: 1.0.1
  category: monitoring
  type: composite
---

# Sponsored Newsletter Finder

A discovery + evaluation composite. Discovery is keyless (the host agent's web search +
directory pages); the deterministic scripts turn chosen URLs into structured data and
estimate cost bands. **Scoring, ranking, tiering, budget allocation, and outreach templates
are the host agent's job** over that data.

## When to use

- "Find newsletters I can sponsor to reach [ICP]."
- "What newsletters does my target audience read?"
- "Give me a ranked list of newsletters for [industry/role]."

Feeds `newsletter-signal-scanner` (which newsletters to subscribe to and monitor).

## Workflow

### 1. Discover (agent web search)

Run multiple query angles to surface candidate newsletters: `"[industry] newsletter"
sponsorship`, `site:substack.com [topic]`, `site:beehiiv.com [topic]`, `"best newsletters for
[role]"`, plus directories (newsletter.directory, paved.com, swapstack.co, sparkloop.co).
Collect candidate newsletter + About/Advertise URLs into a list.

**SERP path (if-set/else):** if `DATAFORSEO_LOGIN`/`DATAFORSEO_PASSWORD` (or `SERPER_API_KEY`)
are set, run those query angles through the **paid SERP** for broader, more reliable result
coverage. If not, **fall back to the host agent's keyless web search** (the default) — same
queries, fewer guaranteed results. Either way, extraction (step 2) is keyless.

### 2. Extract candidate pages (deterministic)

```bash
python3 ${SKILL_DIR}/scripts/page_extract.py \
  --urls https://news.example.com/advertise https://news.example.com/about \
  --output ${WORKSPACE}/newsletters_raw.json
# or
python3 ${SKILL_DIR}/scripts/page_extract.py --urls-file ${WORKSPACE}/urls.txt \
  --output ${WORKSPACE}/newsletters_raw.json
```

Returns per page: `{url, title, meta_description, headings, text, links, domain,
signals:{subscribers, open_rate, cpm, flat_rate}}`.

### 3. Estimate cost bands where pricing is undisclosed

```bash
python3 ${SKILL_DIR}/scripts/cpm_estimate.py --subscribers 18000 --open-rate 40 --json
```

Returns `{size_band, cost_min_usd, cost_max_usd, implied_cpm_min/max, estimate:true}`
from the design's size benchmarks (micro/small/mid/large).

### 4. Score, tier & write the shortlist (agent)

Read `newsletters_raw.json`, score each 1-5 on Audience match / Reach / Engagement / Niche
specificity / Sponsor accessibility (total /25), apply the CPM estimates, cross-reference
competitor-sponsorship findings (search `"[competitor]" "sponsored by" newsletter`), tier
(T1 20-25, T2 15-19, T3 10-14), allocate budget within the user's range, and write the
markdown digest + cold-outreach / media-kit-request templates to a workspace file.

## Outputs

A markdown shortlist (`${WORKSPACE}/newsletter-sponsors-[DATE].md`): Tier 1/2/3 with URL,
subscribers, open rate, audience, frequency, sponsorship type, estimated cost + CPM, past
sponsors, fit rationale, sponsor-page link; a "where competitors advertise" table; a budget
table; and outreach templates.

## Credentials / env

- **Required:** none — discovery and extraction are keyless.
- **Optional (paid, if-set/else):**
  - `DATAFORSEO_LOGIN` / `DATAFORSEO_PASSWORD` (or `SERPER_API_KEY`) — **if set → paid SERP**
    for broader newsletter discovery (step 1); **else → the host agent's keyless web search**
    (the default). Extraction (step 2) is keyless either way.
  - `ANTHROPIC_API_KEY` / `OPENAI_API_KEY` — **if set → optional script-side synthesis**;
    **else → the host agent** scores/tiers/writes the shortlist (the default; without any LLM
    at all, output degrades to a raw discovered list).
  - `SUPABASE_URL` / `SUPABASE_KEY` or `AIRTABLE_API_KEY` — **if set → persist the shortlist as
    a pipeline**; **else → workspace markdown file** (the default).

## Notes & edge cases

- Subscriber counts and open rates are often undisclosed — use `cpm_estimate.py` and label
  outputs as estimates.
- A competitor already sponsoring a newsletter = validated fit → bump priority.
- Best for teams with ~$500-5,000/month and a specific (not mass-market) ICP.
- Route discovery through a proxy/geo when running many queries to avoid IP blocks.
