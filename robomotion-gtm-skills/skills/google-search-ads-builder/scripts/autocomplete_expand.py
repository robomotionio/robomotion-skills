#!/usr/bin/env python3
"""autocomplete_expand.py — Expand seed keywords via Google's public Suggest endpoint.

The keyword-research primitive: for each seed, pull Google autocomplete suggestions and
prefix/suffix-modifier expansions (a..z, "best", "vs", "alternative", "pricing", ...).
Keyless (the suggestqueries endpoint is public). Deterministic — no LLM; the agent does
funnel/intent classification and scoring downstream. Stdlib only.

Examples:
  autocomplete_expand.py --seeds "workflow automation,rpa software" --geo US --output kw.json
  autocomplete_expand.py --seeds "invoice software" --modifiers best,vs,alternative,pricing,free
"""
import argparse
import json
import sys
import time
import urllib.error
import urllib.parse
import urllib.request

SUGGEST = "https://suggestqueries.google.com/complete/search"
DEFAULT_MODIFIERS = ["best", "top", "vs", "alternative", "alternatives", "pricing", "cost",
                     "free", "review", "reviews", "software", "tool", "for", "how to"]
ALPHA = list("abcdefghijklmnopqrstuvwxyz")


def suggest(term, geo, lang):
    params = {"client": "firefox", "q": term, "hl": lang, "gl": geo}
    url = SUGGEST + "?" + urllib.parse.urlencode(params)
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0 robomotion-gtm-skills/ads-builder"})
    for attempt in range(3):
        try:
            with urllib.request.urlopen(req, timeout=20) as r:
                data = json.loads(r.read().decode("utf-8", "replace"))
                return data[1] if isinstance(data, list) and len(data) > 1 else []
        except urllib.error.HTTPError as e:
            if e.code == 429 and attempt < 2:
                time.sleep(2 ** attempt)
                continue
            return []
        except Exception:
            return []
    return []


def main():
    ap = argparse.ArgumentParser(description="Expand seed keywords via Google Suggest (keyless).")
    ap.add_argument("--seeds", required=True, help="comma-separated seed keywords")
    ap.add_argument("--geo", default="US", help="country code (default US)")
    ap.add_argument("--lang", default="en", help="language code (default en)")
    ap.add_argument("--modifiers", default="", help="comma-separated modifiers (default a built-in set)")
    ap.add_argument("--alpha", action="store_true", help="also append a..z suffix expansion per seed")
    ap.add_argument("--max-per-seed", type=int, default=200, help="cap suggestions kept per seed")
    ap.add_argument("--output", default="-", help="output JSON path (default stdout)")
    args = ap.parse_args()

    seeds = [s.strip() for s in args.seeds.split(",") if s.strip()]
    mods = [m.strip() for m in args.modifiers.split(",") if m.strip()] or DEFAULT_MODIFIERS

    out = {}
    seen_global = set()
    for seed in seeds:
        kws = {}
        queries = [seed] + [f"{seed} {m}" for m in mods] + [f"{m} {seed}" for m in mods]
        if args.alpha:
            queries += [f"{seed} {c}" for c in ALPHA]
        for q in queries:
            for s in suggest(q, args.geo, args.lang):
                s = s.strip().lower()
                if s and s not in kws:
                    kws[s] = True
            time.sleep(0.15)  # be polite to the endpoint
            if len(kws) >= args.max_per_seed:
                break
        uniq = [k for k in kws if k not in seen_global]
        seen_global.update(uniq)
        out[seed] = uniq[: args.max_per_seed]

    result = {"seeds": seeds, "geo": args.geo,
              "total_keywords": sum(len(v) for v in out.values()),
              "expansions": out}
    payload = json.dumps(result, ensure_ascii=False, indent=2)
    if args.output == "-":
        print(payload)
    else:
        with open(args.output, "w", encoding="utf-8") as f:
            f.write(payload + "\n")
        print(f"{result['total_keywords']} keywords -> {args.output}", file=sys.stderr)


if __name__ == "__main__":
    main()
