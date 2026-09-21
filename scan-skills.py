#!/usr/bin/env python3
"""Deterministic tripwires for skill content. No model, no network, no keys.

A skill is text an agent obeys and scripts an agent runs, next to a
customer's credentials. Every published scanner for this has been bypassed
in public tests, so this is NOT what makes a skill safe: a person reading
the diff is. What this does is make the cheap attacks expensive and put the
interesting lines in front of that person. A clean run is a tripwire that
did not fire.

    scan-skills.py --changed [BASE]   what a PR touches (default BASE origin/main)
    scan-skills.py --all              the whole repo
    scan-skills.py PATH [PATH ...]    these files or folders

BLOCK findings exit 1. WARN findings are printed for the reviewer and do not
fail the run. A finding a person has read and accepted goes in
``scan-accepted.yaml`` with the reason; it is matched by rule, path and the
exact text, so an accepted line that later changes is a finding again.
"""

from __future__ import annotations

import argparse
import hashlib
import os
import re
import subprocess
import sys
import unicodedata
from pathlib import Path

try:
    import yaml
except ImportError:
    sys.exit("PyYAML required: pip install pyyaml")

ROOT = Path(__file__).resolve().parent
ACCEPTED = ROOT / "scan-accepted.yaml"
SKIP_DIRS = {".git", "node_modules", "__pycache__"}

# Files a skill has no business carrying. Archives and Office files are
# containers a payload hides in; compiled code cannot be read in a diff.
OPAQUE_EXT = {
    ".pyc", ".pyo", ".so", ".dll", ".dylib", ".exe", ".bin", ".wasm", ".jar", ".class",
    ".zip", ".tar", ".gz", ".tgz", ".bz2", ".xz", ".7z", ".rar",
    ".docx", ".xlsx", ".pptx", ".doc", ".xls", ".ppt",
}
BINARY_OK_EXT = {".png", ".jpg", ".jpeg", ".gif", ".webp", ".ico", ".bmp", ".avif",
                 ".woff", ".woff2", ".ttf", ".otf", ".mp3", ".wav", ".mp4", ".webm", ".pdf"}
CODE_EXT = {".sh", ".bash", ".zsh", ".py", ".js", ".mjs", ".cjs", ".ts", ".rb", ".pl", ".ps1", ".php", ".go", ".rs"}

HIDDEN = {
    **{c: "bidi control" for c in range(0x202A, 0x202F)},
    **{c: "bidi isolate" for c in range(0x2066, 0x206A)},
    **{c: "invisible operator" for c in range(0x2060, 0x2065)},
    0x200B: "zero-width space", 0x200C: "zero-width non-joiner", 0x00AD: "soft hyphen",
    0x180E: "mongolian vowel separator", 0x115F: "hangul filler", 0x3164: "hangul filler",
}

# (rule, severity, where, regex, what it means)
#   where: "any" every text file, "code" scripts and fenced shell in markdown
RULES = [
    ("pipe-to-shell", "BLOCK", "any",
     r"(curl|wget|fetch|iwr|irm|Invoke-WebRequest)\b[^\n|;&]{0,300}\|\s*(sudo\s+)?(ba|z|da|k)?sh\b"
     r"|(curl|wget)\b[^\n|;&]{0,300}\|\s*(sudo\s+)?(python3?|node|perl|ruby)\b"
     r"|\b(ba|z)?sh\s+<\(\s*(curl|wget)\b"
     r"|\b(iex|Invoke-Expression)\b[^\n]{0,80}\b(irm|iwr|Invoke-WebRequest|DownloadString)\b",
     "downloads code and runs it in one step; nothing to review, nothing pinned"),
    ("decode-and-run", "BLOCK", "any",
     r"base64\s+(-d|-D|--decode)\b[^\n]{0,200}\|\s*(sudo\s+)?((ba|z)?sh|python3?|node)\b"
     r"|\beval\s+[\"'`]?\$\(\s*(echo|printf|curl|wget|base64)\b"
     r"|\bexec\s*\(\s*(base64\.b64decode|bytes\.fromhex|codecs\.decode|zlib\.decompress)"
     r"|\b(eval|Function)\s*\(\s*(atob|Buffer\.from)\s*\(",
     "runs text that was encoded so it could not be read"),
    ("drop-site", "BLOCK", "any",
     r"\b(webhook\.site|requestbin\.(com|net)|pipedream\.net|ngrok(-free)?\.(io|app|dev)|burpcollaborator\.net"
     r"|interact\.sh|oast\.(fun|pro|live|site|online|me)|transfer\.sh|paste\.ee|0x0\.st|termbin\.com)\b",
     "a throwaway endpoint used to receive stolen data"),
    ("credential-path", "BLOCK", "code",
     r"(~|\$HOME|\$\{HOME\}|/root|/home/[^/\s]+)/\.(ssh/|aws/|kube/|docker/config|netrc\b|npmrc\b|pypirc\b|git-credentials\b"
     r"|config/gcloud|azure/|gnupg/)"
     r"|/\.(hermes|clawdbot|openclaw|codex|claude)/(\.env|auth|credentials)\b"
     r"|\bid_(rsa|ed25519|ecdsa)\b|/etc/shadow\b|Login Data\b|\bsecurity\s+find-(generic|internet)-password\b",
     "reads where credentials live on the machine that runs it"),
    ("env-sweep", "BLOCK", "code",
     r"(^|[;&|(]\s*)(printenv|env)\s*(\||>)|\bos\.environ\b(?!\s*(\.get\s*\(|\[))[^\n]{0,60}\b(post|put|send|dumps|urlopen|request)"
     r"|JSON\.stringify\(\s*process\.env\s*\)",
     "collects the whole environment, which is where bound secrets are"),
    ("registry-override", "BLOCK", "any",
     r"--(extra-)?index-url\s+(?!https://(pypi\.org|download\.pytorch\.org)/)\S+|npm\s+config\s+set\s+registry\b"
     r"|--registry[= ]\s*(?!https://registry\.npmjs\.org)\S+|PIP_(EXTRA_)?INDEX_URL=",
     "installs packages from somewhere other than the official registry"),
    ("persistence", "BLOCK", "code",
     r"\bcrontab\s+-|/etc/cron\.|systemctl\s+(--user\s+)?enable\b|\.config/systemd/user|LaunchAgents/"
     r"|>>\s*~?/?\S*\.(bashrc|zshrc|profile|bash_profile)\b",
     "installs itself to keep running after the task ends"),
    ("remote-instructions", "WARN", "md",
     r"(fetch|load|read|download|retrieve|follow)\b[^\n]{0,80}\b(instructions|rules|guidelines|prompt|workflow)\b"
     r"[^\n]{0,80}https?://",
     "tells the agent to take instructions from a URL, which can change after review"),
    ("stealth-instruction", "WARN", "md",
     r"(do\s+not|don'?t|never)\s+(tell|inform|mention|reveal|notify|alert|show)\b[^\n]{0,40}\b(the\s+)?user\b"
     r"|without\s+(asking|telling|notifying|informing|confirming\s+with)\s+(the\s+)?user"
     r"|ignore\s+(all\s+|any\s+)?(previous|prior|above|earlier)\s+(instructions|rules|prompts)"
     r"|(disregard|bypass|override)\s+(the\s+|your\s+|any\s+)?(system\s+prompt|safety|guardrails|security\s+warnings?)",
     "text that steers the agent away from its user"),
    ("unpinned-install", "WARN", "any",
     r"\bnpm\s+(i|install)\s+(-g\s+|--global\s+)?[@\w/.-]+@latest\b|\bnpx\s+(-y\s+)?[@\w/.-]+@latest\b"
     r"|\bpip3?\s+install\s+(?!-r\b)(?!.*==)[A-Za-z][\w.-]*\s*$",
     "installs whatever is newest at run time, so the reviewed version is not the one that runs"),
]
COMPILED = [(r, sev, where, re.compile(rx, re.I | re.M), why) for r, sev, where, rx, why in RULES]

HTML_COMMENT = re.compile(r"<!--(.*?)-->", re.S)
IMPERATIVE = re.compile(r"\b(you must|always|never|ignore|instead|system:|assistant:|do not|run|execute|send|upload)\b", re.I)
FENCE = re.compile(r"```(?:bash|sh|shell|zsh|console|powershell|ps1|python|py|js|javascript|node)?\n(.*?)```", re.S | re.I)


class Finding:
    def __init__(self, sev, rule, path, line, text, why):
        self.sev, self.rule, self.path, self.line, self.why = sev, rule, path, line, why
        self.text = " ".join(text.split())[:200]

    @property
    def key(self):
        return hashlib.sha256(f"{self.rule}\0{self.path}\0{self.text}".encode()).hexdigest()[:16]


def line_of(data: str, pos: int) -> int:
    return data.count("\n", 0, pos) + 1


def scan_file(path: Path, rel: str) -> list[Finding]:
    out: list[Finding] = []
    ext = path.suffix.lower()
    if path.is_symlink():
        target = os.readlink(path)
        if target.startswith("/") or ".." in Path(os.path.normpath(Path(rel).parent / target)).parts:
            out.append(Finding("BLOCK", "symlink-escape", rel, 1, f"-> {target}",
                               "a link out of the repo reads whatever is there on the machine that runs the skill"))
        return out
    if ext in OPAQUE_EXT:
        out.append(Finding("BLOCK", "opaque-file", rel, 1, ext,
                           "an archive, Office file or compiled code cannot be reviewed in a diff"))
        return out
    raw = path.read_bytes()
    if b"\0" in raw[:8192]:
        if ext not in BINARY_OK_EXT:
            out.append(Finding("BLOCK", "opaque-file", rel, 1, f"binary content in a {ext or 'no-extension'} file",
                               "binary content outside the known media types"))
        return out
    data = raw.decode("utf-8", "replace")

    for i, ch in enumerate(data):
        cp = ord(ch)
        name = HIDDEN.get(cp) or ("tag character" if 0xE0000 <= cp <= 0xE007F else None)
        if cp == 0xFEFF and i > 0:
            name = "byte-order mark inside the text"
        if name:
            ln = line_of(data, i)
            out.append(Finding("BLOCK", "hidden-unicode", rel, ln, f"U+{cp:04X} {name}",
                               "invisible characters hide text from a reviewer that a model still reads"))
            break  # one is enough to send a person to the file
    if re.search(r"(?:\r?\n[ \t]*){200,}", data):
        m = re.search(r"(?:\r?\n[ \t]*){200,}", data)
        out.append(Finding("BLOCK", "padding", rel, line_of(data, m.start()), "200+ blank lines",
                           "pushes content below where a reviewer or a scanner stops reading"))
    longest = max((len(l) for l in data.split("\n")), default=0)
    if longest > 20000 and ext not in {".json", ".svg", ".csv", ".lock", ".map", ".html", ".css"} and not rel.endswith((".min.js", "lock.yaml")):
        out.append(Finding("WARN", "long-line", rel, 1, f"a line of {longest} characters",
                           "a very long line is not something a diff viewer shows in full"))

    is_md = ext in {".md", ".mdx", ".markdown", ".txt"} or path.name in {"SKILL.md"}
    is_code = ext in CODE_EXT or (raw[:2] == b"#!")
    code_text = data if is_code else "\n".join(FENCE.findall(data)) if is_md else ""
    for rule, sev, where, rx, why in COMPILED:
        hay = data if where == "any" or (where == "md" and is_md) else code_text if where == "code" else ""
        if not hay:
            continue
        seen = set()
        for m in rx.finditer(hay):
            text = hay[max(0, hay.rfind("\n", 0, m.start()) + 1): hay.find("\n", m.end()) if hay.find("\n", m.end()) != -1 else len(hay)]
            f = Finding(sev, rule, rel, line_of(data, data.find(text.strip()[:60])) if text.strip() else 1, text, why)
            if f.key not in seen:
                seen.add(f.key)
                out.append(f)
    if is_md:
        for m in HTML_COMMENT.finditer(data):
            body = m.group(1)
            if len(body) > 80 and IMPERATIVE.search(body):
                out.append(Finding("WARN", "hidden-comment", rel, line_of(data, m.start()), body,
                                   "an HTML comment is invisible when the markdown is rendered and still read by the model"))
    return out


def launcher_hooks(rel: str) -> Finding | None:
    name = os.path.basename(rel)
    if name in {"post-install.sh", "pre-run.sh", "env.required", "env.optional"}:
        return Finding("WARN", "launcher-hook", rel, 1, name,
                       "the launcher acts on this file: it runs at image build or start, or decides which secrets enter the sandbox")
    return None


def gather(args) -> list[Path]:
    if args.all:
        roots = [ROOT]
    elif args.changed is not None:
        base = args.changed or "origin/main"
        names = subprocess.run(["git", "diff", "--name-only", "--diff-filter=ACMRT", f"{base}...HEAD"],
                               cwd=ROOT, capture_output=True, text=True).stdout.split("\n")
        names += subprocess.run(["git", "status", "--porcelain", "--untracked-files=all"],
                                cwd=ROOT, capture_output=True, text=True).stdout.split("\n")
        names = [n[3:] if len(n) > 3 and n[2] == " " else n for n in names]
        names = [n.split(" -> ")[-1].strip('"') for n in names if n]
        return sorted({ROOT / n for n in names if (ROOT / n).is_file() or (ROOT / n).is_symlink()})
    else:
        roots = [Path(p).resolve() for p in args.paths]
    files = []
    for r in roots:
        if r.is_file() or r.is_symlink():
            files.append(r)
            continue
        for d, dirs, fs in os.walk(r):
            dirs[:] = [x for x in dirs if x not in SKIP_DIRS]
            files += [Path(d) / f for f in fs]
            files += [Path(d) / x for x in dirs if (Path(d) / x).is_symlink()]
    return sorted(files)


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("paths", nargs="*")
    ap.add_argument("--all", action="store_true")
    ap.add_argument("--changed", nargs="?", const="", default=None, metavar="BASE")
    ap.add_argument("--summary", action="store_true", help="counts per rule and group only")
    ap.add_argument("--markdown", action="store_true", help="a section for a PR body")
    args = ap.parse_args()
    if not (args.all or args.changed is not None or args.paths):
        ap.error("say what to scan: --changed, --all, or paths")

    accepted = {}
    if ACCEPTED.exists():
        for a in (yaml.safe_load(ACCEPTED.read_text()) or {}).get("accepted", []):
            accepted[a["key"]] = a
    own = {ROOT / "scan-skills.py", ACCEPTED}
    findings, waived = [], 0
    for f in gather(args):
        if f in own:
            continue
        rel = f.relative_to(ROOT).as_posix()
        found = scan_file(f, rel)
        if args.changed is not None and (h := launcher_hooks(rel)):
            found.append(h)
        for x in found:
            if x.key in accepted:
                waived += 1
            else:
                findings.append(x)

    blocks = [f for f in findings if f.sev == "BLOCK"]
    warns = [f for f in findings if f.sev == "WARN"]
    if args.summary:
        tally: dict[tuple, int] = {}
        for f in findings:
            k = (f.sev, f.rule, f.path.split("/")[0])
            tally[k] = tally.get(k, 0) + 1
        for (sev, rule, group), n in sorted(tally.items()):
            print(f"{sev:5} {rule:20} {group:26} {n}")
    elif args.markdown:
        print(f"### Scan: {len(blocks)} blocking, {len(warns)} to read, {waived} already accepted")
        for f in blocks + warns:
            print(f"- **{f.sev}** `{f.rule}` `{f.path}:{f.line}` {f.why}\n  `{f.text}`")
    else:
        for f in blocks + warns:
            print(f"{f.sev:5} {f.rule:20} {f.path}:{f.line}\n      {f.text}\n      why: {f.why}   [key {f.key}]")
    print(f"\n{len(blocks)} blocking, {len(warns)} warnings, {waived} accepted", file=sys.stderr)
    sys.exit(1 if blocks else 0)


if __name__ == "__main__":
    main()
