#!/usr/bin/env python3
"""Markdown content scanner for the markdown-only policy profile.

Implements rules 1, 2, and 4 of POLICY.md (file allowlist, content scan,
frontmatter check). Rules 3 (license whitelist) and 5 (eval gate) are
enforced by validate_index.py and run_eval.py respectively.

Usage:
    python3 scripts/scan_content.py skills/<name>             # scan one
    python3 scripts/scan_content.py --all                     # scan everything
    python3 scripts/scan_content.py --changed-since <ref>     # diff-aware

Exit codes:
    0  — clean (or only soft-warnings)
    1  — at least one hard-fail
    2  — usage error
"""

import argparse
import json
import os
import re
import subprocess
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
SKILLS_DIR = REPO_ROOT / "skills"

# ----------------------------------------------------------------------
# Rule 1 — file allowlist
# ----------------------------------------------------------------------

ALLOWED_TOP = {"SKILL.md", "eval-set.json", "LICENSE", "NOTICE", "USAGE.md"}
ALLOWED_DIRS = {"references", "assets", "templates"}
# Text/markup/image only. Binary executables and arbitrary blobs are
# never allowed. PDFs are deliberately excluded — they carry hidden
# JavaScript and embedded fonts.
ALLOWED_LEAF_EXT = {
    ".md", ".txt",
    ".png", ".jpg", ".jpeg", ".svg",
    # markup / text templates (research, writing, diagram skills need these)
    ".html", ".htm",
    ".tex", ".sty", ".bib", ".bst", ".cls",
    ".json", ".yaml", ".yml", ".toml",
    # diagrams as text
    ".mmd", ".puml", ".dot",
    # data tables
    ".csv", ".tsv",
}

REJECTED_NAMES = {
    "package.json", "package-lock.json", "yarn.lock", "pnpm-lock.yaml",
    "requirements.txt", "pyproject.toml", "setup.py", "setup.cfg", "Pipfile",
    "Pipfile.lock", "poetry.lock", "Cargo.toml", "Cargo.lock", "go.mod",
    "go.sum", ".env", ".env.local",
}

REJECTED_EXT = {
    ".sh", ".bash", ".zsh", ".fish", ".ps1", ".bat", ".cmd",
    ".py", ".js", ".ts", ".mjs", ".cjs", ".rb", ".go", ".rs", ".c", ".cpp",
    ".exe", ".dll", ".so", ".dylib", ".bin", ".out",
}


def scan_files(skill_dir: Path) -> list[str]:
    """Return list of hard-fail file findings."""
    findings = []
    if not skill_dir.is_dir():
        return [f"not a directory: {skill_dir}"]

    found_skill_md = False
    for path in sorted(skill_dir.rglob("*")):
        rel = path.relative_to(skill_dir)
        parts = rel.parts

        if path.is_symlink():
            findings.append(f"symlinks not allowed: {rel}")
            continue

        if path.is_dir():
            if len(parts) == 1 and parts[0] == "scripts":
                findings.append(
                    "scripts/ directory not allowed under markdown-only "
                    "profile — file as Package Candidate or rebuild as "
                    "a Robomotion package"
                )
            continue

        if rel.name == "SKILL.md" and len(parts) == 1:
            found_skill_md = True

        if rel.name.startswith(".") and rel.name != ".gitkeep":
            findings.append(f"hidden file not allowed: {rel}")
            continue

        if rel.name in REJECTED_NAMES:
            findings.append(f"package-manager file not allowed: {rel}")
            continue

        if path.suffix.lower() in REJECTED_EXT:
            findings.append(f"executable/code file not allowed: {rel}")
            continue

        # Top-level file
        if len(parts) == 1:
            if rel.name not in ALLOWED_TOP:
                findings.append(f"unexpected top-level file: {rel}")
            continue

        # Subdirectory file
        if parts[0] not in ALLOWED_DIRS:
            findings.append(f"unexpected subdirectory: {parts[0]}/")
            continue

        if path.suffix.lower() not in ALLOWED_LEAF_EXT:
            findings.append(
                f"file in {parts[0]}/ has disallowed extension: {rel}"
            )

    if not found_skill_md:
        findings.append("missing SKILL.md")

    return findings


# ----------------------------------------------------------------------
# Rule 2 — markdown content scanner
# ----------------------------------------------------------------------

HARD_FAIL_PATTERNS = [
    (r"curl\s+[^\n|`]+\|\s*(?:bash|sh|zsh|fish)", "curl-pipe-shell"),
    (r"wget\s+[^\n|`]+\|\s*(?:bash|sh|zsh|fish)", "wget-pipe-shell"),
    (r"\bpip(?:x|3)?\s+install\b", "pip-install"),
    (r"\buv\s+pip\s+install\b", "uv-pip-install"),
    (r"\bnpm\s+install\s+-g\b", "npm-global-install"),
    (r"\byarn\s+global\s+add\b", "yarn-global-add"),
    (r"\bpnpm\s+install\s+-g\b", "pnpm-global-install"),
    (r"\bchmod\s+\+x\b", "chmod-plus-x"),
    (r"(?<![A-Za-z_])eval\s*\(", "eval-call"),
    (r"(?<![A-Za-z_])exec\s*\(", "exec-call"),
    (r"\bsubprocess\.\b", "subprocess-call"),
    (r"\bdocker\s+run\b", "docker-run"),
    (r"\brm\s+-rf\s+/(?:\s|$)", "rm-rf-root"),
    (r"paste\s+your\s+api\s+key", "credential-paste-prompt"),
    (r"enter\s+your\s+password", "credential-paste-prompt"),
]

# `ssh ` and `scp ` are hard-fail under markdown-only but allowed under
# a future markdown-with-ssh-allowed profile. Phase 1 ships only
# markdown-only, so they're hard-fail here.
HARD_FAIL_PATTERNS.extend([
    (r"(?:^|\s)ssh\s+[a-zA-Z0-9_.-]+@", "ssh-invocation"),
    (r"(?:^|\s)scp\s+", "scp-invocation"),
])

# Backticked CLI invocation extractor. We pick the first token of every
# inline `...` block that looks like a shell command (starts with a
# lowercase identifier and contains a space).
INLINE_CODE = re.compile(r"`([^`\n]{2,})`")
# Common false positives we exclude from the CLI declaration check.
# Keep in sync with import_hermes.py SHELL_IGNORE.
CLI_IGNORE = {
    # Robomotion CLI is implicit for every Package Wrapper Skill.
    "robomotion",
    "python", "python3", "node", "npx", "make",
    "cd", "ls", "cat", "echo", "grep", "find", "head", "tail",
    "less", "more", "open", "true", "false", "exit", "return",
    "set", "export", "env", "unset", "source", "test", "let",
    "read", "shift", "trap", "wait", "jobs", "bg", "fg", "kill",
    "mkdir", "rmdir", "rm", "mv", "cp", "ln", "touch", "chmod",
    "chown", "stat", "df", "du", "wc", "sort", "uniq", "tr",
    "awk", "sed", "cut", "paste", "tee", "xargs", "sleep",
    "date", "time", "which", "type", "alias",
    "vim", "nvim", "nano", "emacs", "code", "subl",
    "exec", "explain", "deps", "prefix", "extract", "process",
    "import", "select", "use", "run", "build", "test", "lint",
    "watch", "start", "stop", "status", "list", "show", "get",
    "create", "update", "delete", "remove", "add", "install",
    "config", "configure", "init", "new",
    # subcommand verbs commonly seen in skills as `<verb> --flag` snippets
    "connect", "disconnect", "login", "logout", "auth", "search",
    "query", "send", "receive", "upload", "download", "fetch", "pull",
    "push", "merge", "fork", "branch", "tag", "checkout", "clone",
}


def extract_cli_tokens(body: str) -> set[str]:
    """Pull leading-token of inline-code shell-style commands."""
    tokens = set()
    for m in INLINE_CODE.finditer(body):
        snippet = m.group(1).strip()
        # Skip if no whitespace (probably an identifier, e.g. `var_name`)
        if " " not in snippet:
            continue
        head = snippet.split()[0]
        # Skip flags, paths, identifiers with dots
        if not re.match(r"^[a-z][a-z0-9_-]*$", head):
            continue
        if head in CLI_IGNORE:
            continue
        tokens.add(head)
    return tokens


def scan_markdown(text: str, declared_clis: set[str]) -> tuple[list[dict], list[dict]]:
    """Return (hard_fail_findings, soft_warn_findings)."""
    hard = []
    soft = []

    for pattern, kind in HARD_FAIL_PATTERNS:
        for m in re.finditer(pattern, text, re.IGNORECASE | re.MULTILINE):
            hard.append({
                "kind": kind,
                "match": m.group(0)[:120],
                "offset": m.start(),
            })

    referenced = extract_cli_tokens(text)
    undeclared = referenced - declared_clis
    for cli in sorted(undeclared):
        hard.append({
            "kind": "undeclared-cli",
            "cli": cli,
            "hint": f"add to runtime.requires_cli or remove from SKILL.md",
        })

    # Soft warning: any backtick-shell at all
    if re.search(r"```(?:bash|sh|zsh|shell)", text):
        soft.append({"kind": "shell-codeblock-present"})

    return hard, soft


# ----------------------------------------------------------------------
# Frontmatter
# ----------------------------------------------------------------------

REQUIRED_FRONTMATTER_D = {"name", "description", "version", "license"}


def parse_frontmatter(text: str) -> dict | None:
    if not text.startswith("---"):
        return None
    end = text.find("\n---", 3)
    if end == -1:
        return None
    block = text[3:end]
    data = {}
    current_key = None
    current_indent = 0
    for raw in block.splitlines():
        line = raw.rstrip()
        if not line.strip():
            continue
        # Leading-spaces tracked for nested mapping detection
        indent = len(line) - len(line.lstrip())
        stripped = line.strip()
        if indent == 0 and ":" in stripped:
            k, _, v = stripped.partition(":")
            k = k.strip()
            v = v.strip().strip('"').strip("'")
            data[k] = v
            current_key = k
            current_indent = 0
        # We don't try to fully parse nested YAML; the import script
        # writes a flat-with-known-nests structure that downstream
        # validators handle via PyYAML when needed.
    return data


def get_declared_clis(text: str) -> set[str]:
    """Grep runtime.requires_cli entries out of frontmatter (best-effort)."""
    fm_end = text.find("\n---", 3) if text.startswith("---") else -1
    if fm_end == -1:
        return set()
    fm = text[:fm_end]
    out = set()
    in_section = False
    for raw in fm.splitlines():
        line = raw.rstrip()
        stripped = line.strip()
        if re.match(r"^requires_cli:\s*", stripped):
            in_section = True
            continue
        if in_section:
            if stripped.startswith("-") and "name:" in stripped:
                m = re.search(r"name:\s*[\"']?([a-z0-9_-]+)", stripped)
                if m:
                    out.add(m.group(1))
            elif line and not line.startswith(" "):
                in_section = False
    return out


# ----------------------------------------------------------------------
# Driver
# ----------------------------------------------------------------------

def scan_skill(skill_dir: Path) -> tuple[list[str], list[dict], list[dict]]:
    file_findings = scan_files(skill_dir)
    md_path = skill_dir / "SKILL.md"
    if not md_path.exists():
        return file_findings, [], []
    text = md_path.read_text(encoding="utf-8", errors="replace")
    declared = get_declared_clis(text)
    hard, soft = scan_markdown(text, declared)
    return file_findings, hard, soft


def changed_skills_since(ref: str) -> list[Path]:
    try:
        out = subprocess.check_output(
            ["git", "-C", str(REPO_ROOT), "diff", "--name-only", f"{ref}...HEAD"],
            text=True,
        )
    except subprocess.CalledProcessError as e:
        print(f"git diff failed: {e}", file=sys.stderr)
        return []
    seen = set()
    for line in out.splitlines():
        if not line.startswith("skills/"):
            continue
        parts = line.split("/")
        if len(parts) < 2:
            continue
        seen.add(SKILLS_DIR / parts[1])
    return sorted(p for p in seen if p.is_dir())


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("skill", nargs="?", help="path to a single skill dir")
    ap.add_argument("--all", action="store_true", help="scan every skill")
    ap.add_argument("--changed-since", metavar="REF",
                    help="scan skills changed since git ref")
    ap.add_argument("--json", action="store_true", help="emit machine-readable")
    args = ap.parse_args()

    if args.skill:
        targets = [Path(args.skill).resolve()]
    elif args.changed_since:
        targets = changed_skills_since(args.changed_since)
    elif args.all:
        targets = sorted(p for p in SKILLS_DIR.iterdir() if p.is_dir())
    else:
        ap.print_usage()
        sys.exit(2)

    if not targets:
        print("no skills to scan")
        return 0

    summary = {"clean": [], "warn": [], "fail": []}
    any_fail = False

    for skill_dir in targets:
        files, hard, soft = scan_skill(skill_dir)
        rec = {
            "skill": skill_dir.name,
            "file_findings": files,
            "hard": hard,
            "soft": soft,
        }
        if files or hard:
            summary["fail"].append(rec)
            any_fail = True
        elif soft:
            summary["warn"].append(rec)
        else:
            summary["clean"].append(rec)

    if args.json:
        print(json.dumps(summary, indent=2))
    else:
        for rec in summary["fail"]:
            print(f"FAIL: {rec['skill']}")
            for f in rec["file_findings"]:
                print(f"  - file: {f}")
            for h in rec["hard"]:
                detail = h.get("match") or h.get("cli") or ""
                print(f"  - content: {h.get('kind')} {detail}")
        for rec in summary["warn"]:
            print(f"WARN: {rec['skill']}")
            for s in rec["soft"]:
                print(f"  - {s.get('kind')}")
        clean_n = len(summary["clean"])
        if clean_n:
            print(f"OK: {clean_n} skill(s) clean")

    return 1 if any_fail else 0


if __name__ == "__main__":
    sys.exit(main())
