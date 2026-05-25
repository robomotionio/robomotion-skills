#!/usr/bin/env python3
"""Import a Documentation Skill from upstream Hermes Agent.

Pinned-ref, dry-runnable, idempotent. Refuses to import skills that
ship `scripts/` or fail the markdown-only content scanner. Stub
eval-set.json is generated; humans upgrade quality cases during PR
review.

Usage:
    python3 scripts/import_hermes.py \\
        --upstream /path/to/hermes-agent --ref v2026.4.23 \\
        --role D \\
        --skill software-development/test-driven-development [--apply]

    python3 scripts/import_hermes.py \\
        --upstream /path/to/hermes-agent --ref v2026.4.23 \\
        --role D --batch software-development [--apply]

The default mode is dry-run: prints what would change. `--apply`
writes files. `--all-targets` imports the curated Phase 1 list.
"""

import argparse
import datetime as dt
import hashlib
import json
import os
import re
import shutil
import subprocess
import sys
import textwrap
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
SKILLS_DIR = REPO_ROOT / "skills"
ATTRIBUTION = REPO_ROOT / "ATTRIBUTION.md"
TODAY = dt.date.today().isoformat()

# Curated Phase 1 import targets; expanded list lives in skill-deprecated.yaml
# (rejected entries are recorded there, not here).
PHASE_1_TARGETS = [
    "software-development/plan",
    "software-development/test-driven-development",
    "software-development/systematic-debugging",
    "software-development/writing-plans",
    "software-development/subagent-driven-development",
    "software-development/requesting-code-review",
    "creative/creative-ideation",
    "creative/architecture-diagram",
    "mcp/native-mcp",
    "dogfood",
    "research/research-paper-writing",
    "autonomous-ai-agents/claude-code",
    "autonomous-ai-agents/codex",
]


def run_git(upstream: Path, *args: str) -> str:
    return subprocess.check_output(
        ["git", "-C", str(upstream), *args], text=True
    ).strip()


def resolve_commit(upstream: Path, ref: str) -> str:
    return run_git(upstream, "rev-parse", ref)


def parse_frontmatter(text: str) -> tuple[dict, str]:
    """Return (frontmatter_dict, body)."""
    if not text.startswith("---"):
        return {}, text
    end = text.find("\n---", 3)
    if end == -1:
        return {}, text
    block = text[3:end]
    body = text[end + 4:].lstrip("\n")
    data: dict = {}
    in_hermes = False
    in_tags = False
    in_related = False
    for raw in block.splitlines():
        line = raw.rstrip()
        stripped = line.strip()
        indent = len(line) - len(line.lstrip())
        if not stripped or stripped.startswith("#"):
            continue
        if indent == 0:
            in_hermes = stripped.startswith("metadata:") or stripped == "metadata:"
            in_tags = False
            in_related = False
            if ":" in stripped and not stripped.endswith(":"):
                k, _, v = stripped.partition(":")
                v = v.strip().strip('"').strip("'")
                data[k.strip()] = v
            elif stripped.endswith(":"):
                data[stripped[:-1]] = {}
        else:
            if "tags:" in stripped:
                m = re.search(r"tags:\s*\[(.+?)\]", stripped)
                if m:
                    items = [t.strip().strip('"').strip("'")
                             for t in m.group(1).split(",")]
                    data.setdefault("_hermes_tags", []).extend(items)
            elif "related_skills:" in stripped:
                m = re.search(r"related_skills:\s*\[(.+?)\]", stripped)
                if m:
                    items = [t.strip().strip('"').strip("'")
                             for t in m.group(1).split(",")]
                    data.setdefault("_hermes_related", []).extend(items)
    return data, body


SHELL_IGNORE = {
    # interpreters often invoked but not skill-defining tools
    "python", "python3", "node", "npx", "make",
    # shell builtins / coreutils we never want to gate on
    "cd", "ls", "cat", "echo", "grep", "find", "head", "tail",
    "less", "more", "open", "true", "false", "exit", "return",
    "set", "export", "env", "unset", "source", "test", "let",
    "read", "shift", "trap", "wait", "jobs", "bg", "fg", "kill",
    "mkdir", "rmdir", "rm", "mv", "cp", "ln", "touch", "chmod",
    "chown", "stat", "df", "du", "wc", "sort", "uniq", "tr",
    "awk", "sed", "cut", "paste", "tee", "xargs", "sleep",
    "date", "time", "which", "type", "alias",
    # editors / interactive tools
    "vim", "nvim", "nano", "emacs", "code", "subl",
    # ambiguous English verbs that come after backticks but aren't tools
    "exec", "explain", "deps", "prefix", "extract", "process",
    "import", "select", "use", "run", "build", "test", "lint",
    "watch", "start", "stop", "status", "list", "show", "get",
    "create", "update", "delete", "remove", "add", "install",
    "config", "configure", "init", "new",
}


def extract_cli_tokens(body: str) -> list[str]:
    """Same heuristic as scan_content.py — keep them in sync."""
    seen = []
    inline = re.compile(r"`([^`\n]{2,})`")
    for m in inline.finditer(body):
        snippet = m.group(1).strip()
        if " " not in snippet:
            continue
        head = snippet.split()[0]
        if not re.match(r"^[a-z][a-z0-9_-]*$", head):
            continue
        if head in SHELL_IGNORE:
            continue
        if head not in seen:
            seen.append(head)
    return seen


def slug_collision_safe(leaf: str, category: str, upstream_path: str) -> str:
    """Pick the destination skill directory name.

    Re-importing the same upstream path lands on the same skill folder
    (idempotency). True collisions — different upstream paths competing
    for the same leaf name — fall back to a category-prefixed name.
    """
    target = SKILLS_DIR / leaf
    if not target.exists():
        return leaf
    # Detect "same upstream path" — i.e. an idempotent re-import.
    md = target / "SKILL.md"
    if md.exists():
        existing = md.read_text(encoding="utf-8", errors="replace")
        # Cheap regex match — full YAML parse is overkill here.
        m = re.search(r"^\s*path:\s*([^\s#]+)\s*$", existing, re.MULTILINE)
        if m and m.group(1).strip() == upstream_path:
            return leaf
    return f"{category}-{leaf}"


def build_eval_set(name: str, description: str, category: str) -> dict:
    """Stub eval-set.json with 3 trigger-positive + 2 trigger-negative cases.

    Schema matches scripts/run_eval.py: top-level `skill_name` + `cases[]`.
    Quality cases are intentionally empty — humans add them during PR review.
    """
    desc_keywords = re.findall(r"[A-Za-z][A-Za-z-]{3,}", description.lower())
    keywords = [k for k in desc_keywords if k not in
                {"when", "with", "from", "this", "that", "they", "uses",
                 "supports", "should", "must", "your", "have", "skill"}][:8]
    first_sentence = description.split(".")[0].strip()
    other_category = "productivity" if category != "productivity" else "research"
    return {
        "skill_name": name,
        "cases": [
            {
                "id": "trigger-pos-1",
                "type": "trigger",
                "query": f"Use the {name} skill to handle this request.",
                "expect_triggered": True,
            },
            {
                "id": "trigger-pos-2",
                "type": "trigger",
                "query": f"I need help with {keywords[0] if keywords else name}.",
                "expect_triggered": True,
            },
            {
                "id": "trigger-pos-3",
                "type": "trigger",
                "query": first_sentence + ".",
                "expect_triggered": True,
            },
            {
                "id": "trigger-neg-1",
                "type": "trigger",
                "query": f"Schedule a meeting next Tuesday in the {other_category} app.",
                "expect_triggered": False,
            },
            {
                "id": "trigger-neg-2",
                "type": "trigger",
                "query": "What's the weather forecast for tomorrow?",
                "expect_triggered": False,
            },
        ],
    }


def rewrite_frontmatter(
    *, name: str, role: str, category: str, description: str,
    version: str, license_str: str, tags: list[str],
    upstream_repo: str, upstream_ref: str, upstream_commit: str,
    upstream_path: str, upstream_license: str, requires_cli: list[str],
) -> str:
    if requires_cli:
        cli_lines = ["  requires_cli:"]
        for c in requires_cli:
            cli_lines.append(f"    - name: {c}")
        cli_block = "\n".join(cli_lines)
    else:
        cli_block = "  requires_cli: []"

    tags_yaml = "[" + ", ".join(json.dumps(t) for t in tags) + "]"

    lines = [
        "---",
        f"name: {name}",
        f"description: {json.dumps(description)}",
        f'version: "{version}"',
        f"license: {license_str}",
        f"tags: {tags_yaml}",
        f"role: {role}",
        f"category: {category}",
        "compatibility:",
        "  schema_version: 2",
        '  hermes_agent_min_version: "0.3.0"',
        "policy:",
        "  profile: markdown-only",
        f'  version: "{TODAY}"',
        "runtime:",
        "  requires_packages: []",
        cli_block,
        "  requires_env_vars: []",
        "source:",
        "  kind: upstream-import",
        f"  repo: {upstream_repo}",
        f"  ref: {upstream_ref}",
        f"  commit: {upstream_commit}",
        f"  path: {upstream_path}",
        f"  license: {upstream_license}",
        f"  license_notice_path: ATTRIBUTION.md#{name}",
        "---",
        "",
    ]
    return "\n".join(lines)


def append_attribution(name: str, upstream_path: str, ref: str,
                       commit: str, license_str: str, license_text: str):
    if not ATTRIBUTION.exists():
        ATTRIBUTION.write_text("# Attribution\n\n---\n", encoding="utf-8")
    body = ATTRIBUTION.read_text(encoding="utf-8")
    anchor = f"## {name}"
    if anchor in body:
        return
    section = textwrap.dedent(f"""\

        ## {name}

        - **Upstream:** `{upstream_path}` at `{ref}` (commit `{commit[:12]}`)
        - **License:** {license_str}

        ```
        {textwrap.indent(license_text.strip(), "        ").lstrip()}
        ```

        ---
        """)
    ATTRIBUTION.write_text(body.rstrip() + "\n" + section, encoding="utf-8")


def import_skill(
    upstream: Path, ref: str, commit: str, role: str,
    upstream_path: str, apply: bool, scan_path: Path,
) -> dict:
    """Import one skill. Returns {name, dest, status, notes}."""
    src_dir = upstream / upstream_path
    if not src_dir.is_dir():
        return {"upstream_path": upstream_path, "status": "missing"}

    if (src_dir / "scripts").exists():
        return {"upstream_path": upstream_path, "status": "rejected-scripts"}

    skill_md = src_dir / "SKILL.md"
    if not skill_md.exists():
        return {"upstream_path": upstream_path, "status": "rejected-no-skill-md"}

    text = skill_md.read_text(encoding="utf-8", errors="replace")
    fm, body = parse_frontmatter(text)

    upstream_name = fm.get("name") or src_dir.name
    description = fm.get("description", "")
    version = fm.get("version", "1.0.0")
    license_str = fm.get("license", "MIT")
    tags = fm.get("_hermes_tags", [])
    if not tags:
        tags = []

    # Categorization
    parts = upstream_path.split("/")
    if parts[0] == "skills" and len(parts) >= 2:
        category = parts[1]
    else:
        category = "general"
    if len(parts) == 2:
        # e.g. skills/dogfood — leaf is itself the skill name
        leaf = parts[1]
    else:
        leaf = parts[-1]

    name = slug_collision_safe(leaf, category, upstream_path)
    dest = SKILLS_DIR / name

    requires_cli = extract_cli_tokens(body)

    new_fm = rewrite_frontmatter(
        name=name, role=role, category=category,
        description=description, version=version,
        license_str=license_str, tags=tags,
        upstream_repo="github.com/NousResearch/hermes-agent",
        upstream_ref=ref, upstream_commit=commit,
        upstream_path=upstream_path, upstream_license=license_str,
        requires_cli=requires_cli,
    )
    new_body = body
    new_text = new_fm + new_body.rstrip() + "\n"

    eval_set = build_eval_set(name, description, category)

    notes = []
    if requires_cli:
        notes.append(f"declared CLIs: {', '.join(requires_cli)}")

    if apply:
        dest.mkdir(parents=True, exist_ok=True)
        (dest / "SKILL.md").write_text(new_text, encoding="utf-8")
        (dest / "eval-set.json").write_text(
            json.dumps(eval_set, indent=2) + "\n", encoding="utf-8"
        )
        # Copy allowlisted subdirectories — filter to allowed extensions to
        # match scan_content.ALLOWED_LEAF_EXT. Binary blobs (PDFs, Office
        # docs, executables) are dropped silently and recorded in notes.
        ALLOWED_EXT = {
            ".md", ".txt", ".png", ".jpg", ".jpeg", ".svg",
            ".html", ".htm",
            ".tex", ".sty", ".bib", ".bst", ".cls",
            ".json", ".yaml", ".yml", ".toml",
            ".mmd", ".puml", ".dot",
            ".csv", ".tsv",
        }
        for sub in ("references", "assets", "templates"):
            src_sub = src_dir / sub
            if not src_sub.is_dir():
                continue
            dst_sub = dest / sub
            if dst_sub.exists():
                shutil.rmtree(dst_sub)
            dropped = []
            for p in src_sub.rglob("*"):
                if p.is_dir() or p.is_symlink():
                    continue
                rel = p.relative_to(src_sub)
                if p.suffix.lower() not in ALLOWED_EXT:
                    dropped.append(str(rel))
                    continue
                target = dst_sub / rel
                target.parent.mkdir(parents=True, exist_ok=True)
                shutil.copy2(p, target)
            if dropped:
                notes.append(
                    f"dropped from {sub}/ (disallowed ext): {len(dropped)} file(s)"
                )

        # LICENSE/NOTICE if present upstream and at the directory level
        for fname in ("LICENSE", "NOTICE"):
            f = src_dir / fname
            if f.is_file():
                shutil.copy2(f, dest / fname)

        # Run the content scanner against the materialized output
        ret = subprocess.run(
            [sys.executable, str(scan_path), str(dest)],
            capture_output=True, text=True,
        )
        notes.append(ret.stdout.strip().splitlines()[-1] if ret.stdout else "")
        if ret.returncode != 0:
            return {
                "upstream_path": upstream_path,
                "name": name,
                "dest": str(dest),
                "status": "rejected-content-scanner",
                "notes": notes + [ret.stdout],
            }

        # Append upstream license notice
        try:
            license_text = (upstream / "LICENSE").read_text(encoding="utf-8")
        except OSError:
            license_text = "(upstream LICENSE not found)"
        append_attribution(name, upstream_path, ref, commit, license_str, license_text)

    return {
        "upstream_path": upstream_path,
        "name": name,
        "dest": str(dest),
        "status": "imported" if apply else "would-import",
        "notes": notes,
    }


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--upstream", required=True, type=Path,
                    help="path to a hermes-agent checkout")
    ap.add_argument("--ref", required=True,
                    help="upstream ref to pin (e.g. v2026.4.23)")
    ap.add_argument("--role", choices=["D", "W"], default="D")
    ap.add_argument("--skill", action="append", default=[],
                    help="upstream relative path (e.g. skills/x/y); repeatable")
    ap.add_argument("--all-targets", action="store_true",
                    help="import the curated Phase 1 list")
    ap.add_argument("--apply", action="store_true",
                    help="actually write files (default: dry-run)")
    args = ap.parse_args()

    if not args.upstream.is_dir():
        print(f"--upstream not a directory: {args.upstream}", file=sys.stderr)
        sys.exit(2)

    commit = resolve_commit(args.upstream, args.ref)

    targets = list(args.skill)
    if args.all_targets:
        # Convert curated short paths to "skills/<...>"
        for t in PHASE_1_TARGETS:
            tt = t if t.startswith("skills/") else f"skills/{t}"
            if tt not in targets:
                targets.append(tt)

    if not targets:
        ap.error("no targets — pass --skill or --all-targets")

    scan_path = REPO_ROOT / "scripts" / "scan_content.py"

    print(f"upstream: {args.upstream}")
    print(f"ref:      {args.ref} ({commit})")
    print(f"role:     {args.role}")
    print(f"mode:     {'apply' if args.apply else 'dry-run'}")
    print(f"targets:  {len(targets)}")
    print()

    results = []
    for t in targets:
        if not t.startswith("skills/"):
            t = f"skills/{t}"
        r = import_skill(
            upstream=args.upstream, ref=args.ref, commit=commit, role=args.role,
            upstream_path=t, apply=args.apply, scan_path=scan_path,
        )
        results.append(r)
        marker = "[APPLY]" if args.apply else "[DRY]"
        print(f"{marker} {r['status']:<28} {t}  ->  {r.get('name','?')}")
        for n in r.get("notes", []):
            if n:
                print(f"        {n}")

    rejected = [r for r in results if r["status"].startswith("rejected")]
    if rejected:
        print(f"\n{len(rejected)} rejected — record in skill-deprecated.yaml")


if __name__ == "__main__":
    main()
