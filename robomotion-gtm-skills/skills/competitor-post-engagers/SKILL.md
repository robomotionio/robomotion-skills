---
name: competitor-post-engagers
description: Turn the people who react to and comment on a COMPETITOR's LinkedIn posts into a tiered, qualified lead list. Engagers of a competitor's content are warm, category-aware buyers already evaluating the space. Discover the competitor's top recent posts, extract reactors/commenters (Apify -> PhantomBuster -> Playwright fallback, with a cost-confirm gate), dedup across runs, enrich the survivors via Apollo, then deterministically score each lead by ICP fit x engagement intent x recency into A/B/C tiers. Each lead is tagged with which competitor and which post they engaged.
metadata:
  version: 2.1.1
  category: lead-generation
  type: capability
---

# Competitor Post Engagers

Audience-capture prospecting against a competitor's content. The premise: someone who
likes or comments on a competitor's LinkedIn post is **in-market and category-aware** —
they're already evaluating this space. This skill converts that audience into a tiered
lead list, tagging each lead with the competitor and post they engaged.

It runs the shared **engager -> qualified-lead engine**:
discover posts -> extract engagers (cost gate) -> dedup -> enrich selected (cost gate) ->
score + tier -> export.

## When to use

- "Find leads engaging with [competitor]'s LinkedIn posts."
- "Who's commenting on [competitor]'s content — are any of them ICP?"
- Audience-capture prospecting against one or more competitor company/profile pages.

## Quick start with example configs

Ship-ready ICP configs live in `${SKILL_DIR}/configs/` — copy one and tune it instead of
authoring from scratch:

- **`configs/icp.b2b-saas-revops.json`** — RevOps / GTM buyers at mid-market B2B SaaS
  (heads/VPs of sales, RevOps, growth; 51–1000 employees; software/SaaS).
- **`configs/icp.devtools-eng-leaders.json`** — engineering decision-makers who buy
  developer tooling / platform / DevOps (CTO, VP/Head of Eng/Platform/DevOps; devtools
  keywords like kubernetes, ci/cd, observability).

```bash
cp ${SKILL_DIR}/configs/icp.b2b-saas-revops.json ${WORKSPACE}/icp.json   # then edit
# (default Apify actors are pre-wired — see "Known-good actors" below; no --actor needed)
python3 ${SKILL_DIR}/scripts/find_competitor_posts.py --profile-url "<competitor>" --estimate-only
```

## Known-good actors

The Apify scripts ship sensible **public-marketplace defaults**, so the agent does not have
to supply `--actor`. They are swappable — pass `--actor <user~actor-name>` (or set the env
var) to use any actor whose input takes the same fields. Defaults assume the
[harvestapi](https://apify.com/harvestapi) LinkedIn actor family (popular, public, no
LinkedIn cookie required); confirm current pricing on the actor's Apify Store page.

| Operation | Script | Default actor | Key input fields (what we send) |
|-----------|--------|---------------|---------------------------------|
| Post reactions/comments extraction | `extract_engagers.py` | `harvestapi~linkedin-post-reactions` | `postUrls[]` / `urls[]` / `posts[]`, `maxItems` |
| Profile/company post discovery | `find_competitor_posts.py` | `harvestapi~linkedin-profile-posts` | `profileUrls[]` / `urls[]`, `maxPosts`, `postedLimit` |

Swap example: `--actor apimaestro~linkedin-post-reactions-comments-engagements` (another
public reactions actor) — output is normalized the same way regardless of source.

## Setup

```bash
cd ${SKILL_DIR}/scripts && npm install && npx playwright install chromium   # only if you need the Playwright degrade
```

Python scripts are stdlib-only (no install). At least ONE extraction path must be
configured — see Credentials / env.

## Workflow

### Step 0 — define your ICP + competitors (you, the agent)

Copy a shipped ICP — `${SKILL_DIR}/configs/icp.b2b-saas-revops.json` or
`icp.devtools-eng-leaders.json` (or the minimal `${SKILL_DIR}/scripts/icp.example.json`) —
to `${WORKSPACE}/icp.json` and edit it for the target ICP (titles, seniorities, employee
ranges, industries, keywords, exclusions). List the competitor LinkedIn company/profile URLs
you want to mine.

### Step 1 — discover recent competitor posts

```bash
python3 ${SKILL_DIR}/scripts/find_competitor_posts.py \
  --profile-url "https://linkedin.com/company/acme" \
  --competitor "Acme" --days-back 30 --top-n 3 \
  --estimate-only                       # prints projected Apify cost, no spend
# happy with the cost? re-run with --yes:
python3 ${SKILL_DIR}/scripts/find_competitor_posts.py \
  --profile-url "https://linkedin.com/company/acme" \
  --competitor "Acme" --days-back 30 --top-n 3 \
  --yes --output ${WORKSPACE}/acme_posts.json
```

Ranks the competitor's recent posts by engagement and keeps the top N (cost control — you
only mine the posts with the biggest audiences). With no `APIFY_API_TOKEN` it degrades to
printing a web-search query you run with your own search tool to find the post URLs by hand.

### Step 2 — extract engagers (COST GATE)

```bash
# Estimate first (no spend, no --yes):
python3 ${SKILL_DIR}/scripts/extract_engagers.py \
  --source apify \
  --post-urls "https://linkedin.com/posts/...,https://linkedin.com/posts/..." \
  --competitor "Acme" --estimate-only

# Confirm the spend with --yes:
python3 ${SKILL_DIR}/scripts/extract_engagers.py \
  --source apify \
  --post-urls "https://linkedin.com/posts/...,https://linkedin.com/posts/..." \
  --competitor "Acme" --yes \
  --output ${WORKSPACE}/acme_engagers.json
```

`extract_engagers.py` pulls reactors + commenters and tags every row with the competitor
and source post. Multi-source fallback (use `--source`):

- **`apify`** (default, `APIFY_API_TOKEN`) — managed actor with async run + poll and the
  cost-confirm gate (`--estimate-only` / `--yes`). Configure the actor with `--actor`
  (default a harvestapi-style reactions/comments actor).
- **`phantombuster`** (`PHANTOMBUSTER_API_KEY` + LinkedIn cookie on the phantom, pass
  `--engagers-agent-id`).
- **`playwright`** (`LI_AT` cookie) — keyless local-browser degrade, lowest volume.

Output rows: `{name, headline, profile_url, engagement_type, comment_text?, post_url,
competitor, source}`.

### Step 3 — dedup across runs (credit saver)

```bash
python3 ${SKILL_DIR}/scripts/dedup_history.py \
  --input ${WORKSPACE}/acme_engagers.json \
  --history ${WORKSPACE}/engager_history.csv \
  --output ${WORKSPACE}/new_engagers.json
```

Drops anyone already processed in a prior run (workspace CSV; mirrors to Supabase if
`SUPABASE_URL`/`SUPABASE_KEY` are set). Run this BEFORE enrichment so Apollo credits are
only spent on net-new people. Use `--dry-run` to preview the net-new count.

### Step 4 — select, then enrich the survivors (COST GATE)

Read `new_engagers.json` and **select the ones worth enriching** (the engine scores
everyone, but you control who gets Apollo credits — e.g. skip obvious non-fits by headline).
Then:

```bash
python3 ${SKILL_DIR}/scripts/enrich_apollo.py \
  --input ${WORKSPACE}/new_engagers.json \
  --limit 50 --reveal-email \
  --output ${WORKSPACE}/enriched.json
```

Resolves `{title, seniority, company, company_domain, company_size, industry, email?}` via a
**two-phase Apollo** call: (A) if a row has a company name but no domain, resolve the Apollo
organization to a primary domain (cached per company), then (B) People Match keyed by
name **+ domain** for a higher hit rate (engagers usually arrive name + headline only). With
no `APOLLO_API_KEY` it passes through profile-only (no spend, no error) so the scorer still
runs. Optional email fallback: set `DROPCONTACT_API_KEY` to guess an email from domain + name
when Apollo returns none (used only with `--reveal-email`).

### Step 5 — score + tier (deterministic)

```bash
python3 ${SKILL_DIR}/scripts/score_icp.py \
  --input ${WORKSPACE}/enriched.json \
  --icp ${WORKSPACE}/icp.json \
  --output ${WORKSPACE}/scored.json
```

Computes a 0-100 score = `fit_weight*FIT + intent_weight*INTENT` (defaults 0.6/0.4) and an
A/B/C tier. **FIT** = firmographic match to your ICP; **INTENT** = engagement-type weight
(a comment >> a like) x post recency. Every lead carries a `scoring_breakdown` for audit.
Tune `--tier-a` / `--tier-b` / `--half-life-days` / weights as needed.

### Step 6 — final review + export (you, the agent)

Read `scored.json`. Do the qualitative pass the scorer can't: read `comment_text` (is the
comment a buying signal or a throwaway emoji?), sanity-check tier-A leads, demote false
positives. Then export:

```bash
python3 ${SKILL_DIR}/scripts/export_csv.py \
  --input ${WORKSPACE}/scored.json --min-tier B \
  --output ${WORKSPACE}/competitor_engagers.csv
```

Hand the CSV to the user, import into `contact-cache`, push to a channel, or persist to
Airtable/Supabase.

## Outputs

- `*_posts.json` — top competitor posts by engagement.
- `*_engagers.json` — raw reactors/commenters, tagged with competitor + source post.
- `new_engagers.json` — net-new engagers after cross-run dedup.
- `enriched.json` — net-new engagers with firmographics (+ email if revealed).
- `scored.json` — every lead with `icp_score`, `tier`, and `scoring_breakdown`.
- `competitor_engagers.csv` — flat export, optionally tier-filtered.

## Credentials / env

A LinkedIn engager source is the hard gate — provide **at least one** of:

- **`APIFY_API_TOKEN`** (optional but the primary path) — managed actors for both post
  discovery and engager extraction, with the cost-confirm gate.
- **`PHANTOMBUSTER_API_KEY`** (+ LinkedIn session cookie on the phantom; pass
  `--engagers-agent-id`) — `--source phantombuster`.
- **`LI_AT`** (LinkedIn `li_at` cookie) — keyless `--source playwright` degrade.

Optional enrichment / state:

- **`APOLLO_API_KEY`** — two-phase Apollo enrichment (org-resolve + People Match); without
  it, profile-only pass-through.
- **`MILLIONVERIFIER_API_KEY`** — `enrich_apollo.py --verify` email deliverability; without
  it, a keyless syntax + MX-record check.
- **`DROPCONTACT_API_KEY`** — optional email fallback when Apollo reveals no email.
- **`SUPABASE_URL` / `SUPABASE_KEY`** — mirror cross-run dedup history to Supabase (degrades
  to the CSV ledger).

## Notes & edge cases

- **Engagers of a competitor are warm, category-aware leads** — they're evaluating the
  category right now. Each lead is tagged with which competitor + which post they engaged so
  outreach can reference it.
- **Cost discipline:** discovery and extraction both refuse to spend without `--yes`
  (`--estimate-only` prints the projection first); dedup runs before enrichment; you select
  who gets enriched. Never extract one call per post blindly — discover, rank, mine the top N.
- **Intent > volume:** a thoughtful comment outscores a passive like; a fresh post outscores
  a stale one. That's the `engagement_type x recency` intent half of the score.
- Apify/PhantomBuster may cap reactions/comments on high-virality posts — note partial
  coverage. Pair scraping with a proxy + throttle; LinkedIn anti-bot is aggressive at
  engager-list depth.
- The Playwright degrade is best-effort DOM scraping — expect lower coverage and missing
  headlines/locations; rely on Apollo enrichment to backfill firmographics.
