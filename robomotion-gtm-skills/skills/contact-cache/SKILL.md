---
name: contact-cache
description: A persistent contact database that tracks every person identified or contacted across prospecting strategies, deduplicated by LinkedIn URL or email, so recurring strategies never re-target the same person. Also tracks outreach status through the funnel. The dedup backbone for the event and signal pipelines.
metadata:
  version: 1.0.1
  category: lead-generation
  type: capability
---

# Contact Cache

Check before outreach, add after prospecting. Deduplicates by normalized LinkedIn URL
(priority) then email, with a stable `contact_id` hash, and tracks funnel status. **Default
backend is a workspace CSV ledger** (keyless, runs anywhere); set Supabase env to upgrade to
durable cross-run dedup. Supabase is optional.

## When to use

- Before outreach on any new lead batch: check who's already known/contacted.
- After any prospecting run: add the new contacts with their source strategy.
- "Have we already reached out to these people?" / "Export everyone we've contacted."

## How to run

All ops share `--store <csv>` (used only when Supabase env is unset).

```bash
# check — partition input into known vs new
python3 ${SKILL_DIR}/scripts/contact_cache.py --store ${WORKSPACE}/contacts.csv \
  check --linkedin-urls "https://linkedin.com/in/a,https://linkedin.com/in/b"

# add — upsert a batch from CSV with a strategy tag (skips dupes)
python3 ${SKILL_DIR}/scripts/contact_cache.py --store ${WORKSPACE}/contacts.csv \
  add --csv ${WORKSPACE}/new_leads.csv --strategy luma

# add a single JSON contact
python3 ${SKILL_DIR}/scripts/contact_cache.py --store ${WORKSPACE}/contacts.csv \
  add --contact-json '{"name":"A","linkedin_url":"https://linkedin.com/in/a"}' --strategy events

# update — set funnel status / notes (by LinkedIn URL or email)
python3 ${SKILL_DIR}/scripts/contact_cache.py --store ${WORKSPACE}/contacts.csv \
  update --email a@x.com --status contacted --notes "sent intro"

# export / stats
python3 ${SKILL_DIR}/scripts/contact_cache.py --store ${WORKSPACE}/contacts.csv \
  export --filter-status qualified --format csv
python3 ${SKILL_DIR}/scripts/contact_cache.py --store ${WORKSPACE}/contacts.csv stats
```

Valid statuses: `new → qualified → contacted → replied → meeting_booked →
converted | not_interested`. Unknown statuses are rejected. Set
`CONTACT_CACHE_TABLE` to override the Supabase table name (default `contacts`).

## Outputs

- `check` → `{known, new, known_count, new_count}` partition.
- `add` → `{inserted, skipped, backend}`.
- `update` → `{contact_id, updated, patch}`.
- `export` → CSV/JSON of contacts (optionally filtered).
- `stats` → `{total, by_status, by_strategy}`.

## Credentials / env

- **Required:** none. The default backend is the `--store <csv>` workspace ledger (keyless).
- **Optional:**
  - `SUPABASE_URL` + `SUPABASE_SERVICE_ROLE_KEY` — if set → durable Supabase REST store with
    cross-run dedup (recommended for recurring pipelines). If not → workspace CSV ledger
    (default; dedup is per-store-file, durable as long as you reuse the same `--store` path).
  - `CONTACT_CACHE_TABLE` — Supabase table name override (default `contacts`).

## Notes & edge cases

- Dedup priority: LinkedIn URL first, then email; both normalized before hashing.
- Idempotent upserts — re-adding a known contact refreshes strategy/source, never duplicates.
- Restrict status to the valid set; unknown statuses are rejected.
- This is the dedup backbone for `event-prospecting-pipeline` and `signal-detection-pipeline`.
- **Degrade:** without Supabase env, the script uses the `--store` CSV (or
  `contact_cache.csv` in CWD) and prints a non-durability warning.
