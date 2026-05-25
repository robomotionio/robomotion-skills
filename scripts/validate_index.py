#!/usr/bin/env python3
"""Validate skills-index.json and the underlying skills/ tree.

Implements rules 3 (license whitelist), 4 (frontmatter), and structural
checks (role/scripts consistency). Rules 1 and 2 are enforced by
scripts/scan_content.py. Rule 5 (eval gate) by scripts/run_eval.py.

Usage:
    python3 scripts/validate_index.py                    # validate everything
    python3 scripts/validate_index.py --changed-since X  # diff-aware
"""

import argparse
import json
import re
import subprocess
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
SKILLS_DIR = REPO_ROOT / "skills"
INDEX_PATH = REPO_ROOT / "skills-index.json"

LICENSE_WHITELIST = {
    "MIT", "Apache-2.0", "BSD-2-Clause", "BSD-3-Clause", "CC-BY-4.0",
}

VALID_ROLES = {"D", "W"}  # only D/W are publishable in stable

REQUIRED_TOP_FIELDS = {
    "format_version", "corpus_version", "skills",
}

REQUIRED_ENTRY_FIELDS = {
    "name", "path", "description", "version", "license", "tags",
    "role", "category", "checksum", "size_bytes",
    "compatibility", "policy", "runtime", "source", "review",
}


def changed_skills_since(ref: str) -> set[str]:
    try:
        out = subprocess.check_output(
            ["git", "-C", str(REPO_ROOT), "diff", "--name-only", f"{ref}...HEAD"],
            text=True,
        )
    except subprocess.CalledProcessError as e:
        print(f"git diff failed: {e}", file=sys.stderr)
        return set()
    seen = set()
    for line in out.splitlines():
        if line.startswith("skills/"):
            parts = line.split("/")
            if len(parts) >= 2:
                seen.add(parts[1])
    return seen


def validate_entry(entry: dict, errors: list[str], warnings: list[str]):
    name = entry.get("name", "<unnamed>")

    missing = REQUIRED_ENTRY_FIELDS - set(entry.keys())
    if missing:
        errors.append(f"{name}: missing fields {sorted(missing)}")
        return

    if entry["role"] not in VALID_ROLES:
        errors.append(f"{name}: role must be D or W, got {entry['role']!r}")

    lic = entry.get("license")
    if lic not in LICENSE_WHITELIST:
        if not entry.get("review", {}).get("license_exception_pr"):
            errors.append(
                f"{name}: license {lic!r} not in whitelist "
                f"(set review.license_exception_pr to override)"
            )

    skill_dir = REPO_ROOT / entry["path"]
    if not skill_dir.is_dir():
        errors.append(f"{name}: path {entry['path']} does not exist")
        return

    if not (skill_dir / "SKILL.md").exists():
        errors.append(f"{name}: missing SKILL.md at {skill_dir}")

    # role/scripts consistency
    scripts_dir = skill_dir / "scripts"
    if scripts_dir.is_dir():
        if entry["role"] == "D":
            errors.append(
                f"{name}: Documentation Skills cannot have scripts/ "
                f"— rebuild as a Robomotion package or file as Package Candidate"
            )
        else:
            errors.append(
                f"{name}: scripts/ never permitted under markdown-only profile"
            )

    # checksum format
    cs = entry.get("checksum", "")
    if not re.match(r"^sha256:[0-9a-f]{64}$", cs):
        errors.append(f"{name}: checksum must be sha256:<64-hex>")

    # source
    src = entry.get("source", {})
    if src.get("kind") not in {"upstream-import", "robomotion-native", "user-contrib"}:
        errors.append(f"{name}: source.kind must be upstream-import|robomotion-native|user-contrib")
    if src.get("kind") == "upstream-import":
        if not src.get("commit"):
            errors.append(f"{name}: upstream-import requires source.commit")
        if not src.get("license_notice_path"):
            warnings.append(f"{name}: upstream-import without license_notice_path")

    # review status
    status = entry.get("review", {}).get("status")
    if status not in {"active", "deprecated", "revoked"}:
        errors.append(f"{name}: review.status must be active|deprecated|revoked")

    # policy
    policy = entry.get("policy", {})
    if policy.get("profile") != "markdown-only":
        errors.append(f"{name}: only the markdown-only profile is supported in Phase 1")
    if not policy.get("version"):
        errors.append(f"{name}: policy.version is required")

    # frontmatter cross-check
    fm = (skill_dir / "SKILL.md").read_text(encoding="utf-8", errors="replace")
    if not fm.startswith("---"):
        errors.append(f"{name}: SKILL.md missing frontmatter")
        return

    fm_block_end = fm.find("\n---", 3)
    if fm_block_end == -1:
        errors.append(f"{name}: SKILL.md frontmatter unterminated")
        return
    fm_block = fm[3:fm_block_end]
    fm_name = None
    for line in fm_block.splitlines():
        m = re.match(r"^name:\s*[\"']?([^\"'\n]+)", line.strip())
        if m:
            fm_name = m.group(1).strip()
            break
    if fm_name and fm_name != name:
        errors.append(
            f"{name}: SKILL.md frontmatter name {fm_name!r} != index name {name!r}"
        )


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--changed-since", metavar="REF",
                    help="only validate entries whose skill dir changed since ref")
    args = ap.parse_args()

    if not INDEX_PATH.exists():
        print(f"missing {INDEX_PATH}", file=sys.stderr)
        sys.exit(1)

    with open(INDEX_PATH) as f:
        index = json.load(f)

    errors = []
    warnings = []

    missing_top = REQUIRED_TOP_FIELDS - set(index.keys())
    if missing_top:
        errors.append(f"index: missing top-level fields {sorted(missing_top)}")

    if index.get("format_version") != 2:
        errors.append(f"index: format_version must be 2 (got {index.get('format_version')!r})")

    skills = index.get("skills", [])
    target = None
    if args.changed_since:
        target = changed_skills_since(args.changed_since)

    for entry in skills:
        if target is not None and entry.get("name") not in target:
            continue
        validate_entry(entry, errors, warnings)

    for w in warnings:
        print(f"WARN: {w}")
    for e in errors:
        print(f"FAIL: {e}")

    if errors:
        sys.exit(1)

    print(f"OK: {len(skills)} entries validated, {len(warnings)} warnings")


if __name__ == "__main__":
    main()
