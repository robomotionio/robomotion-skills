#!/usr/bin/env python3
"""
Generate marketing-skills/.robomotion/env.yaml.

Walks the vendored marketing-skills/ mirror (read-only) and emits the
group's env overlay with two maps:

  integrations:
    <name>:
      env_optional: [VAR1, VAR2]    # from tools/clis/<name>.js process.env refs
      skills: [skill-a, skill-b]    # from tools/integrations/<name>.md "Relevant Skills"

  skills:
    <skill>:
      integrations: [name-a, name-b]      # inverted from above
      env_optional: [VAR1, VAR2, ...]     # union of all env vars across integrations

All env vars are OPTIONAL — marketing skills are knowledge that can speak
to any of several alternative tools; the user supplies keys only for the
tools they actually have.

Usage (from skills repo root):
  python3 generate-env-overlay.py
"""

import os
import re
import sys

try:
    import yaml
except ImportError:
    print("PyYAML required: pip install pyyaml")
    sys.exit(1)

REPO_ROOT = os.path.abspath(os.path.dirname(__file__))
MIRROR = os.path.join(REPO_ROOT, "marketing-skills")
OUT_PATH = os.path.join(MIRROR, ".robomotion", "env.yaml")

ENV_RE = re.compile(r"process\.env\.([A-Z][A-Z0-9_]+)")
RELEVANT_RE = re.compile(r"^##\s+Relevant Skills\s*$", re.MULTILINE)
SKILL_BULLET_RE = re.compile(r"^-\s+([a-z0-9][a-z0-9-]*)\s*$", re.MULTILINE)


def scan_clis():
    """integration_name -> sorted list of env var names."""
    clis = {}
    cli_dir = os.path.join(MIRROR, "tools", "clis")
    for fn in sorted(os.listdir(cli_dir)):
        if not fn.endswith(".js"):
            continue
        name = fn[:-3]
        with open(os.path.join(cli_dir, fn)) as f:
            text = f.read()
        vars_ = sorted(set(ENV_RE.findall(text)))
        if vars_:
            clis[name] = vars_
    return clis


def scan_integrations():
    """integration_name -> (env_vars_from_md, relevant_skills)."""
    out = {}
    int_dir = os.path.join(MIRROR, "tools", "integrations")
    for fn in sorted(os.listdir(int_dir)):
        if not fn.endswith(".md"):
            continue
        name = fn[:-3]
        with open(os.path.join(int_dir, fn)) as f:
            text = f.read()
        # Env vars referenced anywhere in the doc (fallback when CLI absent)
        md_vars = sorted(set(ENV_RE.findall(text)))
        # Relevant Skills section
        skills = []
        m = RELEVANT_RE.search(text)
        if m:
            tail = text[m.end():]
            # stop at next "## " heading
            next_h = tail.find("\n## ")
            section = tail if next_h == -1 else tail[:next_h]
            skills = SKILL_BULLET_RE.findall(section)
        out[name] = (md_vars, skills)
    return out


def known_skills():
    """Set of skills under skills/<name>/SKILL.md."""
    skills_dir = os.path.join(MIRROR, "skills")
    return {
        d for d in os.listdir(skills_dir)
        if os.path.isfile(os.path.join(skills_dir, d, "SKILL.md"))
    }


def main():
    clis = scan_clis()
    ints = scan_integrations()
    skills_set = known_skills()

    integrations = {}
    for name, (md_vars, rel_skills) in sorted(ints.items()):
        env_vars = clis.get(name) or md_vars
        rel_skills = [s for s in rel_skills if s in skills_set]
        if not env_vars and not rel_skills:
            continue
        entry = {}
        if env_vars:
            entry["env_optional"] = env_vars
        if rel_skills:
            entry["skills"] = sorted(set(rel_skills))
        integrations[name] = entry

    # Invert: skill -> integrations
    skill_to_ints = {s: [] for s in sorted(skills_set)}
    for int_name, entry in integrations.items():
        for s in entry.get("skills", []):
            skill_to_ints[s].append(int_name)

    skills_map = {}
    for skill in sorted(skill_to_ints):
        ints_for_skill = sorted(set(skill_to_ints[skill]))
        if not ints_for_skill:
            skills_map[skill] = {"integrations": [], "env_optional": []}
            continue
        env_union = sorted({
            v
            for i in ints_for_skill
            for v in integrations[i].get("env_optional", [])
        })
        skills_map[skill] = {
            "integrations": ints_for_skill,
            "env_optional": env_union,
        }

    out = {
        "schema_version": 1,
        "collection": "marketing-skills",
        "note": (
            "All env vars are OPTIONAL. Marketing skills are knowledge; "
            "they can use any of several alternative tools. The user "
            "supplies keys only for the tools they have."
        ),
        "integrations": integrations,
        "skills": skills_map,
    }

    with open(OUT_PATH, "w") as f:
        yaml.dump(out, f, default_flow_style=False, sort_keys=False, allow_unicode=True, width=120)

    # Summary
    skills_with_creds = sum(1 for v in skills_map.values() if v["env_optional"])
    print(f"Integrations indexed: {len(integrations)}")
    print(f"Skills total:         {len(skills_map)} ({skills_with_creds} have credentials)")
    print(f"Wrote:                {OUT_PATH}")


if __name__ == "__main__":
    main()
