#!/usr/bin/env python3
"""qual_prompt.py — persist/load/refine a reusable qualification prompt + build a scorecard.

lead-qualification is mostly the AGENT's reasoning: it runs intake to synthesize a
qualification prompt, scores leads against it, and can refine it. This script does the
deterministic glue:
  save     --name N --prompt-text "..."           -> persist a named qualification prompt
  load     --name N                               -> print a saved prompt
  list                                            -> list saved prompts
  scaffold --leads leads.csv                      -> emit a scored-list scaffold (agent fills)
  finalize --scorecard s.json [--format csv]      -> emit the final scored list

Prompts persist to a JSON store (--store, default ${WORKSPACE}/qual_prompts.json or
qual_prompts.json in CWD) — or to Supabase if you wire it in the agent; this script keeps it
file-based and durable across runs in the workspace. Stdlib only.

Example:
  qual_prompt.py --store prompts.json save --name acme_icp --prompt-text "Qualify if ..."
  qual_prompt.py --store prompts.json load --name acme_icp
  qual_prompt.py scaffold --leads leads.csv --output scorecard.json
  qual_prompt.py finalize --scorecard scorecard.json --format csv
"""
import argparse
import csv
import io
import json
import os
import sys

OUT_FIELDS = ["name", "company", "linkedin_url", "verdict", "confidence", "reasoning"]


def load_store(path):
    if path and os.path.exists(path):
        with open(path, encoding="utf-8") as f:
            return json.load(f)
    return {}


def save_store(path, store):
    with open(path, "w", encoding="utf-8") as f:
        json.dump(store, f, ensure_ascii=False, indent=2)


def main():
    ap = argparse.ArgumentParser(description="Persist/refine qualification prompts + scorecard glue.")
    ap.add_argument("--store", default="qual_prompts.json", help="prompt store JSON path")
    sub = ap.add_subparsers(dest="op", required=True)

    s = sub.add_parser("save")
    s.add_argument("--name", required=True)
    s.add_argument("--prompt-text", required=True)

    l = sub.add_parser("load")
    l.add_argument("--name", required=True)

    sub.add_parser("list")

    sc = sub.add_parser("scaffold")
    sc.add_argument("--leads", required=True)
    sc.add_argument("--output", default="-")

    fi = sub.add_parser("finalize")
    fi.add_argument("--scorecard", required=True)
    fi.add_argument("--format", default="json", choices=["json", "csv"])
    fi.add_argument("--output", default="-")

    args = ap.parse_args()

    if args.op == "save":
        store = load_store(args.store)
        store[args.name] = {"prompt": args.prompt_text}
        save_store(args.store, store)
        print(f"saved prompt '{args.name}' -> {args.store}")
    elif args.op == "load":
        store = load_store(args.store)
        if args.name not in store:
            sys.exit(f"ERROR: no saved prompt named '{args.name}'.")
        print(store[args.name]["prompt"])
    elif args.op == "list":
        store = load_store(args.store)
        print(json.dumps(list(store.keys()), indent=2))
    elif args.op == "scaffold":
        with open(args.leads, newline="", encoding="utf-8") as f:
            leads = list(csv.DictReader(f))
        out = [{
            "name": r.get("name") or r.get("Name") or "",
            "company": r.get("company") or r.get("Company") or "",
            "linkedin_url": r.get("linkedin_url") or r.get("LinkedIn URL") or "",
            "verdict": "", "confidence": "", "reasoning": "",  # agent fills
        } for r in leads]
        payload = json.dumps(out, ensure_ascii=False, indent=2)
        if args.output == "-":
            print(payload)
        else:
            with open(args.output, "w", encoding="utf-8") as f:
                f.write(payload + "\n")
            print(f"scaffold for {len(out)} leads -> {args.output} "
                  f"(agent fills verdict/confidence/reasoning)", file=sys.stderr)
    elif args.op == "finalize":
        with open(args.scorecard, encoding="utf-8") as f:
            rows = json.load(f)
        if args.format == "csv":
            buf = io.StringIO()
            w = csv.DictWriter(buf, fieldnames=OUT_FIELDS)
            w.writeheader()
            for r in rows:
                w.writerow({k: r.get(k, "") for k in OUT_FIELDS})
            payload = buf.getvalue()
        else:
            payload = json.dumps(rows, ensure_ascii=False, indent=2) + "\n"
        if args.output == "-":
            sys.stdout.write(payload)
        else:
            with open(args.output, "w", encoding="utf-8") as f:
                f.write(payload)
            print(f"finalized {len(rows)} leads -> {args.output}", file=sys.stderr)


if __name__ == "__main__":
    main()
