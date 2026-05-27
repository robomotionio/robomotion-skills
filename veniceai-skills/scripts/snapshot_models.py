#!/usr/bin/env python3
"""Snapshot the live Venice model catalog.

Hits ``GET /models`` (optionally filtered by ``?type=...``) and writes a
compact JSON snapshot per model type to ``skills/venice-models/snapshots/``.
The snapshot is the *ground-truth* list of API model IDs — skills and
examples reference these IDs, so regenerating the snapshot flags any
example that has gone stale.

Also produces ``model_ids.txt`` (one ``apiModelId`` per line) which the
sync/CI script can grep for drift in example code blocks.

Usage:
    export VENICE_API_KEY=sk-...
    python scripts/snapshot_models.py
    python scripts/snapshot_models.py --base-url https://api.venice.ai --type text

No third-party deps; stdlib only.

Exit 0 on success, 1 on HTTP/parsing failure. CI-safe.
"""

from __future__ import annotations

import argparse
import json
import os
import sys
import urllib.error
import urllib.request
from pathlib import Path

DEFAULT_BASE_URL = "https://api.venice.ai"
DEFAULT_TYPES = ["text", "image", "embedding", "tts", "asr", "video", "music", "upscale", "inpaint"]
REPO_ROOT = Path(__file__).resolve().parent.parent
SNAPSHOT_DIR = REPO_ROOT / "skills" / "venice-models" / "snapshots"


def fetch_models(base_url: str, model_type: str | None, api_key: str) -> dict:
    url = f"{base_url.rstrip('/')}/api/v1/models"
    if model_type:
        url += f"?type={model_type}"
    req = urllib.request.Request(
        url,
        headers={
            "Authorization": f"Bearer {api_key}",
            "Accept": "application/json",
            "User-Agent": "veniceai-skills-snapshot/0.1",
        },
    )
    with urllib.request.urlopen(req, timeout=30) as resp:
        return json.loads(resp.read().decode("utf-8"))


def normalize_model(entry: dict) -> dict:
    """Keep just the fields we document so snapshots stay small and diff cleanly."""
    model_spec = entry.get("model_spec") or entry.get("modelSpec") or {}
    capabilities = model_spec.get("capabilities") or {}
    constraints = model_spec.get("constraints") or {}
    pricing = model_spec.get("pricing") or {}
    return {
        "id": entry.get("id"),
        "type": entry.get("type"),
        "object": entry.get("object"),
        "owned_by": entry.get("owned_by"),
        "model_spec": {
            "availableContextTokens": model_spec.get("availableContextTokens"),
            "maxCompletionTokens": model_spec.get("maxCompletionTokens"),
            "capabilities": capabilities,
            "constraints": constraints,
            "pricing": pricing,
            **{k: v for k, v in model_spec.items() if k in (
                "voices", "embeddingDimensions", "maxInputTokens",
                "supportsCustomDimensions", "traits", "modelSource",
            )},
        },
    }


def write_snapshot(model_type: str, data: dict) -> Path:
    SNAPSHOT_DIR.mkdir(parents=True, exist_ok=True)
    out = SNAPSHOT_DIR / f"{model_type}.json"
    normalized = {
        "object": data.get("object"),
        "type": data.get("type"),
        "count": len(data.get("data", [])),
        "models": sorted(
            (normalize_model(m) for m in data.get("data", [])),
            key=lambda m: m.get("id") or "",
        ),
    }
    out.write_text(json.dumps(normalized, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return out


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--base-url", default=os.environ.get("VENICE_BASE_URL", DEFAULT_BASE_URL))
    parser.add_argument("--api-key", default=os.environ.get("VENICE_API_KEY"))
    parser.add_argument(
        "--type", dest="types", action="append",
        help="Repeatable. Model type to fetch. Defaults to all known types.",
    )
    args = parser.parse_args()

    if not args.api_key:
        print("ERROR: set VENICE_API_KEY or pass --api-key", file=sys.stderr)
        return 1

    types = args.types or DEFAULT_TYPES
    all_ids: list[str] = []
    had_error = False

    for t in types:
        try:
            payload = fetch_models(args.base_url, t, args.api_key)
        except urllib.error.HTTPError as e:
            print(f"[{t}] HTTP {e.code}: {e.reason}", file=sys.stderr)
            had_error = True
            continue
        except urllib.error.URLError as e:
            print(f"[{t}] network error: {e.reason}", file=sys.stderr)
            had_error = True
            continue

        out = write_snapshot(t, payload)
        ids = sorted(m.get("id") for m in payload.get("data", []) if m.get("id"))
        all_ids.extend(ids)
        print(f"[{t}] {len(ids):>3} models -> {out.relative_to(REPO_ROOT)}")

    if all_ids:
        ids_file = SNAPSHOT_DIR / "model_ids.txt"
        ids_file.write_text("\n".join(sorted(set(all_ids))) + "\n", encoding="utf-8")
        print(f"[ids] {len(set(all_ids)):>3} unique IDs -> {ids_file.relative_to(REPO_ROOT)}")

    return 1 if had_error else 0


if __name__ == "__main__":
    sys.exit(main())
