#!/usr/bin/env python3
"""sigdb.py — shared signature-DB loader/matcher for the tech-stack-teardown scripts.

In-skill module (vendored with this skill only). Loads signatures.json and offers
matchers for the four keyless detection signals:
  - HTML source  (script_src_patterns, html_patterns, meta_generator)
  - HTTP headers (header_patterns)
  - cookies      (cookie_patterns)
  - request domains (request_domains)  [used by the rendered detector]

No network, no LLM — pure matching. Confidence is a coarse, deterministic score.
"""
import json
import os
import re

_DEFAULT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "signatures.json")


def load_signatures(path=None):
    with open(path or _DEFAULT, "r", encoding="utf-8") as f:
        return json.load(f)["technologies"]


def _det(tech):
    return tech.get("detection", {}) or {}


def match_html(html, techs):
    """Match script_src_patterns + html_patterns + meta_generator against raw HTML.

    Returns list of {name, category, confidence, evidence[], signals[], gtm_implication}.
    """
    blob = html.lower()
    # crude meta generator extraction
    gen = ""
    m = re.search(r"<meta[^>]+name=[\"']generator[\"'][^>]+content=[\"']([^\"']+)", blob)
    if m:
        gen = m.group(1).lower()
    out = []
    for t in techs:
        d = _det(t)
        ev, signals = [], set()
        for s in d.get("script_src_patterns", []):
            if s.lower() in blob:
                ev.append(f"src:{s}")
                signals.add("script_src")
        for s in d.get("html_patterns", []):
            if s.lower() in blob:
                ev.append(f"html:{s}")
                signals.add("html")
        for s in d.get("meta_generator", []):
            if gen and s.lower() in gen:
                ev.append(f"meta-generator:{s}")
                signals.add("meta_generator")
        if ev:
            out.append(_record(t, ev, signals))
    return out


def match_headers(headers, techs):
    """headers: dict of lowercased header name -> value string."""
    out = []
    for t in techs:
        d = _det(t)
        hp = d.get("header_patterns", {}) or {}
        if not hp:
            continue
        ev, signals = [], set()
        for hname, vregex in hp.items():
            hn = hname.lower()
            # support a wildcard-ish header-name match (e.g. "x-akamai-.+")
            matched_names = [k for k in headers if k == hn or re.fullmatch(hn, k or "")]
            for k in matched_names:
                try:
                    if re.search(vregex, headers[k] or "", re.I):
                        ev.append(f"header:{k}={headers[k][:60]}")
                        signals.add("header")
                except re.error:
                    if vregex.lower() in (headers[k] or "").lower():
                        ev.append(f"header:{k}={headers[k][:60]}")
                        signals.add("header")
        if ev:
            out.append(_record(t, ev, signals))
    return out


def match_cookies(cookie_names, techs):
    """cookie_names: iterable of cookie name strings (lowercased internally)."""
    names = [c.lower() for c in cookie_names]
    out = []
    for t in techs:
        d = _det(t)
        ev, signals = [], set()
        for cp in d.get("cookie_patterns", []):
            cpl = cp.lower()
            if any(cpl in n for n in names):
                ev.append(f"cookie:{cp}")
                signals.add("cookie")
        if ev:
            out.append(_record(t, ev, signals))
    return out


def match_request_domains(hostnames, techs):
    """hostnames: iterable of third-party request hostnames.

    Matches request_domains as a suffix / substring of each hostname.
    """
    hosts = [h.lower() for h in hostnames]
    out = []
    for t in techs:
        d = _det(t)
        ev, signals = [], set()
        for rd in d.get("request_domains", []):
            rdl = rd.lower()
            hits = [h for h in hosts if rdl in h]
            if hits:
                ev.append(f"request:{rd} ({hits[0]})")
                signals.add("request_domain")
        if ev:
            out.append(_record(t, ev, signals))
    return out


def extract_account_ids(html, techs):
    """Run each tech's id_pattern regex(es) against raw HTML and extract account/pixel IDs.

    Returns {tech_name: {"label": str, "ids": [str,...]}} for techs whose id_pattern
    matched. IDs enable cross-company attribution ("two domains share GTM-XXXX => same
    agency/owner"). Patterns are case-SENSITIVE (IDs are case-sensitive) and each has
    exactly one capture group = the ID.
    """
    out = {}
    for t in techs:
        spec = _det(t).get("id_pattern")
        if not spec:
            continue
        label = spec.get("label", "account ID")
        ids = []
        for pat in spec.get("patterns", []):
            try:
                rx = re.compile(pat)
            except re.error:
                continue
            for m in rx.finditer(html):
                if m.lastindex:
                    val = m.group(1)
                    if val and val not in ids:
                        ids.append(val)
        if ids:
            out[t["name"]] = {"label": label, "ids": ids[:8]}
    return out


def attach_account_ids(detected, id_map):
    """Mutate a detected[] list in place: attach account_id (+ all ids) where id_map has the tech.

    id_map: {tech_name: {"label", "ids"}}. Returns the same list for convenience.
    """
    for d in detected:
        info = id_map.get(d["name"])
        if info and info.get("ids"):
            d["account_id"] = info["ids"][0]
            d["account_ids"] = info["ids"]
            d["id_label"] = info.get("label", "account ID")
    return detected


def globals_index(techs):
    """Return {window_var_name: [tech,...]} for the rendered detector to probe."""
    idx = {}
    for t in techs:
        for g in _det(t).get("global_js_vars", []):
            idx.setdefault(g, []).append(t)
    return idx


# confidence weights per signal (higher = harder to fake / more specific)
_W = {
    "id_pattern": 0.6,
    "request_domain": 0.55,
    "global_js": 0.5,
    "script_src": 0.45,
    "header": 0.4,
    "meta_generator": 0.5,
    "cookie": 0.4,
    "html": 0.25,
}


def _conf(signals):
    if not signals:
        return 0.3
    # combine independent signals; cap at 0.99
    p_miss = 1.0
    for s in signals:
        p_miss *= (1.0 - _W.get(s, 0.3))
    return round(min(0.99, 1.0 - p_miss), 2)


def _record(tech, evidence, signals):
    signals = sorted(set(signals))
    return {
        "name": tech["name"],
        "category": tech["category"],
        "confidence": _conf(signals),
        "signals": signals,
        "evidence": evidence[:6],
        "gtm_implication": tech.get("gtm_implication", ""),
    }


def merge(*detection_lists):
    """Merge per-signal detection lists into one deduped, confidence-ranked list.

    When the same tech is found via multiple signals, union evidence/signals and
    recompute confidence from the combined signal set.
    """
    by_name = {}
    for lst in detection_lists:
        for rec in lst:
            cur = by_name.get(rec["name"])
            if not cur:
                by_name[rec["name"]] = dict(rec)
                continue
            cur["evidence"] = (cur["evidence"] + rec["evidence"])[:8]
            cur["signals"] = sorted(set(cur["signals"]) | set(rec["signals"]))
            cur["confidence"] = _conf(cur["signals"])
            # union any extracted account/pixel IDs across layers
            merged_ids = list(cur.get("account_ids", []))
            for v in rec.get("account_ids", []):
                if v not in merged_ids:
                    merged_ids.append(v)
            if merged_ids:
                cur["account_ids"] = merged_ids
                cur.setdefault("account_id", merged_ids[0])
                cur.setdefault("id_label", rec.get("id_label") or cur.get("id_label", "account ID"))
    out = list(by_name.values())
    out.sort(key=lambda r: (-r["confidence"], r["category"], r["name"]))
    return out
