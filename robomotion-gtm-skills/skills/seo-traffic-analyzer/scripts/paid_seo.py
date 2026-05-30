#!/usr/bin/env python3
"""paid_seo.py — OPTIONAL paid-data enrichment adapter (DataForSEO).

The SEO skills are keyless-first by design: their default path derives DIRECTIONAL
metrics from SERP probes, sitemap crawls, and Autocomplete. This adapter is the
opt-in precision ceiling — when DataForSEO credentials are present it returns
MEASURED metrics (real search volume, CPC, keyword difficulty, domain rank/traffic,
ranked keywords, backlinks/referring domains) that the host agent merges in,
upgrading the otherwise-"directional" labels to "measured".

Provider: DataForSEO (https://dataforseo.com), HTTP Basic auth via
  DATAFORSEO_LOGIN / DATAFORSEO_PASSWORD. Stdlib urllib only — no third-party deps.

Alternative providers (NOT implemented here — drop-in adapters could be added):
  - Semrush  -> SEMRUSH_API_KEY  (GET https://api.semrush.com/ ... type=phrase_this)
  - Ahrefs   -> AHREFS_API_TOKEN (GET https://api.ahrefs.com/v3/ ...)
Both expose comparable volume/difficulty/authority/backlink endpoints; only the
auth scheme and JSON shape differ. This adapter intentionally ships DataForSEO only.

KEYLESS-FIRST CONTRACT: if credentials are absent this prints a clear
"paid enrichment unavailable — keyless path still applies" message to stderr and
exits NON-ZERO without raising — so a skill's main (keyless) flow is never broken
by calling this and finding no creds.

Subcommands:
  keywords  --keywords a,b,c            search volume + CPC + competition + difficulty
  domain    --domain x.com              domain rank / organic-traffic overview
  ranked    --domain x.com --limit N    ranked keywords for the domain
  backlinks --target x.com              referring domains, backlinks, domain rank

Examples:
  paid_seo.py keywords --keywords "rpa software,workflow automation"
  paid_seo.py domain --domain example.com
  paid_seo.py ranked --domain example.com --limit 50
  paid_seo.py backlinks --target example.com
"""
import argparse
import base64
import json
import os
import sys
import urllib.error
import urllib.request

API_BASE = "https://api.dataforseo.com"
NO_CREDS_MSG = (
    "paid enrichment unavailable — keyless path still applies "
    "(set DATAFORSEO_LOGIN / DATAFORSEO_PASSWORD to enable measured metrics; "
    "Semrush/Ahrefs are alternative providers, not implemented here)."
)
EXIT_NO_CREDS = 3
EXIT_API_ERROR = 4


# --------------------------------------------------------------------------- #
# HTTP plumbing
# --------------------------------------------------------------------------- #
def _creds():
    login = os.environ.get("DATAFORSEO_LOGIN", "").strip()
    password = os.environ.get("DATAFORSEO_PASSWORD", "").strip()
    if not login or not password:
        return None
    return login, password


def _post(path, payload, creds):
    """POST a DataForSEO task array; return parsed JSON or raise RuntimeError."""
    login, password = creds
    token = base64.b64encode(f"{login}:{password}".encode("utf-8")).decode("ascii")
    body = json.dumps(payload).encode("utf-8")
    req = urllib.request.Request(
        API_BASE + path,
        data=body,
        headers={
            "Authorization": "Basic " + token,
            "Content-Type": "application/json",
            "User-Agent": "robomotion-gtm-skills-paid-seo/1.0",
        },
        method="POST",
    )
    try:
        with urllib.request.urlopen(req, timeout=60) as r:
            return json.loads(r.read().decode("utf-8", "ignore"))
    except urllib.error.HTTPError as e:
        detail = ""
        try:
            detail = e.read().decode("utf-8", "ignore")[:400]
        except Exception:
            pass
        raise RuntimeError(f"DataForSEO HTTP {e.code} on {path}: {detail}")
    except (urllib.error.URLError, TimeoutError) as e:
        raise RuntimeError(f"DataForSEO request failed on {path}: {e}")


def _items(resp):
    """Defensively dig the result items out of DataForSEO's nested envelope.

    Canonical shape: {tasks: [{result: [{items: [...]}]}]}, but DataForSEO varies:
    some endpoints put the rows directly in result[], some wrap them in
    result[0].items, some return result[0] as the single object itself. Handle all.
    A non-zero top-level status_code (or per-task status_code) means the call failed.
    """
    if not isinstance(resp, dict):
        raise RuntimeError("unexpected (non-object) API response")
    sc = resp.get("status_code")
    if sc is not None and sc != 20000:
        raise RuntimeError(f"API status {sc}: {resp.get('status_message', '')}")
    tasks = resp.get("tasks") or []
    if not tasks:
        return []
    task = tasks[0] or {}
    tsc = task.get("status_code")
    if tsc is not None and tsc != 20000:
        raise RuntimeError(f"task status {tsc}: {task.get('status_message', '')}")
    result = task.get("result") or []
    if not result:
        return []
    out = []
    for res in result:
        if not isinstance(res, dict):
            continue
        items = res.get("items")
        if isinstance(items, list) and items:
            out.extend(items)
        else:
            # result row is itself the datum (e.g. domain overview / backlinks summary)
            out.append(res)
    return out


def _num(d, *keys):
    """First present numeric value among keys (supports dotted paths), else None."""
    for k in keys:
        cur = d
        ok = True
        for part in k.split("."):
            if isinstance(cur, dict) and part in cur:
                cur = cur[part]
            else:
                ok = False
                break
        if ok and isinstance(cur, (int, float)):
            return cur
    return None


# --------------------------------------------------------------------------- #
# Subcommand: keywords  (volume + CPC + competition + difficulty)
# --------------------------------------------------------------------------- #
def cmd_keywords(args, creds):
    kws = [k.strip() for k in args.keywords.split(",") if k.strip()]
    if not kws:
        raise RuntimeError("--keywords is empty")

    loc = {"location_code": args.location_code, "language_code": args.language_code}

    # 1) search volume + CPC + competition (Google Ads keywords_data)
    vol_by_kw = {}
    sv = _post(
        "/v3/keywords_data/google_ads/search_volume/live",
        [dict(keywords=kws, **loc)],
        creds,
    )
    for it in _items(sv):
        kw = (it.get("keyword") or "").strip()
        if not kw:
            continue
        vol_by_kw[kw.lower()] = {
            "volume": _num(it, "search_volume"),
            "cpc": _num(it, "cpc"),
            "competition": (it.get("competition")
                            if isinstance(it.get("competition"), (int, float))
                            else _num(it, "competition_index")),
        }

    # 2) bulk keyword difficulty (DataForSEO Labs)
    diff_by_kw = {}
    try:
        bd = _post(
            "/v3/dataforseo_labs/google/bulk_keyword_difficulty/live",
            [dict(keywords=kws, **loc)],
            creds,
        )
        for it in _items(bd):
            kw = (it.get("keyword") or "").strip()
            if kw:
                diff_by_kw[kw.lower()] = _num(it, "keyword_difficulty")
    except RuntimeError as e:
        # difficulty is a nice-to-have; volume/CPC still ship
        print(f"WARN: keyword difficulty unavailable: {e}", file=sys.stderr)

    rows = []
    for kw in kws:
        m = vol_by_kw.get(kw.lower(), {})
        rows.append({
            "keyword": kw,
            "volume": m.get("volume"),
            "cpc": m.get("cpc"),
            "competition": m.get("competition"),
            "difficulty": diff_by_kw.get(kw.lower()),
        })
    return {"source": "dataforseo", "metric": "measured", "keywords": rows}


# --------------------------------------------------------------------------- #
# Subcommand: domain  (rank / traffic overview)
# --------------------------------------------------------------------------- #
def cmd_domain(args, creds):
    resp = _post(
        "/v3/dataforseo_labs/google/domain_rank_overview/live",
        [{
            "target": args.domain,
            "location_code": args.location_code,
            "language_code": args.language_code,
        }],
        creds,
    )
    items = _items(resp)
    if not items:
        return {"source": "dataforseo", "metric": "measured",
                "domain": args.domain, "overview": None}
    it = items[0]
    metrics = it.get("metrics") or {}
    organic = metrics.get("organic") or {}
    paid = metrics.get("paid") or {}
    return {
        "source": "dataforseo",
        "metric": "measured",
        "domain": args.domain,
        "overview": {
            "organic_keywords": _num(organic, "count", "pos_1", "etv") if organic else None,
            "organic_etv_traffic": _num(organic, "etv"),
            "organic_estimated_paid_traffic_cost": _num(organic, "estimated_paid_traffic_cost"),
            "organic_pos_1": _num(organic, "pos_1"),
            "organic_pos_2_3": _num(organic, "pos_2_3"),
            "paid_keywords": _num(paid, "count"),
            "paid_etv": _num(paid, "etv"),
        },
        "raw_metrics": metrics,
    }


# --------------------------------------------------------------------------- #
# Subcommand: ranked  (ranked keywords for a domain)
# --------------------------------------------------------------------------- #
def cmd_ranked(args, creds):
    resp = _post(
        "/v3/dataforseo_labs/google/ranked_keywords/live",
        [{
            "target": args.domain,
            "location_code": args.location_code,
            "language_code": args.language_code,
            "limit": args.limit,
            "order_by": ["keyword_data.keyword_info.search_volume,desc"],
        }],
        creds,
    )
    rows = []
    for it in _items(resp):
        kd = it.get("keyword_data") or {}
        ki = kd.get("keyword_info") or {}
        kp = kd.get("keyword_properties") or {}
        serp = it.get("ranked_serp_element") or {}
        se = serp.get("serp_item") or {}
        rows.append({
            "keyword": kd.get("keyword"),
            "volume": _num(ki, "search_volume"),
            "cpc": _num(ki, "cpc"),
            "difficulty": _num(kp, "keyword_difficulty"),
            "rank_position": _num(se, "rank_absolute", "rank_group"),
            "url": se.get("url"),
            "etv": _num(se, "etv"),
        })
    return {
        "source": "dataforseo",
        "metric": "measured",
        "domain": args.domain,
        "count": len(rows),
        "ranked_keywords": rows,
    }


# --------------------------------------------------------------------------- #
# Subcommand: backlinks  (summary: referring domains, backlinks, domain rank)
# --------------------------------------------------------------------------- #
def cmd_backlinks(args, creds):
    resp = _post(
        "/v3/backlinks/summary/live",
        [{"target": args.target, "internal_list_limit": 10, "backlinks_status_type": "live"}],
        creds,
    )
    items = _items(resp)
    if not items:
        return {"source": "dataforseo", "metric": "measured",
                "target": args.target, "summary": None}
    it = items[0]
    return {
        "source": "dataforseo",
        "metric": "measured",
        "target": args.target,
        "summary": {
            "domain_rank": _num(it, "rank"),
            "backlinks": _num(it, "backlinks"),
            "referring_domains": _num(it, "referring_domains"),
            "referring_main_domains": _num(it, "referring_main_domains"),
            "referring_ips": _num(it, "referring_ips"),
            "broken_backlinks": _num(it, "broken_backlinks"),
            "dofollow_backlinks": _num(it, "referring_links_attributes.dofollow",
                                       "dofollow"),
        },
    }


# --------------------------------------------------------------------------- #
# CLI
# --------------------------------------------------------------------------- #
def main():
    ap = argparse.ArgumentParser(
        description="OPTIONAL DataForSEO paid-data enrichment for the SEO skills "
                    "(keyless path still applies if creds are absent).",
    )
    sub = ap.add_subparsers(dest="cmd", required=True)

    def add_common(p):
        p.add_argument("--location-code", type=int, default=2840,
                       help="DataForSEO location code (default 2840 = United States)")
        p.add_argument("--language-code", default="en",
                       help="DataForSEO language code (default 'en')")
        p.add_argument("--output", default="-", help="output JSON path (default stdout)")

    pk = sub.add_parser("keywords", help="search volume + CPC + competition + difficulty")
    pk.add_argument("--keywords", required=True, help="comma-separated keywords")
    add_common(pk)
    pk.set_defaults(func=cmd_keywords)

    pd = sub.add_parser("domain", help="domain rank / organic-traffic overview")
    pd.add_argument("--domain", required=True, help="domain, e.g. example.com")
    add_common(pd)
    pd.set_defaults(func=cmd_domain)

    pr = sub.add_parser("ranked", help="ranked keywords for a domain")
    pr.add_argument("--domain", required=True, help="domain, e.g. example.com")
    pr.add_argument("--limit", type=int, default=50, help="max ranked keywords (default 50)")
    add_common(pr)
    pr.set_defaults(func=cmd_ranked)

    pb = sub.add_parser("backlinks", help="backlinks summary (referring domains, rank)")
    pb.add_argument("--target", required=True, help="domain or URL, e.g. example.com")
    add_common(pb)
    pb.set_defaults(func=cmd_backlinks)

    args = ap.parse_args()

    creds = _creds()
    if creds is None:
        print(NO_CREDS_MSG, file=sys.stderr)
        sys.exit(EXIT_NO_CREDS)

    try:
        payload = args.func(args, creds)
    except RuntimeError as e:
        print(f"ERROR: {e}", file=sys.stderr)
        print("paid enrichment failed — fall back to the keyless directional path.",
              file=sys.stderr)
        sys.exit(EXIT_API_ERROR)

    text = json.dumps(payload, ensure_ascii=False, indent=2)
    if args.output == "-":
        print(text)
    else:
        with open(args.output, "w", encoding="utf-8") as f:
            f.write(text + "\n")
        print(f"wrote {args.cmd} enrichment -> {args.output}", file=sys.stderr)


if __name__ == "__main__":
    main()
