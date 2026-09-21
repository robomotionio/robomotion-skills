#!/usr/bin/env python3
"""Keep the vendored skill groups honest: every group is built from ONE
recorded upstream commit, by a script, and nothing else may change it.

Third-party skills are instructions and scripts that run with a customer's
credentials in reach, so an upstream change must never reach a customer
without a person having read its diff. That is why the content is copied
into this repo (a reviewer can read a copy; a submodule shows one changed
SHA) and why the copy is made by this script and not by hand (a hand-made
copy records nothing and hides edits; see `adopt` for what that cost us).

``upstreams.yaml`` is the manifest. A group is rebuilt as:

    upstream tree at `commit`, under `subdir`
      minus `exclude`            paths we do not want
      minus `local_paths`        paths WE own; upstream can never supply them
      plus  .robomotion/patches  our recorded edits to upstream files
    beside  .robomotion/         our metadata, never touched
    beside  `local_paths` files  ours, kept across a sync

Commands::

    sync-upstream.py status                 where every group stands
    sync-upstream.py add <group> <repo> ... a new third-party group
    sync-upstream.py adopt [group ...]      record what a hand-vendored group
                                            was really built from
    sync-upstream.py sync <group>           move a group to a newer commit
    sync-upstream.py verify [group ...]     CI: the tree is exactly what the
                                            manifest says, or exit 1
    sync-upstream.py pr-body <group> OLD NEW   the text a reviewer reads

`verify` is the gate that matters: it rebuilds each group from its pinned
commit and fails on any difference, so a hand edit to vendored content
cannot ride along in a PR unseen.
"""

from __future__ import annotations

import argparse
import datetime as dt
import functools
import hashlib
import os
import posixpath
import re
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

try:
    import yaml
except ImportError:
    sys.exit("PyYAML required: pip install pyyaml")

ROOT = Path(__file__).resolve().parent
MANIFEST = ROOT / "upstreams.yaml"
CACHE = Path(os.environ.get("SKILLS_UPSTREAM_CACHE", Path.home() / ".cache/robomotion-skills/upstreams"))
OURS = ".robomotion"
PATCH_DIR = "patches"
DEFAULT_MIN_AGE_DAYS = 7

# Launcher hooks. The launcher runs these when it finds them in a skill
# folder, so an upstream that learns our folder contract could add one and
# have it executed. They are ours by definition: never taken from upstream
# unless a group's `hooks_allow` names the exact path.
HOOK_NAMES = ("post-install.sh", "pre-run.sh", "env.required", "env.optional")


# ── small helpers ────────────────────────────────────────────────────


def sh(*args: str, cwd: Path | None = None, check: bool = True, env: dict | None = None) -> str:
    p = subprocess.run(args, cwd=cwd, capture_output=True, text=True, env=env)
    if check and p.returncode != 0:
        raise RuntimeError(f"{' '.join(args)[:300]}\n{p.stderr.strip()[-2000:]}")
    return p.stdout


@functools.lru_cache(maxsize=None)
def glob_re(pattern: str) -> re.Pattern:
    """`**` crosses directories, `*` does not. A pattern with no wildcard
    names a path and everything under it."""
    pattern = pattern.strip("/")
    out, i = "", 0
    while i < len(pattern):
        if pattern.startswith("**/", i):
            out, i = out + "(?:.*/)?", i + 3
        elif pattern.startswith("**", i):
            out, i = out + ".*", i + 2
        elif pattern[i] == "*":
            out, i = out + "[^/]*", i + 1
        elif pattern[i] == "?":
            out, i = out + "[^/]", i + 1
        else:
            out, i = out + re.escape(pattern[i]), i + 1
    return re.compile(f"^{out}(?:/.*)?$")


def matches(path: str, patterns: list[str]) -> bool:
    return any(glob_re(p).match(path) for p in patterns)


def blob_sha(data: bytes) -> str:
    return hashlib.sha1(b"blob %d\0" % len(data) + data).hexdigest()


def load_manifest() -> dict:
    if not MANIFEST.exists():
        return {"schema_version": 1, "upstreams": []}
    return yaml.safe_load(MANIFEST.read_text()) or {"schema_version": 1, "upstreams": []}


def save_manifest(m: dict):
    m["upstreams"].sort(key=lambda u: u["group"])
    header = (
        "# One entry per vendored group. Built and checked by sync-upstream.py;\n"
        "# `commit` is the only field an update changes. Read the script's docstring.\n"
    )
    MANIFEST.write_text(header + yaml.safe_dump(m, sort_keys=False, width=100))


def entry_for(m: dict, group: str) -> dict:
    for u in m["upstreams"]:
        if u["group"] == group:
            return u
    sys.exit(f"{group}: not in {MANIFEST.name}")


def local_patterns(u: dict) -> list[str]:
    hooks = [f"**/{n}" for n in HOOK_NAMES]
    return [OURS] + hooks + list(u.get("local_paths") or [])


# ── upstream access ──────────────────────────────────────────────────


def bare_repo(u: dict) -> Path:
    owner, repo = u["repo"].rstrip("/").removesuffix(".git").split("/")[-2:]
    path = CACHE / f"{owner}__{repo}.git"
    if not path.exists():
        CACHE.mkdir(parents=True, exist_ok=True)
        sh("git", "clone", "-q", "--bare", "--filter=blob:none", u["repo"], str(path))
    return path


def fetch(u: dict) -> tuple[Path, str]:
    """Returns (bare repo, head of the tracked branch)."""
    bare = bare_repo(u)
    sh("git", "fetch", "-q", "--filter=blob:none", "origin", f"+refs/heads/{u['track']}:refs/heads/{u['track']}", cwd=bare)
    return bare, sh("git", "rev-parse", f"refs/heads/{u['track']}", cwd=bare).strip()


def require_on_track(bare: Path, u: dict, sha: str):
    """GitHub serves any commit of a fork network by SHA, so a SHA alone does
    not prove the commit belongs to the project. It must be an ancestor of the
    branch we track."""
    p = subprocess.run(
        ["git", "merge-base", "--is-ancestor", sha, f"refs/heads/{u['track']}"], cwd=bare
    )
    if p.returncode != 0:
        sys.exit(f"{u['group']}: {sha[:12]} is not on {u['repo']}@{u['track']}; refusing it")


def read_blobs(bare: Path, blobs: set[str]):
    """The cache is a blobless clone. Left to itself git fetches a missing
    blob when it is first read, one round trip each; ask for all of them at
    once instead."""
    have = subprocess.run(["git", "cat-file", "--batch-check", "--batch-all-objects"], cwd=bare,
                          capture_output=True, text=True).stdout
    present = {line.split()[0] for line in have.splitlines()}
    missing = sorted(blobs - present)
    if missing:
        p = subprocess.run(
            ["git", "-c", "fetch.negotiationAlgorithm=noop", "fetch", "-q", "origin", "--no-tags",
             "--no-write-fetch-head", "--recurse-submodules=no", "--filter=blob:none", "--stdin"],
            cwd=bare, input="\n".join(missing) + "\n", capture_output=True, text=True)
        if p.returncode != 0:
            raise RuntimeError(f"fetching {len(missing)} blobs failed\n{p.stderr.strip()[-1500:]}")


def upstream_tree(bare: Path, sha: str, subdir: str) -> dict[str, tuple[str, str]]:
    """path (relative to subdir) -> (mode, blob sha)."""
    pre = subdir.strip("/") + "/" if subdir.strip("/") else ""
    tree = {}
    for rec in sh("git", "ls-tree", "-r", "-z", sha, cwd=bare).split("\0"):
        if not rec:
            continue
        meta, path = rec.split("\t", 1)
        mode, _typ, blob = meta.split()
        if path.startswith(pre):
            tree[path[len(pre):]] = (mode, blob)
    return tree


def wanted(u: dict, tree: dict[str, tuple[str, str]]) -> tuple[dict[str, tuple[str, str]], list[str]]:
    """The upstream paths this group takes, and notes on what was refused."""
    include = u.get("include") or []
    exclude = u.get("exclude") or []
    allow = u.get("hooks_allow") or []
    ours = local_patterns(u)
    keep, notes = {}, []
    for path, (mode, blob) in tree.items():
        if include and not matches(path, include):
            continue
        if matches(path, exclude):
            continue
        if mode == "160000":
            notes.append(f"skipped submodule {path}")
            continue
        if matches(path, ours) and path not in allow:
            if os.path.basename(path) in HOOK_NAMES:
                notes.append(f"refused upstream launcher hook {path} (name it in hooks_allow to take it)")
            continue
        keep[path] = (mode, blob)
    # `into` puts the upstream tree under a folder of the group. The index
    # looks for skills under skills/, and some projects keep them at the root.
    into = (u.get("into") or "").strip("/")
    if into:
        keep = {f"{into}/{path}": v for path, v in keep.items()}
    return keep, notes


def materialize(u: dict, sha: str, dest: Path) -> list[str]:
    """Write the group as the manifest describes it into `dest` (upstream-owned
    paths only). Returns notes for the reviewer."""
    bare = bare_repo(u)
    require_on_track(bare, u, sha)
    keep, notes = wanted(u, upstream_tree(bare, sha, u.get("subdir", "")))
    pre = u.get("subdir", "").strip("/")
    read_blobs(bare, {blob for _mode, blob in keep.values()})
    cat = subprocess.Popen(["git", "cat-file", "--batch"], cwd=bare, stdin=subprocess.PIPE, stdout=subprocess.PIPE)
    try:
        for path, (mode, blob) in keep.items():
            cat.stdin.write(f"{blob}\n".encode())
            cat.stdin.flush()
            _oid, _typ, size = cat.stdout.readline().split()
            data = cat.stdout.read(int(size))
            cat.stdout.read(1)
            out = dest / path
            out.parent.mkdir(parents=True, exist_ok=True)
            if mode == "120000":
                # A link is kept only when it points at something inside the
                # group. An absolute target, or one that climbs out, would
                # read whatever sits there on the machine that runs the skill.
                target = data.decode("utf-8", "replace")
                inside = posixpath.normpath(posixpath.join(posixpath.dirname(path), target))
                if target.startswith("/") or inside == ".." or inside.startswith("../"):
                    notes.append(f"refused symlink {path} -> {target}")
                    continue
                os.symlink(target, out)
                continue
            out.write_bytes(data)
            out.chmod(0o755 if mode == "100755" else 0o644)
    finally:
        cat.stdin.close()
        cat.wait()
    patches = sorted((ROOT / u["group"] / OURS / PATCH_DIR).glob("*.patch"))
    for patch in patches:
        p = subprocess.run(
            ["git", "apply", "--whitespace=nowarn", str(patch)], cwd=dest, capture_output=True, text=True
        )
        if p.returncode != 0:
            raise RuntimeError(
                f"{u['group']}: {patch.name} no longer applies at {sha[:12]}. Upstream changed a file "
                f"we edit; refresh the patch by hand.\n{p.stderr.strip()}"
            )
    return notes


def owned_files(u: dict) -> dict[str, Path]:
    """Upstream-owned files of the group as they are on disk now."""
    base = ROOT / u["group"]
    ours = local_patterns(u)
    out = {}
    for d, dirs, files in os.walk(base):
        links = [x for x in dirs if (Path(d) / x).is_symlink()]
        for f in files + links:
            p = Path(d) / f
            rel = p.relative_to(base).as_posix()
            if matches(rel, ours) and rel not in (u.get("hooks_allow") or []):
                continue
            out[rel] = p
    return out


def entry(p: Path) -> tuple:
    """What a path IS, for comparing two trees: a link and its target, or a
    file, its bytes and whether it can be run."""
    if p.is_symlink():
        return ("link", os.readlink(p))
    return ("file", p.read_bytes(), os.access(p, os.X_OK))


def compare(u: dict, built: Path) -> list[str]:
    disk = owned_files(u)
    fresh = {p.relative_to(built).as_posix(): p for p in built.rglob("*") if p.is_symlink() or p.is_file()}
    diffs = []
    for rel in sorted(set(disk) | set(fresh)):
        if rel not in fresh:
            diffs.append(f"  only in the repo (not from upstream, not a local path): {rel}")
        elif rel not in disk:
            diffs.append(f"  missing from the repo: {rel}")
        elif entry(disk[rel])[:2] != entry(fresh[rel])[:2]:
            diffs.append(f"  content differs from upstream + patches: {rel}")
        elif entry(disk[rel]) != entry(fresh[rel]):
            diffs.append(f"  executable bit differs: {rel}")
    return diffs


def license_sha(bare: Path, u: dict, sha: str) -> str:
    pre = u.get("subdir", "").strip("/")
    name = u.get("license_file") or "LICENSE"
    for cand in [name] + ([f"{pre}/{name}"] if pre else []):
        p = subprocess.run(["git", "cat-file", "blob", f"{sha}:{cand}"], cwd=bare, capture_output=True)
        if p.returncode == 0:
            return hashlib.sha256(p.stdout).hexdigest()
    return ""


# ── commands ─────────────────────────────────────────────────────────


def cmd_status(args):
    m = load_manifest()
    print(f"{'group':26} {'mode':8} {'pinned':12} {'head':12} behind  head date")
    for u in m["upstreams"]:
        bare, head = fetch(u)
        pin = u.get("commit") or ""
        behind = sh("git", "rev-list", "--count", f"{pin}..{head}", cwd=bare).strip() if pin else "?"
        date = sh("git", "log", "-1", "--format=%cs", head, cwd=bare).strip()
        print(f"{u['group']:26} {u.get('mode', 'mirror'):8} {pin[:12]:12} {head[:12]:12} {behind:>6}  {date}")


def best_match(bare: Path, u: dict, disk: dict[str, str], before: str) -> tuple[str, int]:
    """The commit whose tree holds the most of our files, byte for byte, at
    the same path. Counting our blobs anywhere in a commit is cheap and can
    only overstate that, so it orders the candidates and says when to stop."""
    shas = sh("git", "log", "--format=%H", f"--before={before}", "-n", "400", f"refs/heads/{u['track']}", cwd=bare).split()
    want = set(disk.values())
    bound = []
    for age, sha in enumerate(shas):
        blobs = {rec.split("\t", 1)[0].split()[2]
                 for rec in sh("git", "ls-tree", "-r", "-z", sha, cwd=bare).split("\0") if rec}
        bound.append((len(want & blobs), -age, sha))
    best, score = "", -1
    for upper, _age, sha in sorted(bound, reverse=True):
        if upper <= score:
            break
        tree = upstream_tree(bare, sha, u.get("subdir", ""))
        exact = sum(1 for path, h in disk.items() if tree.get(path, ("", ""))[1] == h)
        if exact > score:
            best, score = sha, exact
    return best, score


def cmd_adopt(args):
    """A group copied in by hand records nothing. Find the upstream commit it
    matches best, pin it, and turn every difference into something explicit:
    an edit becomes a patch, a pruned path becomes an `exclude`. Files of ours
    (hooks, .robomotion) already stay out of the comparison."""
    m = load_manifest()
    groups = args.groups or [
        g.name for g in sorted(ROOT.iterdir()) if (g / OURS / "skill.yaml").exists()
    ]
    for group in groups:
        meta = yaml.safe_load((ROOT / group / OURS / "skill.yaml").read_text())
        url = meta.get("source_url", "")
        if "robomotionio/" in url:
            print(f"{group}: first-party, nothing to adopt")
            continue
        u = next((x for x in m["upstreams"] if x["group"] == group), None)
        if u is None:
            u = {"group": group, "repo": url, "track": "", "commit": "", "subdir": "", "mode": "mirror",
                 "license": meta.get("license", ""), "license_file": "LICENSE", "license_sha256": "",
                 "exclude": [], "local_paths": []}
            m["upstreams"].append(u)
        bare = bare_repo(u)
        if not u["track"]:
            u["track"] = sh("git", "symbolic-ref", "--short", "HEAD", cwd=bare).strip()
        fetch(u)
        disk = {rel: blob_sha(os.readlink(p).encode() if p.is_symlink() else p.read_bytes())
                for rel, p in owned_files(u).items()}
        vendored = sh("git", "log", "--diff-filter=A", "--format=%cs", "--reverse", "--", group, cwd=ROOT).split()
        before = (dt.date.fromisoformat(vendored[0]) + dt.timedelta(days=10)).isoformat() if vendored else "now"
        sha, score = best_match(bare, u, disk, before)
        tree = upstream_tree(bare, sha, u.get("subdir", ""))
        modified = sorted(p for p, h in disk.items() if p in tree and tree[p][1] != h)
        local_only = sorted(p for p in disk if p not in tree)
        up_only = sorted(p for p in tree if p not in disk and tree[p][0] != "160000"
                         and not matches(p, local_patterns(u)))
        u["commit"] = sha
        u["license_sha256"] = license_sha(bare, u, sha)
        # Pruned paths, collapsed to the highest directory that is wholly
        # absent. A group that keeps a small corner of a large upstream is
        # better said the other way round, as an `include`.
        def pruned(paths):
            out = set()
            for p in paths:
                parts = p.split("/")
                for i in range(1, len(parts) + 1):
                    prefix = "/".join(parts[:i])
                    if not any(d == prefix or d.startswith(prefix + "/") for d in disk):
                        out.add(prefix)
                        break
            return out

        excl = pruned(up_only)
        if len(excl) > 12:
            u["include"] = sorted({d.split("/")[0] for d in disk})
            excl = pruned(p for p in up_only if matches(p, u["include"]))
        u["exclude"] = sorted(set(u.get("exclude") or []) | excl)
        print(f"{group}: {sha[:12]} matches {score}/{len(disk)} files; "
              f"{len(modified)} edited, {len(local_only)} local-only, {len(excl)} pruned paths")
        for p in local_only[:10]:
            print(f"    local-only (add to local_paths, or delete): {p}")
        pdir = ROOT / group / OURS / PATCH_DIR
        if len(local_only) > len(disk) // 4:
            u["mode"] = "ported"
            print("    too far from upstream to be a mirror: marked `ported` (tracked, never auto-synced)")
        elif modified and list(pdir.glob("*.patch")):
            print("    patches already exist; not regenerating")
        elif modified:
            with tempfile.TemporaryDirectory() as tmp:
                materialize(u, sha, Path(tmp) / "a")
                out = ""
                for p in modified:
                    (Path(tmp) / "b" / p).parent.mkdir(parents=True, exist_ok=True)
                    shutil.copy2(ROOT / group / p, Path(tmp) / "b" / p)
                    # Empty prefixes: the directories are already named a/ and
                    # b/, and a reviewer's own diff.* settings must not leak in.
                    out += subprocess.run(
                        ["git", "-c", "core.quotePath=false", "diff", "--no-index", "--binary",
                         "--src-prefix=", "--dst-prefix=", f"a/{p}", f"b/{p}"],
                        cwd=tmp, capture_output=True, text=True).stdout
                pdir.mkdir(parents=True, exist_ok=True)
                (pdir / "0001-local-edits.patch").write_text(out)
                print(f"    wrote {OURS}/{PATCH_DIR}/0001-local-edits.patch ({len(modified)} files)")
    save_manifest(m)


def cmd_add(args):
    """A new third-party group: write our metadata, pin it, build it. The
    same path every later update takes, so a group is never born by hand."""
    m = load_manifest()
    if any(u["group"] == args.group for u in m["upstreams"]) or (ROOT / args.group).exists():
        sys.exit(f"{args.group} already exists")
    u = {"group": args.group, "repo": args.repo.rstrip("/"), "track": "", "commit": "", "subdir": "",
         "mode": "mirror", "license": args.license, "license_file": "LICENSE", "license_sha256": "",
         "include": args.include or [], "exclude": args.exclude or [], "local_paths": []}
    u["subdir"], u["into"], u["license_file"] = args.subdir or "", args.into or "", args.license_file
    bare = bare_repo(u)
    u["track"] = sh("git", "symbolic-ref", "--short", "HEAD", cwd=bare).strip()
    fetch(u)
    target = pick_target(bare, u, args.min_age_days)
    ours = ROOT / args.group / OURS
    ours.mkdir(parents=True)
    (ours / "skill.yaml").write_text(yaml.safe_dump({
        "schema_version": 1, "name": args.group, "title": args.title, "type": "group", "version": "1.0.0",
        "author": args.author, "source_url": u["repo"], "license": args.license,
        "summary": args.summary, "category": args.category, "tags": args.tags or [],
    }, sort_keys=False, width=200))
    lic = subprocess.run(["git", "cat-file", "blob", f"{target}:{args.license_file}"], cwd=bare, capture_output=True).stdout
    if not lic:
        sys.exit(f"{args.group}: upstream has no LICENSE file; a group without one cannot be redistributed")
    (ours / "LICENSE").write_bytes(lic)
    (ours / "CHANGELOG.md").write_text(f"# {args.title}\n\nVendored by sync-upstream.py; upstream history is the changelog.\n")
    notes = materialize(u, target, ROOT / args.group)
    u["commit"], u["license_sha256"] = target, license_sha(bare, u, target)
    m["upstreams"].append(u)
    save_manifest(m)
    print(f"{args.group}: added at {target[:12]}")
    for n in notes:
        print(f"  note: {n}")


def pick_target(bare: Path, u: dict, min_age: int) -> str:
    before = (dt.datetime.now(dt.timezone.utc) - dt.timedelta(days=min_age)).isoformat()
    out = sh("git", "log", "-1", "--format=%H", f"--before={before}", f"refs/heads/{u['track']}", cwd=bare).strip()
    return out


def cmd_sync(args):
    m = load_manifest()
    u = entry_for(m, args.group)
    if u.get("mode", "mirror") != "mirror":
        sys.exit(f"{args.group} is `{u['mode']}`: it is not rebuilt from upstream; port changes by hand")
    bare, _head = fetch(u)
    target = args.to or pick_target(bare, u, args.min_age_days)
    if not target:
        sys.exit(f"{args.group}: no commit on {u['track']} is older than {args.min_age_days} days")
    target = sh("git", "rev-parse", target, cwd=bare).strip()
    # Same commit is still a rebuild: the manifest (include, exclude, patches)
    # may have changed, and the tree must follow it.
    new_license = license_sha(bare, u, target)
    if u.get("license_sha256") and new_license != u["license_sha256"] and not args.accept_license:
        sys.exit(f"{args.group}: the upstream licence file changed. Read it, then re-run with --accept-license")
    with tempfile.TemporaryDirectory() as tmp:
        notes = materialize(u, target, Path(tmp))
        for rel, p in owned_files(u).items():
            p.unlink()
        for p in sorted(Path(tmp).rglob("*")):
            if p.is_symlink() or p.is_file():
                out = ROOT / u["group"] / p.relative_to(tmp)
                out.parent.mkdir(parents=True, exist_ok=True)
                shutil.copy2(p, out, follow_symlinks=False)
    for d, _dirs, _files in os.walk(ROOT / u["group"], topdown=False):
        if OURS not in Path(d).parts and not os.listdir(d):
            os.rmdir(d)
    old = u.get("commit", "")
    u["commit"], u["license_sha256"] = target, new_license
    save_manifest(m)
    print(f"{args.group}: rebuilt at {target[:12]}" if old == target else f"{args.group}: {old[:12]} -> {target[:12]}")
    for n in notes:
        print(f"  note: {n}")
    print("now: python3 build-index.py && python3 scan-skills.py --changed")


def cmd_verify(args):
    m = load_manifest()
    todo = [entry_for(m, g) for g in args.groups] if args.groups else m["upstreams"]
    listed = {u["group"] for u in m["upstreams"]}
    failed = False
    for g in sorted(ROOT.iterdir()):
        y = g / OURS / "skill.yaml"
        if y.exists() and g.name not in listed and "robomotionio/" not in (yaml.safe_load(y.read_text()).get("source_url") or ""):
            print(f"FAIL {g.name}: third-party group with no entry in {MANIFEST.name}")
            failed = True
    for u in todo:
        if u.get("mode", "mirror") != "mirror":
            print(f"skip {u['group']} ({u['mode']})")
            continue
        fetch(u)
        with tempfile.TemporaryDirectory() as tmp:
            materialize(u, u["commit"], Path(tmp))
            diffs = compare(u, Path(tmp))
        if diffs:
            failed = True
            print(f"FAIL {u['group']}: not what {u['commit'][:12]} + patches builds")
            print("\n".join(diffs[:40]))
            if len(diffs) > 40:
                print(f"  ... and {len(diffs) - 40} more")
        else:
            print(f"ok   {u['group']} = {u['repo'].split('github.com/')[-1]}@{u['commit'][:12]}")
    sys.exit(1 if failed else 0)


DOMAIN_RE = re.compile(r"https?://([A-Za-z0-9.-]+\.[A-Za-z]{2,})")


def cmd_pr_body(args):
    m = load_manifest()
    u = entry_for(m, args.group)
    bare, _ = fetch(u)
    old, new = args.old, args.new
    slug = u["repo"].split("github.com/")[-1]
    pre = u.get("subdir", "").strip("/")
    log = sh("git", "log", "--format=- `%h` %cs %an: %s", f"{old}..{new}", "--", pre or ".", cwd=bare).strip()
    a, _ = wanted(u, upstream_tree(bare, old, pre))
    b, notes = wanted(u, upstream_tree(bare, new, pre))
    added = sorted(set(b) - set(a))
    removed = sorted(set(a) - set(b))
    changed = sorted(p for p in set(a) & set(b) if a[p] != b[p])
    risky = [p for p in added + changed if b[p][0] == "100755" or re.search(r"\.(sh|py|js|mjs|ts|rb|ps1)$", p)]

    def domains(tree, paths):
        found = set()
        for p in paths:
            blob = subprocess.run(["git", "cat-file", "blob", tree[p][1]], cwd=bare, capture_output=True).stdout
            found |= set(DOMAIN_RE.findall(blob.decode("utf-8", "ignore")))
        return found

    new_domains = sorted(domains(b, added + changed) - domains(a, list(a)))
    lines = [
        f"## {u['group']}: {slug} `{old[:12]}` -> `{new[:12]}`",
        "",
        f"Upstream diff: https://github.com/{slug}/compare/{old}...{new}",
        "",
        f"**{len(changed)} changed, {len(added)} added, {len(removed)} removed** (after include/exclude).",
        "",
        "Read every changed line. A clean scan is a tripwire that did not fire, not an approval.",
        "",
        "### Code that can run" if risky else "### Code that can run\nnone changed",
        *[f"- `{p}`" for p in risky],
        "",
        "### Hosts not seen in this group before" if new_domains else "### Hosts not seen in this group before\nnone",
        *[f"- `{d}`" for d in new_domains],
        "",
        "### Refused" if notes else "",
        *[f"- {n}" for n in notes],
        "",
        "### Upstream commits",
        log or "(none touching the vendored paths)",
    ]
    print("\n".join(lines))


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="cmd", required=True)
    sub.add_parser("status").set_defaults(fn=cmd_status)
    a = sub.add_parser("adopt")
    a.add_argument("groups", nargs="*")
    a.set_defaults(fn=cmd_adopt)
    n = sub.add_parser("add")
    n.add_argument("group")
    n.add_argument("repo")
    for flag in ("--title", "--author", "--license", "--category", "--summary"):
        n.add_argument(flag, required=True)
    n.add_argument("--tags", nargs="*")
    n.add_argument("--include", nargs="*")
    n.add_argument("--exclude", nargs="*")
    n.add_argument("--subdir", help="upstream folder that becomes the group root")
    n.add_argument("--into", help="folder of the group the upstream tree lands in (e.g. skills)")
    n.add_argument("--license-file", default="LICENSE", help="path in the upstream repo")
    n.add_argument("--min-age-days", type=int, default=DEFAULT_MIN_AGE_DAYS)
    n.set_defaults(fn=cmd_add)
    s = sub.add_parser("sync")
    s.add_argument("group")
    s.add_argument("--to", help="upstream commit (default: newest older than --min-age-days)")
    s.add_argument("--min-age-days", type=int, default=DEFAULT_MIN_AGE_DAYS,
                   help="let a commit age before taking it; a poisoned release is usually caught within days")
    s.add_argument("--accept-license", action="store_true")
    s.set_defaults(fn=cmd_sync)
    v = sub.add_parser("verify")
    v.add_argument("groups", nargs="*")
    v.set_defaults(fn=cmd_verify)
    p = sub.add_parser("pr-body")
    p.add_argument("group")
    p.add_argument("old")
    p.add_argument("new")
    p.set_defaults(fn=cmd_pr_body)
    args = ap.parse_args()
    args.fn(args)


if __name__ == "__main__":
    main()
