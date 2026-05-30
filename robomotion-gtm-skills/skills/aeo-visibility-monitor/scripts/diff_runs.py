#!/usr/bin/env python3
"""diff_runs.py — persist an AEO visibility run and diff it against the prior run.

Recurring wrapper helper for aeo-visibility-monitor. The host agent scores a run
(via the aeo-visibility flow) into a metrics blob; this script:
  1. appends the scored run to durable history (Supabase REST if SUPABASE_URL/KEY set,
     else a local CSV/JSONL ledger in the workspace),
  2. loads the immediately-prior run for the same domain,
  3. computes deterministic deltas (overall + per-engine mention rate, prominence,
     share-of-voice, new/lost competitor citations, new cited source domains),
  4. emits an alert verdict given --threshold (or competitor-overtake / drop-to-zero).

DETERMINISTIC only — the agent narrates the alert and decides whether to send it.
Stdlib only (urllib for Supabase REST). Storage is REQUIRED for this monitor: a
diff needs durable prior state.

Run-metrics JSON shape (produced by the agent from scored responses):
  {"domain": "...", "timestamp": "ISO8601", "complete": true,
   "overall": {"mention_rate": 0.42, "prominence": 0.55, "share_of_voice": 0.3},
   "per_engine": {"perplexity": {"mention_rate": 0.5, ...}, ...},
   "competitor_sov": {"rival.com": 0.4, ...},
   "competitor_citations": ["rival.com", ...],
   "source_domains": ["g2.com", ...]}

Example:
  diff_runs.py --run ${WORKSPACE}/scored_run.json --threshold 0.05 \
      --history ${WORKSPACE}/aeo_history.jsonl --output ${WORKSPACE}/diff.json
"""
import argparse
import json
import os
import sys
import time
import urllib.error
import urllib.parse
import urllib.request


def supabase_enabled():
    return bool(os.environ.get("SUPABASE_URL", "").strip()
               and os.environ.get("SUPABASE_KEY", "").strip())


def _sb_request(method, path, body=None, params=None, prefer=None):
    base = os.environ["SUPABASE_URL"].rstrip("/")
    key = os.environ["SUPABASE_KEY"]
    url = f"{base}/rest/v1/{path}"
    if params:
        url += "?" + urllib.parse.urlencode(params)
    headers = {"apikey": key, "Authorization": f"Bearer {key}",
               "Content-Type": "application/json"}
    if prefer:
        headers["Prefer"] = prefer
    data = json.dumps(body).encode("utf-8") if body is not None else None
    req = urllib.request.Request(url, data=data, method=method, headers=headers)
    for attempt in range(3):
        try:
            with urllib.request.urlopen(req, timeout=30) as r:
                txt = r.read().decode("utf-8")
                return json.loads(txt) if txt.strip() else []
        except urllib.error.HTTPError as e:
            if e.code in (429, 503) and attempt < 2:
                time.sleep(2 ** attempt)
                continue
            raise SystemExit(f"ERROR: Supabase {e.code}: {e.read().decode('utf-8','ignore')[:300]}")
        except (urllib.error.URLError, TimeoutError) as e:
            if attempt < 2:
                time.sleep(2 ** attempt)
                continue
            raise SystemExit(f"ERROR: Supabase network: {e}")


SB_TABLE = "aeo_runs"  # columns: domain text, ts text, payload jsonb


def load_prior_supabase(domain):
    rows = _sb_request("GET", SB_TABLE, params={
        "domain": f"eq.{domain}", "select": "payload",
        "order": "ts.desc", "limit": "1"})
    if rows:
        return rows[0].get("payload")
    return None


def append_supabase(run):
    _sb_request("POST", SB_TABLE,
                body={"domain": run["domain"], "ts": run["timestamp"], "payload": run},
                prefer="return=minimal")


def load_prior_file(path, domain):
    if not path or not os.path.exists(path):
        return None
    prior = None
    with open(path, encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            try:
                rec = json.loads(line)
            except json.JSONDecodeError:
                continue
            if rec.get("domain") == domain:
                prior = rec  # last matching line == most recent
    return prior


def append_file(path, run):
    with open(path, "a", encoding="utf-8") as f:
        f.write(json.dumps(run, ensure_ascii=False) + "\n")


def _g(d, *keys, default=0.0):
    for k in keys:
        d = (d or {}).get(k, {})
    return d if isinstance(d, (int, float)) else default


def diff(cur, prev, threshold):
    if not prev:
        return {"baseline": True, "alerts": [],
                "message": "baseline established (no prior run to diff)"}
    deltas = {"overall": {}, "per_engine": {}, "competitors": {}}
    alerts = []

    for metric in ("mention_rate", "prominence", "share_of_voice"):
        c = _g(cur, "overall", metric)
        p = _g(prev, "overall", metric)
        d = round(c - p, 4)
        deltas["overall"][metric] = d
        if abs(d) >= threshold:
            alerts.append(f"overall {metric} moved {d:+.2%} ({p:.2%} -> {c:.2%})")

    engines = set((cur.get("per_engine") or {})) | set((prev.get("per_engine") or {}))
    for e in sorted(engines):
        c = _g(cur, "per_engine", e, "mention_rate")
        p = _g(prev, "per_engine", e, "mention_rate")
        d = round(c - p, 4)
        deltas["per_engine"][e] = d
        if p > 0 and c == 0:
            alerts.append(f"{e} DROPPED you to zero mentions (was {p:.2%})")
        elif abs(d) >= threshold:
            alerts.append(f"{e} mention rate moved {d:+.2%}")

    cur_sov = cur.get("competitor_sov") or {}
    prev_sov = prev.get("competitor_sov") or {}
    our_sov = _g(cur, "overall", "share_of_voice")
    for comp in sorted(set(cur_sov) | set(prev_sov)):
        c = cur_sov.get(comp, 0.0)
        p = prev_sov.get(comp, 0.0)
        d = round(c - p, 4)
        deltas["competitors"][comp] = d
        if c > our_sov >= p:
            alerts.append(f"competitor {comp} OVERTOOK you in share-of-voice ({c:.2%} vs your {our_sov:.2%})")
        elif abs(d) >= threshold:
            alerts.append(f"competitor {comp} SoV moved {d:+.2%}")

    cur_cites = set(cur.get("competitor_citations") or [])
    prev_cites = set(prev.get("competitor_citations") or [])
    new_comp = sorted(cur_cites - prev_cites)
    lost_comp = sorted(prev_cites - cur_cites)

    cur_src = set(cur.get("source_domains") or [])
    prev_src = set(prev.get("source_domains") or [])
    new_src = sorted(cur_src - prev_src)

    if new_comp:
        alerts.append(f"new competitor citations: {', '.join(new_comp)}")

    return {
        "baseline": False,
        "deltas": deltas,
        "new_competitor_citations": new_comp,
        "lost_competitor_citations": lost_comp,
        "new_source_domains": new_src,
        "alerts": alerts,
        "alert": bool(alerts),
        "prev_timestamp": prev.get("timestamp", ""),
        "cur_timestamp": cur.get("timestamp", ""),
    }


def main():
    ap = argparse.ArgumentParser(description="Persist an AEO run and diff vs the prior run.")
    ap.add_argument("--run", required=True, help="scored run metrics JSON (see module docstring)")
    ap.add_argument("--threshold", type=float, default=0.05,
                    help="min absolute delta to alert on (default 0.05 = 5 pts)")
    ap.add_argument("--history", default="", help="local JSONL ledger path (used when no Supabase)")
    ap.add_argument("--no-store", action="store_true", help="diff only; do not append this run")
    ap.add_argument("--output", default="-", help="diff output JSON path (default stdout)")
    args = ap.parse_args()

    with open(args.run, encoding="utf-8") as f:
        run = json.load(f)
    if "domain" not in run or "timestamp" not in run:
        sys.exit("ERROR: run JSON must include 'domain' and 'timestamp'.")

    use_sb = supabase_enabled()
    if not use_sb and not args.history:
        sys.exit("ERROR: storage required. Set SUPABASE_URL/SUPABASE_KEY, or pass --history <path>.")

    if use_sb:
        prior = load_prior_supabase(run["domain"])
    else:
        prior = load_prior_file(args.history, run["domain"])

    # Skip diff if current run is incomplete (avoid false drop-to-zero alerts).
    if run.get("complete") is False:
        result = {"baseline": False, "alert": False, "skipped": True,
                  "message": "run marked incomplete; diff skipped to avoid false alerts"}
    else:
        result = diff(run, prior, args.threshold)

    if not args.no_store:
        if use_sb:
            append_supabase(run)
        else:
            append_file(args.history, run)
    result["stored_to"] = "supabase" if use_sb else (args.history or "none")

    out = json.dumps(result, ensure_ascii=False, indent=2)
    if args.output == "-":
        print(out)
    else:
        with open(args.output, "w", encoding="utf-8") as f:
            f.write(out + "\n")
        print(f"diff -> {args.output} (alert={result.get('alert')})", file=sys.stderr)


if __name__ == "__main__":
    main()
