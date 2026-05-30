---
name: leadership-change-outreach
description: Across a list of companies, detect recent leadership changes (new VP+/C-suite hires and promotions), evaluate the new leader's relevance to the product, enrich their profile, and draft outreach to their new-role priorities — the most receptive buyers, re-evaluating everything in their first 90 days. Composite that hands off to cold-email-outreach or linkedin-outreach.
metadata:
  version: 1.0.1
  category: outreach
  type: composite
---

# Leadership Change Outreach

A composite built on **Apollo two-phase detection** (`leadership_scan.py`): free
people-search by domain + target titles, a strict local title post-filter, then
enrich-by-id for start dates + verified emails, keeping only recent movers. The **agent**
scores relevance and drafts. Without Apollo, degrade to keyless serp detection.

## When to use

- "Check for leadership changes" / "new executive hires" / "leadership signal outreach."
- A company list + an upstream monitor surfaces new leaders to act on.

## How it works (scripts + agent)

1. **Detect + enrich + change-detect** — `leadership_scan.py` runs the Apollo two-phase:
   search -> strict title post-filter (drops 50-60% noise before credits) -> `--enrich` for
   employment history / start_date / LinkedIn / verified email -> keep movers whose
   current-role `start_date` is within `--lookback-days`.
   **Degrade (no Apollo):** `detect_signal.py --signal general --extra "appointed OR joined
   OR promoted"` per company; the **agent** infers start dates from the evidence (lower
   precision, no verified email — flag inferred dates).
2. **(agent) Evaluate relevance** — buyer / champion / mandate fit; score + rank.
3. **(agent) Draft** sequences with `email-drafting` speaking to first-90-day priorities and
   quick wins — not the org's legacy stack (new leaders haven't formed vendor loyalty yet).
4. **Hand off** to `cold-email-outreach` / `linkedin-outreach`; request launch approval.

## How to run

```bash
# Apollo two-phase (primary)
python3 ${SKILL_DIR}/scripts/leadership_scan.py \
  --domains ${WORKSPACE}/companies.json \
  --titles "CMO,VP Marketing,Head of Growth" \
  --enrich --lookback-days 90 --output ${WORKSPACE}/movers.json

# Degrade (no Apollo) — keyless evidence for the agent to infer start dates
python3 ${SKILL_DIR}/scripts/detect_signal.py \
  --companies ${WORKSPACE}/companies.json --signal general \
  --extra "appointed OR joined OR promoted CMO" --extract \
  --output ${WORKSPACE}/leadership_evidence.json
```

## Outputs

- `movers.json` — `companies-with-leadership-changes` + enriched `new-leader-profiles`
  (employment history, start date, LinkedIn URL, verified email) — drafted sequences handed
  to the launch skill + review table.

## Credentials / env

- `env.required`: **none.** The no-Apollo degrade is keyless, drafting is the agent, and the
  launch step hands off to `cold-email-outreach` (CSV export with no key).
- `env.optional` (all degrade): `APOLLO_API_KEY` — if set → two-phase detection+enrichment
  (free search + 1 credit/person enrich); else → keyless serp/web-automation + LLM start-date
  inference + pattern-guess (no verified email). `MILLIONVERIFIER_API_KEY` — if set → verify;
  else → local syntax/dedup (bounce risk). **Send/launch — if a send key (`LEMLIST_API_KEY` /
  `INSTANTLY_API_KEY` / `SENDGRID_API_KEY` / `RESEND_API_KEY`, or `PHANTOMBUSTER_API_KEY` for
  LinkedIn) is set → launch the sequence; else → export a CSV to send manually** (the keyless
  default).

## Notes & edge cases

- Apollo free-search is fuzzy — the strict local title post-filter typically drops 50-60% of
  noise; keep it before spending enrichment credits.
- The signal is the *recent* start date — without a reliable one (no Apollo), confidence
  drops; flag inferred dates.
- Speak to mandate/quick-wins, not the legacy stack. Verify emails before send.
