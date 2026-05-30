#!/usr/bin/env python3
"""brief_scaffold.py — deterministic pre-call scaffolding the agent fills in.

NO LLM, no I/O to the web. Takes the few facts the agent already knows about the prospect
(title, seniority hints, deal context, their tech stack / competitor in play) and emits a
structured scaffold: an authority classification, a communication-style profile, a ranked
list of PREDICTED objections (with a suggested reframe stub), and the full brief-section
skeleton the agent then fills with researched content.

This keeps the *classification logic* deterministic and inspectable (title->authority,
title->style, context->likely-objections) while the agent supplies all the researched
substance and final wording.

Example:
  brief_scaffold.py --title "VP of Engineering" --company "Acme" \
    --deal-stage "evaluation" --has-prior-contact true \
    --competitor "Incumbent X" --price-tier premium \
    --output scaffold.json
"""
import argparse
import json
import sys

# ---- Authority classification matrix: title cue -> {tier, buying_role, strategy} ----
AUTHORITY_MATRIX = [
    # (keywords, tier, buying_role, engagement_strategy)
    (("ceo", "founder", "owner", "president", "managing director", "cxo"),
     "economic_buyer", "Economic Buyer",
     "Lead with business outcome + ROI; keep it strategic, short, peer-to-peer. Get the metric that matters to THEM."),
    (("cfo", "vp finance", "controller", "head of finance"),
     "economic_buyer", "Economic Buyer (Finance)",
     "Quantify cost/ROI/payback up front; have the business case ready; expect procurement rigor."),
    (("cto", "cio", "ciso", "vp eng", "vp engineering", "vp product", "chief"),
     "economic_buyer", "Economic/Technical Buyer",
     "Balance vision + technical credibility; map to a strategic initiative; respect their time."),
    (("vp", "head of", "director", "gm", "general manager"),
     "decision_maker", "Decision Maker",
     "They likely own budget for their function. Tie to their team's number; surface the approval path above them."),
    (("manager", "lead", "team lead", "principal"),
     "champion", "Champion / Influencer",
     "Arm them to sell internally. Find the economic buyer; give them the business case to forward up."),
    (("analyst", "specialist", "coordinator", "associate", "engineer", "ic", "individual contributor"),
     "user_evaluator", "User / Evaluator",
     "Win the technical/usage evaluation; map to their daily pain; ask who signs off and who else evaluates."),
]

# ---- Communication-style profile: role family -> style + adaptation guidance ----
STYLE_MATRIX = [
    (("ceo", "founder", "vp sales", "vp marketing", "chief revenue", "cro", "sales"),
     "Driver / Expressive",
     "Fast, outcome-first, big-picture. Open with the result, not the process. Be confident and concise; "
     "give them control of the agenda; avoid feature deep-dives unless asked."),
    (("cfo", "finance", "controller", "procurement", "legal", "ops", "operations"),
     "Analytical",
     "Precise, evidence-led, risk-aware. Bring numbers, references, and a clear process. Don't oversell; "
     "acknowledge risks and how you de-risk them. Send a written follow-up they can scrutinize."),
    (("cto", "cio", "engineer", "developer", "architect", "security", "it", "technical", "product"),
     "Analytical / Skeptical",
     "Technical depth + honesty. Respect their expertise; avoid hype; be specific about how it works, "
     "integration, security. Offer a trial/POC and concrete docs."),
    (("hr", "people", "success", "support", "community", "enablement", "marketing"),
     "Amiable / Expressive",
     "Relationship-first, collaborative. Establish rapport; emphasize support, partnership, change-management; "
     "show how you make THEIR life and their team's life easier."),
]
DEFAULT_STYLE = ("Balanced",
                 "No strong style read from title — open with a quick rapport check, then mirror their pace and "
                 "depth. Ask an open discovery question early to calibrate.")

# ---- Predicted-objection logic: context flag -> objection + reframe stub ----
# Each tuple: (predicate(args) -> bool, objection, suggested_reframe_stub)
def objection_rules(a):
    out = []
    title_l = (a.title or "").lower()
    if a.competitor:
        out.append({
            "objection": f"We already use {a.competitor}.",
            "reframe_stub": ("Don't trash them. Ask what's working and what isn't; position on the specific "
                             "gap/approach difference, not feature-for-feature. Proof: a customer who switched "
                             "from a similar incumbent."),
            "priority": "high"})
    if a.price_tier in ("premium", "high"):
        out.append({
            "objection": "It's too expensive / no budget.",
            "reframe_stub": ("Reframe price as ROI/cost-of-inaction. Quantify the pain they admitted in discovery. "
                             "Anchor against the cost of the status quo, not against a cheaper tool."),
            "priority": "high"})
    if any(k in title_l for k in ("cto", "cio", "engineer", "architect", "security", "it")):
        out.append({
            "objection": "Concerns about integration / security / implementation lift.",
            "reframe_stub": ("Have integration + security specifics ready (SOC2, SSO, API). Offer a scoped POC. "
                             "Cite a similar-stack customer who implemented quickly."),
            "priority": "high" if a.deal_stage in ("evaluation", "proposal", "technical") else "medium"})
    if any(k in title_l for k in ("manager", "lead", "specialist", "analyst", "ic")):
        out.append({
            "objection": "I'm not the decision-maker / need to check with my boss.",
            "reframe_stub": ("Treat them as a champion. Ask who owns budget and the decision process; offer to "
                             "build the business case they can forward; propose a multi-thread next step."),
            "priority": "high"})
    if a.deal_stage in ("proposal", "negotiation", "evaluation"):
        out.append({
            "objection": "We need to think about it / not the right time.",
            "reframe_stub": ("Surface the real blocker — usually risk, priority, or a missing stakeholder. Tie to "
                             "their stated timeline/metric; propose a small, low-risk next step to keep momentum."),
            "priority": "medium"})
    if not a.has_prior_contact:
        out.append({
            "objection": "Why are you reaching out / what is this about? (cold)",
            "reframe_stub": ("Lead with a relevant trigger/insight specific to them, not a generic pitch. Earn the "
                             "next 30 seconds before asking for anything."),
            "priority": "medium"})
    # always include the universal status-quo objection last
    out.append({
        "objection": "We're fine with how we do it today (status quo / do nothing).",
        "reframe_stub": ("Quantify the cost of the status quo using a pain they named. Don't argue; make the "
                         "do-nothing path feel more expensive/risky than acting."),
        "priority": "medium"})
    # de-dup by objection text, preserve order, high-priority first
    seen, dedup = set(), []
    for o in out:
        if o["objection"] not in seen:
            seen.add(o["objection"])
            dedup.append(o)
    dedup.sort(key=lambda o: 0 if o["priority"] == "high" else 1)
    return dedup


def classify_authority(title):
    tl = (title or "").lower()
    for keys, tier, role, strategy in AUTHORITY_MATRIX:
        if any(k in tl for k in keys):
            return {"tier": tier, "buying_role": role, "engagement_strategy": strategy}
    return {"tier": "unknown", "buying_role": "Unknown — qualify authority on the call",
            "engagement_strategy": "Ask early: who else is involved in this decision and who signs off?"}


def classify_style(title):
    tl = (title or "").lower()
    for keys, style, guidance in STYLE_MATRIX:
        if any(k in tl for k in keys):
            return {"style": style, "adaptation": guidance}
    return {"style": DEFAULT_STYLE[0], "adaptation": DEFAULT_STYLE[1]}


# The full brief skeleton the agent fills with researched content.
BRIEF_SKELETON = [
    {"section": "30-Second Brief", "fill": "Who, why now, the one thing to accomplish, the opening line."},
    {"section": "Company Intelligence",
     "fill": "Overview · financial/growth signals · pain/need indicators · tech & competitive stack · "
             "decision landscape · relationship map · recent news (90d)."},
    {"section": "Prior Interactions",
     "fill": "Chronological timeline from CRM + outreach; what it means for THIS call (never re-pitch a "
             "replier; acknowledge lost deals; multi-thread off colleagues). State 'cold' if none."},
    {"section": "Person Intelligence",
     "fill": "Profile · authority classification (see scaffold) · what they care about (posts/content) · "
             "communication style (see scaffold) · predicted objections (see scaffold)."},
    {"section": "Call Strategy",
     "fill": "Objective · agenda · opening line · prioritized discovery questions · value points mapped to "
             "their pain (proof-point priority: same industry > size > problem > competitor > general) · next step."},
    {"section": "Objection Prep", "fill": "Top predicted objections + your acknowledge/reframe/proof for each."},
    {"section": "Landmines", "fill": "Things NOT to say/do: competitors to not trash, sore points, dead deals."},
    {"section": "After-the-Call", "fill": "Recap template + the specific commitment to secure."},
]


def main():
    ap = argparse.ArgumentParser(description="Deterministic pre-call brief scaffolding.")
    ap.add_argument("--title", default="", help="prospect's job title")
    ap.add_argument("--company", default="", help="company name (echoed into the scaffold)")
    ap.add_argument("--deal-stage", default="", help="current deal/engagement stage (lowercased free text)")
    ap.add_argument("--has-prior-contact", default="false",
                    help="true/false — whether there is prior CRM/outreach contact")
    ap.add_argument("--competitor", default="", help="incumbent/competitor in play, if known")
    ap.add_argument("--price-tier", default="", choices=["", "low", "mid", "premium", "high"],
                    help="your offering's price tier (drives the price objection prediction)")
    ap.add_argument("--output", default="-", help="output scaffold JSON (default stdout)")
    args = ap.parse_args()

    args.deal_stage = (args.deal_stage or "").strip().lower()
    args.has_prior_contact = str(args.has_prior_contact).strip().lower() in ("true", "1", "yes", "y")
    args.price_tier = (args.price_tier or "").strip().lower()

    scaffold = {
        "company": args.company,
        "title": args.title,
        "authority": classify_authority(args.title),
        "communication_style": classify_style(args.title),
        "predicted_objections": objection_rules(args),
        "brief_skeleton": BRIEF_SKELETON,
        "context": {
            "deal_stage": args.deal_stage or None,
            "has_prior_contact": args.has_prior_contact,
            "competitor": args.competitor or None,
            "price_tier": args.price_tier or None,
        },
    }

    out = json.dumps(scaffold, ensure_ascii=False, indent=2)
    if args.output == "-":
        print(out)
    else:
        with open(args.output, "w", encoding="utf-8") as f:
            f.write(out + "\n")
        print(f"brief scaffold ({scaffold['authority']['buying_role']}) -> {args.output}", file=sys.stderr)


if __name__ == "__main__":
    main()
