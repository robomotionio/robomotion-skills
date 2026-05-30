---
name: champion-move-outreach
description: Track known buyers, champions, and power users for job changes; when one moves to a new company, qualify the new company against ICP and draft warm, relationship-led outreach. The highest-conversion outbound signal — these people already trust the product. Composite that hands off to cold-email-outreach or linkedin-outreach.
metadata:
  version: 1.0.1
  category: outreach
  type: composite
---

# Champion Move Outreach

A composite: **scripts detect moves**, **research the new company**, and **re-find the new
email**; the **agent qualifies the new company, picks the approach, and drafts warm,
relationship-led copy**. This is NOT cold email — reference the real prior relationship.

## When to use

- "Track my champions" / "check for job changes" / "who moved from our customer accounts?"
- A list of past buyers/users exists and you want to know who changed jobs.

## How it works (scripts + agent)

1. **Detect moves** — `detect_moves.py` resolves each tracked person's current company/title
   (Apollo people-match if `APOLLO_API_KEY` set; else keyless serp evidence) and flags those
   whose current company differs from `last_known_company` (+ a promotion heuristic).
2. **Research the new company** — `detect_signal.py --signal general` (or `--signal funding`/
   `news`) on the mover's new company for what it does, size, funding, news. **(agent)**
   summarize.
3. **(agent) Qualify** the new company against ICP hard filters + assess the person's new
   authority; pick the approach (re-sell / upgrade / lateral / bottom-up / fresh-start);
   tier 1-3.
4. **Re-find the new email** — `find_contacts.py` against the new domain (their old email is
   stale); `--enrich --verify`. No email -> route to LinkedIn.
5. **(agent) Draft** warm sequences with `email-drafting` (Relationship-Context-Ask; the one
   place "do reference how you know them" applies). Shorter, spaced day 1/7/14.
6. **Hand off** — email contacts -> `cold-email-outreach`; LinkedIn-only -> `linkedin-outreach`;
   very close contacts -> personal/founder touch (skip automation), `slack` approval.

## How to run

```bash
# 1 — detect job changes among tracked champions
python3 ${SKILL_DIR}/scripts/detect_moves.py \
  --people ${WORKSPACE}/champions.json --output ${WORKSPACE}/movers.json

# 2 — research a mover's new company
python3 ${SKILL_DIR}/scripts/detect_signal.py \
  --companies ${WORKSPACE}/new_companies.json --signal general \
  --extra "company overview" --extract --output ${WORKSPACE}/newco_research.json

# 4 — re-find + verify the new work email at the new domain
python3 ${SKILL_DIR}/scripts/find_contacts.py \
  --domains ${WORKSPACE}/new_companies.json --titles "their new title" \
  --enrich --verify --output ${WORKSPACE}/new_contacts.json
```

## Outputs

- `movers.json` (`movers-with-icp-fit` after the agent qualifies), `newco_research.json`,
  `new_contacts.json`, warm drafted sequences (email + LinkedIn split) — handed to the launch
  skill + review table.

## Credentials / env

- `env.required`: **none.** Serp detection/research is keyless, drafting is the agent, and the
  launch step hands off to `cold-email-outreach` (CSV export with no key).
- `env.optional` (all degrade): `APOLLO_API_KEY` — if set → job-change detection + new-email
  find; else → keyless serp evidence + pattern-guess. `DROPCONTACT_API_KEY` — email-finding
  fallback. `MILLIONVERIFIER_API_KEY` — if set → verify; else → local syntax/dedup (bounce
  risk). **Send/launch — if a send key (`LEMLIST_API_KEY` / `INSTANTLY_API_KEY` /
  `SENDGRID_API_KEY` / `RESEND_API_KEY`, or `PHANTOMBUSTER_API_KEY` for LinkedIn) is set →
  launch the sequence; else → export a CSV to send manually** (the keyless default).

## Notes & edge cases

- Run monthly, not daily — moves take time; the first 30 days in-role is the optimal window
  (promotions are the strongest sub-signal). Keep the tracked list fresh.
- This is NOT cold email — reference the relationship explicitly (the allowed exception to
  "never lie about how you found them"). Don't be pushy.
- LinkedIn often beats email here; for very close contacts, skip automation and route to a
  personal touch.
- Their old email is stale — always re-find + verify the new-company address before send.
