#!/usr/bin/env python3
"""apify_profiler.py — OPTIONAL long-tail tech-breadth enrichment via a public Apify actor.

Keyless-first is preserved: this script is *enrichment only* and is gated entirely on
APIFY_API_TOKEN. Without the token it prints a clean "skipped" record and exits 0 — the
four keyless signals (source, headers, rendered requests, DNS) already produce a complete
profile. With the token, it runs a PUBLIC Apify Store technology-profiler (Wappalyzer-style)
actor over the URL for breadth (long-tail/obscure tech the bundled 202-sig DB may miss) and
emits a normalized {detected:[{name, category, ...}]} record that teardown.py / the agent can
merge as an extra layer.

Default actor: a public Wappalyzer-style profiler on the Apify Store (override with --actor).
Choose any public technology-profiler actor you trust; this references no proprietary actor ID.

Examples:
  APIFY_API_TOKEN=... apify_profiler.py --url https://example.com
  APIFY_API_TOKEN=... apify_profiler.py --url example.com --actor user/actor-name --output prof.json
"""
import argparse
import json
import os
import sys
import urllib.error
import urllib.parse
import urllib.request

# A public Wappalyzer-style technology-profiler actor on the Apify Store.
# Override with --actor or APIFY_TECH_ACTOR to use a different public actor.
DEFAULT_ACTOR = os.environ.get("APIFY_TECH_ACTOR", "jupri~wappalyzer")
API_BASE = "https://api.apify.com/v2"


def _normalize_url(u):
    u = u.strip()
    if not u.startswith("http"):
        u = "https://" + u.strip("/")
    return u


def run_actor(actor, token, url, timeout=300):
    """Run the actor synchronously and return its dataset items (list of dicts)."""
    endpoint = (f"{API_BASE}/acts/{actor}/run-sync-get-dataset-items"
                f"?token={urllib.parse.quote(token)}&timeout={timeout}")
    # Most Wappalyzer-style actors accept either {urls:[...]} or {startUrls:[{url}]}.
    payload = json.dumps({
        "url": url,
        "urls": [url],
        "startUrls": [{"url": url}],
    }).encode("utf-8")
    req = urllib.request.Request(
        endpoint, data=payload, method="POST",
        headers={"Content-Type": "application/json", "Accept": "application/json"})
    with urllib.request.urlopen(req, timeout=timeout + 30) as r:
        body = r.read().decode("utf-8", "replace")
    data = json.loads(body)
    return data if isinstance(data, list) else [data]


def normalize_items(items):
    """Best-effort flatten of varied actor output shapes into [{name, category, version?}].

    Different public profiler actors emit different schemas; we accept the common ones
    (a `technologies` list, a `applications` list, or a flat list of {name,categories}).
    """
    out = []
    seen = set()

    def add(name, category="", version=""):
        if not name:
            return
        key = name.lower()
        if key in seen:
            return
        seen.add(key)
        rec = {"name": name, "category": category or "(apify)", "source": "apify"}
        if version:
            rec["version"] = version
        out.append(rec)

    for it in items:
        if not isinstance(it, dict):
            continue
        techs = (it.get("technologies") or it.get("applications")
                 or it.get("tech") or it.get("results") or [])
        if isinstance(techs, list) and techs:
            for t in techs:
                if isinstance(t, dict):
                    cats = t.get("categories") or t.get("category") or []
                    if isinstance(cats, list):
                        cats = ", ".join(str(c.get("name", c) if isinstance(c, dict) else c) for c in cats)
                    add(t.get("name") or t.get("app") or t.get("technology"),
                        str(cats), str(t.get("version", "")))
                elif isinstance(t, str):
                    add(t)
        else:
            # flat record itself may be a tech
            if it.get("name"):
                cats = it.get("categories") or it.get("category") or ""
                if isinstance(cats, list):
                    cats = ", ".join(str(c) for c in cats)
                add(it.get("name"), str(cats), str(it.get("version", "")))
    return out


def main():
    ap = argparse.ArgumentParser(
        description="OPTIONAL Apify technology-profiler enrichment (gated on APIFY_API_TOKEN).")
    ap.add_argument("--url", required=True, help="company domain or URL")
    ap.add_argument("--actor", default=DEFAULT_ACTOR,
                    help=f"public Apify Store actor id (default: {DEFAULT_ACTOR})")
    ap.add_argument("--timeout", type=int, default=300, help="actor run timeout seconds")
    ap.add_argument("--output", default="-", help="output JSON path (default stdout)")
    args = ap.parse_args()

    url = _normalize_url(args.url)
    token = os.environ.get("APIFY_API_TOKEN", "").strip()

    result = {"url": url, "actor": args.actor, "source": "apify",
              "enrichment_only": True, "detected": []}

    if not token:
        result["skipped"] = ("APIFY_API_TOKEN not set — enrichment skipped. The four keyless "
                             "signals already produce a complete profile.")
        _emit(result, args.output)
        return

    try:
        items = run_actor(args.actor, token, url, args.timeout)
        result["detected"] = normalize_items(items)
        result["raw_item_count"] = len(items)
        result["tools_detected"] = len(result["detected"])
    except (urllib.error.HTTPError, urllib.error.URLError, TimeoutError,
            ConnectionError, OSError, json.JSONDecodeError) as e:
        result["error"] = f"apify run failed: {e}"
        result["hint"] = ("verify the actor id is a public Apify Store technology profiler and "
                          "your token has run permission; try --actor <user/actor>.")
    _emit(result, args.output)


def _emit(result, output):
    out = json.dumps(result, ensure_ascii=False, indent=2)
    if output == "-":
        print(out)
    else:
        with open(output, "w", encoding="utf-8") as f:
            f.write(out + "\n")
        print(f"apify profiler -> {output} ({len(result.get('detected', []))} tools, "
              f"{'skipped' if result.get('skipped') else result.get('error','ok')})", file=sys.stderr)


if __name__ == "__main__":
    main()
