#!/usr/bin/env python3
"""Pure-Python minisign verifier.

Used by both scripts/sign_index.py (when the minisign binary isn't
installed on the host) and by the hermes-agent install_skill node on
robot runtimes.

Format reference: https://jedisct1.github.io/minisign/

Public key file:
    line 1: untrusted comment
    line 2: base64 of:
        [0:2]   sig_alg "Ed"
        [2:10]  key_id
        [10:42] Ed25519 pubkey

Signature file (.minisig):
    line 1: untrusted comment
    line 2: base64 of:
        [0:2]   sig_alg "Ed" (legacy) or "ED" (prehashed BLAKE2b-512)
        [2:10]  key_id
        [10:74] Ed25519 signature
    line 3: trusted comment line: "trusted comment: ..."
    line 4: base64 of Ed25519 signature over (sig || trusted_comment)

We require either Ed (sign over the file directly, recommended for
small files like skills-index.json) or ED (sign over BLAKE2b-512 of
the file).
"""

import base64
import hashlib
import sys
from pathlib import Path


def _import_ed25519():
    try:
        from cryptography.hazmat.primitives.asymmetric.ed25519 import (
            Ed25519PublicKey,
        )
        return Ed25519PublicKey
    except ImportError:
        pass
    try:
        # PyNaCl fallback
        from nacl.signing import VerifyKey
        return VerifyKey
    except ImportError:
        raise ImportError(
            "Ed25519 verification requires `cryptography` or `pynacl`. "
            "Install one of them: `pip install cryptography`."
        )


def _verify_signature(pubkey_bytes: bytes, signed: bytes, sig: bytes) -> bool:
    Ed25519PublicKey = _import_ed25519()
    try:
        # cryptography path
        from cryptography.hazmat.primitives.asymmetric.ed25519 import (
            Ed25519PublicKey as Cryp,
        )
        if Ed25519PublicKey is Cryp:
            key = Cryp.from_public_bytes(pubkey_bytes)
            try:
                key.verify(sig, signed)
                return True
            except Exception:
                return False
    except ImportError:
        pass

    # pynacl path
    from nacl.signing import VerifyKey
    from nacl.exceptions import BadSignatureError
    try:
        VerifyKey(pubkey_bytes).verify(signed, sig)
        return True
    except BadSignatureError:
        return False
    except Exception:
        return False


def _decode_minisign_pub(pub_path: str) -> tuple[bytes, bytes]:
    """Return (key_id, pubkey_bytes)."""
    with open(pub_path) as f:
        lines = f.read().strip().splitlines()
    payload = base64.b64decode(lines[1])
    if payload[:2] != b"Ed":
        raise ValueError(f"unsupported pubkey alg: {payload[:2]!r}")
    return payload[2:10], payload[10:42]


def _decode_minisign_sig(sig_path: str) -> tuple[bytes, bytes, bytes, str, bytes]:
    """Return (sig_alg, key_id, signature, trusted_comment, global_sig)."""
    with open(sig_path) as f:
        lines = f.read().strip().splitlines()
    payload = base64.b64decode(lines[1])
    sig_alg = payload[:2]
    if sig_alg not in (b"Ed", b"ED"):
        raise ValueError(f"unsupported sig alg: {sig_alg!r}")
    key_id = payload[2:10]
    signature = payload[10:74]

    trusted = ""
    global_sig = b""
    if len(lines) >= 4:
        line3 = lines[2]
        prefix = "trusted comment: "
        if line3.startswith(prefix):
            trusted = line3[len(prefix):]
        global_sig = base64.b64decode(lines[3])

    return sig_alg, key_id, signature, trusted, global_sig


def verify_minisign(file_path: str, pub_path: str,
                    sig_path: str | None = None,
                    accepted_pubs: list[str] | None = None) -> tuple[bool, str]:
    """Verify a minisign signature.

    `accepted_pubs` allows multiple public keys (rotation window). The
    primary pub_path is always tried first; the rest are tried in order.

    Returns (ok, message).
    """
    if sig_path is None:
        sig_path = file_path + ".minisig"
    if not Path(sig_path).exists():
        return False, f"signature missing: {sig_path}"

    try:
        sig_alg, sig_key_id, signature, trusted, global_sig = _decode_minisign_sig(
            sig_path
        )
    except Exception as e:
        return False, f"malformed signature: {e}"

    with open(file_path, "rb") as f:
        file_bytes = f.read()

    if sig_alg == b"Ed":
        signed = file_bytes
    else:  # b"ED"
        signed = hashlib.blake2b(file_bytes, digest_size=64).digest()

    candidates = [pub_path] + list(accepted_pubs or [])
    last_err = ""
    for cand in candidates:
        try:
            key_id, pubkey = _decode_minisign_pub(cand)
        except Exception as e:
            last_err = f"malformed pubkey {cand}: {e}"
            continue
        if key_id != sig_key_id:
            last_err = f"key_id mismatch on {cand}: sig={sig_key_id.hex()} pub={key_id.hex()}"
            continue
        ok = _verify_signature(pubkey, signed, signature)
        if not ok:
            last_err = f"signature did not verify against {cand}"
            continue

        # Verify the global signature over (sig || trusted_comment) when
        # present. This is what minisign -V does by default.
        if global_sig and trusted:
            global_signed = signature + trusted.encode("utf-8")
            ok2 = _verify_signature(pubkey, global_signed, global_sig)
            if not ok2:
                return False, "global signature (trusted comment) did not verify"
        return True, f"ok (key {key_id.hex()})"

    return False, last_err or "no acceptable public key"


def main():
    if len(sys.argv) < 3:
        print("usage: verify_index.py <file> <pub> [<sig>]", file=sys.stderr)
        sys.exit(2)
    f, p = sys.argv[1], sys.argv[2]
    s = sys.argv[3] if len(sys.argv) > 3 else None
    ok, msg = verify_minisign(f, p, s)
    print(msg)
    sys.exit(0 if ok else 1)


if __name__ == "__main__":
    main()
