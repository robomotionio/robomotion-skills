#!/usr/bin/env python3
"""extract_engagers.py — Stage 2 of the KOL engager->qualified-lead engine.

Given a KOL profile (or a set of already-chosen high-engagement post URLs), extract the
people who REACTED or COMMENTED on those posts. Multi-source, degrade-friendly:

  1. Apify actor       (--actor, harvestapi-style)  primary, managed, async run+poll
  2. PhantomBuster     (PHANTOMBUSTER_API_KEY + LI_AT on the phantom)
  3. keyless Playwright (LI_AT)  -> shell out to pb_engagers_pw.mjs

A COST-CONFIRM gate guards the paid Apify path: the script estimates the run cost from the
post count and the actor's pay-per-result/compute-unit price and REFUSES to spend until you
pass --yes (or shows the estimate and exits with --estimate-only). Stdlib only.

Output rows: {name, headline, profile_url, engagement_type, comment_text?, post_url,
              kol_source, post_topic}.
The agent then runs enrich_apollo.py -> score_icp.py -> dedup_history.py.

Auth (one of):
  APIFY_API_TOKEN      [primary]
  PHANTOMBUSTER_API_KEY (+ LI_AT)            [degrade 1]
  LI_AT                                       [degrade 2, keyless Playwright]

Examples:
  # Apify, show the cost estimate then stop
  extract_engagers.py --post-urls "https://www.linkedin.com/posts/...,..." \
      --kol-source "https://linkedin.com/in/alice" --post-topic "rpa automation" \
      --actor "harvestapi~linkedin-post-reactions" --estimate-only

  # Apify, confirm spend and run
  extract_engagers.py --post-urls "..." --actor "harvestapi~linkedin-post-reactions" \
      --yes --output engagers.json

  # PhantomBuster degrade
  extract_engagers.py --post-urls "..." --source phantombuster \
      --engagers-agent-id "$PB_ENGAGERS_AGENT_ID" --output engagers.json

  # keyless Playwright degrade
  LI_AT=... extract_engagers.py --post-urls "..." --source playwright --output engagers.json
"""
import argparse
import json
import os
import subprocess
import sys
import time
import urllib.error
import urllib.parse
import urllib.request

APIFY_BASE = "https://api.apify.com/v2"
PB_LAUNCH = "https://api.phantombuster.com/api/v2/agents/launch"
PB_FETCH = "https://api.phantombuster.com/api/v2/agents/fetch-output"

# Default per-post cost assumption for the estimate gate (USD). Real price comes from the
# actor's pricing; this is a conservative fallback used only when the API gives us nothing.
DEFAULT_PRICE_PER_POST = 0.30


def norm_url(u):
    if not u:
        return ""
    return u.split("?")[0].rstrip("/").lower().replace("http://", "https://")


# ------------------------------- Apify (primary) -----------------------------

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


def apify_price_per_post(actor, tok):
    """Best-effort per-result price from the actor's public pricing; falls back to default."""
    aid = actor.replace("/", "~")
    try:
        info = apify_req(f"acts/{aid}", tok).get("data", {})
    except SystemExit:
        return DEFAULT_PRICE_PER_POST, "default"
    pricing = info.get("pricingInfos") or []
    if pricing:
        latest = pricing[-1]
        ppr = latest.get("pricePerUnitUsd")
        if isinstance(ppr, (int, float)) and ppr > 0:
            return float(ppr), "actor-pricing"
    return DEFAULT_PRICE_PER_POST, "default"


def apify_estimate(actor, n_posts, tok):
    price, basis = apify_price_per_post(actor, tok)
    return price * max(1, n_posts), price, basis


def apify_run_poll(actor, payload, tok, max_wait=900):
    aid = actor.replace("/", "~")
    run = apify_req(f"acts/{aid}/runs", tok, method="POST", body=payload).get("data", {})
    run_id = run.get("id")
    ds_id = run.get("defaultDatasetId")
    if not run_id:
        sys.exit("ERROR: Apify run did not start (no run id returned).")
    waited = 0
    while waited < max_wait:
        time.sleep(5)
        waited += 5
        st = apify_req(f"actor-runs/{run_id}", tok).get("data", {})
        status = st.get("status")
        ds_id = st.get("defaultDatasetId") or ds_id
        if status in ("SUCCEEDED", "FAILED", "ABORTED", "TIMED-OUT"):
            if status != "SUCCEEDED":
                sys.exit(f"ERROR: Apify run ended {status}.")
            break
    else:
        sys.exit(f"ERROR: Apify run still running after {max_wait}s (run {run_id}).")
    items = apify_req(f"datasets/{ds_id}/items?clean=true&format=json", tok)
    return items if isinstance(items, list) else []


def from_apify(args, tok):
    posts = [p.strip() for p in args.post_urls.split(",") if p.strip()]
    est, price, basis = apify_estimate(args.actor, len(posts), tok)
    msg = (f"COST ESTIMATE: {len(posts)} post(s) x ${price:.3f}/post ({basis}) "
           f"= ~${est:.2f} on actor '{args.actor}'.")
    if args.estimate_only:
        print(msg, file=sys.stderr)
        print(json.dumps({"estimate_usd": round(est, 2), "posts": len(posts),
                          "price_per_post": price, "basis": basis, "actor": args.actor}))
        sys.exit(0)
    if not args.yes:
        sys.exit(f"{msg}\nREFUSING to spend. Re-run with --yes to confirm, "
                 f"or --estimate-only to just see the cost.")
    print(msg + " Confirmed (--yes).", file=sys.stderr)

    payload = {args.actor_post_field: posts}
    if args.actor_input:
        payload.update(json.loads(args.actor_input))
    raw = apify_run_poll(args.actor, payload, tok)
    rows = []
    for it in raw:
        if not isinstance(it, dict):
            continue
        prof = (it.get("profileUrl") or it.get("publicProfileUrl")
                or it.get("linkedinUrl") or it.get("authorProfileUrl") or "")
        name = (it.get("name") or it.get("fullName")
                or " ".join(x for x in (it.get("firstName"), it.get("lastName")) if x).strip())
        comment = it.get("commentText") or it.get("comment") or it.get("text") or ""
        etype = (it.get("engagementType") or it.get("reactionType")
                 or ("comment" if comment else "reaction"))
        rows.append({
            "name": name,
            "headline": it.get("headline") or it.get("occupation") or it.get("jobTitle") or "",
            "profile_url": prof,
            "engagement_type": "comment" if comment else "reaction"
            if etype in ("reaction", "comment") else str(etype).lower(),
            "comment_text": comment,
            "post_url": it.get("postUrl") or it.get("post") or "",
        })
    return rows


# --------------------------- PhantomBuster (degrade 1) -----------------------

def pb_req(url, key, data=None):
    body = json.dumps(data).encode() if data is not None else None
    req = urllib.request.Request(
        url, data=body, method="POST" if data is not None else "GET",
        headers={"X-Phantombuster-Key-1": key, "Content-Type": "application/json"},
    )
    for attempt in range(4):
        try:
            with urllib.request.urlopen(req, timeout=90) as r:
                return json.loads(r.read().decode("utf-8"))
        except urllib.error.HTTPError as e:
            if e.code in (429, 503) and attempt < 3:
                time.sleep(2 ** attempt)
                continue
            sys.exit(f"ERROR: Phantombuster {e.code}: {e.read().decode('utf-8','ignore')[:300]}")
        except urllib.error.URLError as e:
            if attempt < 3:
                time.sleep(2 ** attempt)
                continue
            sys.exit(f"ERROR: network: {e}")


def pb_launch_wait(key, aid, argument):
    pb_req(PB_LAUNCH, key, {"id": aid, "argument": argument})
    payload = []
    for _ in range(120):
        time.sleep(5)
        out = pb_req(f"{PB_FETCH}?id={aid}", key)
        d = out.get("data", {}) if isinstance(out, dict) else {}
        if (d.get("status") or "").lower() in ("finished", "stopped"):
            payload = d.get("resultObject") or d.get("output") or []
            break
    if isinstance(payload, str):
        try:
            payload = json.loads(payload)
        except Exception:
            payload = []
    return payload if isinstance(payload, list) else []


def from_phantombuster(args):
    key = os.environ.get("PHANTOMBUSTER_API_KEY", "").strip()
    if not key:
        sys.exit("ERROR: PHANTOMBUSTER_API_KEY not set for --source phantombuster.")
    aid = args.engagers_agent_id or os.environ.get("PB_ENGAGERS_AGENT_ID", "")
    if not aid:
        sys.exit("ERROR: --engagers-agent-id (or PB_ENGAGERS_AGENT_ID) required for phantombuster.")
    posts = [p.strip() for p in args.post_urls.split(",") if p.strip()]
    rows = []
    for post_url in posts:
        for e in pb_launch_wait(key, aid, {"postUrl": post_url}):
            if not isinstance(e, dict):
                continue
            comment = e.get("commentText") or e.get("comment") or ""
            rows.append({
                "name": e.get("fullName") or e.get("name") or "",
                "headline": e.get("headline") or e.get("jobTitle") or "",
                "profile_url": e.get("profileUrl") or e.get("linkedinUrl") or "",
                "engagement_type": "comment" if comment else "reaction",
                "comment_text": comment,
                "post_url": post_url,
            })
    return rows


# ---------------------------- Playwright (degrade 2) -------------------------

def from_playwright(args):
    if not os.environ.get("LI_AT", "").strip():
        sys.exit("ERROR: LI_AT not set for --source playwright.")
    here = os.path.dirname(os.path.abspath(__file__))
    mjs = os.path.join(here, "pb_engagers_pw.mjs")
    cmd = ["node", mjs, "--post-urls", args.post_urls, "--output", "-"]
    if args.limit:
        cmd += ["--limit", str(args.limit)]
    res = subprocess.run(cmd, capture_output=True, text=True)
    if res.returncode != 0:
        sys.exit(f"ERROR: Playwright degrade failed: {res.stderr.strip()[:300]}")
    try:
        raw = json.loads(res.stdout or "[]")
    except json.JSONDecodeError:
        sys.exit("ERROR: Playwright degrade returned non-JSON.")
    rows = []
    for r in raw:
        rows.append({
            "name": r.get("name", ""),
            "headline": r.get("title") or r.get("headline") or "",
            "profile_url": r.get("linkedin_url") or r.get("profile_url") or "",
            "engagement_type": r.get("engagement_type") or "reaction",
            "comment_text": r.get("comment_text", ""),
            "post_url": r.get("source_post") or r.get("post_url") or "",
        })
    return rows


# ------------------------------ source selection -----------------------------

def auto_source(args):
    if args.actor and os.environ.get("APIFY_API_TOKEN", "").strip():
        return "apify"
    if os.environ.get("PHANTOMBUSTER_API_KEY", "").strip() and \
       (args.engagers_agent_id or os.environ.get("PB_ENGAGERS_AGENT_ID", "")):
        return "phantombuster"
    if os.environ.get("LI_AT", "").strip():
        return "playwright"
    sys.exit("ERROR: no engager source available. Provide ONE of: APIFY_API_TOKEN (+ --actor), "
             "PHANTOMBUSTER_API_KEY (+ engagers-agent-id), or LI_AT.")


def main():
    ap = argparse.ArgumentParser(description="Extract KOL post reactors+commenters (multi-source).")
    ap.add_argument("--post-urls", required=True, help="comma-separated chosen post URLs")
    ap.add_argument("--kol-source", default="", help="KOL profile URL these posts belong to (tag)")
    ap.add_argument("--post-topic", default="", help="topic label of the chosen post (tag)")
    ap.add_argument("--source", choices=["auto", "apify", "phantombuster", "playwright"],
                    default="auto")
    # Apify
    ap.add_argument("--actor", default="harvestapi~linkedin-post-reactions",
                    help="Apify actor id (harvestapi-style)")
    ap.add_argument("--actor-post-field", default="postUrls",
                    help="actor input field name for the post URL list")
    ap.add_argument("--actor-input", default="", help="extra actor input as inline JSON")
    ap.add_argument("--estimate-only", action="store_true", help="print cost estimate and exit")
    ap.add_argument("--yes", action="store_true", help="confirm Apify spend (cost gate)")
    # PhantomBuster
    ap.add_argument("--engagers-agent-id", default="", help="PhantomBuster engager agent id")
    # shared
    ap.add_argument("--limit", type=int, default=0, help="cap engagers per post (Playwright)")
    ap.add_argument("--output", default="-", help="output JSON path (default stdout)")
    args = ap.parse_args()

    source = auto_source(args) if args.source == "auto" else args.source
    print(f"engager source: {source}", file=sys.stderr)

    if source == "apify":
        tok = os.environ.get("APIFY_API_TOKEN", "").strip()
        if not tok:
            sys.exit("ERROR: APIFY_API_TOKEN not set for --source apify.")
        rows = from_apify(args, tok)
    elif source == "phantombuster":
        rows = from_phantombuster(args)
    else:
        rows = from_playwright(args)

    # tag + intra-run dedup by normalized profile_url
    seen, out = set(), []
    for r in rows:
        r["comment_text"] = r.get("comment_text") or ""
        if not r["comment_text"]:
            r.pop("comment_text", None)
        r["kol_source"] = args.kol_source
        r["post_topic"] = args.post_topic
        k = norm_url(r.get("profile_url", ""))
        if k and k in seen:
            continue
        if k:
            seen.add(k)
        out.append(r)

    payload = json.dumps(out, ensure_ascii=False, indent=2)
    if args.output == "-":
        print(payload)
    else:
        with open(args.output, "w", encoding="utf-8") as f:
            f.write(payload + "\n")
        print(f"{len(out)} engagers ({source}) -> {args.output}", file=sys.stderr)


if __name__ == "__main__":
    main()
