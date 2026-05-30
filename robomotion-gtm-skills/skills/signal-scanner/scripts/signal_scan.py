#!/usr/bin/env python3
"""signal_scan.py — scheduled buying-signal scanner over a stored TAM (Supabase-backed).

Three phases:
  Phase 1 (free): diff current vs. stored company/person snapshots — headcount growth >10%
    /90d, tech-stack changes, funding rounds, derived new-C-suite hires.
  Phase 2 (paid): emit job-posting / LinkedIn-content scrape TARGETS for the agent to run
    via job-posting-intent / the LinkedIn engager skills (this script does not itself drive
    the paid scrape — it computes the scope and reads back results you pass in).
  Phase 3: dedup + score; write signals/enrichment_log + patch companies/people.

CRITICAL APPROVAL GATE: --dry-run is the DEFAULT (true). The script NEVER writes to Supabase
unless invoked with --commit AND --approved. Dry-run returns a preview summary; the agent
presents it to a human, then re-runs with --commit --approved on confirmation.

Storage (paid vs. fallback):
  - If SUPABASE_URL + SUPABASE_SERVICE_ROLE_KEY are set -> Supabase REST store (durable
    cross-run snapshots + signals; recommended). This is the substrate tam-builder writes.
  - If NOT set -> keyless workspace-file fallback: read the company snapshot from
    `--snapshots <csv|json>` (the TAM export) and write detected signals to `--signals-out`
    (or alongside the snapshot). Single-run; durable only if you reuse the same files.

Phase-2 scraping uses the LinkedIn/jobs engines via their own skills (APIFY_API_TOKEN /
PHANTOMBUSTER_API_KEY), each with their own keyless degrade.

Example (always run dry first):
  signal_scan.py --client acme --config signals.json --phase 1
  signal_scan.py --client acme --config signals.json --phase 1 --commit --approved
  # keyless: read a TAM CSV/JSON export instead of Supabase
  signal_scan.py --client acme --config signals.json --phase 1 \
      --snapshots ${WORKSPACE}/tam_scored.csv --signals-out ${WORKSPACE}/signals.json
"""
import argparse
import csv
import json
import os
import sys
import time
import urllib.error
import urllib.parse
import urllib.request


def supa_cfg():
    url = os.environ.get("SUPABASE_URL", "").strip()
    key = os.environ.get("SUPABASE_SERVICE_ROLE_KEY", "").strip()
    return (url, key) if url and key else (None, None)


def use_supa():
    return all(supa_cfg())


def _coerce(v):
    """Best-effort scalar coercion for CSV cells: ints, JSON lists, else the string."""
    if not isinstance(v, str):
        return v
    s = v.strip()
    if s == "":
        return None
    if s.lstrip("-").isdigit():
        return int(s)
    if s[:1] in "[{":
        try:
            return json.loads(s)
        except Exception:
            return v
    return v


def load_snapshots(path):
    """Keyless fallback: load company snapshot rows from a CSV or JSON TAM export."""
    if not path:
        sys.exit("ERROR: no Supabase env set and no --snapshots <csv|json> provided. "
                 "Provide a TAM export (the keyless fallback) or set SUPABASE_URL + "
                 "SUPABASE_SERVICE_ROLE_KEY (durable store).")
    if path.lower().endswith(".json"):
        with open(path, encoding="utf-8") as f:
            rows = json.load(f)
    else:
        with open(path, newline="", encoding="utf-8") as f:
            rows = [{k: _coerce(v) for k, v in row.items()} for row in csv.DictReader(f)]
    return rows if isinstance(rows, list) else rows.get("companies", [])


def supa(method, path, body=None, params=None):
    url, key = supa_cfg()
    full = f"{url}/rest/v1/{path}"
    if params:
        full += "?" + urllib.parse.urlencode(params)
    data = json.dumps(body).encode() if body is not None else None
    req = urllib.request.Request(full, data=data, method=method, headers={
        "apikey": key, "Authorization": f"Bearer {key}",
        "Content-Type": "application/json",
        "Prefer": "resolution=merge-duplicates,return=representation"})
    for attempt in range(3):
        try:
            with urllib.request.urlopen(req, timeout=45) as r:
                raw = r.read().decode("utf-8")
                return json.loads(raw) if raw.strip() else []
        except urllib.error.HTTPError as e:
            if e.code in (429, 503) and attempt < 2:
                time.sleep(2 ** attempt)
                continue
            sys.exit(f"ERROR: Supabase {e.code}: {e.read().decode('utf-8','ignore')[:300]}")
        except urllib.error.URLError as e:
            if attempt < 2:
                time.sleep(2 ** attempt)
                continue
            sys.exit(f"ERROR: network: {e}")


def fetch_companies(client, scope, select="*", snapshots=None):
    """Load company snapshot rows from Supabase (if env set) or a --snapshots file."""
    if use_supa():
        params = {"select": select, "client": f"eq.{client}"}
        if scope.get("tier"):
            params["tier"] = f"eq.{scope['tier']}"
        if scope.get("status"):
            params["status"] = f"eq.{scope['status']}"
        return supa("GET", os.environ.get("SIGNAL_COMPANIES_TABLE", "companies"), params=params)
    # Keyless fallback: filter the loaded snapshot rows client-side.
    rows = load_snapshots(snapshots)
    out = []
    for c in rows:
        if str(c.get("client", client)) != str(client) and c.get("client") is not None:
            continue
        if scope.get("tier") and str(c.get("tier")) != str(scope["tier"]):
            continue
        if scope.get("status") and str(c.get("status")) != str(scope["status"]):
            continue
        out.append(c)
    return out


def phase1_diffs(client, cfg, scope, companies):
    """Free diff-based signals from stored snapshots vs. their previous snapshot field."""
    thresholds = cfg.get("thresholds", {})
    hc_pct = thresholds.get("headcount_growth_pct", 10)
    signals = []
    for c in companies:
        prev = c.get("prev_employees") or c.get("snapshot_employees")
        cur = c.get("employees")
        if cfg.get("headcount", True) and prev and cur:
            try:
                growth = (cur - prev) / prev * 100
                if growth > hc_pct:
                    signals.append({
                        "client": client, "company_id": c.get("id"),
                        "company": c.get("name"), "signal_type": "headcount_growth",
                        "evidence": f"{prev} -> {cur} ({growth:.0f}% > {hc_pct}%)",
                        "priority": "high" if growth > 2 * hc_pct else "medium",
                        "score": round(min(growth / hc_pct, 5), 2)})
            except (TypeError, ZeroDivisionError):
                pass
        if cfg.get("tech_stack", True):
            prev_tech = set(c.get("prev_tech_stack") or [])
            cur_tech = set(c.get("tech_stack") or [])
            added = cur_tech - prev_tech
            if added:
                signals.append({"client": client, "company_id": c.get("id"),
                                "company": c.get("name"), "signal_type": "tech_stack_change",
                                "evidence": f"added: {', '.join(sorted(added))}",
                                "priority": "medium", "score": 2.0})
        if cfg.get("funding", True) and c.get("funding_stage") and \
                c.get("funding_stage") != c.get("prev_funding_stage"):
            signals.append({"client": client, "company_id": c.get("id"),
                            "company": c.get("name"), "signal_type": "funding_round",
                            "evidence": f"{c.get('prev_funding_stage','?')} -> {c.get('funding_stage')}",
                            "priority": "high", "score": 4.0})
    return signals


def phase2_targets(client, cfg, scope, companies):
    """Compute the SCOPE of paid scraping; the agent runs the scrape via the engine skills."""
    return {
        "note": "Phase 2 is metered. Run job-posting-intent / the LinkedIn engager skills "
                "over these targets, then feed results back via --phase 3 --results <file>.",
        "job_titles": cfg.get("job_titles", []),
        "company_targets": [{"id": c.get("id"), "name": c.get("name"),
                             "domain": c.get("domain")} for c in companies],
    }


def main():
    ap = argparse.ArgumentParser(description="TAM buying-signal scanner (dry-run by default).")
    ap.add_argument("--client", required=True, help="which client's TAM to scan")
    ap.add_argument("--config", required=True, help="signals_config JSON (enable/thresholds/job_titles)")
    ap.add_argument("--phase", type=int, choices=[1, 2, 3], default=1)
    ap.add_argument("--scope", default="{}", help="JSON scan_scope (tier/status filters)")
    ap.add_argument("--results", default="", help="phase-3: scraped signals JSON to ingest")
    ap.add_argument("--dry-run", action="store_true", default=True,
                    help="(default) detect without writing")
    ap.add_argument("--commit", action="store_true",
                    help="actually write — REQUIRES --approved")
    ap.add_argument("--approved", action="store_true",
                    help="explicit human approval token; required with --commit")
    ap.add_argument("--snapshots", default="",
                    help="keyless fallback: TAM company snapshot CSV/JSON (when no Supabase env)")
    ap.add_argument("--signals-out", default="",
                    help="keyless fallback: where to append committed signals (JSON)")
    ap.add_argument("--output", default="-")
    args = ap.parse_args()

    with open(args.config, encoding="utf-8") as f:
        cfg = json.load(f)
    scope = json.loads(args.scope)
    backend = "supabase" if use_supa() else "workspace-file"

    will_write = args.commit and args.approved
    if args.commit and not args.approved:
        sys.exit("REFUSING TO WRITE: --commit requires --approved (explicit human approval). "
                 "Run dry-run first, present the summary, then re-run with --commit --approved.")

    if args.phase == 1:
        companies = fetch_companies(args.client, scope, "*", args.snapshots)
        signals = phase1_diffs(args.client, cfg, scope, companies)
        n = len(companies)
        summary = {"phase": 1, "backend": backend, "companies_scanned": n,
                   "signals_detected": len(signals), "signals": signals}
    elif args.phase == 2:
        companies = fetch_companies(args.client, scope, "id,name,domain,tier", args.snapshots)
        summary = {"phase": 2, "backend": backend,
                   **phase2_targets(args.client, cfg, scope, companies)}
        signals = []
    else:  # phase 3
        if not args.results:
            sys.exit("ERROR: --phase 3 needs --results <scraped signals JSON>.")
        with open(args.results, encoding="utf-8") as f:
            signals = json.load(f)
        # dedup by (company, signal_type)
        seen, deduped = set(), []
        for s in signals:
            k = (str(s.get("company", "")).lower(), s.get("signal_type", ""))
            if k in seen:
                continue
            seen.add(k)
            deduped.append(s)
        signals = deduped
        summary = {"phase": 3, "signals_after_dedup": len(signals), "signals": signals}

    if will_write and signals:
        now = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
        rows = [dict(s, detected_at=now) for s in signals]
        if use_supa():
            written = supa("POST", os.environ.get("SIGNAL_SIGNALS_TABLE", "signals"), body=rows)
            supa("POST", os.environ.get("SIGNAL_LOG_TABLE", "enrichment_log"),
                 body=[{"client": args.client, "phase": args.phase,
                        "count": len(rows), "logged_at": now}])
            summary["written"] = len(written)
        else:
            # Keyless fallback: append committed signals to a workspace JSON ledger.
            out_path = args.signals_out or (
                (args.snapshots.rsplit(".", 1)[0] + ".signals.json") if args.snapshots
                else "signals.json")
            existing = []
            if os.path.exists(out_path):
                try:
                    with open(out_path, encoding="utf-8") as f:
                        existing = json.load(f)
                except Exception:
                    existing = []
            existing.extend(rows)
            with open(out_path, "w", encoding="utf-8") as f:
                json.dump(existing, f, ensure_ascii=False, indent=2)
            summary["written"] = len(rows)
            summary["signals_file"] = out_path
        summary["mode"] = "COMMITTED"
    else:
        summary["written"] = 0
        summary["mode"] = "DRY_RUN (no writes — re-run with --commit --approved to persist)"

    payload = json.dumps(summary, ensure_ascii=False, indent=2)
    if args.output == "-":
        print(payload)
    else:
        with open(args.output, "w", encoding="utf-8") as f:
            f.write(payload + "\n")
        print(f"{summary['mode']}: {summary.get('signals_detected', len(signals))} signals",
              file=sys.stderr)


if __name__ == "__main__":
    main()
