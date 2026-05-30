"""Shared helpers for the robomotion-gtm-skills test suite.

The suite runs under either stdlib `unittest` (zero dependencies) or `pytest` if it
happens to be installed — every test is a plain ``unittest.TestCase`` so both runners
discover them. No third-party imports here; the skill scripts are stdlib-only and the
harness keeps that property so it runs anywhere ``python3`` does.

Network tests are gated behind ``GTM_NET_TESTS=1`` (see ``net_gate``) so the default
run is fully offline and deterministic.
"""
import importlib.util
import os
import re
import shlex
import subprocess
import sys
import unittest

# group root = parent of this tests/ dir; skills live under <root>/skills/<slug>/
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SKILLS_DIR = os.path.join(ROOT, "skills")

_load_counter = 0


def script_path(skill, script):
    """Absolute path to skills/<skill>/scripts/<script>."""
    return os.path.join(SKILLS_DIR, skill, "scripts", script)


def load_script(skill, script):
    """Import a skill script as a uniquely-named module and return it.

    Many scripts share function names (``main``, ``normalize`` ...), so each import gets a
    unique module name to avoid collisions. The script's own directory is placed on
    ``sys.path`` during import so vendored sibling imports (``import apify_common`` /
    ``pain_filter`` / ``sigdb``) resolve exactly as they do when run as ``python3 script.py``.
    Importing is side-effect-free: every script guards its work under ``if __name__ ==
    '__main__'``.
    """
    global _load_counter
    path = script_path(skill, script)
    _load_counter += 1
    safe = re.sub(r"\W", "_", f"{skill}_{script}")
    modname = f"gtm_{safe}_{_load_counter}"
    spec = importlib.util.spec_from_file_location(modname, path)
    mod = importlib.util.module_from_spec(spec)
    sdir = os.path.dirname(path)
    sys.path.insert(0, sdir)
    sys.modules[modname] = mod
    try:
        spec.loader.exec_module(mod)
    finally:
        if sys.path and sys.path[0] == sdir:
            sys.path.pop(0)
    return mod


def run_script(skill, script, *args, env=None, stdin=None, timeout=60):
    """Run skills/<skill>/scripts/<script> as a subprocess and return the CompletedProcess.

    ``env`` keys are overlaid on the current environment (so PATH etc. survive). Used by
    end-to-end unit tests (argparse + I/O) and by the mocked/keyless suites.
    """
    full_env = dict(os.environ)
    if env:
        full_env.update(env)
    return subprocess.run(
        [sys.executable, script_path(skill, script), *args],
        capture_output=True, text=True, timeout=timeout, env=full_env, input=stdin,
    )


def iter_skills():
    """Yield (slug, abspath) for every skill directory, sorted."""
    for slug in sorted(os.listdir(SKILLS_DIR)):
        d = os.path.join(SKILLS_DIR, slug)
        if os.path.isdir(d):
            yield slug, d


def iter_scripts():
    """Yield (skill_slug, script_filename, abspath) for every *.py under skills/*/scripts/."""
    for slug, d in iter_skills():
        sdir = os.path.join(d, "scripts")
        if not os.path.isdir(sdir):
            continue
        for fn in sorted(os.listdir(sdir)):
            if fn.endswith(".py"):
                yield slug, fn, os.path.join(sdir, fn)


# ---- SKILL.md example-command parsing (used by the CLI-contract tests) -----------------

_FENCE = re.compile(r"```(?:bash|sh|console)?\n(.*?)```", re.S)
# a script invocation: python3 <pathtoken-ending-in-scripts/NAME.py> <args...>.
# The path token may be ${SKILL_DIR}/scripts/x.py (same skill) or a cross-skill
# reference like ${SKILL_DIR}/../other-skill/scripts/x.py or ../other/scripts/x.py.
_INVOKE = re.compile(r"python3?\s+(\S*scripts/[A-Za-z0-9_./${}~-]+\.py)(.*)")


def _join_continuations(block):
    """Join shell line-continuations (trailing backslash) into single logical lines."""
    lines, buf = [], ""
    for raw in block.splitlines():
        s = raw.rstrip()
        if s.endswith("\\"):
            buf += s[:-1] + " "
            continue
        buf += s
        lines.append(buf)
        buf = ""
    if buf:
        lines.append(buf)
    return lines


def _flags_in(argstr):
    """Return the set of long-option flags (``--foo``) used in an argument string.

    Strips ``--foo=bar`` to ``--foo`` and ignores values, quotes, and shell vars. Tokens
    that fail shell-lexing (rare, e.g. an unbalanced quote in a doc example) are skipped.
    """
    try:
        toks = shlex.split(argstr, comments=True)
    except ValueError:
        toks = argstr.split()
    flags = set()
    for t in toks:
        if t.startswith("--") and len(t) > 2:
            flags.add(t.split("=", 1)[0])
    return flags


def _resolve_script(token, skill_dir):
    """Resolve a SKILL.md script path token to an absolute path.

    ``${SKILL_DIR}`` (or ``$SKILL_DIR``) is the skill's own directory; cross-skill
    references via ``../other-skill/`` resolve against it too, since the agent runs
    examples from the skill dir.
    """
    t = token.replace("${SKILL_DIR}", skill_dir).replace("$SKILL_DIR", skill_dir)
    t = t.replace("${WORKSPACE}", skill_dir).replace("$WORKSPACE", skill_dir)
    if not os.path.isabs(t):
        t = os.path.join(skill_dir, t)
    return os.path.normpath(t)


def parse_skill_examples(skill_md_path):
    """Parse a SKILL.md and return {absolute_script_path: set(flags)} aggregated over all
    fenced example blocks. Cross-skill references resolve to the sibling skill's script."""
    skill_dir = os.path.dirname(os.path.abspath(skill_md_path))
    with open(skill_md_path, encoding="utf-8") as f:
        text = f.read()
    found = {}
    for block in _FENCE.findall(text):
        for line in _join_continuations(block):
            m = _INVOKE.search(line)
            if not m:
                continue
            path = _resolve_script(m.group(1), skill_dir)
            flags = _flags_in(m.group(2))
            found.setdefault(path, set()).update(flags)
    return found


_USAGE = re.compile(r"^usage:(.*?)(?:\n\n|\n(?=\w))", re.S | re.M)
_DECL_FLAG = re.compile(r"--[A-Za-z0-9][A-Za-z0-9-]*")


_SUBCMD = re.compile(r"\{([a-z0-9_][a-z0-9_,\-]*)\}")


def declared_flags(help_text):
    """Extract the set of long-option flags an argparse script declares.

    Parses the auto-generated ``usage:`` block (authoritative — every optional appears
    there, and it contains no prose), falling back to the whole help text if the usage
    block can't be isolated. ``--help`` itself is always included.
    """
    m = _USAGE.search(help_text)
    scope = m.group(1) if m else help_text
    flags = set(_DECL_FLAG.findall(scope))
    flags.add("--help")
    return flags


def _run_help(path, *subcmds):
    return subprocess.run(
        [sys.executable, path, *subcmds, "--help"],
        capture_output=True, text=True, timeout=30,
    )


def script_declared_flags(path):
    """All long-option flags a script accepts, recursing into argparse subcommands.

    Subparser scripts (e.g. ``paid_seo.py {keywords,domain,...}``) declare their real
    flags under each subcommand, not at the top level — so probe ``<script> <sub>
    --help`` for each subcommand listed in the top-level usage. Returns None if the
    top-level ``--help`` fails.
    """
    r = _run_help(path)
    if r.returncode != 0:
        return None
    flags = declared_flags(r.stdout)
    m = _USAGE.search(r.stdout)
    usage = m.group(1) if m else ""
    for grp in _SUBCMD.findall(usage):
        for cmd in (c.strip() for c in grp.split(",")):
            if not cmd:
                continue
            rs = _run_help(path, cmd)
            if rs.returncode == 0:
                flags |= declared_flags(rs.stdout)
    return flags


def is_cli_script(path):
    """True if a script is an argparse CLI (vs. a vendored import-only helper module like
    ``apify_common.py`` / ``sigdb.py``, which expose no command line)."""
    try:
        with open(path, encoding="utf-8") as f:
            src = f.read()
    except OSError:
        return False
    return "argparse" in src and "ArgumentParser" in src


# ---- network gating --------------------------------------------------------------------

NET_ENABLED = os.environ.get("GTM_NET_TESTS", "").strip() not in ("", "0", "false", "no")


def net_gate(test):
    """Decorator: skip a network-dependent test unless GTM_NET_TESTS is set."""
    return unittest.skipUnless(
        NET_ENABLED,
        "network test — set GTM_NET_TESTS=1 to run keyless-path integration tests",
    )(test)
