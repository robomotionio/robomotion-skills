---
name: kol-engager-icp
description: Turn key-opinion-leader (KOL) audiences on LinkedIn into a strictly ICP-qualified, deduplicated lead list. For each KOL, pick their single most topic-relevant high-engagement recent post (a topic-relevance gate keeps off-topic viral audiences out), extract the reactors and commenters via a managed Apify actor (PhantomBuster and keyless Playwright degrades), enrich firmographics through Apollo, then score every engager on a deterministic ICP-fit x intent x recency model into tiers A/B/C and dedup across runs. Surfaces only tier A/B by default, each lead tagged with the KOL and post topic they engaged. Use after KOL discovery or with a manual KOL list.
metadata:
  version: 2.1.1
  category: lead-generation
  type: capability
---

# KOL Engager ICP

Capture in-market leads from influencer audiences — *qualified*, not raw. KOL audiences are
BROAD, so this skill is built around a strict ICP filter and a topic-relevance gate: engagers
of a KOL's off-topic viral post are noise. The hard cost lever is **one post per KOL**.

Pipeline: `select_kol_posts` -> `extract_engagers` -> `enrich_apollo` -> `score_icp` ->
`dedup_history`. Every paid step has a degrade path; the Apify steps are cost-gated.

## When to use

- "Find leads from KOL/influencer audiences." / "Scrape engagers from influencer posts."
- After `kol-discovery`, or with a manual KOL list.

## Quick start with example configs

Ship-ready (strict) ICP configs live in `${SKILL_DIR}/configs/` — copy one and tune rather
than authoring from scratch (KOL audiences are broad, so these intentionally include hard
`exclude_titles` + `competitors` gates):

- **`configs/icp.b2b-saas-revops.json`** — RevOps / GTM buyers at B2B SaaS.
- **`configs/icp.devtools-eng-leaders.json`** — engineering leaders buying developer tooling /
  platform / DevOps.

```bash
cp ${SKILL_DIR}/configs/icp.b2b-saas-revops.json ${WORKSPACE}/icp.json   # then edit
# default Apify actors are pre-wired (see "Known-good actors"); --actor is optional
python3 ${SKILL_DIR}/scripts/select_kol_posts.py --kol-urls "<kol>" --topic-keywords "rpa,automation" --estimate-only
```

## Known-good actors

The Apify scripts ship sensible **public-marketplace defaults**, so `--actor` is optional.
They are swappable — pass `--actor <user~actor-name>` to use any actor whose input takes the
same fields. Defaults assume the [harvestapi](https://apify.com/harvestapi) LinkedIn actor
family (popular, public, no LinkedIn cookie required); verify current pricing on the actor's
Apify Store page (the script also reads live `pricePerUnitUsd` from the actor when available).

| Operation | Script | Default actor | Key input fields (what we send) |
|-----------|--------|---------------|---------------------------------|
| KOL profile-post discovery | `select_kol_posts.py` | `harvestapi~linkedin-profile-posts` | `profileUrls[]`, `maxPosts`, `limit` |
| Post reactions/comments extraction | `extract_engagers.py` | `harvestapi~linkedin-post-reactions` | `postUrls[]`, `--actor-post-field`, extra `--actor-input` |

Swap example: `--actor apimaestro~linkedin-post-reactions-comments-engagements`; output is
normalized identically regardless of source.

## How to run

### 1. Pick one topic-relevant post per KOL (`select_kol_posts.py`)

```bash
# Estimate Apify cost first (no spend)
python3 ${SKILL_DIR}/scripts/select_kol_posts.py \
  --kol-urls "https://linkedin.com/in/alice,https://linkedin.com/in/bob" \
  --topic-keywords "rpa,automation,workflow,orchestration" \
  --actor "harvestapi~linkedin-profile-posts" --estimate-only

# Confirm spend and pick (writes only posts that clear the topic-relevance gate)
python3 ${SKILL_DIR}/scripts/select_kol_posts.py \
  --kol-urls "https://linkedin.com/in/alice,https://linkedin.com/in/bob" \
  --topic-keywords "rpa,automation,workflow,orchestration" \
  --min-topic-hits 1 --days-back 30 \
  --actor "harvestapi~linkedin-profile-posts" --yes \
  --output ${WORKSPACE}/chosen_posts.json
```

Keyless degrade: gather a KOL's recent posts via web search (or hand them in) as a JSON list
and pass `--posts-file posts.json` instead of `--actor` — the same topic gate + ranking runs.

The output's `eligible:false` rows are KOLs whose recent posts were all off-topic — skip them.

### 2. Extract reactors + commenters (`extract_engagers.py`)

```bash
# Cost estimate for the chosen posts
python3 ${SKILL_DIR}/scripts/extract_engagers.py \
  --post-urls "<post1>,<post2>" \
  --kol-source "https://linkedin.com/in/alice" --post-topic "rpa, automation" \
  --actor "harvestapi~linkedin-post-reactions" --estimate-only

# Confirm and run (Apify primary)
python3 ${SKILL_DIR}/scripts/extract_engagers.py \
  --post-urls "<post1>,<post2>" \
  --kol-source "https://linkedin.com/in/alice" --post-topic "rpa, automation" \
  --actor "harvestapi~linkedin-post-reactions" --yes \
  --output ${WORKSPACE}/engagers.json
```

Run `extract_engagers.py` once per KOL so each batch is tagged with the right
`--kol-source` / `--post-topic`, then concatenate the JSON arrays.

Degrades (auto-selected when no Apify token, or force with `--source`):
- **PhantomBuster:** `--source phantombuster --engagers-agent-id "$PB_ENGAGERS_AGENT_ID"`
  (needs `PHANTOMBUSTER_API_KEY` + a LinkedIn cookie on the phantom).
- **Keyless Playwright:** `--source playwright` with `LI_AT` set. One-time setup:
  `cd ${SKILL_DIR}/scripts && npm install && npx playwright install chromium`. Scrapes both
  reactors and commenters (with comment text).

### 3. Enrich firmographics (`enrich_apollo.py`)

```bash
python3 ${SKILL_DIR}/scripts/enrich_apollo.py \
  --input ${WORKSPACE}/engagers.json --reveal-email \
  --output ${WORKSPACE}/enriched.json
```

Adds title/seniority/company/company_domain/company_size/industry (+ email with
`--reveal-email`) via a **two-phase Apollo** call: (A) org-resolve a bare company name to its
primary domain (cached per employer), then (B) People Match keyed by name **+ domain** for a
higher hit rate on broad KOL audiences. Without `APOLLO_API_KEY` it degrades to profile-only
(seeds `title` from the LinkedIn headline) so scoring still runs. Optional `DROPCONTACT_API_KEY`
gives an email fallback when Apollo reveals none. Enrichment costs credits — enrich the
engagers you actually intend to score, not every reaction (use `--limit`).

### 4. Score ICP fit + intent (`score_icp.py`)

```bash
cp ${SKILL_DIR}/configs/icp.b2b-saas-revops.json ${WORKSPACE}/icp.json   # or icp.devtools-eng-leaders / scripts/icp.example.json; then edit
python3 ${SKILL_DIR}/scripts/score_icp.py \
  --input ${WORKSPACE}/enriched.json --icp ${WORKSPACE}/icp.json \
  --output ${WORKSPACE}/scored.json
```

Deterministic 0-100 score = **ICP fit (0-60)** + **intent (0-25, comment>reaction x recency)**
+ **topic (0-15)**, with a `scoring_breakdown` per lead and tiers A/B/C. Hard gates force
tier C: competitor employer, an excluded title, or ICP fit below `--min-icp-fit`. By default
only tier A/B are written (`--keep-c` to keep all). Tune `--tier-a` / `--tier-b`.

### 5. Cross-run dedup (`dedup_history.py`)

```bash
python3 ${SKILL_DIR}/scripts/dedup_history.py \
  --input ${WORKSPACE}/scored.json \
  --history ${WORKSPACE}/kol_leads_seen.csv \
  --output ${WORKSPACE}/new_leads.json
```

Drops leads already seen in prior runs (same in-market people engage many KOLs), records the
survivors in the CSV ledger, and writes only the new ones. Add `--supabase-table kol_leads`
(with `SUPABASE_URL`/`SUPABASE_KEY`) for a shared multi-machine ledger.

### 6. Final review (you, the agent)

Read `new_leads.json` (tier A/B, each tagged with `kol_source` + `post_topic`), sanity-check
the top tier-A leads against the `scoring_breakdown`, and return the qualified table.

## Outputs

`new_leads.json` — `[{name, headline, title, seniority, company, company_domain,
company_size, industry, email?, profile_url, engagement_type, comment_text?, post_url,
kol_source, post_topic, icp_score, icp_tier, icp_gates, scoring_breakdown}]`, tier A/B,
deduplicated by normalized `profile_url` across the whole run history.

## Credentials / env

- **Required:** none. The keyless `--source playwright` + `LI_AT` path is the fallback
  engager source.
- **Optional:**
  - Engager source — if `APIFY_API_TOKEN` (or `PHANTOMBUSTER_API_KEY` + cookie) is set →
    managed actor (higher volume; cost-gated). If not → keyless Playwright (`--source
    playwright` + `LI_AT`).
  - `APOLLO_API_KEY` — two-phase enrichment (org-resolve + People Match); profile-only degrade
    without it.
  - `MILLIONVERIFIER_API_KEY` — `enrich_apollo.py --verify` deliverability; keyless syntax+MX
    check without it.
  - `DROPCONTACT_API_KEY` (email fallback); `PB_ENGAGERS_AGENT_ID`; `SUPABASE_URL` +
    `SUPABASE_KEY` (shared dedup ledger; degrades to the CSV ledger).

## Notes & edge cases

- **One post per KOL** is the hard cost lever — `select_kol_posts.py` enforces it; never
  scrape every post.
- **Topic-relevance gate** (`--min-topic-hits`) is what keeps a KOL's off-topic viral
  audience out of your funnel. Raise it for noisier KOLs.
- **Strict ICP tiering** is the whole point here: KOL audiences are broad, so default to
  surfacing only tier A/B and keep `--min-icp-fit` honest.
- **Cost gates:** both Apify steps refuse to spend without `--yes`; use `--estimate-only` to
  preview cost first.
- Every lead is **tagged** with the KOL and post topic it came from — keep that for
  personalized outreach ("saw you engaged with Alice's RPA post").
- Proxy + throttle the LinkedIn paths; dedup runs both intra-run (by `profile_url`) and
  cross-run (the ledger).
