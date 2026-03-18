#!/usr/bin/env python3
"""
Generate skills-index.json from SKILL.md frontmatter files.

Source of truth: each skills/<name>/SKILL.md frontmatter contains:
  - name: skill directory name
  - description: full routing description

This script:
  1. Reads all SKILL.md files
  2. Extracts name + description from frontmatter
  3. Strips "Do NOT use..." suffix for the index description
  4. Preserves tags from existing index (if present)
  5. Writes skills-index.json

Usage:
    python3 scripts/generate_index.py          # regenerate index
    python3 scripts/generate_index.py --check  # check for drift without writing
"""

import json
import os
import re
import sys

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SKILLS_DIR = os.path.join(REPO_ROOT, "skills")
INDEX_PATH = os.path.join(REPO_ROOT, "skills-index.json")


def parse_frontmatter(md_path):
    """Extract YAML frontmatter from a SKILL.md file."""
    with open(md_path) as f:
        content = f.read()
    m = re.match(r'^---\n(.*?)\n---', content, re.DOTALL)
    if not m:
        return None
    # Manual parsing for simple key: "value" pairs (avoids yaml dependency)
    data = {}
    for line in m.group(1).strip().split("\n"):
        match = re.match(r'^(\w+):\s*"(.+)"$', line)
        if match:
            data[match.group(1)] = match.group(2)
    return data if data else None


def make_index_description(full_desc):
    """
    Convert SKILL.md description to index description.
    Strips 'Do NOT use for...' suffix and ensures it ends with CLI reference.
    """
    # Remove "Do NOT use..." part
    desc = re.split(r'\.\s*Do NOT use', full_desc)[0]
    desc = desc.rstrip(".")

    # Extract CLI name from description
    cli_match = re.search(r'`robomotion (\S+)`', desc)
    if cli_match:
        cli = cli_match.group(1)
        # Remove any trailing "via `robomotion xxx`" so we can add it standardized
        desc = re.sub(r'\s*via\s+`robomotion \S+`\.?$', '', desc)
        desc = f"{desc} via the `robomotion {cli}` CLI."
    else:
        desc += "."

    return desc


def main():
    check_mode = "--check" in sys.argv

    # Load existing index for tags preservation
    existing_tags = {}
    if os.path.exists(INDEX_PATH):
        with open(INDEX_PATH) as f:
            existing = json.load(f)
        for skill in existing.get("skills", []):
            existing_tags[skill["name"]] = skill.get("tags", [])

    # Scan all skill directories
    skills = []
    errors = []

    for name in sorted(os.listdir(SKILLS_DIR)):
        skill_dir = os.path.join(SKILLS_DIR, name)
        md_path = os.path.join(skill_dir, "SKILL.md")

        if not os.path.isdir(skill_dir) or not os.path.exists(md_path):
            continue

        fm = parse_frontmatter(md_path)
        if not fm or "name" not in fm or "description" not in fm:
            errors.append(f"{name}: missing or invalid frontmatter")
            continue

        if fm["name"] != name:
            errors.append(f"{name}: frontmatter name '{fm['name']}' != directory name")

        index_desc = make_index_description(fm["description"])
        tags = existing_tags.get(name, [])

        skills.append({
            "name": name,
            "path": f"skills/{name}",
            "description": index_desc,
            "version": "1.0.0",
            "author": "robomotion",
            "tags": tags,
            "license": "Apache-2.0",
        })

    if errors:
        print(f"Errors ({len(errors)}):")
        for e in errors:
            print(f"  - {e}")

    # Build index
    index = {
        "version": 1,
        "name": "Robomotion Official Skills",
        "description": "Curated skills for Robomotion LLM Agents",
        "skills": skills,
    }

    if check_mode:
        if os.path.exists(INDEX_PATH):
            with open(INDEX_PATH) as f:
                current = json.load(f)
            current_names = {s["name"] for s in current.get("skills", [])}
            new_names = {s["name"] for s in skills}
            added = new_names - current_names
            removed = current_names - new_names
            if added:
                print(f"New skills not in index: {sorted(added)}")
            if removed:
                print(f"Skills in index but no SKILL.md: {sorted(removed)}")
            if not added and not removed:
                print(f"Index is in sync ({len(skills)} skills)")
        else:
            print(f"No existing index. Would create with {len(skills)} skills.")
    else:
        with open(INDEX_PATH, "w") as f:
            json.dump(index, f, indent=2, ensure_ascii=False)
            f.write("\n")
        print(f"Generated skills-index.json with {len(skills)} skills")


if __name__ == "__main__":
    main()
