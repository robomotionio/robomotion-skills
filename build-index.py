#!/usr/bin/env python3
"""Generate index.yaml — the discovery manifest for this skill repo.

Walks the repo looking for ``.robomotion/skill.yaml`` (our authoritative
per-unit metadata). For each unit:

  * type: group  → also walks ``skills/<name>/SKILL.md`` inside it.
  * type: skill  → reads the unit's own SKILL.md.

Inner skills inherit ``author`` / ``source_url`` / ``license`` from their
group (denormalized into each row so the Designer doesn't have to look up).

Output is deterministic (no timestamps) so CI drift-checks are stable.
Content hashes capture "what changed".

Usage::

    python3 build-index.py            # write index.yaml
    python3 build-index.py --check    # exit 1 if index.yaml is out of date

We do not read ``.claude-plugin/plugin.json`` or any other upstream
metadata file — ``.robomotion/skill.yaml`` is the only source of truth.
"""

from __future__ import annotations

import hashlib
import os
import re
import sys

try:
    import yaml
except ImportError:
    sys.exit("PyYAML required: pip install pyyaml")

SCHEMA_VERSION = 1
ROBOMOTION_DIR = ".robomotion"
SKILL_YAML = "skill.yaml"
SKIP_DIRS = {".git", ".github", "node_modules", "docs"}


# ---------- front-matter helpers (SKILL.md) ----------------------------------

def frontmatter(md: str) -> str:
    if not md.startswith("---"):
        return ""
    end = md.find("\n---", 3)
    return md[3:end] if end != -1 else ""


def fm_scalar(fm: str, key: str) -> str:
    m = re.search(rf'^{re.escape(key)}\s*:\s*"?(.+?)"?\s*$', fm, re.M)
    return m.group(1).strip() if m else ""


def fm_metadata_scalar(fm: str, key: str) -> str:
    m = re.search(
        rf'^metadata\s*:[\s\S]*?^\s+{re.escape(key)}\s*:\s*"?(.+?)"?\s*$', fm, re.M
    )
    return m.group(1).strip() if m else ""


def fm_tags(fm: str) -> list:
    raw = fm_scalar(fm, "tags")
    if not raw:
        return []
    inner = re.sub(r"^\[|\]$", "", raw)
    return [t.strip().strip("\"'").strip() for t in inner.split(",") if t.strip()]


# ---------- env helpers ------------------------------------------------------

def env_names(path: str) -> list:
    if not os.path.isfile(path):
        return []
    out = []
    with open(path, encoding="utf-8") as fh:
        for line in fh:
            line = line.strip()
            if not line or line.startswith("#"):
                continue
            name = line.split("=", 1)[0].strip()
            if re.match(r"^[A-Za-z_][A-Za-z0-9_]*$", name):
                out.append(name)
    return out


# ---------- file / hash helpers ----------------------------------------------

def _prune(dirs: list) -> None:
    dirs[:] = [d for d in dirs if d != "__pycache__"]


def _is_artifact(f: str) -> bool:
    return f.endswith((".pyc", ".pyo"))


def file_list(d: str) -> list:
    out = []
    for root, dirs, files in os.walk(d):
        _prune(dirs)
        for f in files:
            if _is_artifact(f):
                continue
            out.append(os.path.relpath(os.path.join(root, f), d).replace(os.sep, "/"))
    return sorted(out)


def dir_content_hash(d: str) -> str:
    h = hashlib.sha256()
    for root, dirs, files in os.walk(d):
        _prune(dirs)
        for f in sorted(files):
            if _is_artifact(f):
                continue
            p = os.path.join(root, f)
            rel = os.path.relpath(p, d).replace(os.sep, "/")
            h.update(rel.encode())
            h.update(b"\0")
            with open(p, "rb") as fh:
                h.update(fh.read())
            h.update(b"\0")
    return h.hexdigest()[:12]


# ---------- skill.yaml + inner-skill discovery -------------------------------

def load_skill_yaml(path: str) -> dict:
    with open(path, encoding="utf-8") as fh:
        return yaml.safe_load(fh) or {}


def find_units(repo_root: str) -> list:
    """Find every dir holding .robomotion/skill.yaml. Returns relative paths."""
    units = []
    for root, dirs, files in os.walk(repo_root):
        dirs[:] = [d for d in dirs if d not in SKIP_DIRS and not d.startswith(".")]
        sy = os.path.join(root, ROBOMOTION_DIR, SKILL_YAML)
        if os.path.isfile(sy):
            rel = os.path.relpath(root, repo_root).replace(os.sep, "/")
            units.append("" if rel == "." else rel)
    return sorted(units)


def needs_sandbox(skill_dir: str) -> str:
    scripts = os.path.join(skill_dir, "scripts")
    has_scripts = os.path.isdir(scripts) and any(os.scandir(scripts))
    if has_scripts or os.path.isfile(os.path.join(skill_dir, "post-install.sh")):
        return "container"
    return "host"


def read_skill(repo_root: str, skill_rel: str, group: dict | None) -> dict:
    """Build an index entry for one SKILL.md folder."""
    skill_abs = os.path.join(repo_root, skill_rel)
    md_path = os.path.join(skill_abs, "SKILL.md")
    md = open(md_path, encoding="utf-8").read()
    fm = frontmatter(md)
    name = fm_scalar(fm, "name") or os.path.basename(skill_rel)
    summary = fm_scalar(fm, "summary") or fm_scalar(fm, "description")
    version = (
        fm_scalar(fm, "version")
        or fm_metadata_scalar(fm, "version")
        or (group["version"] if group else "")
    )
    entry = {
        "name": name,
        "path": skill_rel,
        "title": fm_scalar(fm, "title") or name,
        "summary": summary,
        "version": version,
        "tags": fm_tags(fm),
        "mode": needs_sandbox(skill_abs),
        "env": {
            "required": env_names(os.path.join(skill_abs, "env.required")),
            "optional": env_names(os.path.join(skill_abs, "env.optional")),
        },
        "content_hash": dir_content_hash(skill_abs),
        "files": file_list(skill_abs),
    }
    # Inherit attribution from the enclosing group (denormalized for the Designer)
    if group is not None:
        entry["author"] = group["author"]
        entry["source_url"] = build_inner_source_url(group, skill_rel)
        entry["license"] = group["license"]
        entry["group"] = group["path"] or "."
    return entry


def build_inner_source_url(group: dict, skill_rel: str) -> str:
    """For an inner skill, link directly to its upstream subdir if possible.
    Falls back to the group's source_url."""
    base = (group.get("source_url") or "").rstrip("/")
    if not base or not base.startswith("http"):
        return base
    group_path = group["path"] or ""
    if group_path and skill_rel.startswith(group_path + "/"):
        sub = skill_rel[len(group_path) + 1:]
        # For vendored github URLs, link to /tree/main/<sub>
        if "github.com" in base:
            return f"{base}/tree/main/{sub}"
        return f"{base}/{sub}"
    return base


def discover_inner_skills(repo_root: str, group_rel: str) -> list:
    """For a group, walk <group>/skills/<name>/SKILL.md."""
    skills_dir = os.path.join(repo_root, group_rel, "skills")
    if not os.path.isdir(skills_dir):
        return []
    rels = []
    for entry in sorted(os.listdir(skills_dir)):
        sub = os.path.join(skills_dir, entry)
        if os.path.isdir(sub) and os.path.isfile(os.path.join(sub, "SKILL.md")):
            rels.append(f"{group_rel}/skills/{entry}")
    return rels


def has_file(unit_root: str, name: str) -> bool:
    return os.path.isfile(os.path.join(unit_root, ROBOMOTION_DIR, name))


# ---------- main -------------------------------------------------------------

def build(repo_root: str) -> dict:
    groups, standalone = [], []
    for unit_rel in find_units(repo_root):
        unit_abs = os.path.join(repo_root, unit_rel) if unit_rel else repo_root
        sy = load_skill_yaml(os.path.join(unit_abs, ROBOMOTION_DIR, SKILL_YAML))
        sy["path"] = unit_rel
        unit_type = sy.get("type", "group" if os.path.isdir(os.path.join(unit_abs, "skills")) else "skill")

        meta = {
            "path": unit_rel,
            "name": sy.get("name", os.path.basename(unit_rel) or unit_rel),
            "title": sy.get("title", sy.get("name", "")),
            "type": unit_type,
            "version": sy.get("version", ""),
            "author": sy.get("author", ""),
            "source_url": sy.get("source_url", ""),
            "license": sy.get("license", ""),
            "summary": sy.get("summary", ""),
            "tags": sy.get("tags", []) or [],
            "has_post_install": has_file(unit_abs, "post-install.sh"),
            "has_env_yaml": has_file(unit_abs, "env.yaml"),
            "has_changelog": has_file(unit_abs, "CHANGELOG.md"),
            "has_license": has_file(unit_abs, "LICENSE"),
            "content_hash": dir_content_hash(os.path.join(unit_abs, ROBOMOTION_DIR)),
        }

        if unit_type == "group":
            inner_rels = discover_inner_skills(repo_root, unit_rel)
            meta["skills"] = [read_skill(repo_root, r, meta) for r in inner_rels]
            # files[] = shared assets at the group root (everything OUTSIDE skills/<name>/)
            # — used by the launcher to fetch the group's .robomotion/, tools/, bin/, root docs,
            # etc. via the per-file index fetch path. Inner skill files are listed separately
            # in each skill entry.
            all_files = file_list(unit_abs)
            inner_prefixes = [
                ("" if not unit_rel else os.path.relpath(r, unit_rel).replace(os.sep, "/"))
                for r in inner_rels
            ]
            meta["files"] = [
                f for f in all_files
                if not any(f == p or f.startswith(p + "/") for p in inner_prefixes)
            ]
            groups.append(meta)
        else:
            # type: skill — unit_rel itself contains SKILL.md
            entry = read_skill(repo_root, unit_rel, None)
            entry["author"] = meta["author"]
            entry["source_url"] = meta["source_url"]
            entry["license"] = meta["license"]
            standalone.append(entry)

    return {
        "schema_version": SCHEMA_VERSION,
        "groups": groups,
        "skills": standalone,
    }


def main() -> int:
    repo_root = os.path.abspath(os.path.dirname(__file__))
    index = build(repo_root)
    text = yaml.dump(
        index,
        default_flow_style=False,
        sort_keys=False,
        allow_unicode=True,
        width=120,
    )
    out = os.path.join(repo_root, "index.yaml")

    n_groups = len(index["groups"])
    n_group_skills = sum(len(g["skills"]) for g in index["groups"])
    n_standalone = len(index["skills"])

    if "--check" in sys.argv:
        current = open(out, encoding="utf-8").read() if os.path.isfile(out) else ""
        if current != text:
            sys.stderr.write("index.yaml is stale — run `python3 build-index.py` and commit.\n")
            return 1
        print(f"index.yaml up to date ({n_groups} group(s), {n_group_skills} grouped skill(s), {n_standalone} standalone)")
        return 0

    with open(out, "w", encoding="utf-8") as fh:
        fh.write(text)
    print(f"wrote index.yaml: {n_groups} group(s), {n_group_skills} grouped skill(s), {n_standalone} standalone")
    return 0


if __name__ == "__main__":
    sys.exit(main())
