#!/usr/bin/env python3
"""
detect-env.py — find env-var references in every skill's scripts and
report (or write) per-skill env.required / env.optional files.

Implements §3.5b of how-to-write-or-port-a-skill-to-robomotion.md.

For every unit (directory with .robomotion/skill.yaml) the detector:

  1. Catalogs scripts:
       per-skill:        <unit>/skills/<skill>/scripts/**  (or unit root for type: skill)
       group-shared:     <unit>/scripts/**, <unit>/tools/clis/**, <unit>/bin/**
  2. Extracts env-var references from each script (.py/.js/.ts/.mjs/.sh)
     and classifies each as required vs optional based on access pattern.
  3. For each skill, decides which scripts it owns:
       - per-skill scripts → always owned
       - group-shared scripts → owned only if SKILL.md mentions the filename
         (OR if the unit has no inner skills, in which case the standalone
         skill owns everything)
  4. Unions env vars across owned scripts → expected env.required / env.optional.
  5. Compares to what's currently on disk; reports drift; optionally writes.

Modes:
  default          → report only (no files touched)
  --write          → write env.required / env.optional where missing/incomplete
  --check          → exit 1 if any skill is missing declared required vars (CI)
  --unit <name>    → restrict to one unit directory
  --skill <name>   → restrict to one skill (within --unit or globally)
  --verbose        → show per-script detection details

Heuristic notes:
  - Python: os.environ["X"] / os.getenv("X") (no default arg, no `.get`)
    → required. os.environ.get(...) / os.getenv("X", default) → optional.
  - JS:  process.env.X used in `throw` / `if (!...)` paths → required;
         used with `||`, `??`, default-assignment → optional.
         (Heuristic: scan the surrounding 2 lines for `throw`/`required`.)
  - Shell: ${X:?...} → required; everything else → optional.
  - Cross-check upstream .env.example / .env.sample: every var listed there
    is upgraded to required unless its line contains "optional".
  - Vars classified BOTH required and optional across scripts → required wins.
"""

import argparse
import os
import re
import sys
from collections import defaultdict
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent
SCRIPT_EXTS = {".py", ".js", ".ts", ".mjs", ".sh"}

# ---------------------------------------------------------------------------
# Env-var extraction per language
# ---------------------------------------------------------------------------

# OS / shell / runtime vars that the platform sets — never report as needing
# user configuration even if a script reads them.
PLATFORM_VARS = {
    # POSIX
    "PATH", "HOME", "USER", "USERNAME", "LOGNAME", "SHELL", "PWD", "OLDPWD",
    "TERM", "COLORTERM", "LANG", "LC_ALL", "LC_CTYPE", "LC_MESSAGES",
    "TMPDIR", "TMP", "TEMP", "IFS",
    "PS1", "PS2", "PS3", "PS4",
    "BASH", "BASH_VERSION", "BASH_SOURCE", "ZSH_VERSION",
    "HOSTNAME", "UID", "EUID", "GROUPS", "RANDOM", "SECONDS", "LINENO",
    "FUNCNAME", "OSTYPE", "MACHTYPE", "DISPLAY", "XDG_CONFIG_HOME",
    "XDG_DATA_HOME", "XDG_CACHE_HOME", "XDG_RUNTIME_DIR",
    # Windows / msys
    "SYSTEMROOT", "WINDIR", "APPDATA", "LOCALAPPDATA", "PROGRAMFILES",
    "PROGRAMDATA", "MSYSTEM", "COMSPEC",
    # Node
    "NODE_ENV", "NODE_OPTIONS", "NODE_PATH", "NPM_CONFIG_PREFIX",
    # CI / runtime
    "CI", "GITHUB_ACTIONS", "RUNNER_OS",
    # Robomotion launcher injects these
    "CLAUDE_PLUGIN_ROOT", "SKILL_DIR", "SESSION_ID", "SHARED_DIR",
}

PY_ENVIRON_BRACKET = re.compile(r"""os\.environ\[\s*["']([A-Z_][A-Z0-9_]*)["']\s*\]""")
PY_ENVIRON_GET = re.compile(r"""os\.environ\.get\(\s*["']([A-Z_][A-Z0-9_]*)["']""")
PY_GETENV = re.compile(r"""os\.getenv\(\s*["']([A-Z_][A-Z0-9_]*)["']\s*(,)?""")

JS_REF = re.compile(r"""process\.env\.([A-Z_][A-Z0-9_]*)""")
JS_BRACKET = re.compile(r"""process\.env\[\s*["']([A-Z_][A-Z0-9_]*)["']\s*\]""")

SH_BRACE_REQUIRED = re.compile(r"""\$\{([A-Z_][A-Z0-9_]*):\?""")


def _is_required_context(ctx: str) -> bool:
    # `if not <name>:` is too broad — matches the common
    # `if not config["foo"]:` fallback idiom and produces false positives.
    # Stick to explicit failure verbs and the JS `if (!process.env.X)` form.
    return bool(
        re.search(r"\b(raise|sys\.exit|assert|throw)\b", ctx)
        or re.search(r"if\s*\(\s*!\s*process\.env\.", ctx)
    )


def scan_python(text):
    """Classify Python env-var refs using surrounding-line context."""
    required, optional = set(), set()
    lines = text.splitlines()
    for i, line in enumerate(lines):
        ctx = "\n".join(lines[i: min(len(lines), i + 5)])
        ctx_required = _is_required_context(ctx)

        # os.environ["X"] — KeyError if unset → always required.
        for m in PY_ENVIRON_BRACKET.finditer(line):
            required.add(m.group(1))

        # os.environ.get("X", ...) — optional unless followed by raise/assert.
        for m in PY_ENVIRON_GET.finditer(line):
            name = m.group(1)
            if ctx_required:
                required.add(name)
            else:
                optional.add(name)

        # os.getenv("X") / os.getenv("X", default)
        for m in PY_GETENV.finditer(line):
            name = m.group(1)
            if ctx_required:
                required.add(name)
            else:
                optional.add(name)
    return required, optional


def scan_javascript(text):
    required, optional = set(), set()
    lines = text.splitlines()
    for i, line in enumerate(lines):
        names = set(JS_REF.findall(line)) | set(JS_BRACKET.findall(line))
        if not names:
            continue
        ctx = "\n".join(lines[max(0, i - 1): min(len(lines), i + 3)])
        has_fallback = bool(
            re.search(r"process\.env(?:\.[A-Z_][A-Z0-9_]*|\[[^\]]+\])\s*\|\|", line)
            or re.search(r"process\.env(?:\.[A-Z_][A-Z0-9_]*|\[[^\]]+\])\s*\?\?", line)
            or re.search(r"process\.env(?:\.[A-Z_][A-Z0-9_]*|\[[^\]]+\])\s*=", line)
        )
        is_required = _is_required_context(ctx)
        for name in names:
            if is_required and not has_fallback:
                required.add(name)
            else:
                optional.add(name)
    return required, optional


def scan_shell(text):
    """Only ${X:?} is unambiguous; bare $X could be a local var, so skip."""
    required, optional = set(), set()
    for m in SH_BRACE_REQUIRED.finditer(text):
        required.add(m.group(1))
    return required, optional


def scan_envfile_example(text):
    """Parse an upstream .env.example: every NAME=... line is required by default."""
    required = set()
    for raw in text.splitlines():
        line = raw.strip()
        if not line or line.startswith("#"):
            continue
        if "=" not in line:
            continue
        name = line.split("=", 1)[0].strip()
        if not re.match(r"^[A-Z_][A-Z0-9_]*$", name):
            continue
        # "optional" annotation in the same line keeps it out of required
        if "optional" in raw.lower():
            continue
        required.add(name)
    return required


def scan_file(path: Path):
    """Return (required, optional) sets, or (None, None) if unscannable."""
    try:
        text = path.read_text(encoding="utf-8", errors="replace")
    except (OSError, UnicodeDecodeError):
        return set(), set()
    ext = path.suffix.lower()
    if ext == ".py":
        return scan_python(text)
    if ext in (".js", ".ts", ".mjs"):
        return scan_javascript(text)
    if ext == ".sh":
        return scan_shell(text)
    return set(), set()


# ---------------------------------------------------------------------------
# Unit / skill discovery
# ---------------------------------------------------------------------------


def discover_units(repo_root: Path):
    """Yield (unit_dir, type) for every .robomotion/skill.yaml in the repo."""
    for sy in sorted(repo_root.glob("*/.robomotion/skill.yaml")):
        unit = sy.parent.parent
        text = sy.read_text(encoding="utf-8", errors="replace")
        m = re.search(r"^type:\s*(\w+)", text, re.MULTILINE)
        type_ = m.group(1) if m else "skill"
        yield unit, type_


def _walk_skill_leaves(base: Path):
    """Recursively yield directories containing SKILL.md under ``base``.
    Stops descending the moment SKILL.md is found in a directory (skills
    don't nest). Hidden dirs are skipped. Matches build-index.py's
    _walk_skill_leaves for consistency between discovery and indexing.
    """
    if not base.is_dir():
        return
    for child in sorted(base.iterdir()):
        if child.name.startswith('.') or not child.is_dir():
            continue
        if (child / "SKILL.md").is_file():
            yield child
        else:
            yield from _walk_skill_leaves(child)


def inner_skill_dirs(unit_dir: Path):
    """Yield skill dirs under a group:
      <unit>/skills/**/SKILL.md               (recursive)
      <unit>/.claude/skills/**/SKILL.md       (recursive)
      <unit>/plugins/<plugin>/skills/<name>   (Claude Code marketplace meta-group)
    """
    for parent in (unit_dir / "skills", unit_dir / ".claude" / "skills"):
        yield from _walk_skill_leaves(parent)
    plugins = unit_dir / "plugins"
    if plugins.is_dir():
        for plugin in sorted(plugins.iterdir()):
            psk = plugin / "skills"
            if not psk.is_dir():
                continue
            for child in sorted(psk.iterdir()):
                if child.is_dir() and (child / "SKILL.md").is_file():
                    yield child


_SKIP_DIRS = {"node_modules", ".venv", "__pycache__", "__tests__", "tests", "test"}


def list_scripts(root: Path, recursive=True):
    """All files under root with a scannable extension. Skips test/dep dirs."""
    if not root.is_dir():
        return []
    out = []
    iterator = root.rglob("*") if recursive else root.iterdir()
    for p in iterator:
        if not p.is_file():
            continue
        if p.suffix.lower() not in SCRIPT_EXTS:
            continue
        parts_lower = {x.lower() for x in p.parts}
        if parts_lower & _SKIP_DIRS:
            continue
        # also skip *.test.* / *.spec.* files
        stem = p.name.lower()
        if ".test." in stem or ".spec." in stem:
            continue
        out.append(p)
    return out


# ---------------------------------------------------------------------------
# Per-skill env aggregation
# ---------------------------------------------------------------------------


def build_script_catalog(unit_dir: Path):
    """
    Return:
      shared:  {script_basename: (required:set, optional:set)}
      per_dir: {script_basename: (required, optional)} for *any* script anywhere
               in the unit (used to attribute per-skill scripts too).
    """
    shared_roots = [
        unit_dir / "scripts",
        unit_dir / "tools" / "clis",
        unit_dir / "bin",
    ]
    shared = {}
    for root in shared_roots:
        for path in list_scripts(root):
            req, opt = scan_file(path)
            if req or opt:
                shared[path.name] = (req, opt)
    return shared


def detect_for_skill(skill_dir: Path, shared, env_example_required):
    """
    Returns expected (required:set, optional:set) for the skill.
    skill_dir = directory with SKILL.md.
    shared    = catalog of group-level scripts {name: (req, opt)}.
    env_example_required = vars from upstream .env.example (force-required).
    """
    skill_md = (skill_dir / "SKILL.md")
    md_text = skill_md.read_text(encoding="utf-8", errors="replace") if skill_md.is_file() else ""

    required, optional = set(), set()

    # 1. Per-skill scripts (anything under <skill>/scripts/ or referenced extra dirs).
    own_scripts = list_scripts(skill_dir / "scripts")
    for path in own_scripts:
        req, opt = scan_file(path)
        required |= req
        optional |= opt

    # 2. Group-shared scripts referenced by name in SKILL.md.
    for name, (req, opt) in shared.items():
        if not name:
            continue
        # quote name as a literal — script names are unambiguous tokens
        if re.search(r"(?<![A-Za-z0-9_])" + re.escape(name) + r"(?![A-Za-z0-9_])", md_text):
            required |= req
            optional |= opt

    # 3. .env.example upgrades detected vars optional→required, but does NOT
    #    pull in unrelated vars that the skill's scripts don't actually touch.
    upgrade = (required | optional) & env_example_required
    required |= upgrade

    # Filter platform-injected vars from BOTH sets.
    required -= PLATFORM_VARS
    optional -= PLATFORM_VARS

    # Required wins over optional.
    optional -= required
    return required, optional


def read_envfile(path: Path):
    if not path.is_file():
        return set()
    out = set()
    for raw in path.read_text(encoding="utf-8", errors="replace").splitlines():
        line = raw.strip()
        if not line or line.startswith("#"):
            continue
        name = line.split("=", 1)[0].strip()
        if re.match(r"^[A-Z_][A-Z0-9_]*$", name):
            out.add(name)
    return out


def write_envfile(path: Path, names, header):
    body = [f"# {header}"]
    body += sorted(names)
    body.append("")
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(body), encoding="utf-8")


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------


def process_skill(skill_dir, shared, env_example_required, write, verbose):
    """Return (ok, status_str)."""
    expected_req, expected_opt = detect_for_skill(skill_dir, shared, env_example_required)
    declared_req = read_envfile(skill_dir / "env.required")
    declared_opt = read_envfile(skill_dir / "env.optional")
    declared = declared_req | declared_opt

    missing_req = expected_req - declared
    missing_opt = expected_opt - declared
    # Vars wrongly declared optional that detector says required:
    wrong_class = expected_req & declared_opt

    if not (expected_req or expected_opt):
        return True, "no scripts touch env"

    issues = []
    if missing_req:
        issues.append(f"missing required={sorted(missing_req)}")
    if missing_opt:
        issues.append(f"missing optional={sorted(missing_opt)}")
    if wrong_class:
        issues.append(f"declared optional but should be required={sorted(wrong_class)}")

    if not issues:
        return True, f"OK (req={len(expected_req)} opt={len(expected_opt)})"

    if write:
        # Merge expected with anything declared but undetected (humans may know better).
        merged_req = expected_req | declared_req
        merged_opt = (expected_opt | declared_opt) - merged_req
        if merged_req:
            write_envfile(
                skill_dir / "env.required",
                merged_req,
                "env.required — generated by detect-env.py (review before commit)",
            )
        if merged_opt:
            write_envfile(
                skill_dir / "env.optional",
                merged_opt,
                "env.optional — generated by detect-env.py (review before commit)",
            )

    return False, "; ".join(issues)


def main():
    ap = argparse.ArgumentParser(description="Detect env-var refs per skill.")
    ap.add_argument("--write", action="store_true", help="write env files (default: report only)")
    ap.add_argument("--check", action="store_true", help="exit 1 if any skill has drift")
    ap.add_argument("--unit", help="restrict to one unit directory")
    ap.add_argument("--skill", help="restrict to one skill name")
    ap.add_argument("--verbose", action="store_true")
    args = ap.parse_args()

    units = list(discover_units(REPO_ROOT))
    if args.unit:
        units = [(u, t) for u, t in units if u.name == args.unit]

    total = ok = drift = 0
    for unit_dir, type_ in units:
        rel = unit_dir.name
        shared = build_script_catalog(unit_dir)
        env_example_required = set()
        for fn in (".env.example", ".env.sample"):
            p = unit_dir / fn
            if p.is_file():
                env_example_required |= scan_envfile_example(p.read_text(errors="replace"))

        if args.verbose:
            print(f"\n=== {rel} (type={type_}, shared scripts with env={len(shared)}) ===")

        if type_ == "group":
            skill_dirs = list(inner_skill_dirs(unit_dir))
        else:
            skill_dirs = [unit_dir]

        if args.skill:
            skill_dirs = [d for d in skill_dirs if d.name == args.skill]

        for skill_dir in skill_dirs:
            total += 1
            is_ok, status = process_skill(
                skill_dir, shared, env_example_required, args.write, args.verbose
            )
            if is_ok:
                ok += 1
                if args.verbose:
                    print(f"  ✓ {skill_dir.relative_to(REPO_ROOT)} — {status}")
            else:
                drift += 1
                print(f"  ✗ {skill_dir.relative_to(REPO_ROOT)} — {status}")

    print(
        f"\n{total} skill(s) scanned · {ok} OK · {drift} drift"
        + (" · WROTE files" if args.write else "")
    )
    if args.check and drift:
        sys.exit(1)


if __name__ == "__main__":
    main()
