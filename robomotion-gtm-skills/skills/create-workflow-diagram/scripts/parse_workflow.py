#!/usr/bin/env python3
"""parse_workflow.py — Parse a plain-text workflow into a node/connection model.

Deterministic, stdlib only. Splits the description into steps (on -> / arrows / numbered
lists / line breaks), assigns an emoji icon per step from action keywords, detects simple
linear branches, and emits node x/y positions for the chosen layout + canvas size. The
host agent authors the styled HTML/SVG from this model (or cleans labels first via its own
reasoning); render.mjs screenshots it.

Examples:
  parse_workflow.py --workflow "Find leads -> Enrich -> Qualify -> Send"
  parse_workflow.py --workflow "1. Scrape 2. Clean 3. Score" --layout snake --size square
"""
import argparse
import json
import re
import sys

SIZES = {
    "landscape": (1920, 1080),
    "square": (1080, 1080),
    "wide": (1200, 630),
}

# action-keyword -> emoji icon
ICONS = [
    (("find", "search", "discover", "scrape", "collect", "gather"), "🔍"),
    (("enrich", "augment", "append", "lookup"), "✨"),
    (("qualify", "score", "rank", "filter", "evaluate"), "🎯"),
    (("send", "email", "outreach", "message", "notify", "deliver"), "📨"),
    (("clean", "normalize", "dedup", "transform", "process"), "🧹"),
    (("store", "save", "write", "persist", "database", "db"), "💾"),
    (("review", "approve", "check", "verify", "validate"), "✅"),
    (("analyze", "report", "summarize", "insight"), "📊"),
    (("build", "create", "generate", "draft", "make"), "🛠️"),
    (("call", "api", "fetch", "request", "pull"), "🔗"),
    (("schedule", "trigger", "start", "run"), "▶️"),
    (("pay", "invoice", "bill", "charge"), "💳"),
]
DEFAULT_ICON = "⚙️"
BRANCH_RE = re.compile(r"\b(if|or|else|when|otherwise)\b", re.IGNORECASE)


def split_steps(text):
    text = text.strip()
    # normalize arrow variants to a single delimiter
    norm = re.sub(r"\s*(→|->|⟶|=>)\s*", "", text)
    if "" in norm:
        parts = norm.split("")
    elif "\n" in norm:
        parts = norm.splitlines()
    else:
        # numbered list "1. a 2. b" or "1) a 2) b"
        parts = re.split(r"(?:^|\s)\d+[.)]\s*", norm)
    steps = [p.strip(" .;,") for p in parts if p.strip(" .;,")]
    return steps


def pick_icon(label):
    low = label.lower()
    for words, icon in ICONS:
        if any(w in low for w in words):
            return icon
    return DEFAULT_ICON


def split_label_detail(raw):
    """A step may carry a parenthetical or ':' tool detail."""
    detail = ""
    m = re.search(r"\((.*?)\)", raw)
    if m:
        detail = m.group(1).strip()
        raw = raw[: m.start()].strip() + raw[m.end():].strip()
    elif ":" in raw:
        label, _, det = raw.partition(":")
        return label.strip(), det.strip()
    return raw.strip(), detail


def layout_positions(n, layout, w, h):
    """Return list of (x, y) center positions for n nodes in [0..w]x[0..h]."""
    pad_x, pad_y = int(w * 0.08), int(h * 0.12)
    if layout == "top-bottom":
        usable = h - 2 * pad_y
        step = usable / max(n - 1, 1)
        return [(w // 2, int(pad_y + i * step)) for i in range(n)]
    if layout == "snake":
        cols = min(n, 4 if w >= h else 3)
        rows = (n + cols - 1) // cols
        cw = (w - 2 * pad_x) / max(cols, 1)
        ch = (h - 2 * pad_y) / max(rows, 1)
        pos = []
        for i in range(n):
            r = i // cols
            c = i % cols
            if r % 2 == 1:  # snake reverse on odd rows
                c = cols - 1 - c
            pos.append((int(pad_x + cw * (c + 0.5)), int(pad_y + ch * (r + 0.5))))
        return pos
    # left-right (default)
    usable = w - 2 * pad_x
    step = usable / max(n - 1, 1)
    return [(int(pad_x + i * step), h // 2) for i in range(n)]


def main():
    ap = argparse.ArgumentParser(description="Parse a workflow string into a node/connection model.")
    ap.add_argument("--workflow", required=True, help="steps separated by ->, arrows, numbers, or newlines")
    ap.add_argument("--layout", default="left-right", choices=["left-right", "top-bottom", "snake"])
    ap.add_argument("--size", default="landscape", choices=sorted(SIZES.keys()))
    ap.add_argument("--title", default="", help="optional diagram heading")
    ap.add_argument("--output", default="-", help="output JSON path (default stdout)")
    args = ap.parse_args()

    steps = split_steps(args.workflow)
    if not steps:
        sys.exit("ERROR: no steps parsed from --workflow")

    # auto-switch to snake for crowding when caller left the default
    layout = args.layout
    if layout == "left-right" and len(steps) >= 6:
        layout = "snake"

    w, h = SIZES[args.size]
    positions = layout_positions(len(steps), layout, w, h)

    nodes = []
    for i, raw in enumerate(steps):
        label, detail = split_label_detail(raw)
        x, y = positions[i]
        nodes.append({
            "id": i,
            "label": label,
            "detail": detail,
            "icon": pick_icon(label + " " + detail),
            "branch": bool(BRANCH_RE.search(raw)),
            "x": x, "y": y,
        })

    connections = [{"from": i, "to": i + 1} for i in range(len(nodes) - 1)]

    model = {
        "title": args.title,
        "layout": layout,
        "size": args.size,
        "canvas": {"width": w, "height": h},
        "nodes": nodes,
        "connections": connections,
    }
    text = json.dumps(model, ensure_ascii=False, indent=2)
    if args.output == "-":
        print(text)
    else:
        with open(args.output, "w", encoding="utf-8") as f:
            f.write(text + "\n")
        print(f"{len(nodes)} nodes ({layout}) -> {args.output}", file=sys.stderr)


if __name__ == "__main__":
    main()
