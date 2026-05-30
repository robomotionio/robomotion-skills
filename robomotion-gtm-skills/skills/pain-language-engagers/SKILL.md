---
name: pain-language-engagers
description: Find warm leads by searching LinkedIn for pain-language posts — the frustrations and operational complaints your ICP voices publicly — then capturing the post AUTHOR (highest-intent: they voiced the pain) plus the reactors/commenters, enriching via Apollo, and scoring each with a deterministic pain×ICP×role fit/intent model. Targets people living with the problem, not people selling the solution. Use for "find leads complaining about X" / "LinkedIn pain-based prospecting."
metadata:
  version: 2.1.1
  category: lead-generation
  type: capability
---

# Pain-Language Engagers

Pain-based LinkedIn prospecting with rigorous **pain-vs-solution discipline**. You (the
agent) generate pain-language keywords from the product/pain intake; deterministic scripts
find posts EXPRESSING the pain, drop vendor/announcement/self-promo/hiring/listicle noise,
capture the **post author (highest intent) + engagers**, enrich them, and score each with a
**pain × ICP × role** model that weights authors above engagers and stronger pain matches
higher. Every lead is auditable: it carries `matched_pain_terms[]`, `role`, and a
`scoring_breakdown`.

## When to use

- "Find leads complaining about [problem]." / "Find people discussing problems we solve."
- "LinkedIn pain-based prospecting."

## Quick start with example configs

Ship-ready, tuned **pain-term sets** + a matching ICP live in `${SKILL_DIR}/configs/`. Each
pain set carries `pain_terms` (operator-voice complaints), a `pain_regex`, and an
`exclude_extra` lexicon (solution/announcement language to drop):

- **`configs/pain.ops-drudgery.json`** — Ops/RevOps drowning in manual, copy-paste,
  spreadsheet work.
- **`configs/pain.support-overwhelm.json`** — Support/CX leaders buried in ticket volume.
- **`configs/pain.data-quality.json`** — data/analytics owners fighting dirty, stale data.
- **`configs/icp.ops-finance-buyers.json`** — matching ICP (Ops/RevOps/Finance/Data buyers).

```bash
cfg=${SKILL_DIR}/configs/pain.ops-drudgery.json
# pain_terms / exclude_extra are JSON arrays — extract them for the script flags, e.g.:
python3 -c "import json;d=json.load(open('$cfg'));print(','.join(d['pain_terms']))" > /tmp/terms
python3 -c "import json;d=json.load(open('$cfg'));open('/tmp/excl','w').write('\n'.join(d['exclude_extra']))"
python3 ${SKILL_DIR}/scripts/search_pain_posts.py \
  --pain-terms "$(cat /tmp/terms)" \
  --pain-regex "$(python3 -c "import json;print(json.load(open('$cfg'))['pain_regex'])")" \
  --exclude-file /tmp/excl --output ${WORKSPACE}/posts.json
cp ${SKILL_DIR}/configs/icp.ops-finance-buyers.json ${WORKSPACE}/icp.json   # then tune
```

## Known-good actors

The Apify scripts ship sensible **public-marketplace defaults**, so `--actor` is optional
(also overridable via `APIFY_POST_SEARCH_ACTOR` / `APIFY_ENGAGEMENTS_ACTOR`). They are
swappable. Defaults assume the [harvestapi](https://apify.com/harvestapi) LinkedIn actor
family (popular, public, no LinkedIn cookie required); confirm current pricing on the actor's
Apify Store page. Both run **async with the in-flight `--max-cost-usd` abort gate**.

| Operation | Script | Default actor | Key input fields (what we send) |
|-----------|--------|---------------|---------------------------------|
| LinkedIn post search | `search_pain_posts.py` | `harvestapi~linkedin-post-search` | `searchQueries[]` / `query` / `search`, per-term limit |
| Post author + engagements extraction | `extract_engagers.py` | `harvestapi~linkedin-post-engagements` | `postUrls[]`, `--actor` overridable |

Swap example: `--actor apimaestro~linkedin-post-search-scraper` for the search step; output
is normalized + pain-filtered identically regardless of source.

## Pipeline (engager → qualified-lead engine)

```
search_pain_posts.py → extract_engagers.py → enrich_apollo.py → score_icp.py → dedup_history.py
   (pain-filtered)        (author+engagers)      (Apollo)         (pain×ICP×role)   (cross-run)
```

### Step 0 — generate keywords (you, the agent)

From `product_pain` (what you solve, who feels it, how they complain), generate ~15–25
**pain-language** phrases a frustrated operator would actually type — NOT solution/category
keywords (those attract builders/VCs). Also produce an ICP config and an optional pain
regex. Start from a **shipped tuned set** in `configs/` (`pain.ops-drudgery.json`,
`pain.support-overwhelm.json`, `pain.data-quality.json`, + `icp.ops-finance-buyers.json` —
see "Quick start with example configs"), or the lighter `scripts/pain_terms.example.json` /
`scripts/icp.example.json`.

### Step 1 — find pain posts (Apify, degrade web-search)

```bash
python3 ${SKILL_DIR}/scripts/search_pain_posts.py \
  --pain-terms "manual data entry,copy paste between systems,spreadsheet hell" \
  --pain-regex "still (doing|using).*(manually|by hand)" \
  --actor "harvestapi~linkedin-post-search" \
  --posts-per-term 10 --max-cost-usd 1.00 \
  --output ${WORKSPACE}/posts.json
```

Runs the Apify actor **async with poll + cost gate**, then applies `pain_filter.py`: keeps
posts matching pain terms/regex, drops "excited to announce", "we just launched", "proud
to", hiring posts, listicles, funding news. **No `APIFY_API_TOKEN`** → emits a keyless
`site:linkedin.com/posts` web-search plan you run, then re-filter with `pain_filter.py`.

### Step 2 — extract authors + engagers (Apify → PhantomBuster → Playwright)

```bash
python3 ${SKILL_DIR}/scripts/extract_engagers.py \
  --posts ${WORKSPACE}/posts.json --source auto \
  --actor "harvestapi~linkedin-post-engagements" --max-cost-usd 1.00 \
  --output ${WORKSPACE}/engagers.json
```

Captures the **author as a lead (`role=author`, highest intent — they wrote the pain)** plus
reactors/commenters (`role=engager`), deduped by profile URL. `--source auto` picks Apify
(`APIFY_API_TOKEN`) → PhantomBuster (`PHANTOMBUSTER_API_KEY` + `--engagers-agent-id`, LI_AT
on the phantom) → Playwright. The Playwright path emits a run plan for:

```bash
cd ${SKILL_DIR}/scripts && npm install && npx playwright install chromium
LI_AT="<li_at cookie>" node ${SKILL_DIR}/scripts/pb_engagers_pw.mjs \
  --post-urls "<pain post urls>" --output ${WORKSPACE}/reactors.json
```

(Playwright scrapes reactors only — merge each post's author back in per the plan.)

### Step 3 — enrich (Apollo, degrade profile-only)

```bash
python3 ${SKILL_DIR}/scripts/enrich_apollo.py \
  --input ${WORKSPACE}/engagers.json --limit 100 --output ${WORKSPACE}/enriched.json
```

**Two-phase Apollo** → (A) org-resolve a bare company name to its primary domain (cached per
employer), then (B) People Match keyed by name **+ domain** → `{title, seniority, company,
company_domain, company_size, industry, email?}` — domain seeding lifts the hit rate on
authors/engagers who arrive name + headline only. **No `APOLLO_API_KEY`** → leads pass
through profile-only (unenriched). Optional `DROPCONTACT_API_KEY` gives an email fallback when
Apollo reveals none.

### Step 4 — score (deterministic pain × ICP × role)

```bash
python3 ${SKILL_DIR}/scripts/score_icp.py \
  --input ${WORKSPACE}/enriched.json --icp ${SKILL_DIR}/configs/icp.ops-finance-buyers.json \
  --fit-weight 0.55 --intent-weight 0.45 --output ${WORKSPACE}/scored.json
```

0–100 score + tier A/B/C. Intent model: **author (+70) >> engager (+35)**, more
`matched_pain_terms` → higher, comment > reaction. Exclude-title / competitor = hard
disqualifier (fit 0). Emits `scoring_breakdown` per lead.

### Step 5 — cross-run dedup

```bash
python3 ${SKILL_DIR}/scripts/dedup_history.py \
  --input ${WORKSPACE}/scored.json --history ${WORKSPACE}/lead_history.csv \
  --run-id $(date +%F) --output ${WORKSPACE}/new_leads.json
```

Drops leads already surfaced in prior runs (workspace CSV; mirrors to Supabase when
`SUPABASE_URL`+`SUPABASE_KEY` set), appends survivors.

### Step 6 — final review (you, the agent)

Review `new_leads.json`: confirm each tier-A lead's `matched_pain_terms` + `role` justify
the score, draft pain-anchored outreach (quote their actual complaint), return the table.

## Outputs

`new_leads.json` — `[{name, headline, profile_url, role(author/engager), engagement_type,
comment_text?, post_url, matched_pain_terms[], title, seniority, company, company_domain,
company_size, industry, email?, fit_score, intent_score, score, tier, scoring_breakdown}]`,
deduped by profile URL within and across runs, sorted by score.

## Credentials / env

- **Required:** none. The keyless `pb_engagers_pw.mjs` Playwright + `LI_AT` path is the
  fallback extraction source.
- **Optional:**
  - Extraction — if `APIFY_API_TOKEN` (or `PHANTOMBUSTER_API_KEY` + cookie) is set → managed
    actors (cost-gated). If not → keyless Playwright + `LI_AT`.
  - `APOLLO_API_KEY` — two-phase enrichment (org-resolve + People Match); profile-only degrade
    without it.
  - `MILLIONVERIFIER_API_KEY` — `enrich_apollo.py --verify` deliverability; keyless syntax+MX
    check without it.
  - `DROPCONTACT_API_KEY` (email fallback); `APIFY_POST_SEARCH_ACTOR` /
    `APIFY_ENGAGEMENTS_ACTOR` (or `--actor`); `PB_ENGAGERS_AGENT_ID`; `SUPABASE_URL` +
    `SUPABASE_KEY` (dedup mirror; degrades to the CSV ledger).

## Notes & edge cases

- **Pain, not solution.** Every keyword is something a frustrated operator would type;
  `pain_filter.py` enforces it (run `--selftest`). The post AUTHOR is the strongest lead.
- **Cost gate.** Apify runs abort above `--max-cost-usd` (default 1.00); `<=0` refuses.
- Enrich only the title/role pre-ranked top N to control Apollo credits.
- Every lead is auditable: `matched_pain_terms[]` + `role` + `scoring_breakdown` on each row.
