#!/usr/bin/env python3
"""contact_cache.py — dedup new contacts against a persistent contact cache.

The piece that makes the prospecting engine repeatable without re-spamming. Given a new
contact list and a cache file (JSON lines or JSON array of previously-contacted people),
it splits new contacts into NEW (add to cache) vs ALREADY-CONTACTED (skip), matching on
normalized email and/or LinkedIn URL. Optionally appends the new ones to the cache.

Deterministic, stdlib only. The agent runs the sub-skills; this only does the dedup math.
 (In production the cache is a supabase/airtable/datatable store; this
file-backed cache is the keyless default.)

Examples:
  contact_cache.py --new new_contacts.json --cache cache.json --update --output to_contact.json
  contact_cache.py --new new.json --cache cache.json            # report only, don't write cache
"""
import argparse
import json
import os
import sys


def norm_email(e):
    return (e or "").strip().lower()


def norm_url(u):
    u = (u or "").split("?")[0].rstrip("/").lower()
    return u.replace("http://", "https://")


def load_list(path):
    if not path or not os.path.exists(path):
        return []
    raw = open(path, encoding="utf-8").read().strip()
    if not raw:
        return []
    if raw.startswith("["):
        return json.loads(raw)
    # JSON-lines
    return [json.loads(line) for line in raw.splitlines() if line.strip()]


def keys_of(rec):
    ks = set()
    e = norm_email(rec.get("email"))
    if e and "<" not in e:
        ks.add("e:" + e)
    u = norm_url(rec.get("linkedin_url"))
    if u:
        ks.add("u:" + u)
    return ks


def main():
    ap = argparse.ArgumentParser(description="Dedup new contacts against a persistent contact cache.")
    ap.add_argument("--new", required=True, help="JSON list of new contacts")
    ap.add_argument("--cache", required=True, help="cache file (JSON array or JSON-lines); created if missing")
    ap.add_argument("--update", action="store_true", help="append NEW contacts to the cache file")
    ap.add_argument("--output", default="-", help="write the NEW (to-contact) list here; default stdout")
    args = ap.parse_args()

    new = load_list(args.new)
    if not isinstance(new, list):
        new = [new]
    cache = load_list(args.cache)

    cached_keys = set()
    for rec in cache:
        cached_keys |= keys_of(rec)

    to_contact, already, batch_keys = [], 0, set()
    for rec in new:
        ks = keys_of(rec)
        if ks & cached_keys or ks & batch_keys:  # also dedup within this batch
            already += 1
            continue
        batch_keys |= ks
        to_contact.append(rec)

    print(f"INFO: {len(to_contact)} new to contact, {already} already-contacted/dup "
          f"(cache had {len(cache)}).", file=sys.stderr)

    if args.update and to_contact:
        merged = cache + to_contact
        open(args.cache, "w", encoding="utf-8").write(json.dumps(merged, ensure_ascii=False, indent=2) + "\n")
        print(f"INFO: cache updated -> {len(merged)} total ({args.cache}).", file=sys.stderr)

    payload = json.dumps(to_contact, ensure_ascii=False, indent=2)
    if args.output == "-":
        print(payload)
    else:
        open(args.output, "w", encoding="utf-8").write(payload + "\n")
        print(f"{len(to_contact)} contacts -> {args.output}", file=sys.stderr)


if __name__ == "__main__":
    main()
