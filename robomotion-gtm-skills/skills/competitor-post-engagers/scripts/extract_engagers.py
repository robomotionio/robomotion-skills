#!/usr/bin/env python3
"""extract_engagers.py — extract LinkedIn post reactors + commenters (multi-source).

Engine step 1 of the engager->qualified-lead pipeline. Given one or more LinkedIn
post URLs, pull everyone who liked / reacted / commented / reposted them. Engagers of a
COMPETITOR's content are warm, category-aware leads — each row is tagged with the source
post (and the competitor it belongs to, if --competitor is passed).

Source priority (multi-source fallback — at least one must be configured):
  1. Apify actor  (APIFY_API_TOKEN)        — primary; managed async run + poll lifecycle,
                                              with a COST-CONFIRM gate (--estimate-only /
                                              --yes) so you never spend silently.
  2. PhantomBuster (PHANTOMBUSTER_API_KEY + a LinkedIn session cookie on the phantom).
  3. Playwright    (LI_AT cookie)          — keyless local-browser degrade, lowest volume.

Stdlib only (Apify + PhantomBuster paths). The Playwright path shells out to the bundled
pb_engagers_pw.mjs (needs `npx playwright install chromium`).

Output rows (JSON list):
  {name, headline, profile_url, engagement_type(like|reaction|comment|repost),
   comment_text?, post_url, competitor?, source}

Examples:
  # Estimate Apify cost first (no spend, no --yes):
  extract_engagers.py --source apify --post-urls "URL1,URL2" --estimate-only

  # Actually run Apify (must pass --yes to spend):
  extract_engagers.py --source apify --post-urls "URL1,URL2" \
      --competitor "Acme" --yes --output engagers.json

  # PhantomBuster degrade:
  extract_engagers.py --source phantombuster --engagers-agent-id B \
      --post-urls "URL1" --output engagers.json

  # Keyless Playwright degrade:
  LI_AT=... extract_engagers.py --source playwright --post-urls "URL1" --output engagers.json
"""
import argparse
import json
import os
import subprocess
import sys
import time
import urllib.error
import urllib.request

APIFY_BASE = "https://api.apify.com/v2"
PB_LAUNCH = "https://api.phantombuster.com/api/v2/agents/launch"
PB_FETCH = "https://api.phantombuster.com/api/v2/agents/fetch-output"

# Default actor: a harvestapi-style LinkedIn post reactions/comments scraper.
# Override with --actor for any actor whose input takes a list of post URLs.
DEFAULT_ACTOR = "harvestapi~linkedin-post-reactions"
# Conservative public list-price estimate for harvestapi-style engager actors,
# USD per 1,000 engager records returned. Override with --price-per-1k.
DEFAULT_PRICE_PER_1K = 2.0
# Typical engagers harvested per post when unknown (for the pre-run estimate only).
EST_ENGAGERS_PER_POST = 120


# --------------------------------------------------------------------------- helpers
def norm_url(u):
    if not u:
        return ""
    u = u.split("?")[0].rstrip("/").lower()
    return u.replace("http://", "https://")


def classify_engagement(raw):
    """Map a source's free-form action label to like|reaction|comment|repost."""
    t = (raw or "").strip().lower()
    if not t:
        return "reaction"
    if "comment" in t:
        return "comment"
    if "repost" in t or "reshare" in t or "share" in t:
        return "repost"
    if t in ("like", "likes"):
        return "like"
    return "reaction"


def normalize_engager(e, post_url, competitor, source):
    """Coerce a heterogeneous source row into the engine's canonical schema."""
    name = (e.get("fullName") or e.get("name")
            or f"{e.get('firstName','')} {e.get('lastName','')}".strip())
    headline = (e.get("headline") or e.get("jobTitle") or e.get("occupation")
                or e.get("title") or "")
    purl = (e.get("profileUrl") or e.get("linkedinUrl") or e.get("profileLink")
            or e.get("publicProfileUrl") or e.get("url") or "")
    etype = classify_engagement(
        e.get("engagement_type") or e.get("reactionType") or e.get("type")
        or e.get("action") or ("comment" if e.get("commentText") or e.get("comment") else ""))
    comment_text = e.get("comment_text") or e.get("commentText") or e.get("comment") or ""
    row = {
        "name": name,
        "headline": headline,
        "profile_url": purl,
        "engagement_type": etype,
        "post_url": post_url,
        "source": source,
    }
    if comment_text:
        row["comment_text"] = comment_text
    if competitor:
        row["competitor"] = competitor
    return row


def dedup_and_emit(rows, output):
    seen, out = set(), []
    for r in rows:
        k = norm_url(r.get("profile_url"))
        # Same person may both like AND comment; keep the richer (comment) row.
        if k and k in seen:
            for ex in out:
                if norm_url(ex["profile_url"]) == k and r.get("comment_text") and not ex.get("comment_text"):
                    ex["engagement_type"] = "comment"
                    ex["comment_text"] = r["comment_text"]
            continue
        if k:
            seen.add(k)
        out.append(r)
    payload = json.dumps(out, ensure_ascii=False, indent=2)
    if output == "-":
        print(payload)
    else:
        with open(output, "w", encoding="utf-8") as f:
            f.write(payload + "\n")
        print(f"{len(out)} engagers ({len(rows)} pre-dedup) -> {output}", file=sys.stderr)
    return out


# --------------------------------------------------------------------------- Apify
def apify_token():
    k = os.environ.get("APIFY_API_TOKEN", "").strip()
    if not k:
        sys.exit("ERROR: APIFY_API_TOKEN not set (required for --source apify). "
                 "Use --source phantombuster or --source playwright instead.")
    return k


def apify_req(url, token, method="GET", body=None, timeout=120):
    data = json.dumps(body).encode() if body is not None else None
    sep = "&" if "?" in url else "?"
    req = urllib.request.Request(
        f"{url}{sep}token={token}", data=data, method=method,
        headers={"Content-Type": "application/json"})
    for attempt in range(4):
        try:
            with urllib.request.urlopen(req, timeout=timeout) as r:
                raw = r.read().decode("utf-8")
                return json.loads(raw) if raw.strip() else {}
        except urllib.error.HTTPError as e:
            if e.code in (429, 502, 503) and attempt < 3:
                time.sleep(2 ** attempt)
                continue
            sys.exit(f"ERROR: Apify {e.code}: {e.read().decode('utf-8','ignore')[:300]}")
        except urllib.error.URLError as e:
            if attempt < 3:
                time.sleep(2 ** attempt)
                continue
            sys.exit(f"ERROR: network: {e}")


def apify_estimate(posts, price_per_1k):
    est_records = len(posts) * EST_ENGAGERS_PER_POST
    est_cost = (est_records / 1000.0) * price_per_1k
    return est_records, est_cost


def extract_apify(args, posts):
    token = apify_token()
    actor = args.actor.replace("/", "~")
    est_records, est_cost = apify_estimate(posts, args.price_per_1k)

    # ---- COST-CONFIRM GATE -------------------------------------------------
    print(
        f"[cost-estimate] actor={actor} posts={len(posts)} "
        f"~{est_records} engager records  ~${est_cost:.2f} "
        f"(@ ${args.price_per_1k:.2f}/1k; estimate only)", file=sys.stderr)
    if args.estimate_only:
        print(json.dumps({"actor": actor, "posts": len(posts),
                          "est_records": est_records, "est_cost_usd": round(est_cost, 2),
                          "price_per_1k": args.price_per_1k}, indent=2))
        sys.exit(0)
    if not args.yes:
        sys.exit("REFUSED: Apify run would spend credits. Re-run with --yes to confirm "
                 "(or --estimate-only to just print the projected cost). No spend made.")
    # ------------------------------------------------------------------------

    actor_input = {"postUrls": posts, "urls": posts, "posts": posts,
                   "maxItems": args.max_per_post * len(posts) if args.max_per_post else None}
    actor_input = {k: v for k, v in actor_input.items() if v is not None}

    run = apify_req(f"{APIFY_BASE}/acts/{actor}/runs", token, "POST", actor_input)
    run_id = (run.get("data") or {}).get("id")
    dataset_id = (run.get("data") or {}).get("defaultDatasetId")
    if not run_id:
        sys.exit(f"ERROR: Apify did not return a run id: {json.dumps(run)[:300]}")

    # ---- async poll lifecycle ---------------------------------------------
    for _ in range(180):  # up to ~15 min at 5s
        time.sleep(5)
        st = apify_req(f"{APIFY_BASE}/actor-runs/{run_id}", token)
        status = ((st.get("data") or {}).get("status") or "").upper()
        dataset_id = (st.get("data") or {}).get("defaultDatasetId") or dataset_id
        if status in ("SUCCEEDED", "FAILED", "ABORTED", "TIMED-OUT"):
            if status != "SUCCEEDED":
                print(f"WARN: Apify run ended {status}; emitting whatever landed.", file=sys.stderr)
            break
    items = apify_req(f"{APIFY_BASE}/datasets/{dataset_id}/items?clean=true&format=json", token)
    if isinstance(items, dict):
        items = items.get("items") or items.get("data") or []

    rows = []
    for it in items if isinstance(items, list) else []:
        if not isinstance(it, dict):
            continue
        post = it.get("postUrl") or it.get("post_url") or (posts[0] if len(posts) == 1 else "")
        rows.append(normalize_engager(it, post, args.competitor, "apify"))
    return rows


# --------------------------------------------------------------------------- PhantomBuster
def pb_key():
    k = os.environ.get("PHANTOMBUSTER_API_KEY", "").strip()
    if not k:
        sys.exit("ERROR: PHANTOMBUSTER_API_KEY not set (required for --source phantombuster).")
    return k


def pb_req(url, key, body=None):
    data = json.dumps(body).encode() if body is not None else None
    req = urllib.request.Request(
        url, data=data, method="POST" if body is not None else "GET",
        headers={"X-Phantombuster-Key-1": key, "Content-Type": "application/json"})
    for attempt in range(4):
        try:
            with urllib.request.urlopen(req, timeout=90) as r:
                return json.loads(r.read().decode("utf-8"))
        except urllib.error.HTTPError as e:
            if e.code in (429, 503) and attempt < 3:
                time.sleep(2 ** attempt)
                continue
            sys.exit(f"ERROR: PhantomBuster {e.code}: {e.read().decode('utf-8','ignore')[:300]}")
        except urllib.error.URLError as e:
            if attempt < 3:
                time.sleep(2 ** attempt)
                continue
            sys.exit(f"ERROR: network: {e}")


def pb_rows(payload):
    if isinstance(payload, dict):
        payload = payload.get("resultObject") or payload.get("data") or []
    if isinstance(payload, str):
        try:
            payload = json.loads(payload)
        except Exception:
            payload = []
    return payload if isinstance(payload, list) else []


def extract_phantombuster(args, posts):
    key = pb_key()
    aid = args.engagers_agent_id or os.environ.get("PB_ENGAGERS_AGENT_ID", "")
    if not aid:
        sys.exit("ERROR: --engagers-agent-id (or PB_ENGAGERS_AGENT_ID) required for phantombuster.")
    rows = []
    for post in posts:
        res = pb_req(PB_LAUNCH, key, {"id": aid, "argument": {"postUrl": post}})
        for _ in range(120):
            time.sleep(5)
            out = pb_req(f"{PB_FETCH}?id={aid}", key)
            status = ((out.get("data") or {}).get("status") or "").lower()
            if status in ("finished", "stopped"):
                break
        payload = res.get("data") if isinstance(res, dict) else res
        for e in pb_rows(payload):
            if isinstance(e, dict):
                rows.append(normalize_engager(e, post, args.competitor, "phantombuster"))
    return rows


# --------------------------------------------------------------------------- Playwright
def extract_playwright(args, posts):
    if not os.environ.get("LI_AT", "").strip():
        sys.exit("ERROR: LI_AT (LinkedIn li_at cookie) required for --source playwright.")
    script = os.path.join(os.path.dirname(os.path.abspath(__file__)), "pb_engagers_pw.mjs")
    cmd = ["node", script, "--post-urls", ",".join(posts)]
    if args.max_per_post:
        cmd += ["--limit", str(args.max_per_post * len(posts))]
    res = subprocess.run(cmd, capture_output=True, text=True)
    if res.returncode != 0:
        sys.exit(f"ERROR: playwright degrade failed: {res.stderr[:400]}")
    try:
        raw = json.loads(res.stdout or "[]")
    except Exception:
        sys.exit(f"ERROR: could not parse playwright output: {res.stdout[:200]}")
    rows = []
    for e in raw:
        r = normalize_engager(e, e.get("source_post") or e.get("post_url") or "",
                              args.competitor, "playwright")
        rows.append(r)
    return rows


# --------------------------------------------------------------------------- main
def main():
    ap = argparse.ArgumentParser(
        description="Extract LinkedIn post reactors/commenters (Apify | PhantomBuster | Playwright).")
    ap.add_argument("--source", choices=["apify", "phantombuster", "playwright"],
                    default="apify", help="extraction backend (default apify)")
    ap.add_argument("--post-urls", required=True, help="comma-separated LinkedIn post URLs")
    ap.add_argument("--competitor", default="", help="tag every row with this competitor name")
    # Apify
    ap.add_argument("--actor", default=DEFAULT_ACTOR,
                    help=f"Apify actor id (default {DEFAULT_ACTOR})")
    ap.add_argument("--estimate-only", action="store_true",
                    help="Apify: print projected cost and exit (no spend)")
    ap.add_argument("--yes", action="store_true",
                    help="Apify: confirm spend (required to actually run the actor)")
    ap.add_argument("--price-per-1k", type=float, default=DEFAULT_PRICE_PER_1K,
                    help=f"Apify cost estimate USD/1k records (default {DEFAULT_PRICE_PER_1K})")
    ap.add_argument("--max-per-post", type=int, default=0, help="cap engagers per post (0=actor default)")
    # PhantomBuster
    ap.add_argument("--engagers-agent-id", default="", help="PhantomBuster post-engager agent id")
    ap.add_argument("--output", default="-")
    args = ap.parse_args()

    posts = [u.strip() for u in args.post_urls.split(",") if u.strip()]
    if not posts:
        sys.exit("ERROR: no post URLs given.")

    if args.source == "apify":
        rows = extract_apify(args, posts)
    elif args.source == "phantombuster":
        rows = extract_phantombuster(args, posts)
    else:
        rows = extract_playwright(args, posts)

    dedup_and_emit(rows, args.output)


if __name__ == "__main__":
    main()
