#!/usr/bin/env python3
"""contact_cache.py — persistent, deduplicated contact store for prospecting.

Tracks every person identified/contacted across strategies, deduped by normalized LinkedIn
URL (priority) or email, with a funnel status. Backed by Supabase REST when SUPABASE_URL +
SUPABASE_SERVICE_ROLE_KEY are set; otherwise a workspace CSV (single-run / non-durable
dedup — note the degrade). Stdlib only.

Ops:
  check   --linkedin-urls / --emails        -> partition known vs new
  add     --contact-json / --csv  --strategy -> upsert (skip dupes), report inserted/skipped
  update  --linkedin-url|--email --status --notes -> set funnel status
  export  [--filter-status S] [--filter-strategy S] -> CSV/JSON of contacts
  stats                                      -> funnel counts

Example:
  contact_cache.py --store ${WORKSPACE}/contacts.csv check --linkedin-urls "https://linkedin.com/in/a"
  contact_cache.py --store ${WORKSPACE}/contacts.csv add --csv new.csv --strategy luma
  contact_cache.py --store ${WORKSPACE}/contacts.csv update --email a@x.com --status contacted
  contact_cache.py --store ${WORKSPACE}/contacts.csv stats
"""
import argparse
import csv
import hashlib
import io
import json
import os
import sys
import time
import urllib.error
import urllib.parse
import urllib.request

STATUSES = ["new", "qualified", "contacted", "replied", "meeting_booked",
            "converted", "not_interested"]
FIELDS = ["contact_id", "name", "title", "company", "linkedin_url", "email",
          "location", "strategy", "status", "notes", "first_seen", "last_updated"]
TABLE = os.environ.get("CONTACT_CACHE_TABLE", "contacts")


def norm_url(u):
    return u.split("?")[0].rstrip("/").lower().replace("http://", "https://") if u else ""


def norm_email(e):
    return e.strip().lower() if e else ""


def contact_id(linkedin_url, email):
    basis = norm_url(linkedin_url) or norm_email(email)
    if not basis:
        return ""
    return hashlib.sha256(basis.encode("utf-8")).hexdigest()[:16]


# ---------- Supabase backend ----------
def supa_cfg():
    url = os.environ.get("SUPABASE_URL", "").strip()
    key = os.environ.get("SUPABASE_SERVICE_ROLE_KEY", "").strip()
    return (url, key) if url and key else (None, None)


def supa_req(method, path, body=None, params=None):
    url, key = supa_cfg()
    full = f"{url}/rest/v1/{path}"
    if params:
        full += "?" + urllib.parse.urlencode(params)
    data = json.dumps(body).encode() if body is not None else None
    req = urllib.request.Request(full, data=data, method=method, headers={
        "apikey": key, "Authorization": f"Bearer {key}",
        "Content-Type": "application/json",
        "Prefer": "resolution=merge-duplicates,return=representation",
    })
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


# ---------- CSV backend ----------
def csv_load(path):
    rows = {}
    if path and os.path.exists(path):
        with open(path, newline="", encoding="utf-8") as f:
            for row in csv.DictReader(f):
                cid = row.get("contact_id")
                if cid:
                    rows[cid] = {k: row.get(k, "") for k in FIELDS}
    return rows


def csv_save(path, rows):
    with open(path, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=FIELDS)
        w.writeheader()
        for r in rows.values():
            w.writerow(r)


def use_supa():
    return all(supa_cfg())


# ---------- ops ----------
def op_check(args, store):
    ids_in = []
    for u in (args.linkedin_urls or "").split(","):
        if u.strip():
            ids_in.append(("linkedin", u.strip(), contact_id(u.strip(), "")))
    for e in (args.emails or "").split(","):
        if e.strip():
            ids_in.append(("email", e.strip(), contact_id("", e.strip())))
    known_ids = set()
    if use_supa():
        cids = [cid for _, _, cid in ids_in if cid]
        if cids:
            res = supa_req("GET", TABLE, params={"contact_id": f"in.({','.join(cids)})",
                                                 "select": "contact_id"})
            known_ids = {r["contact_id"] for r in res}
    else:
        rows = csv_load(args.store)
        known_ids = {cid for _, _, cid in ids_in if cid in rows}
    known, new = [], []
    for kind, raw, cid in ids_in:
        (known if cid in known_ids else new).append({"type": kind, "value": raw, "contact_id": cid})
    print(json.dumps({"known": known, "new": new,
                      "known_count": len(known), "new_count": len(new)}, indent=2))


def build_contact(d, strategy):
    cid = contact_id(d.get("linkedin_url", ""), d.get("email", ""))
    now = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
    return {
        "contact_id": cid,
        "name": d.get("name", ""), "title": d.get("title", ""),
        "company": d.get("company", ""),
        "linkedin_url": norm_url(d.get("linkedin_url", "")),
        "email": norm_email(d.get("email", "")),
        "location": d.get("location", ""),
        "strategy": strategy or d.get("strategy", ""),
        "status": d.get("status", "new"),
        "notes": d.get("notes", ""),
        "first_seen": now, "last_updated": now,
    }


def op_add(args, store):
    incoming = []
    if args.contact_json:
        data = json.loads(args.contact_json)
        incoming = data if isinstance(data, list) else [data]
    elif args.csv:
        with open(args.csv, newline="", encoding="utf-8") as f:
            incoming = list(csv.DictReader(f))
    if not incoming:
        sys.exit("ERROR: add needs --contact-json or --csv.")
    contacts = [build_contact(d, args.strategy) for d in incoming]
    contacts = [c for c in contacts if c["contact_id"]]  # need an identifier
    inserted = skipped = 0
    if use_supa():
        res = supa_req("POST", TABLE, body=contacts) or []
        inserted = len(res)
        skipped = len(contacts) - inserted
    else:
        rows = csv_load(args.store)
        for c in contacts:
            if c["contact_id"] in rows:
                # idempotent: refresh strategy/source, keep first_seen
                rows[c["contact_id"]]["strategy"] = c["strategy"] or rows[c["contact_id"]]["strategy"]
                rows[c["contact_id"]]["last_updated"] = c["last_updated"]
                skipped += 1
            else:
                rows[c["contact_id"]] = c
                inserted += 1
        csv_save(args.store, rows)
    print(json.dumps({"inserted": inserted, "skipped": skipped,
                      "backend": "supabase" if use_supa() else "csv"}, indent=2))


def op_update(args, store):
    cid = contact_id(args.linkedin_url or "", args.email or "")
    if not cid:
        sys.exit("ERROR: update needs --linkedin-url or --email.")
    if args.status and args.status not in STATUSES:
        sys.exit(f"ERROR: invalid status '{args.status}'. Valid: {', '.join(STATUSES)}")
    patch = {"last_updated": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())}
    if args.status:
        patch["status"] = args.status
    if args.notes:
        patch["notes"] = args.notes
    if use_supa():
        res = supa_req("PATCH", TABLE, body=patch, params={"contact_id": f"eq.{cid}"})
        ok = bool(res)
    else:
        rows = csv_load(args.store)
        ok = cid in rows
        if ok:
            rows[cid].update(patch)
            csv_save(args.store, rows)
    print(json.dumps({"contact_id": cid, "updated": ok, "patch": patch}, indent=2))


def op_export(args, store):
    if use_supa():
        params = {"select": "*"}
        if args.filter_status:
            params["status"] = f"eq.{args.filter_status}"
        if args.filter_strategy:
            params["strategy"] = f"eq.{args.filter_strategy}"
        rows = supa_req("GET", TABLE, params=params)
    else:
        rows = list(csv_load(args.store).values())
        if args.filter_status:
            rows = [r for r in rows if r.get("status") == args.filter_status]
        if args.filter_strategy:
            rows = [r for r in rows if r.get("strategy") == args.filter_strategy]
    if args.format == "csv":
        buf = io.StringIO()
        w = csv.DictWriter(buf, fieldnames=FIELDS)
        w.writeheader()
        for r in rows:
            w.writerow({k: r.get(k, "") for k in FIELDS})
        sys.stdout.write(buf.getvalue())
    else:
        print(json.dumps(rows, ensure_ascii=False, indent=2))
    print(f"{len(rows)} contacts exported", file=sys.stderr)


def op_stats(args, store):
    if use_supa():
        rows = supa_req("GET", TABLE, params={"select": "status,strategy"})
    else:
        rows = list(csv_load(args.store).values())
    counts, by_strategy = {}, {}
    for r in rows:
        counts[r.get("status", "new")] = counts.get(r.get("status", "new"), 0) + 1
        s = r.get("strategy", "") or "(none)"
        by_strategy[s] = by_strategy.get(s, 0) + 1
    print(json.dumps({"total": len(rows), "by_status": counts,
                      "by_strategy": by_strategy}, indent=2))


def main():
    ap = argparse.ArgumentParser(description="Persistent deduplicated contact cache.")
    ap.add_argument("--store", default="", help="CSV path (used when Supabase env not set)")
    sub = ap.add_subparsers(dest="op", required=True)

    c = sub.add_parser("check", help="partition known vs new")
    c.add_argument("--linkedin-urls", default="")
    c.add_argument("--emails", default="")

    a = sub.add_parser("add", help="upsert contacts")
    a.add_argument("--contact-json", default="", help="JSON object or array")
    a.add_argument("--csv", default="", help="CSV of contacts")
    a.add_argument("--strategy", default="", help="source strategy tag")

    u = sub.add_parser("update", help="set status/notes")
    u.add_argument("--linkedin-url", default="")
    u.add_argument("--email", default="")
    u.add_argument("--status", default="")
    u.add_argument("--notes", default="")

    e = sub.add_parser("export", help="export contacts")
    e.add_argument("--filter-status", default="")
    e.add_argument("--filter-strategy", default="")
    e.add_argument("--format", default="json", choices=["json", "csv"])

    sub.add_parser("stats", help="funnel summary")

    args = ap.parse_args()
    if not use_supa() and not args.store and args.op in ("add", "update", "export", "stats", "check"):
        # check can run against supabase without a store; warn for csv mode
        if not use_supa():
            sys.stderr.write("WARN: no Supabase env and no --store; using ephemeral CSV in CWD "
                             "(non-durable). Set SUPABASE_URL+SUPABASE_SERVICE_ROLE_KEY for "
                             "cross-run dedup.\n")
            args.store = args.store or "contact_cache.csv"

    {"check": op_check, "add": op_add, "update": op_update,
     "export": op_export, "stats": op_stats}[args.op](args, args.store)


if __name__ == "__main__":
    main()
