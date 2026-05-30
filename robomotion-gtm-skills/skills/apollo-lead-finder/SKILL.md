---
name: apollo-lead-finder
description: Two-phase Apollo.io prospecting — run a free People Search to discover ICP-matching leads, then enrich only the best matches to reveal verified emails/phones. Use to build SDR prospect lists from an ICP (titles, seniority, company size, geo, industry) while spending Apollo credits only on ranked winners.
metadata:
  version: 1.0.1
  category: lead-generation
  type: capability
---

# Apollo Lead Finder

Two-phase prospecting that keeps the **free-search / paid-enrich boundary strict**:
discover broadly for free, enrich narrowly for credits. Apollo is **optional**: with a
key you get the recommended, higher-quality path; without one the skill degrades to a
keyless LinkedIn-profile discovery + email pattern-guess and still produces leads.

## When to use

- "Find VPs of Sales at US mid-market SaaS companies and get their emails."
- Any prospecting where Apollo's filter taxonomy (titles, seniority, employee range,
  geo, industry tags) expresses the ICP.

## Workflow

### Phase 1 — discover (free, no credits)

```bash
python3 ${SKILL_DIR}/scripts/apollo_search.py \
  --titles "VP of Sales,Head of Sales" \
  --seniorities vp,director \
  --employee-ranges "51,200" "201,500" \
  --locations "United States" \
  --keyword-tags saas \
  --exclude-titles "assistant,intern" \
  --num-results 1000 \
  --existing ${WORKSPACE}/known_contacts.csv \
  --output ${WORKSPACE}/discovery.json
```

Returns name, title, company, LinkedIn URL, location. Emails are **not** revealed yet.
`--existing` dedups against a CSV of contacts you already have (by normalized LinkedIn
URL) so you never spend credits re-enriching known people.

**Keyless degrade (no `APOLLO_API_KEY`):** run `serp_search.py` instead — it discovers
LinkedIn profiles via a keyless web search and returns the same record shape (name/title/
company/linkedin_url, email blank). Lower precision/coverage than Apollo; the agent
resolves name/company from `result_title`/`snippet`.

```bash
python3 ${SKILL_DIR}/scripts/serp_search.py \
  --titles "VP of Sales,Head of Sales" --keyword-tags saas \
  --locations "United States" --num-results 50 \
  --existing ${WORKSPACE}/known_contacts.csv --output ${WORKSPACE}/discovery.json
```

### Step 2 — rank & select (you, the agent)

Read `discovery.json` and **select only the best-fit winners** to enrich — score by
title match, seniority, company fit, and ICP signals. Write the winners to
`winners.json`. This selection is the credit-saving step; do not enrich the whole set.

### Phase 2 — enrich winners (costs credits)

```bash
python3 ${SKILL_DIR}/scripts/apollo_enrich.py \
  --input ${WORKSPACE}/winners.json \
  --limit 50 \
  --verify \
  --output ${WORKSPACE}/enriched.json
```

Reveals verified email/phone for the selected subset. **Keyless degrade (no
`APOLLO_API_KEY`):** `apollo_enrich.py` pattern-guesses an email from name + company
domain (`first.last@domain`) and MX-checks it — `email_status: guessed`, no phone, lower
confidence. `--verify` uses MillionVerifier when `MILLIONVERIFIER_API_KEY` is set, else a
keyless syntax + MX-record check (`ok_syntax_mx` / `no_mx` / `invalid_syntax`).

### Step 4 — export

Deliver `enriched.json` as a table to the user and persist it (workspace file or
Agent Teams channel attachment; optionally a `contact-cache`/Airtable/Supabase store).

## Outputs

- `discovery.json` — full free discovery set.
- `enriched.json` — selected subset with `email`, `phone`, `email_status`, and (if
  `--verify`) `email_verification`.

## Credentials / env

- **Required:** none. The skill runs keyless via `serp_search.py` (discovery) +
  `apollo_enrich.py`'s pattern-guess (email).
- **Optional:**
  - `APOLLO_API_KEY` — if set → Apollo People Search + verified People Match enrichment
    (better quality/coverage, verified email + phone). If not → keyless serp discovery +
    email pattern-guess (default).
  - `MILLIONVERIFIER_API_KEY` — if set → MillionVerifier deliverability. If not → keyless
    syntax + MX-record check.
  - `DROPCONTACT_API_KEY` — email-finding fallback for contacts Apollo can't email.

## Notes & edge cases

- Strict two-phase split: **never** enrich the full discovery set — only ranked winners.
- Dedup (Phase 1 `--existing`) **before** enrich so credits are never spent on known contacts.
- Apollo paginates 100/page; the script caps at `--num-results` and backs off on 429.
- Contacts Apollo can't email come back with `email: ""` (LinkedIn URL preserved), not dropped.
- Keyless path: pattern-guessed emails are best-effort (mark them `guessed`); verify before
  sending, and prefer the Apollo path when deliverability matters.
