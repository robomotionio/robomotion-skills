#!/usr/bin/env python3
"""search_pain_posts.py — find LinkedIn posts EXPRESSING the pain (not selling the fix).

Given agent-generated pain-language keywords, search LinkedIn posts via an Apify
LinkedIn-post-search actor (async run+poll + COST GATE), then apply the vendored
pain-vs-solution DISCIPLINE (pain_filter.py): keep posts living the problem, drop
vendor/announcement/self-promo/hiring/listicle posts. Degrade to keyless web-search
(site:linkedin.com/posts) when no Apify token.

Auth: APIFY_API_TOKEN (optional — degrade emits a keyless web-search plan the agent runs).

Output: candidate posts -> [{post_url, author_name, author_profile_url, text,
                              matched_pain_terms[], reason, source}].

Example:
  search_pain_posts.py \
    --pain-terms "manual data entry,copy paste between systems,spreadsheet hell" \
    --pain-regex "still (doing|using).*(manually|by hand)" \
    --actor "harvestapi~linkedin-post-search" \
    --posts-per-term 10 --max-cost-usd 1.00 --output posts.json
"""
import argparse
import json
import os
import sys

import pain_filter as pf

try:
    import apify_common as apify
except Exception:  # pragma: no cover
    apify = None


def _g(d, *keys):
    for k in keys:
        v = d.get(k)
        if v:
            return v
    return ""


def from_apify(actor, term, n, max_cost, timeout):
    """Run the actor for one pain term; return raw post dicts. Field names vary by actor."""
    run_input = {
        "searchQueries": [term], "query": term, "search": term,
        "maxPosts": n, "maxItems": n, "limit": n, "postsPerQuery": n,
        "sortBy": "date",
    }
    items = apify.run_actor(actor, run_input, max_cost_usd=max_cost, timeout_s=timeout)
    return [it for it in items if isinstance(it, dict)]


def normalize_post(p):
    return {
        "post_url": _g(p, "postUrl", "url", "postLink", "link", "shareUrl"),
        "author_name": _g(p, "authorName", "author", "fullName", "name",
                          "actorName") or "",
        "author_profile_url": _g(p, "authorProfileUrl", "profileUrl", "authorUrl",
                                 "linkedinUrl", "actorUrl") or "",
        "author_headline": _g(p, "authorHeadline", "headline", "occupation") or "",
        "text": pf.post_text(p),
    }


def web_search_plan(terms, regex, per_term, exclude_file):
    """Keyless degrade: a deterministic site:linkedin.com/posts search plan + filter spec
    the host agent executes with its own web-search, then re-runs pain_filter on results."""
    queries = []
    for t in terms:
        queries.append(f'site:linkedin.com/posts "{t}"')
    return {
        "degrade": "web-search",
        "instructions": (
            "No APIFY_API_TOKEN. Run each query below with your web-search tool, collect "
            "the linkedin.com/posts result URLs + snippet text into a posts.json array of "
            "{url, text}, then run: pain_filter.py --posts posts.json --pain-terms '<terms>' "
            "--pain-regex '<regex>' to apply the SAME pain-vs-solution discipline. Keep only "
            "the 'kept' posts as candidates. The post AUTHOR is the highest-intent lead."),
        "queries": queries,
        "per_term": per_term,
        "pain_terms": terms,
        "pain_regex": regex,
        "exclude_file": exclude_file or "(built-in pain_filter lexicon)",
    }


def main():
    ap = argparse.ArgumentParser(description="Find LinkedIn posts expressing the pain.")
    ap.add_argument("--pain-terms", default="", help="comma-separated pain include terms")
    ap.add_argument("--pain-terms-file", default="", help="file: one pain term per line")
    ap.add_argument("--pain-regex", default="", help="optional pain pattern (Python regex)")
    ap.add_argument("--exclude-file", default="", help="extra exclude terms (one per line)")
    ap.add_argument("--actor", default=os.environ.get("APIFY_POST_SEARCH_ACTOR",
                    "harvestapi~linkedin-post-search"),
                    help="Apify LinkedIn-post-search actor (configurable)")
    ap.add_argument("--posts-per-term", type=int, default=10)
    ap.add_argument("--max-cost-usd", type=float, default=1.00,
                    help="Apify cost gate; run aborts above this (default 1.00)")
    ap.add_argument("--timeout-s", type=int, default=600)
    ap.add_argument("--output", default="-")
    args = ap.parse_args()

    terms = [t.strip() for t in args.pain_terms.split(",") if t.strip()]
    terms += pf.load_lines(args.pain_terms_file) or []
    if not terms and not args.pain_regex:
        sys.exit("ERROR: provide --pain-terms / --pain-terms-file or --pain-regex.")
    excludes = list(pf.DEFAULT_EXCLUDES) + (pf.load_lines(args.exclude_file) or [])

    tok = apify.token() if apify else ""
    if not tok:
        plan = web_search_plan(terms, args.pain_regex, args.posts_per_term, args.exclude_file)
        payload = json.dumps(plan, ensure_ascii=False, indent=2)
        if args.output == "-":
            print(payload)
        else:
            with open(args.output, "w", encoding="utf-8") as f:
                f.write(payload + "\n")
        print("No APIFY_API_TOKEN -> emitted keyless web-search degrade plan.", file=sys.stderr)
        return

    seen, kept = set(), []
    dropped = 0
    for term in terms:
        try:
            raw = from_apify(args.actor, term, args.posts_per_term, args.max_cost_usd,
                             args.timeout_s)
        except apify.CostGateError as e:
            sys.exit(f"COST GATE: {e}")
        except apify.ApifyError as e:
            print(f"WARN: actor failed on '{term}': {e}", file=sys.stderr)
            continue
        for p in raw:
            np = normalize_post(p)
            url = np["post_url"]
            key = (url or np["text"][:120]).lower()
            if key in seen:
                continue
            res = pf.classify_post(np["text"], terms, excludes, args.pain_regex or None)
            if not res["keep"]:
                dropped += 1
                continue
            seen.add(key)
            np["matched_pain_terms"] = res["matched_pain_terms"]
            np["reason"] = res["reason"]
            np["source"] = f"apify:{args.actor}"
            kept.append(np)

    payload = json.dumps(kept, ensure_ascii=False, indent=2)
    if args.output == "-":
        print(payload)
    else:
        with open(args.output, "w", encoding="utf-8") as f:
            f.write(payload + "\n")
    print(f"{len(kept)} pain posts kept, {dropped} solution/announce posts dropped -> "
          f"{args.output}", file=sys.stderr)


if __name__ == "__main__":
    main()
