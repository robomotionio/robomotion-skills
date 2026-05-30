---
name: expansion-signal-spotter
description: Find expansion revenue inside the existing customer base by monitoring accounts for upsell/cross-sell signals — team growth, new job postings, funding, champion promotions, usage pressure, public news — and produce a weekly opportunity list with context and talk tracks. Multi-signal accounts rank highest.
metadata:
  version: 1.0.0
  category: lead-generation
  type: composite
---

# Expansion Signal Spotter

A weekly scan over a customer account list. The keyless sweep + sub-skill signal sources are
deterministic; signal aggregation, the expansion play, and the talk track are the agent's.

## When to use

- "Which customers are ready to expand?" / "Find upsell opportunities in our accounts."
- "Run the weekly expansion signal scan." / "Who should I pitch [new tier] to?"

## How to run

### Step 1 — filter accounts + keyless web sweep

```bash
python3 ${SKILL_DIR}/scripts/account_signals.py \
  --accounts ${WORKSPACE}/accounts.csv \
  --min-account-value 1000 \
  --exclude "ChurnCo,PausedInc" \
  --output ${WORKSPACE}/signals.json
```

Filters by min value / exclusions up front (exclude churn-risk/paused/disputed accounts to
keep the list actionable), then sweeps each account for hiring, leadership-change, and
public-news hits.

### Step 2 — add job + funding signals (sub-skills)

For each account, run `job-posting-intent` / `job-scraper` over the account domain (new
relevant roles) and `funding-signal-monitor` (funding announcement). Use
`PHANTOMBUSTER_API_KEY` (+ cookie) to monitor `key_contacts` profiles for promotions if
available. Merge these into each account's `signal_stack`.

### Step 3 — aggregate + write plays (you, the agent)

Aggregate signals per account; **multi-signal accounts rank highest**. Per opportunity, fill
`signal_stack`, `expansion_play`, `talk_track`, and `rank`. Render the weekly list and
persist (store prior-week snapshots so "new since last scan" is computable; degrade to a
single scan if no durable store).

## Outputs

`signals.json` — `[{company, domain, tier, account_value, primary_contact_linkedin,
web_signals{hiring,leadership,news}, signal_stack, expansion_play, talk_track, rank}]`.

## Credentials / env

- **Required:** none — the serp backbone runs keyless.
- **Optional:** `APIFY_API_TOKEN` (job-posting/LinkedIn-scale signals);
  `PHANTOMBUSTER_API_KEY` + cookie (LinkedIn profile monitoring of key contacts);
  `SUPABASE_URL` + `SUPABASE_SERVICE_ROLE_KEY` or an Airtable key (week-over-week history —
  degrades to a single scan); `ANTHROPIC_API_KEY` only if the talk-track LLM isn't
  platform-provided.

## Notes & edge cases

- Multi-signal accounts are the strongest — weight them above single-signal hits.
- Store prior-week snapshots so "new since last scan" is computable; degrade to a single scan
  without a durable store.
- Proxy + throttle LinkedIn; respect Apify costs (optional).
- Exclude churn-risk/paused/disputed accounts up front (the `--exclude` filter).
