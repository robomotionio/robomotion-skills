---
name: disqualification-handling
description: Handle disqualified and near-miss inbound leads gracefully — categorize each, draft the right response (polite decline, referral request, or nurture routing), and route to the correct destination so no inbound lead is ghosted and every disqualification preserves the relationship. Composite that reuses email-drafting and routes to a nurture/one-off send tool.
metadata:
  version: 1.0.1
  category: outreach
  type: composite
---

# Disqualification Handling

A composite: `categorize.py` **tags** each lead's handling category deterministically; the
**agent drafts** the right response per category (via `email-drafting`); then `launch_campaign.py`
**sends/routes** (one-off decline or nurture) — or stops at draft-only with no send key.

## When to use

- "Handle the disqualified leads" / "draft rejection emails" / "what do we do with the ones
  that didn't qualify?"
- After an inbound-lead-qualification step produces disqualified/near-miss leads.

## How it works (scripts + agent)

1. **Categorize** — `categorize.py` maps each lead's `sub_verdict` / `mismatch_type` to a
   handling category + action:
   - **referral** (right-company/wrong-person) -> referral ask (highest value)
   - **nurture** (close-but-not-quite) -> nurture sequence
   - **decline** (clearly outside ICP) -> polite decline + do-not-contact
   - **competitor** (competitor employee) -> LOG only, **NEVER email**
   - **existing_customer** -> route to CS/upsell, **never a decline**
2. **(agent)** For `referral`, pick the referral-target persona from ICP (or pull from CRM /
   Apollo if known). Draft the appropriate response per category with `email-drafting`,
   matching the configured tone; include a resource link if set.
3. **Route / send** — nurture -> `launch_campaign.py --tool lemlist/instantly`; one-off
   decline -> `--tool sendgrid/resend`; competitor/CS flags + do-not-contact -> store write +
   `slack` CS handoff (agent). Draft-only mode (no send key) just returns the drafts.

## How to run

```bash
# 1 — tag handling categories
python3 ${SKILL_DIR}/scripts/categorize.py \
  --input ${WORKSPACE}/disqualified.json --output ${WORKSPACE}/tagged.json

# 3 — send a one-off decline (only the 'decline' leads; agent drafts seq.json first)
python3 ${SKILL_DIR}/scripts/launch_campaign.py \
  --tool resend --campaign-name "polite declines" \
  --leads ${WORKSPACE}/declines.json --sequence ${WORKSPACE}/decline_msg.json

# nurture routing
python3 ${SKILL_DIR}/scripts/launch_campaign.py \
  --tool instantly --campaign-name "nurture" \
  --leads ${WORKSPACE}/nurture.json --sequence ${WORKSPACE}/nurture_seq.json
```

## Outputs

- `tagged.json` — each lead `{handling_category, handling_action, referral_target_persona}`,
  the agent's drafted responses per category, and the routing/send results; summary to channel.

## Credentials / env

- `env.required`: **none.** The default is draft-only (categorize + draft, no send), and
  `--tool generic_csv` exports a tool-ready CSV with no key.
- `env.optional` (all degrade): **Send/route — if a send key (`SENDGRID_API_KEY` /
  `RESEND_API_KEY` for one-off declines, `LEMLIST_API_KEY` / `INSTANTLY_API_KEY` for nurture)
  is set → send/route the response; else → draft-only or export a CSV** (`--tool generic_csv`,
  the keyless default). `HUBSPOT_API_KEY` — if set → CRM referral lookup + routing/tagging;
  else → manual. `APOLLO_API_KEY` — if set → find the referral contact; else → ICP persona
  only. `SUPABASE_URL` + `SUPABASE_SERVICE_ROLE_KEY` — if set → do-not-contact list /
  competitive-intel log; else → workspace CSV ledger.

## Notes & edge cases

- **NEVER** send a rejection to a competitor employee — log for competitive intelligence and stop.
- Existing customers are not disqualified — route to CS / upsell, never a decline email.
- Every decline must preserve the relationship; add declined leads to the do-not-contact list.
- Right-company/wrong-person is the highest-value path — a referral ask is warmer than cold.
