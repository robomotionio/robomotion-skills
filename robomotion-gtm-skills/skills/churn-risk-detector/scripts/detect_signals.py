#!/usr/bin/env python3
"""detect_signals.py — deterministic, threshold-/keyword-based churn signal extraction.

NO LLM. Reads whatever signal sources exist (customer list + optional tickets, comms log,
usage export, billing export, survey export) and emits the per-account signals JSON that
score_accounts.py consumes. Only the *mechanical* detections live here (counts, dates,
thresholds, escalation keywords); the host agent adds the deeper sentiment/relationship
reads (negative-sentiment shift in tone, new-stakeholder basic questions) from its own
reading and merges them in before scoring.

COMPREHENSIVE SIGNAL CATALOG (each carries a fixed severity feeding score_accounts.py):
  usage      : usage/seat decline, login-frequency drop, feature abandonment
  support    : unresolved-ticket age, ticket-volume spike, escalation language
  commercial : renewal proximity (no engagement), payment failure, downgrade/seat-reduction,
               discount request
  engagement : gone-silent (comms gap)
  relationship: champion departure, exec/sponsor turnover
  sentiment  : NPS/CSAT drop (numeric), detractor score

All inputs are CSV (keyless). Customer list is required; everything else is optional and
each missing source simply drops its lens (graceful degrade).

CSV shapes (case-insensitive headers; extra columns ignored):
  --customers : account, mrr, renewal_date[, seats]               (renewal_date YYYY-MM-DD)
  --tickets   : account, date, subject[, body], status, resolution_days
  --comms     : account, date                                     (last-touch rows; latest used)
  --usage     : account, logins_prev, logins_curr[, active_users_prev, active_users_curr,
                seats_prev, seats_curr, features_prev, features_curr]
  --billing   : account, event   (payment_failure|downgrade|seat_reduction|discount_request)
  --survey    : account[, nps_prev, nps_curr][, csat_prev, csat_curr][, nps][, csat]
  --people    : account, role, status   (status=departed|left|churned; role=champion|exec|sponsor)

Example:
  detect_signals.py --customers c.csv --tickets t.csv --usage u.csv --survey s.csv \
     --silence-days 30 --renewal-window 60 --output signals.json
"""
import argparse
import csv
import json
import sys
from collections import defaultdict
from datetime import datetime, timezone

ESCALATION_WORDS = ("cancel", "frustrated", "frustrating", "alternative", "competitor",
                    "switch", "refund", "unhappy", "disappointed", "escalate", "unacceptable",
                    "churn", "terminate", "not renewing", "deprovision")
DEPARTURE_STATUS = ("departed", "left", "gone", "churned", "resigned", "no longer", "offboarded")
KEY_ROLES = ("champion", "advocate", "sponsor")
EXEC_ROLES = ("exec", "executive", "vp", "chief", "cxo", "ceo", "cto", "coo", "cfo", "cmo",
              "director", "head of", "sponsor")


def now():
    return datetime.now(timezone.utc)


def pdate(s):
    if not s:
        return None
    s = str(s).strip()
    for fmt in ("%Y-%m-%d", "%m/%d/%Y", "%d/%m/%Y", "%Y-%m-%dT%H:%M:%S"):
        try:
            return datetime.strptime(s[:19] if "T" in s else s, fmt).replace(tzinfo=timezone.utc)
        except ValueError:
            continue
    return None


def read_csv(path):
    if not path:
        return []
    with open(path, newline="", encoding="utf-8-sig") as f:
        rows = []
        for r in csv.DictReader(f):
            rows.append({(k or "").strip().lower(): (v or "").strip() for k, v in r.items()})
        return rows


def fnum(v):
    try:
        return float(str(v).replace(",", "").replace("$", ""))
    except (ValueError, TypeError):
        return None


def acct_of(r):
    return r.get("account") or r.get("company") or r.get("customer")


def pct_drop(prev, cur):
    if prev and cur is not None and prev > 0:
        return (prev - cur) / prev * 100
    return None


def main():
    ap = argparse.ArgumentParser(description="Deterministic churn signal extraction (keyword/threshold).")
    ap.add_argument("--customers", required=True, help="customer list CSV (account,mrr,renewal_date[,seats])")
    ap.add_argument("--tickets", default="", help="support tickets CSV")
    ap.add_argument("--comms", default="", help="comms last-touch CSV")
    ap.add_argument("--usage", default="", help="usage CSV (logins/seats/active_users/features prev+curr)")
    ap.add_argument("--billing", default="", help="billing events CSV")
    ap.add_argument("--survey", default="", help="NPS/CSAT survey CSV")
    ap.add_argument("--people", default="", help="account stakeholders CSV (role,status)")
    ap.add_argument("--silence-days", type=int, default=30, help="comms-silence threshold (default 30)")
    ap.add_argument("--renewal-window", type=int, default=60, help="renewal-soon window in days (default 60)")
    ap.add_argument("--unresolved-days", type=int, default=7, help="ticket unresolved threshold (default 7)")
    ap.add_argument("--usage-drop-pct", type=float, default=30.0, help="login-drop %% threshold (default 30)")
    ap.add_argument("--seat-drop-pct", type=float, default=15.0, help="seat-reduction %% threshold (default 15)")
    ap.add_argument("--feature-drop-pct", type=float, default=40.0, help="feature-abandonment %% threshold")
    ap.add_argument("--nps-drop", type=float, default=2.0, help="absolute NPS-point drop threshold (default 2)")
    ap.add_argument("--csat-drop", type=float, default=1.0, help="absolute CSAT-point drop threshold (default 1)")
    ap.add_argument("--ticket-spike", type=int, default=5, help="ticket-count spike threshold (default 5)")
    ap.add_argument("--output", default="-", help="output signals JSON (default stdout)")
    args = ap.parse_args()

    customers = read_csv(args.customers)
    if not customers:
        sys.exit("ERROR: --customers CSV is empty or missing.")

    sig = defaultdict(list)
    meta = {}
    for c in customers:
        acct = acct_of(c)
        if not acct:
            continue
        meta[acct] = {"mrr": fnum(c.get("mrr") or c.get("arr")),
                      "renewal_date": c.get("renewal_date", ""),
                      "seats": fnum(c.get("seats"))}
        # renewal proximity — high if soon, critical if very soon (<=14d)
        rd = pdate(c.get("renewal_date"))
        if rd:
            days = (rd - now()).days
            if 0 <= days <= args.renewal_window:
                sev = "critical" if days <= 14 else "high"
                sig[acct].append({"name": f"renewal in {days}d", "severity": sev,
                                  "lens": "commercial", "note": "verify a renewal discussion is underway"})

    # ---- tickets: unresolved >N days, escalation language, volume spike ----
    tcount = defaultdict(int)
    for t in read_csv(args.tickets):
        acct = acct_of(t)
        if not acct:
            continue
        tcount[acct] += 1
        status = (t.get("status") or "").lower()
        rdays = fnum(t.get("resolution_days"))
        if status not in ("closed", "resolved", "done") and rdays is not None and rdays > args.unresolved_days:
            sig[acct].append({"name": f"ticket unresolved >{args.unresolved_days}d", "severity": "high",
                              "lens": "support", "note": t.get("subject", "")})
        blob = (t.get("subject", "") + " " + t.get("body", "")).lower()
        hits = [w for w in ESCALATION_WORDS if w in blob]
        if hits:
            sig[acct].append({"name": "escalation language: " + ", ".join(hits[:3]),
                              "severity": "critical", "lens": "support", "note": t.get("subject", "")})
    for acct, n in tcount.items():
        if n >= args.ticket_spike:
            sig[acct].append({"name": f"support-ticket spike ({n} tickets)", "severity": "medium",
                              "lens": "support"})

    # ---- comms silence ----
    last_touch = {}
    for r in read_csv(args.comms):
        acct = acct_of(r)
        d = pdate(r.get("date"))
        if acct and d and (acct not in last_touch or d > last_touch[acct]):
            last_touch[acct] = d
    for acct, d in last_touch.items():
        gap = (now() - d).days
        if gap >= args.silence_days:
            sev = "high" if gap >= args.silence_days * 2 else "medium"
            sig[acct].append({"name": f"gone silent {gap}d", "severity": sev, "lens": "engagement"})

    # ---- usage: login drop, active-user/usage decline, seat reduction, feature abandonment ----
    for r in read_csv(args.usage):
        acct = acct_of(r)
        if not acct:
            continue
        # login-frequency drop
        d = pct_drop(fnum(r.get("logins_prev")), fnum(r.get("logins_curr")))
        if d is not None and d >= args.usage_drop_pct:
            sev = "high" if d >= args.usage_drop_pct * 2 else "medium"
            sig[acct].append({"name": f"login-frequency drop {d:.0f}%", "severity": sev, "lens": "usage"})
        # overall usage / active-user decline
        d2 = pct_drop(fnum(r.get("active_users_prev")), fnum(r.get("active_users_curr")))
        if d2 is not None and d2 >= args.usage_drop_pct:
            sev = "high" if d2 >= args.usage_drop_pct * 2 else "medium"
            sig[acct].append({"name": f"active-user decline {d2:.0f}%", "severity": sev, "lens": "usage"})
        # seat reduction (commercial signal even if billing not exported)
        ds = pct_drop(fnum(r.get("seats_prev")), fnum(r.get("seats_curr")))
        if ds is not None and ds >= args.seat_drop_pct:
            sev = "high" if ds >= args.seat_drop_pct * 2 else "medium"
            sig[acct].append({"name": f"seat reduction {ds:.0f}%", "severity": sev, "lens": "commercial"})
        # feature abandonment
        df = pct_drop(fnum(r.get("features_prev")), fnum(r.get("features_curr")))
        if df is not None and df >= args.feature_drop_pct:
            sig[acct].append({"name": f"feature abandonment {df:.0f}%", "severity": "medium", "lens": "usage"})

    # ---- billing events ----
    billing_sev = {"payment_failure": "critical", "downgrade": "high",
                   "seat_reduction": "high", "discount_request": "medium"}
    for r in read_csv(args.billing):
        acct = acct_of(r)
        ev = (r.get("event") or "").lower().replace(" ", "_")
        if acct and ev in billing_sev:
            sig[acct].append({"name": ev.replace("_", " "), "severity": billing_sev[ev], "lens": "commercial"})

    # ---- survey: NPS / CSAT drop and detractor levels ----
    for r in read_csv(args.survey):
        acct = acct_of(r)
        if not acct:
            continue
        nps_prev, nps_cur = fnum(r.get("nps_prev")), fnum(r.get("nps_curr"))
        if nps_prev is not None and nps_cur is not None and (nps_prev - nps_cur) >= args.nps_drop:
            sig[acct].append({"name": f"NPS drop {nps_prev:.0f}->{nps_cur:.0f}", "severity": "high",
                              "lens": "sentiment"})
        csat_prev, csat_cur = fnum(r.get("csat_prev")), fnum(r.get("csat_curr"))
        if csat_prev is not None and csat_cur is not None and (csat_prev - csat_cur) >= args.csat_drop:
            sig[acct].append({"name": f"CSAT drop {csat_prev:.1f}->{csat_cur:.1f}", "severity": "high",
                              "lens": "sentiment"})
        # absolute detractor (single-point) reads
        nps = fnum(r.get("nps")) if nps_cur is None else nps_cur
        if nps is not None and nps <= 6:
            sig[acct].append({"name": f"NPS detractor ({nps:.0f})", "severity": "medium", "lens": "sentiment"})
        csat = fnum(r.get("csat")) if csat_cur is None else csat_cur
        if csat is not None and csat <= 2.5:
            sig[acct].append({"name": f"low CSAT ({csat:.1f})", "severity": "medium", "lens": "sentiment"})

    # ---- people: champion departure, exec/sponsor turnover ----
    for r in read_csv(args.people):
        acct = acct_of(r)
        if not acct:
            continue
        role = (r.get("role") or "").lower()
        status = (r.get("status") or "").lower()
        if any(s in status for s in DEPARTURE_STATUS):
            if any(k in role for k in KEY_ROLES):
                sig[acct].append({"name": "champion departure", "severity": "critical",
                                  "lens": "relationship", "note": r.get("role", "")})
            elif any(e in role for e in EXEC_ROLES):
                sig[acct].append({"name": "exec/sponsor turnover", "severity": "high",
                                  "lens": "relationship", "note": r.get("role", "")})
            else:
                sig[acct].append({"name": "key contact departure", "severity": "medium",
                                  "lens": "relationship", "note": r.get("role", "")})

    out_accounts = []
    for acct, m in meta.items():
        out_accounts.append({"account": acct, "mrr": m["mrr"], "renewal_date": m["renewal_date"],
                             "signals": sig.get(acct, [])})

    out = json.dumps(out_accounts, ensure_ascii=False, indent=2)
    if args.output == "-":
        print(out)
    else:
        with open(args.output, "w", encoding="utf-8") as f:
            f.write(out + "\n")
        print(f"signals for {len(out_accounts)} accounts -> {args.output}", file=sys.stderr)


if __name__ == "__main__":
    main()
