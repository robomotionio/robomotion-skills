#!/usr/bin/env python3
"""init_launch.py — Scaffold a feature-launch kit folder and print the tier asset plan.

Keyless. Stdlib only. Deterministic glue for `feature-launch-playbook`: slugify the feature
name, create `<output>/<feature-slug>/`, and print the exact asset list + checklist for the
launch tier (read from the bundled launch_tiers.json) so the AGENT generates only the
tier-appropriate assets. No copy is written here — the agent authors every asset.

Examples:
  init_launch.py --feature "Advanced Filtering" --tier 1 --output ./content
"""
import argparse
import json
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))


def slugify(name):
    s = re.sub(r"[^a-z0-9]+", "-", name.lower()).strip("-")
    return s or "feature"


def main():
    ap = argparse.ArgumentParser(description="Scaffold a feature-launch folder + print the tier plan.")
    ap.add_argument("--feature", required=True, help="feature name")
    ap.add_argument("--tier", required=True, choices=["1", "2", "3"], help="1 major / 2 medium / 3 minor")
    ap.add_argument("--output", default=".", help="parent dir for the launch folder (default cwd)")
    ap.add_argument("--tiers-file", default=os.path.join(HERE, "launch_tiers.json"))
    args = ap.parse_args()

    with open(args.tiers_file, encoding="utf-8") as f:
        matrix = json.load(f)

    tier = matrix["tiers"][args.tier]
    slug = slugify(args.feature)
    folder = os.path.join(args.output, slug)
    os.makedirs(folder, exist_ok=True)

    plan = {
        "feature": args.feature,
        "slug": slug,
        "tier": args.tier,
        "tier_label": tier["label"],
        "folder": folder,
        "assets_to_generate": tier["assets"],
        "checklist": matrix["checklist_by_tier"][args.tier],
        "kit_path": os.path.join(folder, "launch-kit.md"),
        "checklist_path": os.path.join(folder, "checklist.md"),
        "note": ("The agent authors each asset in assets_to_generate into launch-kit.md "
                 "(outcome-driven headline first) and writes checklist.md. Social arms can "
                 "delegate to create-linkedin-content / create-x-content for voice; visuals "
                 "to graphics-studio."),
    }
    json.dump(plan, sys.stdout, ensure_ascii=False, indent=2)
    sys.stdout.write("\n")
    print(f"scaffolded {folder} (tier {args.tier}: {tier['label']})", file=sys.stderr)


if __name__ == "__main__":
    main()
