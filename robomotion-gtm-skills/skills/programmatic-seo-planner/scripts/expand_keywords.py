#!/usr/bin/env python3
"""expand_keywords.py — keyless keyword expansion via Google Autocomplete.

The keyword-research primitive: for each seed topic, query Google's public
suggest endpoint with prefix/suffix modifiers ("what/how/why/best/vs/...") and
return the deduplicated suggestion universe. No API key, stdlib only (urllib).

This is a DETERMINISTIC fetch tool — it does NOT cluster or score. The host
agent does semantic clustering / pillar-spoke architecture from this raw set.

Example:
  expand_keywords.py --seeds "sales automation,lead scoring" --output seeds.json
  expand_keywords.py --seeds "crm" --modifiers question,comparison --max-per-seed 80
"""
import argparse
import json
import sys
import time
import urllib.error
import urllib.parse
import urllib.request

SUGGEST_URL = "http://suggestqueries.google.com/complete/search"

# Modifier sets — prefix/suffix tokens that surface distinct intent angles.
MODIFIERS = {
    "base": [""],
    "question": ["what is", "how to", "why", "when to", "which", "how do i", "what are"],
    "comparison": ["vs", "or", "alternative to", "compared to", "versus"],
    "commercial": ["best", "top", "tools", "software", "platform", "pricing", "for"],
    "guide": ["guide", "examples", "templates", "checklist", "tutorial", "tips"],
    "alphabet": list("abcdefghijklmnopqrstuvwxyz"),
}


def fetch_suggestions(query):
    params = {"client": "firefox", "q": query}
    url = SUGGEST_URL + "?" + urllib.parse.urlencode(params)
    req = urllib.request.Request(url, headers={"User-Agent": "robomotion-gtm-skills/topical-authority-mapper"})
    for attempt in range(4):
        try:
            with urllib.request.urlopen(req, timeout=20) as r:
                raw = r.read().decode("utf-8", "ignore")
                data = json.loads(raw)
                # firefox client returns [query, [suggestions...]]
                return data[1] if isinstance(data, list) and len(data) > 1 else []
        except urllib.error.HTTPError as e:
            if e.code == 429 and attempt < 3:
                time.sleep(2 ** attempt)
                continue
            return []
        except (urllib.error.URLError, json.JSONDecodeError):
            if attempt < 3:
                time.sleep(2 ** attempt)
                continue
            return []
    return []


def build_queries(seed, modifier_keys):
    qs = []
    for key in modifier_keys:
        for mod in MODIFIERS.get(key, [""]):
            mod = mod.strip()
            if not mod:
                qs.append(seed)
            elif key in ("question", "comparison", "commercial", "guide"):
                # prefix-style modifiers go before seed except a few suffixes
                if mod in ("vs", "or", "alternative to", "compared to", "versus",
                           "for", "pricing", "guide", "examples", "templates",
                           "checklist", "tutorial", "tips"):
                    qs.append(f"{seed} {mod}")
                else:
                    qs.append(f"{mod} {seed}")
            elif key == "alphabet":
                qs.append(f"{seed} {mod}")
            else:
                qs.append(seed)
    # dedup, preserve order
    seen, out = set(), []
    for q in qs:
        q = q.strip()
        if q and q not in seen:
            seen.add(q)
            out.append(q)
    return out


def main():
    ap = argparse.ArgumentParser(description="Keyless keyword expansion via Google Autocomplete.")
    ap.add_argument("--seeds", required=True, help="comma-separated seed topics")
    ap.add_argument("--modifiers", default="base,question,comparison,commercial,guide",
                    help="comma-separated modifier sets: " + ",".join(MODIFIERS))
    ap.add_argument("--max-per-seed", type=int, default=120, help="cap suggestions kept per seed")
    ap.add_argument("--delay", type=float, default=0.15, help="polite delay between calls (s)")
    ap.add_argument("--output", default="-", help="output JSON path (default stdout)")
    args = ap.parse_args()

    seeds = [s.strip() for s in args.seeds.split(",") if s.strip()]
    modifier_keys = [m.strip() for m in args.modifiers.split(",") if m.strip()]

    result = {}
    for seed in seeds:
        collected, seen = [], set()
        for q in build_queries(seed, modifier_keys):
            for sug in fetch_suggestions(q):
                s = sug.strip()
                low = s.lower()
                if s and low not in seen:
                    seen.add(low)
                    collected.append(s)
            time.sleep(args.delay)
            if len(collected) >= args.max_per_seed:
                break
        result[seed] = collected[: args.max_per_seed]

    payload = {"seeds": seeds, "modifiers": modifier_keys, "suggestions": result,
               "total": sum(len(v) for v in result.values())}
    out = json.dumps(payload, ensure_ascii=False, indent=2)
    if args.output == "-":
        print(out)
    else:
        with open(args.output, "w", encoding="utf-8") as f:
            f.write(out + "\n")
        print(f"{payload['total']} suggestions across {len(seeds)} seeds -> {args.output}",
              file=sys.stderr)


if __name__ == "__main__":
    main()
