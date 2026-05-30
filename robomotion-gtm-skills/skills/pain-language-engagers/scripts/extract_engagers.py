#!/usr/bin/env python3
"""extract_engagers.py — turn pain posts into people: AUTHOR + reactors/commenters.

For each qualifying pain post (from search_pain_posts.py), capture BOTH:
  - the post AUTHOR  -> role="author"  (HIGHEST intent: they VOICED the pain), and
  - the reactors/commenters -> role="engager" (intent: they resonated with it).

Extraction source chain (first available wins):
  1. Apify LinkedIn post-engagement actor (async run+poll + COST GATE)   [APIFY_API_TOKEN]
  2. PhantomBuster LinkedIn post-likers/commenters phantom               [PHANTOMBUSTER_API_KEY + LI_AT on phantom]
  3. Playwright degrade (pb_engagers_pw.mjs) — emit a run plan           [LI_AT]

Output rows:
  [{name, headline, profile_url, role, engagement_type, comment_text?, post_url,
    matched_pain_terms[], author_intent}]
where author rows ALWAYS carry the post's matched_pain_terms (they wrote the pain) and
author_intent=true. Deduped by normalized profile_url across all posts.

Example:
  extract_engagers.py --posts posts.json --source apify \
     --actor "harvestapi~linkedin-post-engagements" --max-cost-usd 1.00 --output engagers.json
"""
import argparse
import json
import os
import sys
import time
import urllib.error
import urllib.request

import pain_filter as pf  # for shared url-normalization style only

try:
    import apify_common as apify
except Exception:  # pragma: no cover
    apify = None

PB_LAUNCH = "https://api.phantombuster.com/api/v2/agents/launch"
PB_FETCH = "https://api.phantombuster.com/api/v2/agents/fetch-output"


def norm_url(u):
    if not u:
        return ""
    return u.split("?")[0].rstrip("/").lower().replace("http://", "https://")


def _g(d, *keys):
    for k in keys:
        v = d.get(k)
        if v:
            return v
    return ""


# ---- source 1: Apify --------------------------------------------------------------------
def apify_engagers(actor, post_url, max_cost, timeout):
    run_input = {"postUrl": post_url, "postUrls": [post_url], "url": post_url,
                 "includeReactions": True, "includeComments": True}
    items = apify.run_actor(actor, run_input, max_cost_usd=max_cost, timeout_s=timeout)
    rows = []
    for e in items:
        if not isinstance(e, dict):
            continue
        rows.append({
            "name": _g(e, "name", "fullName", "actorName") or "",
            "headline": _g(e, "headline", "occupation", "jobTitle", "subtitle") or "",
            "profile_url": _g(e, "profileUrl", "linkedinUrl", "url", "actorUrl") or "",
            "engagement_type": _g(e, "reactionType", "engagementType", "type") or "reaction",
            "comment_text": _g(e, "commentText", "comment", "text") or "",
        })
    return rows


# ---- source 2: PhantomBuster ------------------------------------------------------------
def pb_key():
    return os.environ.get("PHANTOMBUSTER_API_KEY", "").strip()


def pb_call(url, key, data=None):
    body = json.dumps(data).encode() if data is not None else None
    r = urllib.request.Request(
        url, data=body, method="POST" if data is not None else "GET",
        headers={"X-Phantombuster-Key-1": key, "Content-Type": "application/json"})
    for attempt in range(4):
        try:
            with urllib.request.urlopen(r, timeout=90) as resp:
                return json.loads(resp.read().decode("utf-8"))
        except urllib.error.HTTPError as e:
            if e.code in (429, 503) and attempt < 3:
                time.sleep(2 ** attempt)
                continue
            raise RuntimeError(f"Phantombuster {e.code}: "
                               f"{e.read().decode('utf-8','ignore')[:200]}")
        except urllib.error.URLError as e:
            if attempt < 3:
                time.sleep(2 ** attempt)
                continue
            raise RuntimeError(f"network: {e}")


def pb_launch_wait(key, aid, argument, timeout_s=600):
    pb_call(PB_LAUNCH, key, {"id": aid, "argument": argument})
    deadline = time.time() + timeout_s
    payload = []
    while time.time() < deadline:
        time.sleep(5)
        out = pb_call(f"{PB_FETCH}?id={aid}", key)
        data = out.get("data", {}) if isinstance(out, dict) else {}
        status = (data.get("status") or "").lower()
        if status in ("finished", "stopped"):
            payload = data.get("resultObject") or data.get("output") or []
            break
    if isinstance(payload, str):
        try:
            payload = json.loads(payload)
        except Exception:
            payload = []
    return payload if isinstance(payload, list) else []


def pb_engagers(aid, post_url, key, timeout):
    rows = []
    for e in pb_launch_wait(key, aid, {"postUrl": post_url}, timeout):
        if not isinstance(e, dict):
            continue
        rows.append({
            "name": _g(e, "fullName", "name") or "",
            "headline": _g(e, "jobTitle", "headline", "occupation") or "",
            "profile_url": _g(e, "profileUrl", "linkedinUrl") or "",
            "engagement_type": _g(e, "reactionType", "action") or "reaction",
            "comment_text": _g(e, "commentText", "comment") or "",
        })
    return rows


def main():
    ap = argparse.ArgumentParser(description="Extract authors + engagers from pain posts.")
    ap.add_argument("--posts", required=True, help="posts.json from search_pain_posts.py")
    ap.add_argument("--source", choices=["auto", "apify", "phantombuster", "playwright"],
                    default="auto")
    ap.add_argument("--actor", default=os.environ.get("APIFY_ENGAGEMENTS_ACTOR",
                    "harvestapi~linkedin-post-engagements"))
    ap.add_argument("--engagers-agent-id", default=os.environ.get("PB_ENGAGERS_AGENT_ID", ""))
    ap.add_argument("--max-cost-usd", type=float, default=1.00, help="Apify cost gate")
    ap.add_argument("--timeout-s", type=int, default=600)
    ap.add_argument("--max-engagers-per-post", type=int, default=0, help="0 = no cap")
    ap.add_argument("--output", default="-")
    args = ap.parse_args()

    with open(args.posts, encoding="utf-8") as f:
        posts = json.load(f)
    if isinstance(posts, dict):  # a degrade plan from search step, not real posts
        sys.exit("ERROR: --posts is a degrade plan, not extracted posts. Run the web-search "
                 "plan first, build posts.json of real {post_url, author_*, matched_pain_terms}.")

    # pick source
    src = args.source
    if src == "auto":
        if apify and apify.token():
            src = "apify"
        elif pb_key() and args.engagers_agent_id:
            src = "phantombuster"
        elif os.environ.get("LI_AT", "").strip():
            src = "playwright"
        else:
            sys.exit("ERROR: no extraction source. Provide ONE of: APIFY_API_TOKEN | "
                     "PHANTOMBUSTER_API_KEY + --engagers-agent-id (+LI_AT on phantom) | LI_AT.")

    if src == "playwright":
        urls = [p.get("post_url") for p in posts if p.get("post_url")]
        plan = {
            "degrade": "playwright",
            "command": ("LI_AT=<cookie> node ${SKILL_DIR}/scripts/pb_engagers_pw.mjs "
                        f"--post-urls \"{','.join(urls)}\" --output ${{WORKSPACE}}/reactors.json"),
            "note": ("Playwright scrapes REACTORS only. Merge each post's AUTHOR back in as "
                     "role='author' (highest intent) using author_name/author_profile_url "
                     "from posts.json, carrying matched_pain_terms."),
            "authors": [{"name": p.get("author_name", ""),
                         "profile_url": p.get("author_profile_url", ""),
                         "headline": p.get("author_headline", ""),
                         "post_url": p.get("post_url", ""),
                         "matched_pain_terms": p.get("matched_pain_terms", [])}
                        for p in posts],
        }
        out = json.dumps(plan, ensure_ascii=False, indent=2)
        (print(out) if args.output == "-"
         else open(args.output, "w", encoding="utf-8").write(out + "\n"))
        print(f"playwright degrade plan for {len(urls)} posts -> {args.output}", file=sys.stderr)
        return

    seen, leads = set(), []

    def add(name, headline, profile_url, role, eng_type, comment, post_url, terms):
        lk = norm_url(profile_url)
        if lk and lk in seen:
            return
        if lk:
            seen.add(lk)
        row = {"name": name, "headline": headline, "profile_url": profile_url,
               "role": role, "engagement_type": eng_type, "post_url": post_url,
               "matched_pain_terms": terms, "author_intent": role == "author"}
        if comment:
            row["comment_text"] = comment
        leads.append(row)

    key = pb_key()
    for p in posts:
        post_url = p.get("post_url") or ""
        terms = p.get("matched_pain_terms", [])
        # AUTHOR first — highest intent, always carries the pain terms they wrote
        if p.get("author_profile_url") or p.get("author_name"):
            add(p.get("author_name", ""), p.get("author_headline", ""),
                p.get("author_profile_url", ""), "author", "authored", "", post_url, terms)
        if not post_url:
            continue
        try:
            if src == "apify":
                rows = apify_engagers(args.actor, post_url, args.max_cost_usd, args.timeout_s)
            else:
                rows = pb_engagers(args.engagers_agent_id, post_url, key, args.timeout_s)
        except (apify.CostGateError if apify else Exception) as e:
            if apify and isinstance(e, apify.CostGateError):
                sys.exit(f"COST GATE: {e}")
            raise
        except Exception as e:
            print(f"WARN: extract failed on {post_url}: {e}", file=sys.stderr)
            continue
        if args.max_engagers_per_post > 0:
            rows = rows[: args.max_engagers_per_post]
        for r in rows:
            add(r["name"], r["headline"], r["profile_url"], "engager",
                r["engagement_type"], r.get("comment_text", ""), post_url, terms)

    payload = json.dumps(leads, ensure_ascii=False, indent=2)
    if args.output == "-":
        print(payload)
    else:
        with open(args.output, "w", encoding="utf-8") as f:
            f.write(payload + "\n")
    n_auth = sum(1 for x in leads if x["role"] == "author")
    print(f"{len(leads)} leads ({n_auth} authors / {len(leads)-n_auth} engagers) "
          f"via {src} -> {args.output}", file=sys.stderr)


if __name__ == "__main__":
    main()
