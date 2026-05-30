#!/usr/bin/env python3
"""select_kol_posts.py — Stage 1 of the engine: pick ONE post per KOL.

For each KOL profile, pull recent posts and choose the SINGLE most topic-relevant,
high-engagement, recent one (the hard cost lever — one post per KOL). A post must clear a
TOPIC-RELEVANCE GATE (>= --min-topic-hits topic-keyword matches) to be eligible; engagers of
an off-topic viral post are noise. Outputs the chosen post URLs to feed extract_engagers.py.

Sources (degrade-friendly):
  1. Apify profile-posts actor (--actor) with the cost-confirm gate     [primary]
  2. --posts-file  : a JSON list of posts you already have (keyless)    [degrade]

Output rows: {kol_url, post_url, post_topic, relevance_hits, engagement, posted_days_ago,
              eligible}. Only eligible=true posts are written by default.

Auth: APIFY_API_TOKEN (only for the Apify source). Stdlib only.

Examples:
  # Apify, estimate first
  select_kol_posts.py --kol-urls "https://linkedin.com/in/alice,https://linkedin.com/in/bob" \
      --topic-keywords "rpa,automation,workflow,orchestration" \
      --actor "harvestapi~linkedin-profile-posts" --estimate-only

  # Apify, confirm and pick
  select_kol_posts.py --kol-urls "..." --topic-keywords "rpa,automation" \
      --actor "harvestapi~linkedin-profile-posts" --yes --output chosen_posts.json

  # keyless: posts you already gathered (web search / manual)
  select_kol_posts.py --kol-urls "https://linkedin.com/in/alice" \
      --topic-keywords "rpa,automation" --posts-file posts.json --output chosen_posts.json
"""
import argparse
import json
import os
import sys
import time
import urllib.error
import urllib.parse
import urllib.request

APIFY_BASE = "https://api.apify.com/v2"
DEFAULT_PRICE_PER_KOL = 0.10


def apify_req(path, tok, method="GET", body=None, timeout=120):
    url = f"{APIFY_BASE}/{path}"
    sep = "&" if "?" in url else "?"
    url = f"{url}{sep}token={urllib.parse.quote(tok)}"
    data = json.dumps(body).encode() if body is not None else None
    req = urllib.request.Request(
        url, data=data, method=method,
        headers={"Content-Type": "application/json", "Accept": "application/json"},
    )
    for attempt in range(4):
        try:
            with urllib.request.urlopen(req, timeout=timeout) as r:
                txt = r.read().decode("utf-8")
                return json.loads(txt) if txt.strip() else {}
        except urllib.error.HTTPError as e:
            if e.code in (429, 503) and attempt < 3:
                time.sleep(2 ** attempt)
                continue
            sys.exit(f"ERROR: Apify {e.code}: {e.read().decode('utf-8','ignore')[:300]}")
        except urllib.error.URLError as e:
            if attempt < 3:
                time.sleep(2 ** attempt)
                continue
            sys.exit(f"ERROR: network: {e}")


def apify_run_poll(actor, payload, tok, max_wait=900):
    aid = actor.replace("/", "~")
    run = apify_req(f"acts/{aid}/runs", tok, method="POST", body=payload).get("data", {})
    run_id, ds_id = run.get("id"), run.get("defaultDatasetId")
    if not run_id:
        sys.exit("ERROR: Apify run did not start.")
    waited = 0
    while waited < max_wait:
        time.sleep(5)
        waited += 5
        st = apify_req(f"actor-runs/{run_id}", tok).get("data", {})
        ds_id = st.get("defaultDatasetId") or ds_id
        if st.get("status") in ("SUCCEEDED", "FAILED", "ABORTED", "TIMED-OUT"):
            if st.get("status") != "SUCCEEDED":
                sys.exit(f"ERROR: Apify run ended {st.get('status')}.")
            break
    else:
        sys.exit(f"ERROR: Apify run timed out (run {run_id}).")
    items = apify_req(f"datasets/{ds_id}/items?clean=true&format=json", tok)
    return items if isinstance(items, list) else []


def post_text(p):
    return str(p.get("text") or p.get("postContent") or p.get("content") or "").lower()


def post_url(p):
    return p.get("postUrl") or p.get("url") or p.get("postLink") or p.get("link") or ""


def engagement(p):
    likes = p.get("likeCount") or p.get("reactionCount") or p.get("likes") \
        or p.get("numLikes") or 0
    comments = p.get("commentCount") or p.get("comments") or p.get("numComments") or 0
    try:
        return int(likes) + int(comments)
    except (TypeError, ValueError):
        return 0


def days_ago(p):
    """Best-effort recency in days; large number if unknown (so it ranks low)."""
    for k in ("postedAtTimestamp", "timestamp", "publishedAt", "postedAt", "date"):
        v = p.get(k)
        if v is None:
            continue
        try:
            if isinstance(v, (int, float)) and v > 1e11:  # ms epoch
                return (time.time() - v / 1000) / 86400
            if isinstance(v, (int, float)):
                return (time.time() - v) / 86400
        except Exception:
            pass
    return 9999.0


def fetch_posts_apify(kol, actor, tok, num):
    payload = {"profileUrls": [kol], "maxPosts": num, "limit": num}
    raw = apify_run_poll(actor, payload, tok)
    return [p for p in raw if isinstance(p, dict)]


def choose(posts, topics, min_hits, days_back):
    """Return (best_post, hits) where best clears the topic gate, else (None, 0)."""
    scored = []
    for p in posts:
        if not post_url(p):
            continue
        if days_ago(p) > days_back:
            continue
        blob = post_text(p)
        hits = sum(1 for t in topics if t in blob)
        if hits < min_hits:
            continue
        scored.append((hits, engagement(p), -days_ago(p), p))
    if not scored:
        return None, 0
    scored.sort(key=lambda x: (x[0], x[1], x[2]), reverse=True)
    best = scored[0]
    return best[3], best[0]


def main():
    ap = argparse.ArgumentParser(description="Pick one recent topic-relevant post per KOL.")
    ap.add_argument("--kol-urls", required=True, help="comma-separated KOL profile URLs")
    ap.add_argument("--topic-keywords", required=True, help="comma-separated relevance terms")
    ap.add_argument("--min-topic-hits", type=int, default=1,
                    help="min topic-keyword matches for a post to be eligible (gate)")
    ap.add_argument("--days-back", type=int, default=30, help="recency window")
    ap.add_argument("--num-posts", type=int, default=20, help="posts to pull per KOL")
    ap.add_argument("--actor", default="harvestapi~linkedin-profile-posts",
                    help="Apify profile-posts actor id")
    ap.add_argument("--posts-file", default="",
                    help="keyless degrade: JSON list of posts (skips Apify)")
    ap.add_argument("--estimate-only", action="store_true")
    ap.add_argument("--yes", action="store_true", help="confirm Apify spend (cost gate)")
    ap.add_argument("--output", default="-")
    args = ap.parse_args()

    kols = [u.strip() for u in args.kol_urls.split(",") if u.strip()]
    topics = [t.strip().lower() for t in args.topic_keywords.split(",") if t.strip()]
    topic_label = ", ".join(t.strip() for t in args.topic_keywords.split(",") if t.strip())

    keyless = bool(args.posts_file)
    tok = os.environ.get("APIFY_API_TOKEN", "").strip()

    if not keyless:
        if not tok:
            sys.exit("ERROR: APIFY_API_TOKEN not set. Either set it (+ --actor) or pass "
                     "--posts-file for the keyless degrade.")
        est = DEFAULT_PRICE_PER_KOL * len(kols)
        msg = (f"COST ESTIMATE: {len(kols)} KOL profile(s) x ~${DEFAULT_PRICE_PER_KOL:.3f} "
               f"= ~${est:.2f} on actor '{args.actor}'.")
        if args.estimate_only:
            print(msg, file=sys.stderr)
            print(json.dumps({"estimate_usd": round(est, 2), "kols": len(kols),
                              "actor": args.actor}))
            sys.exit(0)
        if not args.yes:
            sys.exit(f"{msg}\nREFUSING to spend. Re-run with --yes, or --estimate-only.")
        print(msg + " Confirmed (--yes).", file=sys.stderr)

    preloaded = {}
    if keyless:
        with open(args.posts_file, encoding="utf-8") as f:
            data = json.load(f)
        if isinstance(data, dict):  # {kol_url: [posts]}
            preloaded = data
        else:  # flat list -> group by author profile url if present, else all-to-each
            for p in data:
                k = p.get("authorUrl") or p.get("profileUrl") or (kols[0] if kols else "")
                preloaded.setdefault(k, []).append(p)

    out = []
    for kol in kols:
        if keyless:
            posts = preloaded.get(kol) or preloaded.get(kol.rstrip("/")) or \
                (list(preloaded.values())[0] if len(kols) == 1 and preloaded else [])
        else:
            posts = fetch_posts_apify(kol, args.actor, tok, args.num_posts)
        best, hits = choose(posts, topics, args.min_topic_hits, args.days_back)
        if best is None:
            out.append({"kol_url": kol, "post_url": "", "post_topic": topic_label,
                        "relevance_hits": 0, "engagement": 0, "posted_days_ago": None,
                        "eligible": False,
                        "note": "no recent post cleared the topic-relevance gate"})
            continue
        out.append({
            "kol_url": kol,
            "post_url": post_url(best),
            "post_topic": topic_label,
            "relevance_hits": hits,
            "engagement": engagement(best),
            "posted_days_ago": round(days_ago(best), 1),
            "eligible": True,
        })

    eligible = [r for r in out if r["eligible"]]
    payload = json.dumps(out, ensure_ascii=False, indent=2)
    if args.output == "-":
        print(payload)
    else:
        with open(args.output, "w", encoding="utf-8") as f:
            f.write(payload + "\n")
        print(f"{len(eligible)}/{len(out)} KOLs got an eligible post -> {args.output}",
              file=sys.stderr)


if __name__ == "__main__":
    main()
