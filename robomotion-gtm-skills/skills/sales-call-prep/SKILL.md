---
name: sales-call-prep
description: Pre-sales-call intelligence — reconstruct the full prior-interaction timeline (CRM + outreach + notes), deep-dive the company with a sales lens (pain/budget/competitive stack/decision process) and the person (authority, buying style, likely objections), then map your product to their situation to produce a complete call strategy: 30-second brief, talk track, discovery questions, objection prep, landmines. This answers "how do I sell to this person", not "who are they" (see meeting-brief).
metadata:
  version: 2.0.1
  category: research
  type: composite
---

# Sales Call Prep

Deterministic helpers pull CRM history + web pages; **you, the agent, reconstruct the
timeline, deep-dive company + person, map product-to-prospect, and write the call
strategy.** The prior-interaction line is the single most call-changing fact — always
check CRM + outreach before web research.

> **v2.0.0 — depth upgrade.** Adds `brief_scaffold.py` — a deterministic pre-call scaffold
> that classifies the prospect's **authority tier + buying role**, infers a **communication
> style + adaptation guidance**, predicts the **top objections with reframe stubs**, and
> emits the full **brief-section skeleton**. This SKILL.md carries the authority matrix, the
> communication-style matrix, the predicted-objection logic, and the brief skeleton.

## When to use

- "Prep me for my sales call", "call prep for [company]", "research [person] before our demo".
- Distinct from `meeting-brief`: this is "how do I sell to this person".

## How to run

### Step 1 — prior interactions (deterministic CRM read + agent)

```bash
python3 ${SKILL_DIR}/scripts/crm_history.py --crm hubspot \
  --company "Acme" --domain acme.com --output ${WORKSPACE}/history.json
```

Pulls the company's associated deals + contacts (HubSpot or Pipedrive) and sets
`has_prior_contact`. For Salesforce/Close or an outreach tool (`lemlist`/`instantly`
campaign, emails sent, their reply, lead category), read those APIs directly (agent-routed)
and merge. Build a chronological timeline; **never re-pitch someone who already replied;
acknowledge lost deals; multi-thread off colleagues.** If no CRM/outreach is configured,
state "true cold meeting" explicitly and run pure web research.

### Step 2 — company deep dive, sales lens (deterministic fetch + agent)

```bash
python3 ${SKILL_DIR}/scripts/fetch_url.py --url https://acme.com \
  --output ${WORKSPACE}/company.json
```

Across 7 dimensions: overview, financial/growth signals, pain/need indicators,
tech/competitive stack (mine job postings via your search tool), decision landscape,
relationship map, recent news (90d). Crunchbase/LinkedIn/job boards are JS/auth — route
via `web-automation` + Robomotion Proxy.

### Step 3 — person deep dive (deterministic scaffold + agent)

```bash
python3 ${SKILL_DIR}/scripts/brief_scaffold.py \
  --title "VP of Engineering" --company "Acme" --deal-stage evaluation \
  --has-prior-contact false --competitor "Incumbent X" --price-tier premium \
  --output ${WORKSPACE}/scaffold.json
```

Emits a deterministic `scaffold.json`: authority classification, communication style +
adaptation, predicted objections (ranked, with reframe stubs), and the brief skeleton. Then
add the researched substance — professional profile, what they care about (posts/content).
LinkedIn is anti-bot — prefer `phantombuster` (session cookie) or `web-automation` + proxy;
degrade to search snippets.

**Authority-classification matrix** (title cue → buying role → engagement strategy):

| Title cue | Buying role | How to engage |
|---|---|---|
| CEO / Founder / President / CxO | Economic Buyer | Lead with business outcome + ROI; strategic, short, peer-to-peer. |
| CFO / VP Finance / Controller | Economic Buyer (Finance) | Quantify ROI/payback up front; expect procurement rigor. |
| CTO / CIO / CISO / VP Eng/Product | Economic/Technical Buyer | Vision + technical credibility; map to a strategic initiative. |
| VP / Head of / Director / GM | Decision Maker | Owns functional budget; tie to their number; surface the path above. |
| Manager / Lead / Principal | Champion / Influencer | Arm them to sell up; find the economic buyer; hand them the business case. |
| Analyst / Specialist / Engineer (IC) | User / Evaluator | Win the technical eval; map to daily pain; ask who signs off. |

**Communication-style adaptation** (role family → style → how to adapt):

| Role family | Style | Adapt by |
|---|---|---|
| CEO/Founder/Sales/Revenue | Driver / Expressive | Outcome-first, big-picture, confident, concise; give them agenda control. |
| CFO/Finance/Procurement/Legal/Ops | Analytical | Precise, evidence-led, risk-aware; numbers + references; written follow-up. |
| CTO/Eng/Security/IT/Product | Analytical / Skeptical | Technical depth + honesty; no hype; offer a POC + concrete docs. |
| HR/People/Success/Marketing | Amiable / Expressive | Relationship-first; emphasize support, partnership, change-management. |

**Predicted-objection logic** — the scaffold ranks objections from context (competitor in
play → "we already use X"; premium price → "too expensive"; technical title → integration/
security; IC/manager → "not the decision-maker"; mid/late stage → "need to think"; cold →
"why are you reaching out"; always → status-quo). Each ships a reframe stub; you turn it into
acknowledge → reframe → proof, with a same-industry/size proof point.

### Step 4 — product-to-prospect mapping + strategy (you, the agent)

Connect genuine pain → your capability + proof (don't force-fit; never trash competitors).
Proof-point priority: same industry > same size > same problem > same competitor > general.
Write the full brief using the scaffold's `brief_skeleton` as the section list:

| # | Section | What goes in it |
|---|---|---|
| 1 | **30-Second Brief** | Who, why now, the one thing to accomplish, the opening line. |
| 2 | **Company Intelligence** | Overview · growth signals · pain indicators · tech/competitive stack · decision landscape · relationship map · 90d news. |
| 3 | **Prior Interactions** | CRM+outreach timeline + what it means for THIS call (never re-pitch a replier; acknowledge lost deals). State "cold" if none. |
| 4 | **Person Intelligence** | Profile · authority (scaffold) · what they care about · communication style (scaffold) · predicted objections (scaffold). |
| 5 | **Call Strategy** | Objective · agenda · opening line · prioritized discovery Qs · value points mapped to pain · next step. |
| 6 | **Objection Prep** | Top predicted objections → acknowledge / reframe / proof for each. |
| 7 | **Landmines** | What NOT to say/do: competitors not to trash, sore points, dead deals. |
| 8 | **After-the-Call** | Recap template + the specific commitment to secure. |

## Outputs

- A single pre-call document with all sections above. Workspace + Agent Teams channel attachment.

## Credentials / env

- **Required:** none for the core — `fetch_url.py` and `brief_scaffold.py` are keyless and the
  strategy synthesis is your job as the agent (no LLM key in the script layer).
- **Optional:** if a CRM key is set (`HUBSPOT_API_KEY` / `PIPEDRIVE_API_TOKEN`, or
  Salesforce/Close) → `crm_history.py` reconstructs the prior-interaction timeline; if not →
  keyless CSV/paste of past touches, else "cold meeting" + web research (default). If an
  outreach key is set (`LEMLIST_API_KEY` / `INSTANTLY_API_KEY`) → outreach history; if not →
  skip. If `PHANTOMBUSTER_API_KEY` + LinkedIn cookie are set → reliable person research; if
  not → keyless serp/fetch (default). `APIFY_API_TOKEN` — if set → their-product review
  scraping; if not → keyless fetch. Google Calendar MCP for calendar-driven mode.

## Notes & edge cases

- Always check CRM + outreach before web research — the prior-interaction line changes the call.
- Map only genuine pain→capability connections; differentiate on approach, don't trash competitors.
- `crm_history.py` matches by `--domain` first (more reliable), then `--company` name.
