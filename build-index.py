#!/usr/bin/env python3
"""Generate index.json — the discovery manifest for this skill repo.

The Designer reads ONE index.json per repo instead of probing every skill's
SKILL.md over the GitHub API (which rate-limits at scale). CI regenerates this
and fails if the committed copy is stale (see --check).

Output is deterministic (no timestamps) so the drift check is stable. Content
hashes capture "what changed". Run:

    python3 build-index.py            # write index.json
    python3 build-index.py --check    # exit 1 if index.json is out of date

See docs/skill-system-scale-design.md (Pillar 1).
"""

from __future__ import annotations

import hashlib
import json
import os
import re
import sys

SCHEMA_VERSION = 1
SHARED_DIR = "_shared"
SKIP_DIRS = {".git", ".github", "node_modules", "docs"}


def frontmatter(md: str) -> str:
    if not md.startswith("---"):
        return ""
    end = md.find("\n---", 3)
    return md[3:end] if end != -1 else ""


def fm_scalar(fm: str, key: str) -> str:
    m = re.search(rf'^{re.escape(key)}\s*:\s*"?(.+?)"?\s*$', fm, re.M)
    return m.group(1).strip() if m else ""


def fm_metadata_scalar(fm: str, key: str) -> str:
    m = re.search(rf'^metadata\s*:[\s\S]*?^\s+{re.escape(key)}\s*:\s*"?(.+?)"?\s*$', fm, re.M)
    return m.group(1).strip() if m else ""


def fm_tags(fm: str) -> list:
    raw = fm_scalar(fm, "tags")
    if not raw:
        return []
    inner = re.sub(r"^\[|\]$", "", raw)
    return [t.strip().strip("\"'").strip() for t in inner.split(",") if t.strip()]


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


def _prune(dirs: list) -> None:
    """Drop transient dirs in place so they never enter the index walk."""
    dirs[:] = [x for x in dirs if x != "__pycache__"]


def _is_artifact(f: str) -> bool:
    return f.endswith((".pyc", ".pyo"))


def file_list(d: str) -> list:
    """Sorted relative (posix) paths of every regular file under d — the
    manifest the launcher uses to fetch a skill/_shared file-by-file.
    Skips transient build artifacts (__pycache__, *.pyc)."""
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


def nearest_shared(repo_root: str, skill_rel: str) -> str | None:
    """Walk up from the skill's parent dir to the repo root; return the
    relative path of the nearest `_shared/` dir, or None."""
    d = os.path.dirname(skill_rel)
    while True:
        cand = os.path.join(d, SHARED_DIR) if d else SHARED_DIR
        if os.path.isdir(os.path.join(repo_root, cand)):
            return cand.replace(os.sep, "/")
        if not d:
            return None
        d = os.path.dirname(d)


def classify(skill_dir: str) -> str:
    scripts = os.path.join(skill_dir, "scripts")
    has_scripts = os.path.isdir(scripts) and any(os.scandir(scripts))
    if has_scripts or os.path.isfile(os.path.join(skill_dir, "post-install.sh")):
        return "container"
    return "host"


def build(repo_root: str) -> dict:
    skills, shared_paths = [], set()
    for root, dirs, files in os.walk(repo_root):
        dirs[:] = [d for d in dirs if d not in SKIP_DIRS and not d.startswith(".")]
        if "SKILL.md" not in files:
            continue
        rel = os.path.relpath(root, repo_root).replace(os.sep, "/")
        if rel == ".":
            continue
        md = open(os.path.join(root, "SKILL.md"), encoding="utf-8").read()
        fm = frontmatter(md)
        name = fm_scalar(fm, "name") or os.path.basename(rel)
        group = os.path.dirname(rel).replace(os.sep, "/")
        shared = nearest_shared(repo_root, rel)
        if shared:
            shared_paths.add(shared)
        skills.append({
            "name": name,
            "path": rel,
            "group": group,
            "summary": fm_scalar(fm, "summary") or fm_scalar(fm, "description"),
            "tags": fm_tags(fm),
            "version": fm_scalar(fm, "version") or fm_metadata_scalar(fm, "version") or "",
            "mode": classify(root),
            "env": {
                "required": env_names(os.path.join(root, "env.required")),
                "optional": env_names(os.path.join(root, "env.optional")),
            },
            "shared": shared,
            "contentHash": dir_content_hash(root),
            "files": file_list(root),
        })

    skills.sort(key=lambda s: s["path"])
    shared = [
        {
            "path": p,
            "contentHash": dir_content_hash(os.path.join(repo_root, p)),
            "files": file_list(os.path.join(repo_root, p)),
        }
        for p in sorted(shared_paths)
    ]
    return {"schemaVersion": SCHEMA_VERSION, "skills": skills, "shared": shared}


def main() -> int:
    repo_root = os.path.dirname(os.path.abspath(__file__))
    index = build(repo_root)
    text = json.dumps(index, indent=2, ensure_ascii=False) + "\n"
    out = os.path.join(repo_root, "index.json")

    if "--check" in sys.argv:
        current = open(out, encoding="utf-8").read() if os.path.isfile(out) else ""
        if current != text:
            sys.stderr.write("index.json is stale — run `python3 build-index.py` and commit.\n")
            return 1
        print(f"index.json up to date ({len(index['skills'])} skills)")
        return 0

    with open(out, "w", encoding="utf-8") as fh:
        fh.write(text)
    print(f"wrote index.json ({len(index['skills'])} skills, {len(index['shared'])} shared)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
