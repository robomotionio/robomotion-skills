#!/usr/bin/env python3
"""minisign wrapper for skills-index.json.

Signing requires the `minisign` binary on PATH. Verification is
implemented in pure Python in scripts/verify_index.py so robots
don't need the minisign binary installed — they only need the
public key bundled with the hermes-agent package.

Usage:
    python3 scripts/sign_index.py sign <index.json> <private.key>
    python3 scripts/sign_index.py verify <index.json> <public.pub>
    python3 scripts/sign_index.py keygen <out.pub> <out.key>

Environment:
    MINISIGN_PASSWORD — used non-interactively when signing in CI.
"""

import argparse
import os
import shutil
import subprocess
import sys
from pathlib import Path


def _require_minisign():
    if shutil.which("minisign") is None:
        sys.stderr.write(
            "minisign binary not found on PATH. "
            "Install it with `apt-get install minisign` (Ubuntu/Debian), "
            "`brew install minisign` (macOS), or download from "
            "https://jedisct1.github.io/minisign/\n"
        )
        sys.exit(2)


def cmd_sign(index_path: str, key_path: str) -> int:
    _require_minisign()
    out_sig = index_path + ".minisig"
    pw = os.environ.get("MINISIGN_PASSWORD", "")

    cmd = [
        "minisign", "-S",
        "-s", key_path,
        "-m", index_path,
        "-x", out_sig,
        "-t", "robomotion-skills index signature",
    ]
    proc = subprocess.run(cmd, input=pw + "\n", text=True, capture_output=True)
    if proc.returncode != 0:
        sys.stderr.write(proc.stderr)
        return proc.returncode
    print(f"signed -> {out_sig}")
    return 0


def cmd_verify(index_path: str, pub_path: str) -> int:
    # Try the binary path first if available, else fall back to pure Python
    if shutil.which("minisign"):
        sig_path = index_path + ".minisig"
        if not os.path.exists(sig_path):
            sys.stderr.write(f"signature not found: {sig_path}\n")
            return 1
        proc = subprocess.run(
            ["minisign", "-V", "-p", pub_path, "-m", index_path, "-x", sig_path],
            capture_output=True, text=True,
        )
        if proc.returncode != 0:
            sys.stderr.write(proc.stderr)
            return proc.returncode
        print(proc.stdout.strip())
        return 0

    # Pure-Python fallback (uses verify_index.py)
    here = Path(__file__).resolve().parent
    sys.path.insert(0, str(here))
    from verify_index import verify_minisign  # type: ignore
    ok, msg = verify_minisign(index_path, pub_path)
    print(msg)
    return 0 if ok else 1


def cmd_keygen(pub_path: str, key_path: str) -> int:
    _require_minisign()
    pw = os.environ.get("MINISIGN_PASSWORD", "")
    cmd = ["minisign", "-G", "-p", pub_path, "-s", key_path]
    proc = subprocess.run(cmd, input=pw + "\n" + pw + "\n", text=True,
                          capture_output=True)
    if proc.returncode != 0:
        sys.stderr.write(proc.stderr)
        return proc.returncode
    print(f"keypair generated -> {pub_path} + {key_path}")
    return 0


def main():
    ap = argparse.ArgumentParser()
    sub = ap.add_subparsers(dest="cmd", required=True)
    sp_sign = sub.add_parser("sign")
    sp_sign.add_argument("index")
    sp_sign.add_argument("key")
    sp_ver = sub.add_parser("verify")
    sp_ver.add_argument("index")
    sp_ver.add_argument("pub")
    sp_kg = sub.add_parser("keygen")
    sp_kg.add_argument("pub")
    sp_kg.add_argument("key")
    args = ap.parse_args()

    if args.cmd == "sign":
        return cmd_sign(args.index, args.key)
    if args.cmd == "verify":
        return cmd_verify(args.index, args.pub)
    if args.cmd == "keygen":
        return cmd_keygen(args.pub, args.key)
    return 2


if __name__ == "__main__":
    sys.exit(main())
