#!/usr/bin/env python3
"""init_run.py — Scaffold a social-kit run folder and print the orchestration plan.

Keyless. Stdlib only. Deterministic glue for `social-kit`: derive a topic-slug from the
brief, create `content/YYYY-MM-DD-<topic-slug>/` (with a `graphic/` subfolder), and print
which sub-skills to invoke given the skip flags. No copy/graphic is produced here — the
agent orchestrates create-x-content, create-linkedin-content, and graphics-studio.

Examples:
  init_run.py --brief "Shipped a 10x faster lead scraper" --output ./content
  init_run.py --brief "..." --skip-x --format poster --output ./content
"""
import argparse
import datetime
import json
import os
import re
import sys


def slugify(text, maxlen=48):
    s = re.sub(r"[^a-z0-9]+", "-", text.lower()).strip("-")
    s = re.sub(r"-{2,}", "-", s)
    return s[:maxlen].strip("-") or "post"


def main():
    ap = argparse.ArgumentParser(description="Scaffold a social-kit run folder + print the plan.")
    ap.add_argument("--brief", required=True, help="the content brief")
    ap.add_argument("--output", default="./content", help="parent dir (default ./content)")
    ap.add_argument("--format", default="", help="graphic format hint (else agent recommends)")
    ap.add_argument("--style", default="", help="graphic style (else house default)")
    ap.add_argument("--variants-x", type=int, default=0, help="X variant count (0 = sub-skill decides)")
    ap.add_argument("--variants-linkedin", type=int, default=0, help="LinkedIn variant count (0 = decide)")
    ap.add_argument("--skip-x", action="store_true")
    ap.add_argument("--skip-linkedin", action="store_true")
    ap.add_argument("--skip-graphic", action="store_true")
    args = ap.parse_args()

    today = datetime.date.today().isoformat()
    topic = " ".join(args.brief.split()[:8])
    slug = f"{today}-{slugify(topic)}"
    folder = os.path.join(args.output, slug)
    os.makedirs(folder, exist_ok=True)
    if not args.skip_graphic:
        os.makedirs(os.path.join(folder, "graphic"), exist_ok=True)

    steps = []
    if not args.skip_x:
        steps.append({"sub_skill": "create-x-content", "out": folder,
                      "variants": args.variants_x or None})
    if not args.skip_linkedin:
        steps.append({"sub_skill": "create-linkedin-content", "out": folder,
                      "variants": args.variants_linkedin or None})
    if not args.skip_graphic:
        steps.append({"sub_skill": "graphics-studio",
                      "out": os.path.join(folder, "graphic"),
                      "format": args.format or "(agent recommends from brief shape)",
                      "style": args.style or "(house default)"})

    plan = {
        "brief": args.brief,
        "topic_slug": slug,
        "folder": folder,
        "steps": steps,
        "voice_guide_preflight": ("Before drafting, ensure an X and a LinkedIn voice guide "
                                  "exist for each non-skipped platform; if missing, delegate "
                                  "to generate-voice-guide, paste a path, or skip that platform."),
        "note": ("Distill the graphic brief from the strongest X variant (headline + 2-4 "
                 "beats + verbatim must-keep strings). Deliver a cross-linked summary."),
    }
    json.dump(plan, sys.stdout, ensure_ascii=False, indent=2)
    sys.stdout.write("\n")
    print(f"scaffolded {folder} ({len(steps)} steps)", file=sys.stderr)


if __name__ == "__main__":
    main()
