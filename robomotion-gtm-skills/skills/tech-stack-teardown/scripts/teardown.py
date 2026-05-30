#!/usr/bin/env python3
"""teardown.py — orchestrator: merge 4 keyless detection signals into ONE tech profile.

Runs (in-process where possible, subprocess for the node leg):
  1. fetch_headers.py   — HTTP headers + cookies          (signal: headers/cookie)
  2. source_inspect.py  — homepage HTML source            (signal: script_src/html/meta)
  3. detect_requests.mjs— rendered third-party requests   (signal: request_domain/global_js)
                          [optional — only if node + playwright available]
  4. dns_scan.py        — MX/SPF/DKIM/DMARC/TXT/blacklist  (signal: dns)

Then merges all detections into a unified, deduped, confidence-ranked profile grouped by
category, infers the GO-TO-MARKET MOTION from the detected stack, and emits JSON + a
markdown teardown. Supports --snapshot (save) / --diff (compare vs a prior run) for change
tracking. No LLM — pure orchestration + deterministic inference.

Examples:
  teardown.py --domain stripe.com
  teardown.py --domain acme.com --no-render --json out.json --md out.md
  teardown.py --domain acme.com --snapshot prev.json          # save profile for later
  teardown.py --domain acme.com --diff prev.json              # compare vs prev.json
"""
import argparse
import json
import os
import shutil
import subprocess
import sys

import sigdb

HERE = os.path.dirname(os.path.abspath(__file__))
PY = sys.executable or "python3"


# ---------------------------------------------------------------------------
# GTM motion inference rules. Each rule: (label, description, required_any[],
# bonus[], min_hits). Scored by how many of its tech names are present.
# Tech-name matching is case-insensitive substring against the detected set.
# ---------------------------------------------------------------------------
MOTION_RULES = [
    {
        "label": "Enterprise ABM / sales-led demand-gen",
        "signals": ["Marketo", "Salesforce", "Pardot", "6sense", "Demandbase", "Eloqua",
                    "Drift", "Qualified", "Mutiny", "Chili Piper", "Bing", "LinkedIn Insight",
                    "Adobe", "OneTrust", "Tealium"],
        "min": 3,
        "why": "Enterprise MAP (Marketo/Eloqua/Pardot) + Salesforce + intent/ABM (6sense/Demandbase) "
               "+ LinkedIn/Bing paid is the classic enterprise account-based motion.",
    },
    {
        "label": "Inbound / PLG sales-assist",
        "signals": ["HubSpot", "Calendly", "Chili Piper", "Drift", "Intercom", "Default",
                    "HubSpot Meetings", "HubSpot Chat", "Koala", "Warmly", "Common Room", "Qualified"],
        "min": 3,
        "why": "HubSpot/Intercom inbound + self-serve booking (Calendly/Chili Piper) + chat-to-pipeline "
               "is an inbound, product-led sales-assist motion.",
    },
    {
        "label": "Product-led growth (PLG)",
        "signals": ["Amplitude", "Mixpanel", "PostHog", "Heap", "Pendo", "Segment", "RudderStack",
                    "LaunchDarkly", "Statsig", "Split.io", "Stripe", "Sentry", "Customer.io",
                    "Koala", "Paddle", "Lemon Squeezy"],
        "min": 3,
        "why": "Product analytics (Amplitude/Mixpanel/PostHog) + feature flags (LaunchDarkly/Statsig) "
               "+ self-serve billing (Stripe/Paddle) signals a product-led growth motion.",
    },
    {
        "label": "DTC / ecommerce lifecycle",
        "signals": ["Shopify", "WooCommerce", "BigCommerce", "Klaviyo", "Recharge", "Yotpo", "Okendo",
                    "Gorgias", "Privy", "Justuno", "Stamped.io", "Judge.me", "Meta Pixel", "TikTok Pixel",
                    "Pinterest Tag", "Bold Commerce", "Shopify Payments", "Drip"],
        "min": 3,
        "why": "Storefront (Shopify/Woo) + lifecycle email/SMS (Klaviyo) + reviews/UGC (Yotpo/Okendo) "
               "+ social pixels is a DTC ecommerce lifecycle motion.",
    },
    {
        "label": "Outbound SDR / cold-email motion",
        "signals": ["Salesloft", "Outreach.io", "Apollo", "Smartlead", "Instantly", "ZoomInfo",
                    "Clearbit", "RB2B", "Leadfeeder", "Albacross", "Vector", "Koala", "Warmly"],
        "min": 2,
        "why": "Sales-engagement (Salesloft/Outreach) + prospecting/visitor-ID (Apollo/ZoomInfo/RB2B/"
               "Clearbit) + cold-send (Smartlead/Instantly) is an outbound SDR motion.",
    },
    {
        "label": "Content / creator / newsletter-led",
        "signals": ["Ghost", "Substack", "Beehiiv", "ConvertKit", "Mailchimp", "WordPress",
                    "Outbrain", "Taboola", "YouTube Embed", "Webflow"],
        "min": 3,
        "why": "Publishing CMS (Ghost/WordPress) + newsletter capture (Substack/Beehiiv/ConvertKit) "
               "+ content distribution (Outbrain/Taboola) is a content/creator-led motion.",
    },
    {
        "label": "CRO / paid-acquisition optimization",
        "signals": ["Optimizely", "VWO", "AB Tasty", "Kameleoon", "Convert.com", "Unbounce",
                    "Instapage", "Leadpages", "Hotjar", "Microsoft Clarity", "FullStory",
                    "Crazy Egg", "Mouseflow", "OptinMonster", "AdRoll", "Criteo", "Google Ads"],
        "min": 3,
        "why": "Experimentation (Optimizely/VWO) + heatmaps (Hotjar/FullStory) + landing pages "
               "(Unbounce/Instapage) + retargeting (AdRoll/Criteo) is a CRO-driven paid-acquisition motion.",
    },
]


def _run_py(script, args):
    try:
        out = subprocess.run([PY, os.path.join(HERE, script)] + args,
                             capture_output=True, text=True, timeout=180)
        if out.returncode != 0 and not out.stdout.strip():
            return {"error": out.stderr.strip()[:400] or f"{script} exited {out.returncode}"}
        return json.loads(out.stdout) if out.stdout.strip() else {"error": "no output"}
    except (subprocess.TimeoutExpired, json.JSONDecodeError, OSError) as e:
        return {"error": f"{script}: {e}"}


def _run_node(script, args):
    node = shutil.which("node")
    if not node:
        return {"skipped": "node not on PATH", "detected": [], "third_party_domains": []}
    try:
        out = subprocess.run([node, os.path.join(HERE, script)] + args,
                             capture_output=True, text=True, timeout=120)
        if out.stdout.strip():
            return json.loads(out.stdout)
        return {"skipped": out.stderr.strip()[:300] or "no output", "detected": []}
    except (subprocess.TimeoutExpired, json.JSONDecodeError, OSError) as e:
        return {"skipped": f"{script}: {e}", "detected": []}


def infer_motion(detected_names):
    low = [n.lower() for n in detected_names]

    def present(sig):
        s = sig.lower()
        return any(s in n for n in low)

    results = []
    for rule in MOTION_RULES:
        hits = [s for s in rule["signals"] if present(s)]
        if len(hits) >= rule["min"]:
            score = round(min(0.99, 0.45 + 0.12 * (len(hits) - rule["min"]) + 0.1 * rule["min"]), 2)
            results.append({
                "motion": rule["label"],
                "confidence": score,
                "matched_tools": hits,
                "why": rule["why"],
            })
    results.sort(key=lambda r: (-r["confidence"], -len(r["matched_tools"])))
    return results


def build_profile(domain, headers, source, render, dns):
    # merge the three browser-side detection signals (deduped, confidence-ranked)
    merged = sigdb.merge(headers.get("detected", []),
                         source.get("detected", []),
                         render.get("detected", []))
    # attach the origin layer(s) for each tech, rebuilt from the raw inputs
    layer_idx = {}
    for layer, obj in (("headers", headers), ("source", source), ("rendered", render)):
        for d in obj.get("detected", []):
            layer_idx.setdefault(d["name"], set()).add(layer)
    # DNS tools (no confidence struct) -> add as dns-layer detections
    dns_auth = dns.get("email_auth", {})
    for tool in dns_auth.get("tools_from_dns", []):
        layer_idx.setdefault(tool, set()).add("dns")

    for d in merged:
        d["layers"] = sorted(layer_idx.get(d["name"], set()))
        # multi-layer corroboration bumps confidence
        if len(d["layers"]) >= 2:
            d["confidence"] = round(min(0.99, d["confidence"] + 0.05 * (len(d["layers"]) - 1)), 2)

    # add DNS-only tools that source/headers/render didn't catch
    seen = {d["name"] for d in merged}
    techs = sigdb.load_signatures()
    cat_of = {t["name"]: t["category"] for t in techs}
    impl_of = {t["name"]: t.get("gtm_implication", "") for t in techs}
    for tool in dns_auth.get("tools_from_dns", []):
        if tool not in seen:
            merged.append({
                "name": tool, "category": cat_of.get(tool, "email/dns"),
                "confidence": 0.7, "signals": ["dns"], "layers": ["dns"],
                "evidence": ["dns: MX/SPF/DKIM/TXT"], "gtm_implication": impl_of.get(tool, ""),
            })
            seen.add(tool)

    merged.sort(key=lambda r: (-r["confidence"], r["category"], r["name"]))

    by_category = {}
    for d in merged:
        by_category.setdefault(d["category"], []).append(d)

    motions = infer_motion([d["name"] for d in merged])

    # attribution fingerprint: aggregate every extracted account/pixel ID across all
    # layers. Two teardowns that share an ID (same GTM-XXXX, GA4 G-XXXX, FB pixel, etc.)
    # are very likely the same owner / agency / parent company.
    fingerprint = build_fingerprint(merged, headers, source, render)

    return {
        "domain": domain,
        "detected": merged,
        "by_category": by_category,
        "gtm_motion_inference": motions,
        "attribution_fingerprint": fingerprint,
        "tool_count": len(merged),
    }


def build_fingerprint(merged, headers, source, render):
    """Collect all extracted account/pixel IDs into one attribution fingerprint.

    Returns {"ids": [{tech, label, category, value, layers[]}...], "flat": ["GA4=G-...",...]}.
    Sourced from the merged detections plus the per-layer account_ids maps so nothing is lost.
    """
    cat_of = {d["name"]: d["category"] for d in merged}
    label_of = {d["name"]: d.get("id_label", "account ID") for d in merged}
    # tech -> {value -> set(layers)}
    acc = {}

    def add(tech, value, layer):
        if not value:
            return
        acc.setdefault(tech, {}).setdefault(value, set()).add(layer)

    # from merged detections (source/headers merged earlier — layer = "merged")
    for d in merged:
        for v in d.get("account_ids", []) or ([d["account_id"]] if d.get("account_id") else []):
            add(d["name"], v, "merged")
    # from each raw layer's account_ids map (authoritative per-layer provenance)
    for layer, obj in (("source", source), ("rendered", render), ("headers", headers)):
        amap = obj.get("account_ids", {}) or {}
        for tech, ids in amap.items():
            for v in ids:
                add(tech, v, layer)

    ids = []
    for tech in sorted(acc):
        for value in sorted(acc[tech]):
            ids.append({
                "tech": tech,
                "label": label_of.get(tech, "account ID"),
                "category": cat_of.get(tech, ""),
                "value": value,
                "layers": sorted(l for l in acc[tech][value] if l != "merged") or ["merged"],
            })
    flat = [f"{i['tech']}={i['value']}" for i in ids]
    return {"ids": ids, "flat": flat, "count": len(ids)}


def render_markdown(profile, headers, source, render, dns):
    d = profile["domain"]
    L = [f"# Tech Stack Teardown — {d}", ""]

    motions = profile["gtm_motion_inference"]
    L.append("## GTM motion inference")
    if motions:
        for m in motions:
            L.append(f"- **{m['motion']}** (confidence {m['confidence']}) — "
                     f"matched: {', '.join(m['matched_tools'])}")
            L.append(f"  - {m['why']}")
    else:
        L.append("- No clear motion pattern matched. Stack may be early-stage, minimal, "
                 "or use tools that leave no public trace (Sales Nav, Clay, Apollo prospecting).")
    L.append("")

    L.append(f"## Detected stack ({profile['tool_count']} technologies)")
    for cat in sorted(profile["by_category"]):
        L.append(f"\n### {cat}")
        for t in profile["by_category"][cat]:
            layers = "/".join(t.get("layers", []) or t.get("signals", []))
            impl = f" — {t['gtm_implication']}" if t.get("gtm_implication") else ""
            idstr = ""
            if t.get("account_id"):
                lbl = t.get("id_label", "account ID")
                extra = t.get("account_ids", [])
                idval = "`" + "`, `".join(extra) + "`" if len(extra) > 1 else f"`{t['account_id']}`"
                idstr = f" [{lbl}: {idval}]"
            L.append(f"- **{t['name']}** (conf {t['confidence']}, via {layers}){idstr}{impl}")
    L.append("")

    # attribution fingerprint — the extracted account/pixel IDs for cross-company linking
    fp = profile.get("attribution_fingerprint", {})
    L.append("## Attribution fingerprint")
    if fp.get("ids"):
        L.append(f"Extracted {fp['count']} account/pixel ID(s). Two teardowns sharing any of "
                 "these IDs are very likely the same owner / agency / parent company "
                 "(e.g. a shared `GTM-XXXX` container or `G-XXXX` GA4 stream).")
        L.append("")
        L.append("| Tech | ID type | Value | Seen via |")
        L.append("|------|---------|-------|----------|")
        for i in fp["ids"]:
            L.append(f"| {i['tech']} | {i['label']} | `{i['value']}` | {'/'.join(i['layers'])} |")
        L.append("")
        L.append(f"**Fingerprint (flat):** `{' '.join(fp['flat'])}`")
    else:
        L.append("- No account/pixel IDs extracted (IDs may be tag-manager-injected and unrendered; "
                 "run with the rendered layer enabled, or the site uses no ID-bearing trackers).")
    L.append("")

    auth = dns.get("email_auth", {})
    L.append("## Email authentication & deliverability")
    L.append(f"- **Email provider (MX):** {', '.join(auth.get('email_provider')) or 'unknown'}")
    L.append(f"- **SPF:** {'present' if auth.get('spf_present') else 'MISSING'} "
             f"`{auth.get('spf_all_qualifier','')}` — senders: "
             f"{', '.join(auth.get('spf_senders')) or '(none mapped)'}")
    L.append(f"- **DKIM selectors found:** {', '.join(auth.get('dkim_selectors_found')) or 'none'} "
             f"→ tools: {', '.join(auth.get('dkim_tools')) or '(none)'}")
    pol = auth.get("dmarc_policy") or "none"
    L.append(f"- **DMARC:** {'present' if auth.get('dmarc_present') else 'MISSING'} "
             f"(p={pol}, pct={auth.get('dmarc_pct','')}) — "
             f"{'ENFORCED' if auth.get('dmarc_enforced') else 'monitoring-only / none'}; "
             f"rua: {', '.join(auth.get('dmarc_rua_providers')) or '(none)'}")
    if auth.get("txt_verifications"):
        L.append(f"- **TXT verifications:** {', '.join(auth['txt_verifications'])}")
    flags = auth.get("deliverability_flags", {})
    warn = [k for k, v in flags.items() if v and k != "dmarc_enforced"]
    if warn:
        L.append(f"- ⚠️ **Deliverability flags:** {', '.join(warn)}")
    bl = dns.get("blacklists", {})
    if bl:
        L.append(f"- **Blacklists:** {'LISTED — ' + ', '.join(k for k,v in bl.get('listings',{}).items() if v) if bl.get('any_listed') else 'clean'} "
                 f"(IP {bl.get('ip','?')})")
    ob = dns.get("outbound_domains", [])
    if ob:
        L.append(f"- **Possible cold-outbound domains:** "
                 + ", ".join(f"{o['domain']}{' (cold-send)' if o['likely_cold_outbound'] else ''}" for o in ob))
    L.append("")

    # data-collection notes
    notes = []
    if source.get("error"):
        notes.append(f"source: {source['error']}")
    if render.get("skipped"):
        notes.append(f"rendered layer skipped: {render['skipped']}")
    if not headers.get("fetch", {}).get("ok", True):
        notes.append(f"headers: {headers.get('fetch',{}).get('error','')}")
    if notes:
        L.append("## Collection notes")
        for n in notes:
            L.append(f"- {n}")
        L.append("")

    return "\n".join(L)


def diff_profiles(old, new):
    old_map = {t["name"]: t for t in old.get("detected", [])}
    new_map = {t["name"]: t for t in new.get("detected", [])}
    added = sorted(set(new_map) - set(old_map))
    removed = sorted(set(old_map) - set(new_map))
    old_m = {m["motion"] for m in old.get("gtm_motion_inference", [])}
    new_m = {m["motion"] for m in new.get("gtm_motion_inference", [])}
    return {
        "domain": new.get("domain"),
        "added_tools": [{"name": n, "category": new_map[n]["category"]} for n in added],
        "removed_tools": [{"name": n, "category": old_map[n]["category"]} for n in removed],
        "motion_added": sorted(new_m - old_m),
        "motion_removed": sorted(old_m - new_m),
        "no_change": not (added or removed or (new_m ^ old_m)),
    }


def main():
    ap = argparse.ArgumentParser(description="Tech-stack teardown orchestrator (keyless 4-signal).")
    ap.add_argument("--domain", required=True, help="company domain (e.g. example.com)")
    ap.add_argument("--no-render", action="store_true", help="skip the Playwright rendered-request layer")
    ap.add_argument("--no-dns", action="store_true", help="skip the DNS layer")
    ap.add_argument("--no-blacklist", action="store_true", help="skip DNS-blacklist checks")
    ap.add_argument("--apify", action="store_true",
                    help="add OPTIONAL Apify technology-profiler enrichment (needs APIFY_API_TOKEN)")
    ap.add_argument("--render-wait", default="5000", help="rendered-layer settle wait ms (default 5000)")
    ap.add_argument("--json", default="-", help="JSON output path (default stdout)")
    ap.add_argument("--md", default=None, help="markdown report output path (default: none)")
    ap.add_argument("--snapshot", default=None, help="save the unified profile to this path for later --diff")
    ap.add_argument("--diff", default=None, help="compare this run's profile vs a prior snapshot JSON")
    args = ap.parse_args()

    domain = args.domain.strip()
    norm = domain
    for pre_ in ("https://", "http://"):
        if norm.startswith(pre_):
            norm = norm[len(pre_):]
    norm = norm.strip("/").split("/")[0].lower()
    url = f"https://{norm}"

    headers = _run_py("fetch_headers.py", ["--url", norm])
    source = _run_py("source_inspect.py", ["--domain", norm])
    render = {"detected": [], "third_party_domains": [], "skipped": "disabled (--no-render)"} if args.no_render \
        else _run_node("detect_requests.mjs", ["--url", url, "--wait", str(args.render_wait)])
    if args.no_dns:
        dns = {"email_auth": {}}
    else:
        dns_args = ["--domain", norm]
        if args.no_blacklist:
            dns_args.append("--no-blacklist")
        dns = _run_py("dns_scan.py", dns_args)

    # OPTIONAL enrichment: Apify long-tail technology profiler (keyless path stays primary).
    apify = None
    if args.apify:
        apify = _run_py("apify_profiler.py", ["--url", url])

    profile = build_profile(norm, headers, source, render, dns)

    # fold Apify-only tech names in as a low-confidence enrichment layer (breadth, not authority)
    if apify and apify.get("detected"):
        seen = {d["name"].lower() for d in profile["detected"]}
        added = []
        for t in apify["detected"]:
            if t["name"].lower() not in seen:
                profile["detected"].append({
                    "name": t["name"], "category": t.get("category", "(apify)"),
                    "confidence": 0.5, "signals": ["apify"], "layers": ["apify"],
                    "evidence": ["apify technology profiler"],
                    "gtm_implication": "",
                })
                seen.add(t["name"].lower())
                added.append(t["name"])
        if added:
            profile["detected"].sort(key=lambda r: (-r["confidence"], r["category"], r["name"]))
            profile["by_category"] = {}
            for d in profile["detected"]:
                profile["by_category"].setdefault(d["category"], []).append(d)
            profile["tool_count"] = len(profile["detected"])
            profile["apify_enrichment"] = {"added_tools": added, "count": len(added)}

    profile["raw"] = {
        "headers": {k: headers.get(k) for k in ("notable_headers", "set_cookie_names",
                                                "security_headers_present", "fetch")},
        "source_stats": source.get("stats", {}),
        "rendered": {k: render.get(k) for k in ("third_party_domains", "window_globals_present",
                                                "stats", "skipped", "error")},
        "dns": dns,
        "apify": ({k: apify.get(k) for k in ("actor", "skipped", "error", "tools_detected")}
                  if apify else None),
    }

    if args.diff:
        try:
            with open(args.diff, "r", encoding="utf-8") as f:
                old = json.load(f)
            profile["diff_vs_prior"] = diff_profiles(old, profile)
        except (OSError, json.JSONDecodeError) as e:
            profile["diff_vs_prior"] = {"error": f"could not read prior snapshot: {e}"}

    if args.snapshot:
        snap = {k: profile[k] for k in ("domain", "detected", "by_category",
                                        "gtm_motion_inference", "attribution_fingerprint",
                                        "tool_count")}
        with open(args.snapshot, "w", encoding="utf-8") as f:
            json.dump(snap, f, ensure_ascii=False, indent=2)
        print(f"snapshot saved -> {args.snapshot}", file=sys.stderr)

    if args.md:
        md = render_markdown(profile, headers, source, render, dns)
        with open(args.md, "w", encoding="utf-8") as f:
            f.write(md + "\n")
        print(f"markdown report -> {args.md}", file=sys.stderr)

    out = json.dumps(profile, ensure_ascii=False, indent=2)
    if args.json == "-":
        print(out)
    else:
        with open(args.json, "w", encoding="utf-8") as f:
            f.write(out + "\n")
        print(f"profile JSON -> {args.json} ({profile['tool_count']} tools, "
              f"{len(profile['gtm_motion_inference'])} motion(s))", file=sys.stderr)


if __name__ == "__main__":
    main()
