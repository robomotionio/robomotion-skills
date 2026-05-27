#!/usr/bin/env python3
"""
claude-seo brand-kit generator (v2 — proper arrangement).

Same brand system as claude-ads v1.7.0: OS-window-framed dark CRT terminal
with TEAL-GREEN accent palette. Applies all claude-ads layout fixes:
  · 01-B clean L-routed connectors (no overlap at scoring node)
  · 02-A linear pipeline
  · 03-B HUB + 8 category clusters (no more concentric-ring overlap)
  · 04-B radial wheel with brighter labels
  · 05-A horizontal timeline
  · OS title bar with traffic lights (dark, matching canvas family)
  · Banner with animated row-highlight scanner

Emits all 15 variants (5 diagrams × 3 each).
The 5 locked picks (1B 2A 3B 4B 5A) are referenced from README and
showcased in branding/final.html.

Usage:
    python3 generate_diagrams.py
"""

import math
from pathlib import Path
from textwrap import dedent

ROOT = Path(__file__).resolve().parent.parent.parent
ASSETS = ROOT / "assets"
DIAG_DIR = ASSETS / "diagrams"
ASSETS.mkdir(parents=True, exist_ok=True)
DIAG_DIR.mkdir(parents=True, exist_ok=True)

# ============================================================================
# BRAND-ORANGE PALETTE — unified across claude-ads + claude-seo
# ============================================================================
ACCENT          = "#D97757"
ACCENT_BRIGHT   = "#F5B095"
ACCENT_MID      = "#E89270"
ACCENT_DEEP     = "#7A3A1F"
ACCENT_DARKER   = "#5C2A14"
ACCENT_LIGHT    = "#F0A283"
ACCENT_FAINT    = "#6F3922"
CANVAS          = "#1F1B16"

# ============================================================================
# SHARED STYLE
# ============================================================================
STYLE = dedent(f"""
<defs>
  <style type="text/css"><![CDATA[
    @import url('https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@500;600;700&family=Inter:wght@400;500;600&display=swap');
    .bg            {{ fill: {CANVAS}; }}
    .bg-soft       {{ fill: {CANVAS}; }}
    .box           {{ fill: #26221C; stroke: #4A3D32; stroke-width: 1; }}
    .box-focal     {{ fill: #1F2D27; stroke: {ACCENT}; stroke-width: 1.4; }}
    .box-future    {{ fill: #221E18; stroke: #3A312A; stroke-width: 1; stroke-dasharray: 4 3; }}
    .box-soft      {{ fill: #232019; stroke: #3A312A; stroke-width: 1; }}
    .label-h       {{ font-family: 'JetBrains Mono', monospace; fill: #F5F4ED; font-size: 16px; font-weight: 700; letter-spacing: 0.3px; }}
    .label         {{ font-family: 'JetBrains Mono', monospace; fill: #F5F4ED; font-size: 14px; font-weight: 600; }}
    .label-sub     {{ font-family: 'JetBrains Mono', monospace; fill: #9C8B7E; font-size: 11px; letter-spacing: 1.4px; text-transform: uppercase; }}
    .label-tiny    {{ font-family: 'JetBrains Mono', monospace; fill: #6F5F54; font-size: 10px; letter-spacing: 1px; text-transform: uppercase; }}
    .label-radial  {{ font-family: 'JetBrains Mono', monospace; fill: #E0D2C4; font-size: 13px; font-weight: 600; letter-spacing: 0.6px; }}
    .label-accent  {{ font-family: 'JetBrains Mono', monospace; fill: {ACCENT}; font-size: 12px; font-weight: 600; letter-spacing: 1px; text-transform: uppercase; }}
    .conn          {{ stroke: #6F5F54; stroke-width: 1; fill: none; }}
    .conn-soft     {{ stroke: #4A3D32; stroke-width: 1; fill: none; }}
    .conn-dashed   {{ stroke: #4A3D32; stroke-width: 1; fill: none; stroke-dasharray: 4 3; }}
    .accent-fill   {{ fill: {ACCENT}; }}
    .accent-bright {{ fill: {ACCENT_BRIGHT}; }}
    .corner-mark   {{ font-family: 'JetBrains Mono', monospace; fill: #5A5750; font-size: 10px; letter-spacing: 1.4px; text-transform: uppercase; }}
  ]]></style>
  <marker id="arrow" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="5" markerHeight="5" orient="auto-start-reverse">
    <path d="M 0 0 L 10 5 L 0 10 z" fill="#6F5F54"/>
  </marker>
</defs>
""").strip()


# ---- OS window chrome (DARK title bar) ----
TITLE_H = 48
WIN_RADIUS = 10
WIN_BORDER = "#3A312A"
WIN_BAR_BG = "#2A2520"
WIN_BAR_FG = "#E0D2C4"
TL_YELLOW = "#fbbf24"
TL_GREEN  = "#10b981"
TL_RED    = "#ef4444"
TL_RADIUS = 9
TL_SPACING = 28


def window_chrome(w, title):
    cy = TITLE_H / 2
    tl_x_close = w - 28
    tl_x_max   = tl_x_close - TL_SPACING
    tl_x_min   = tl_x_max - TL_SPACING
    return f'''
  <path d="M 0 {WIN_RADIUS} Q 0 0 {WIN_RADIUS} 0 L {w-WIN_RADIUS} 0 Q {w} 0 {w} {WIN_RADIUS} L {w} {TITLE_H} L 0 {TITLE_H} Z" fill="{WIN_BAR_BG}"/>
  <line x1="0" y1="{TITLE_H}" x2="{w}" y2="{TITLE_H}" stroke="{WIN_BORDER}" stroke-width="1"/>
  <text x="20" y="{cy + 5}" font-family="JetBrains Mono, monospace" font-size="15" fill="{WIN_BAR_FG}" font-weight="600">{title}</text>
  <circle cx="{tl_x_min}"   cy="{cy}" r="{TL_RADIUS}" fill="{TL_YELLOW}" stroke="{WIN_BORDER}" stroke-width="0.7"/>
  <circle cx="{tl_x_max}"   cy="{cy}" r="{TL_RADIUS}" fill="{TL_GREEN}"  stroke="{WIN_BORDER}" stroke-width="0.7"/>
  <circle cx="{tl_x_close}" cy="{cy}" r="{TL_RADIUS}" fill="{TL_RED}"    stroke="{WIN_BORDER}" stroke-width="0.7"/>
'''


def svg(viewbox_w, viewbox_h, body, corner="claude-seo · v2.0.0", win_title=None):
    if win_title is None:
        win_title = f"claude-seo.app — {corner}"
    total_h = viewbox_h + TITLE_H
    chrome = window_chrome(viewbox_w, win_title)
    inner_corner = f'<text x="{viewbox_w-20}" y="{viewbox_h-12}" class="corner-mark" text-anchor="end">{corner}</text>'
    return dedent(f"""<?xml version="1.0" encoding="UTF-8"?>
<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {viewbox_w} {total_h}"
     preserveAspectRatio="xMidYMid meet" width="100%" font-family="JetBrains Mono, monospace">
{STYLE}
<rect x="0.5" y="0.5" width="{viewbox_w-1}" height="{total_h-1}" rx="{WIN_RADIUS}" fill="{WIN_BAR_BG}" stroke="{WIN_BORDER}" stroke-width="1"/>
{chrome}
<g transform="translate(0, {TITLE_H})">
  <rect class="bg" width="{viewbox_w}" height="{viewbox_h}"/>
  {body}
  {inner_corner}
</g>
</svg>
""")


# ---- helpers ----
def box(x, y, w, h, klass="box", rx=4, animate=False):
    anim = '<animate attributeName="opacity" values="0.85;1;0.85" dur="4.2s" repeatCount="indefinite"/>' if animate else ""
    return f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="{rx}" class="{klass}">{anim}</rect>'


def text(x, y, content, klass="label", anchor="middle"):
    return f'<text x="{x}" y="{y}" class="{klass}" text-anchor="{anchor}">{content}</text>'


def label_box(cx, cy, w, h, lines, klass="box", focal=False):
    if focal:
        klass = "box-focal"
    x = cx - w / 2
    y = cy - h / 2
    line_h = 20
    total_h = (len(lines) - 1) * line_h
    start_y = cy - total_h / 2 + 5
    out = [box(x, y, w, h, klass, animate=focal)]
    for i, ln in enumerate(lines):
        cls = "label-accent" if (i == 0 and len(lines) > 1) else "label"
        out.append(text(cx, start_y + i * line_h, ln, cls))
    return "\n".join(out)


def conn(x1, y1, x2, y2, klass="conn", arrow="arrow"):
    return f'<path d="M {x1} {y1} L {x2} {y2}" class="{klass}" marker-end="url(#{arrow})"/>'


def line_only(x1, y1, x2, y2, klass="conn-soft"):
    return f'<path d="M {x1} {y1} L {x2} {y2}" class="{klass}"/>'


# ============================================================================
# CLAUDE-SEO CONTENT
# ============================================================================
SUB_SKILLS = {
    "audit":           ["seo-audit", "seo-page", "seo-flow"],
    "content":         ["seo-content", "seo-content-brief", "seo-cluster"],
    "schema":          ["seo-schema", "seo-sitemap", "seo-images"],
    "technical":       ["seo-technical", "seo-google", "seo-backlinks"],
    "ai · search":     ["seo-geo", "seo-sxo", "seo-drift"],
    "local · maps":    ["seo-local", "seo-maps"],
    "commerce · intl": ["seo-ecommerce", "seo-hreflang", "seo-plan", "seo-programmatic", "seo-competitor-pages"],
    "extensions":      ["seo-dataforseo", "seo-image-gen"],
}

# 10-principle framework
FRAMEWORK = [
    ("perceive", "gather signals",     ["observe-external", "observe-internal", "listen"]),
    ("analyze",  "make sense of them", ["think", "connect-lateral", "connect-system"]),
    ("validate", "test the read",      ["feel", "accept"]),
    ("act",      "ship the response",  ["create", "grow"]),
]

WAVES = [
    ("v1.7.0", "mar 2026", "google APIs",          "GSC · PSI · CrUX\nindexing · GA4",          False),
    ("v1.8.0", "mar 2026", "free backlinks",       "moz · bing · common-crawl",                  False),
    ("v1.9.0", "apr 2026", "community challenge",  "cluster · sxo · drift\necommerce · hreflang",False),
    ("v2.0.0", "may 2026", "AI search + framework","GEO · 10-principle thinking",                True),
    ("v2.5.0", "q3 2026",  "auto-fix engine",      "patch generation\nweb-vitals lab",           False),
    ("v3.0.0", "q4 2026",  "audit-as-code",        "CI integration\nrolling baselines",          False),
]


# ============================================================================
# DIAGRAM 01 — SYSTEM ARCHITECTURE (3 variants)
# ============================================================================
def diag_01_a():
    """A: Top-down hierarchical flow."""
    body = []
    W, H = 1200, 950
    cx = W / 2
    body.append(label_box(cx, 100, 360, 80, ["entry", "/seo audit"], focal=True))
    body.append(label_box(cx, 240, 360, 80, ["orchestrator", "seo/SKILL.md"]))
    body.append(label_box(280,  430, 280, 130, ["sub-skills", "25 modules", "8 categories"]))
    body.append(label_box(cx,   430, 280, 130, ["audit agents", "6 parallel", "content · schema · perf", "technical · sitemap · visual"]))
    body.append(label_box(920,  430, 280, 130, ["ai search", "GEO · brand mentions", "AI Overviews · LLMs"]))
    body.append(label_box(cx, 660, 480, 100, ["scoring engine", "weighted by 7 dimensions"]))
    body.append(label_box(cx, 830, 480, 100, ["audit report", "score 0-100 · action plan · pdf"]))

    body.append(conn(cx, 140, cx, 200))
    body.append(line_only(cx, 280, cx, 350))
    body.append(line_only(280, 350, 920, 350))
    body.append(conn(280, 350, 280, 365))
    body.append(conn(cx,  350, cx,  365))
    body.append(conn(920, 350, 920, 365))
    body.append(line_only(280, 495, 280, 590))
    body.append(line_only(cx,  495, cx,  590))
    body.append(line_only(920, 495, 920, 590))
    body.append(line_only(280, 590, 920, 590))
    body.append(conn(cx, 590, cx, 610))
    body.append(conn(cx, 710, cx, 780))
    return svg(W, H, "\n".join(body), corner="01 · system architecture · A")


def diag_01_b():
    """B: Left-to-right horizontal (clean L-routed connectors, no overlap)."""
    body = []
    W, H = 1600, 700
    cy = H / 2
    x_entry  = 150;  x_orch  = 430;  x_branch = 800
    x_join   = 1080; x_score = 1200; x_report = 1430

    body.append(label_box(x_entry,  cy,  220, 100, ["entry", "/seo audit"], focal=True))
    body.append(label_box(x_orch,   cy,  220, 100, ["orchestrator", "seo/SKILL.md"]))
    body.append(label_box(x_branch, 200, 240, 90,  ["sub-skills", "25 modules"]))
    body.append(label_box(x_branch, cy,  240, 90,  ["audit agents", "6 parallel"]))
    body.append(label_box(x_branch, 500, 240, 90,  ["ai search", "GEO · LLMs"]))
    body.append(label_box(x_score,  cy,  220, 100, ["scoring", "weighted dimensions"]))
    body.append(label_box(x_report, cy,  220, 100, ["report", "score · plan"]))

    body.append(conn(x_entry + 110, cy, x_orch - 110, cy))
    body.append(line_only(x_orch + 110, cy, x_orch + 165, cy))
    body.append(line_only(x_orch + 165, 200, x_orch + 165, 500))
    body.append(conn(x_orch + 165, 200, x_branch - 120, 200))
    body.append(conn(x_orch + 165, cy,  x_branch - 120, cy))
    body.append(conn(x_orch + 165, 500, x_branch - 120, 500))
    body.append(line_only(x_branch + 120, 200, x_join - 60, 200))
    body.append(line_only(x_branch + 120, cy,  x_join - 60, cy))
    body.append(line_only(x_branch + 120, 500, x_join - 60, 500))
    body.append(line_only(x_join - 60, 200, x_join - 60, 500))
    body.append(conn(x_join - 60, cy, x_score - 110, cy))
    body.append(conn(x_score + 110, cy, x_report - 110, cy))
    return svg(W, H, "\n".join(body), corner="01 · system architecture · B")


def diag_01_c():
    """C: Radial hub-and-spoke."""
    body = []
    W, H = 1200, 1000
    cx, cy = W / 2, H / 2
    body.append(label_box(cx, cy, 280, 100, ["orchestrator", "seo/SKILL.md"], focal=True))
    angles = [-90, -30, 30, 90, 150, 210]
    labels = [
        (["audit report", "score · plan"], False),
        (["sub-skills", "25 modules"], False),
        (["audit agents", "6 parallel"], False),
        (["scoring", "7 dimensions"], False),
        (["ai search", "GEO · drift"], False),
        (["entry", "/seo audit"], True),
    ]
    R = 340
    for ang_deg, (lns, focal) in zip(angles, labels):
        ang = math.radians(ang_deg)
        nx = cx + R * math.cos(ang)
        ny = cy + R * math.sin(ang)
        body.append(f'<path d="M {cx + 140*math.cos(ang)} {cy + 50*math.sin(ang)} L {nx - 120*math.cos(ang)} {ny - 40*math.sin(ang)}" class="conn-soft"/>')
        body.append(label_box(nx, ny, 240, 80, lns, focal=focal))
    return svg(W, H, "\n".join(body), corner="01 · system architecture · C")


# ============================================================================
# DIAGRAM 02 — AUDIT PIPELINE (3 variants)
# ============================================================================
def diag_02_a():
    """A: Linear horizontal flow."""
    body = []
    W, H = 1600, 480
    cy = H / 2
    stages = [
        ("input", "/seo audit", True),
        ("crawl", "up to 500\npages", False),
        ("dispatch", "6 specialists\nin parallel", False),
        ("collect", "scores +\nfindings", False),
        ("report", "score · plan\n· action items", False),
    ]
    box_w = 220; box_h = 130
    gap = (W - 5 * box_w) / 6
    for i, (eyebrow, body_text, focal) in enumerate(stages):
        x = gap + i * (box_w + gap) + box_w / 2
        lines = [eyebrow] + body_text.split("\n")
        body.append(label_box(x, cy, box_w, box_h, lines, focal=focal))
        if i < len(stages) - 1:
            x_next = gap + (i + 1) * (box_w + gap) + box_w / 2
            body.append(conn(x + box_w / 2 + 4, cy, x_next - box_w / 2 - 4, cy))
    return svg(W, H, "\n".join(body), corner="02 · audit pipeline · A")


def diag_02_b():
    """B: Swimlane parallel tracks."""
    body = []
    W, H = 1600, 720
    body.append(label_box(150, 100, 220, 80, ["input", "/seo audit"], focal=True))
    lanes = [
        ("audit lane",   220, ["technical", "page", "content", "schema", "images"]),
        ("ai search",    400, ["geo", "sxo", "drift"]),
        ("commerce",     560, ["ecommerce", "hreflang", "plan", "programmatic"]),
    ]
    for label, y, items in lanes:
        body.append(text(80, y + 30, label, "label-sub", anchor="start"))
        for i, it in enumerate(items):
            x = 320 + i * 160
            body.append(label_box(x + 70, y + 25, 140, 50, [it]))
    body.append(label_box(W - 180, H / 2, 280, 100, ["score · report", "0-100 + action plan"]))
    body.append(line_only(280, 100, 280, H / 2))
    body.append(conn(280, H / 2, W - 320, H / 2))
    return svg(W, H, "\n".join(body), corner="02 · audit pipeline · B")


def diag_02_c():
    """C: Vertical compact."""
    body = []
    W, H = 900, 1100
    cx = W / 2
    stages = [
        ("input · /seo audit", "from prompt", True),
        ("crawl site", "up to 500 pages", False),
        ("dispatch agents", "6 parallel · context fork", False),
        ("run checks", "271 tests · weighted", False),
        ("aggregate scores", "by 7 dimensions", False),
        ("emit report", "md + pdf + action plan", False),
    ]
    for i, (label, annot, focal) in enumerate(stages):
        y = 100 + i * 160
        body.append(label_box(cx, y, 480, 90, [label]))
        body.append(text(cx + 280, y - 5, annot, "label-tiny", anchor="start"))
        body.append(text(cx + 280, y + 15, f"step {i+1:02d}", "label-accent", anchor="start"))
        if i < len(stages) - 1:
            body.append(conn(cx, y + 45, cx, y + 115))
    return svg(W, H, "\n".join(body), corner="02 · audit pipeline · C")


# ============================================================================
# DIAGRAM 03 — SUB-SKILL ECOSYSTEM (3 variants, 25 sub-skills, 8 categories)
# ============================================================================
def diag_03_a():
    """A: 4-column grid grouped by domain."""
    body = []
    W, H = 1600, 1100
    body.append(text(W/2, 80, "25 sub-skills · 8 categories", "label-sub"))
    cats = list(SUB_SKILLS.items())
    cols = 4
    col_w = (W - 100) / cols
    for idx, (title, items) in enumerate(cats):
        col = idx % cols
        row = idx // cols
        # heights vary per row based on max items in that row
        row_items = [len(cats[r*cols + c][1]) for r in range(2) for c in range(cols) if r*cols+c < len(cats) and r == row]
        max_items_in_row = max(row_items) if row_items else 1
        gx = 50 + col * col_w
        gy = 130 + row * (max(180, max_items_in_row * 52 + 80))
        body.append(text(gx + 20, gy + 28, title.upper(), "label-accent", anchor="start"))
        body.append(text(gx + col_w - 30, gy + 28, f"{len(items):02d}", "label-tiny", anchor="end"))
        body.append(box(gx + 10, gy + 45, col_w - 30, len(items) * 52 + 14, "box-soft", rx=6))
        for j, item in enumerate(items):
            yy = gy + 60 + j * 52
            body.append(label_box(gx + col_w/2 - 5, yy + 22, col_w - 70, 42, [item]))
    return svg(W, H, "\n".join(body), corner="03 · sub-skill ecosystem · A")


def diag_03_b():
    """B: Hub + 8 category clusters (proper arrangement, no overlap)."""
    body = []
    W, H = 1600, 1100
    cx, cy = W / 2, H / 2

    # 8 category clusters positioned around the orchestrator.
    # Top row: audit, content, schema, technical (4 panels)
    # Bottom row: ai-search, local-maps, commerce-intl, extensions (4 panels)
    panel_w = 360
    panel_h_top = 220
    panel_h_btm = 220
    top_y = 130
    btm_y = H - 130

    clusters_data = [
        # (title, items, cx, cy, w, h, side)
        ("audit",           SUB_SKILLS["audit"],            80 + panel_w/2,                  top_y, panel_w, panel_h_top, "top"),
        ("content",         SUB_SKILLS["content"],          80 + panel_w + 30 + panel_w/2,   top_y, panel_w, panel_h_top, "top"),
        ("schema",          SUB_SKILLS["schema"],           W - 80 - panel_w - 30 - panel_w/2, top_y, panel_w, panel_h_top, "top"),
        ("technical",       SUB_SKILLS["technical"],        W - 80 - panel_w/2,              top_y, panel_w, panel_h_top, "top"),

        ("ai · search",     SUB_SKILLS["ai · search"],      80 + panel_w/2,                  btm_y, panel_w, panel_h_btm, "bottom"),
        ("local · maps",    SUB_SKILLS["local · maps"],     80 + panel_w + 30 + panel_w/2,   btm_y, panel_w, panel_h_btm, "bottom"),
        ("commerce · intl", SUB_SKILLS["commerce · intl"],  W - 80 - panel_w - 30 - panel_w/2, btm_y, panel_w, panel_h_btm + 80, "bottom"),
        ("extensions",      SUB_SKILLS["extensions"],       W - 80 - panel_w/2,              btm_y, panel_w, panel_h_btm, "bottom"),
    ]

    # Draw connectors FIRST (under everything)
    for title, items, gcx, gcy, gw, gh, side in clusters_data:
        if side == "top":
            body.append(line_only(gcx, gcy + gh/2, gcx, cy - 55))
        else:
            body.append(line_only(gcx, gcy - gh/2, gcx, cy + 55))

    # Draw horizontal "rail" lines at orchestrator level
    body.append(line_only(80 + panel_w/2,             cy - 55, W - 80 - panel_w/2, cy - 55))
    body.append(line_only(80 + panel_w/2,             cy + 55, W - 80 - panel_w/2, cy + 55))

    # Cluster panels
    for title, items, gcx, gcy, gw, gh, side in clusters_data:
        gx = gcx - gw/2
        gy = gcy - gh/2
        body.append(box(gx, gy, gw, gh, "box-soft", rx=8))
        body.append(text(gx + 18, gy + 26, title.upper(), "label-accent", anchor="start"))
        body.append(text(gx + gw - 18, gy + 26, f"{len(items):02d}", "label-tiny", anchor="end"))

        item_w = gw - 40
        item_h = 38
        for i, item in enumerate(items):
            iy = gy + 50 + i * (item_h + 6)
            body.append(label_box(gx + gw/2, iy + item_h/2, item_w, item_h, [item]))

    # Orchestrator drawn last (on top)
    body.append(label_box(cx, cy, 320, 110, ["orchestrator", "seo/SKILL.md"], focal=True))
    return svg(W, H, "\n".join(body), corner="03 · sub-skill ecosystem · B")


def diag_03_c():
    """C: Cluster cards — 8 grouped panels in clean 4×2 grid."""
    body = []
    W, H = 1600, 1200
    body.append(text(W/2, 60, "25 sub-skills · 8 domain clusters", "label-sub"))
    groups = [
        ("audit",           SUB_SKILLS["audit"]),
        ("content",         SUB_SKILLS["content"]),
        ("schema",          SUB_SKILLS["schema"]),
        ("technical",       SUB_SKILLS["technical"]),
        ("ai · search",     SUB_SKILLS["ai · search"]),
        ("local · maps",    SUB_SKILLS["local · maps"]),
        ("commerce · intl", SUB_SKILLS["commerce · intl"]),
        ("extensions",      SUB_SKILLS["extensions"]),
    ]
    cols = 4
    col_w = (W - 100) / cols
    row_h_top = 290
    row_h_btm = 400
    for idx, (title, items) in enumerate(groups):
        col = idx % cols
        row = idx // cols
        gx = 50 + col * col_w + 10
        gy = 110 + row * (row_h_top + 30)
        gw = col_w - 20
        gh = row_h_btm if (idx == 6) else (row_h_top if len(items) <= 4 else row_h_btm - 80)
        body.append(box(gx, gy, gw, gh, "box-soft", rx=8))
        body.append(text(gx + 18, gy + 28, title.upper(), "label-accent", anchor="start"))
        body.append(text(gx + gw - 18, gy + 28, f"{len(items):02d}", "label-tiny", anchor="end"))
        item_w = gw - 40
        item_h = 42
        for i, item in enumerate(items):
            iy = gy + 50 + i * (item_h + 8)
            body.append(label_box(gx + gw/2, iy + item_h/2, item_w, item_h, [item]))
    return svg(W, H, "\n".join(body), corner="03 · sub-skill ecosystem · C")


# ============================================================================
# DIAGRAM 04 — 10-PRINCIPLE THINKING FRAMEWORK (3 variants)
# ============================================================================
def diag_04_a():
    """A: Horizontal flow — 4 phase columns, principles stacked below each."""
    body = []
    W, H = 1700, 720
    body.append(text(W/2, 60, "10-principle thinking framework · perceive → act", "label-sub"))
    stage_w = (W - 200) / 4
    cy = 200
    for i, (stage, subtitle, principles) in enumerate(FRAMEWORK):
        cx = 100 + stage_w * i + stage_w / 2
        focal = (i == 0)
        body.append(label_box(cx, cy, stage_w - 60, 110, [f"phase {i+1:02d}", stage, subtitle], focal=focal))
        if i < 3:
            nx = 100 + stage_w * (i + 1) + stage_w / 2
            body.append(conn(cx + (stage_w - 60)/2 + 4, cy, nx - (stage_w - 60)/2 - 4, cy))
        for j, p in enumerate(principles):
            py = cy + 130 + j * 70
            body.append(label_box(cx, py, stage_w - 90, 56, [p]))
    return svg(W, H, "\n".join(body), corner="04 · thinking framework · A")


def diag_04_b():
    """B: Radial wheel — central hub, 4 stage satellites, 10 principles on outer ring.
    PROPER SPACING + EXPLICIT LINKING: each principle has a clean connector to its
    parent stage card, lines never cross the central card or other stage cards."""
    body = []
    W, H = 1500, 1500
    cx, cy = W / 2, H / 2

    # Dimensions
    HUB_W, HUB_H = 360, 110          # central card
    STAGE_W, STAGE_H = 220, 80
    PRINCIPLE_W, PRINCIPLE_H = 210, 52
    R_STAGE = 340                    # well clear of hub (hub half-width = 180)
    R_PRINCIPLE = 580                # well clear of stage cards (stage half-width = 110, R_STAGE+110 = 450)

    # Faint ring guides
    body.append(f'<circle cx="{cx}" cy="{cy}" r="{R_PRINCIPLE}" fill="none" stroke="{ACCENT_FAINT}" stroke-width="1" stroke-dasharray="3 3" opacity="0.25"/>')
    body.append(f'<circle cx="{cx}" cy="{cy}" r="{R_STAGE}" fill="none" stroke="{ACCENT_FAINT}" stroke-width="1" stroke-dasharray="3 3" opacity="0.30"/>')

    # Quadrant separator dashed lines (between stage quadrants)
    for ang_deg in [-135, -45, 45, 135]:
        a = math.radians(ang_deg)
        x1 = cx + (R_STAGE - 40) * math.cos(a)
        y1 = cy + (R_STAGE - 40) * math.sin(a)
        x2 = cx + (R_PRINCIPLE + 50) * math.cos(a)
        y2 = cy + (R_PRINCIPLE + 50) * math.sin(a)
        body.append(f'<path d="M {x1} {y1} L {x2} {y2}" class="conn-dashed" opacity="0.25"/>')

    # Stage positions
    quadrant_angles = [-90, 0, 90, 180]   # perceive top, analyze right, validate bottom, act left

    # Precompute stage card centres (used by both stage rendering + principle connectors)
    stage_centres = []
    for ang_deg in quadrant_angles:
        ang = math.radians(ang_deg)
        sx = cx + R_STAGE * math.cos(ang)
        sy = cy + R_STAGE * math.sin(ang)
        stage_centres.append((sx, sy, ang_deg))

    # Principles — pre-compute angles within each quadrant
    # Spread principles ±28° from stage centre angle
    principle_layout = []  # list of (stage_idx, principle_name, px, py, principle_ang_deg)
    for stage_i, (_, _, principles) in enumerate(FRAMEWORK):
        stage_centre_deg = quadrant_angles[stage_i]
        n = len(principles)
        spread = 28
        if n == 1:
            local_offsets = [0]
        else:
            local_offsets = [-spread + i * (2 * spread / (n - 1)) for i in range(n)]
        for k, (p, off) in enumerate(zip(principles, local_offsets)):
            p_ang_deg = stage_centre_deg + off
            p_ang = math.radians(p_ang_deg)
            px = cx + R_PRINCIPLE * math.cos(p_ang)
            py = cy + R_PRINCIPLE * math.sin(p_ang)
            principle_layout.append((stage_i, p, px, py, p_ang_deg))

    # ─── Draw connectors FIRST (underneath everything) ───
    # Each principle gets its own line from its parent stage card edge to the principle's near edge.
    for stage_i, pname, px, py, p_ang_deg in principle_layout:
        sx_centre, sy_centre, stage_ang_deg = stage_centres[stage_i]
        # Direction from stage centre to principle centre
        dx = px - sx_centre
        dy = py - sy_centre
        d = math.hypot(dx, dy)
        if d == 0:
            continue
        ux, uy = dx / d, dy / d
        # Start at stage card edge in that direction
        # Approximate edge crossing: STAGE_W/2 horizontal or STAGE_H/2 vertical, whichever first
        # Simple ellipse-edge approximation
        edge_dist_stage = min(
            abs((STAGE_W / 2) / ux) if abs(ux) > 0.01 else 1e9,
            abs((STAGE_H / 2) / uy) if abs(uy) > 0.01 else 1e9
        )
        x1 = sx_centre + ux * edge_dist_stage
        y1 = sy_centre + uy * edge_dist_stage
        # End at principle card edge (going back toward the stage)
        edge_dist_pri = min(
            abs((PRINCIPLE_W / 2) / ux) if abs(ux) > 0.01 else 1e9,
            abs((PRINCIPLE_H / 2) / uy) if abs(uy) > 0.01 else 1e9
        )
        x2 = px - ux * edge_dist_pri
        y2 = py - uy * edge_dist_pri
        body.append(f'<path d="M {x1:.1f} {y1:.1f} L {x2:.1f} {y2:.1f}" class="conn-soft" opacity="0.6"/>')

    # ─── Stage cards ───
    for (stage, subtitle, _), (sx, sy, _) in zip(FRAMEWORK, stage_centres):
        body.append(label_box(sx, sy, STAGE_W, STAGE_H, [stage, subtitle]))

    # ─── Principle boxes ───
    for stage_i, pname, px, py, _ in principle_layout:
        body.append(label_box(px, py, PRINCIPLE_W, PRINCIPLE_H, [pname]))

    # ─── Central hub (drawn LAST so it sits on top, never overlapped) ───
    body.append(label_box(cx, cy, HUB_W, HUB_H, ["thinking framework", "10 principles · 4 phases"], focal=True))

    return svg(W, H, "\n".join(body), corner="04 · thinking framework · B")


def diag_04_c():
    """C: Swim-lane — 4 horizontal lanes, one per stage."""
    body = []
    W, H = 1500, 820
    body.append(text(W/2, 60, "10-principle framework · 4 phases, 10 principles", "label-sub"))
    lane_h = 150
    lane_gap = 20
    start_y = 110
    label_x = 30
    content_x = 240
    for i, (stage, subtitle, principles) in enumerate(FRAMEWORK):
        ly = start_y + i * (lane_h + lane_gap)
        focal = (i == 0)
        klass = "box-focal" if focal else "box-soft"
        body.append(box(label_x, ly, W - 60, lane_h, klass, rx=8))
        body.append(text(label_x + 30, ly + 50, f"phase {i+1:02d}", "label-accent", anchor="start"))
        body.append(text(label_x + 30, ly + 78, stage, "label", anchor="start"))
        body.append(text(label_x + 30, ly + 105, subtitle, "label-tiny", anchor="start"))
        n = len(principles)
        avail = W - content_x - 60
        pill_w = min(280, (avail - (n - 1) * 24) / max(n, 1))
        for j, p in enumerate(principles):
            px = content_x + j * (pill_w + 24) + pill_w / 2
            body.append(label_box(px, ly + lane_h / 2, pill_w, 70, [p]))
    return svg(W, H, "\n".join(body), corner="04 · thinking framework · C")


# ============================================================================
# DIAGRAM 05 — WAVE ROADMAP (3 variants)
# ============================================================================
def diag_05_a():
    """A: Horizontal timeline with alternating cards."""
    body = []
    W, H = 1800, 600
    cy = 310
    n = len(WAVES)
    x_start, x_end = 120, W - 120
    step = (x_end - x_start) / (n - 1)
    body.append(f'<line x1="{x_start}" y1="{cy}" x2="{x_end}" y2="{cy}" class="conn-soft" stroke-width="2"/>')
    for i, (v, dt, title, items, focal) in enumerate(WAVES):
        x = x_start + i * step
        r = 14 if focal else 10
        fill = ACCENT_BRIGHT if focal else ACCENT
        body.append(f'<circle cx="{x}" cy="{cy}" r="{r}" fill="{fill}" stroke="#0A0807" stroke-width="2"/>')
        above = (i % 2 == 0)
        by = cy - 160 if above else cy + 30
        body.append(label_box(x, by + 60, 260, 130, [v + " · " + dt, title, ""], focal=focal))
        for k, ln in enumerate(items.split("\n")):
            body.append(text(x, by + 90 + k * 16, ln, "label-tiny"))
        if above:
            body.append(line_only(x, cy - r, x, by + 60 + 65))
        else:
            body.append(line_only(x, cy + r, x, by + 60 - 65))
    return svg(W, H, "\n".join(body), corner="05 · roadmap · A")


def diag_05_b():
    """B: Vertical timeline."""
    body = []
    W, H = 900, 1300
    cx = W / 2
    n = len(WAVES)
    y_start, y_end = 100, H - 100
    step = (y_end - y_start) / (n - 1)
    body.append(f'<line x1="{cx}" y1="{y_start}" x2="{cx}" y2="{y_end}" class="conn-soft" stroke-width="2"/>')
    for i, (v, dt, title, items, focal) in enumerate(WAVES):
        y = y_start + i * step
        r = 16 if focal else 12
        fill = ACCENT_BRIGHT if focal else ACCENT
        body.append(f'<circle cx="{cx}" cy="{y}" r="{r}" fill="{fill}" stroke="#0A0807" stroke-width="2"/>')
        left = (i % 2 == 0)
        side = -1 if left else 1
        bx = cx + side * 260
        body.append(label_box(bx, y, 360, 110, [v + " · " + dt, title], focal=focal))
        for k, ln in enumerate(items.split("\n")):
            body.append(text(bx, y + 70 + k * 14, ln, "label-tiny"))
        body.append(line_only(cx + side * r, y, bx - side * 180, y))
    return svg(W, H, "\n".join(body), corner="05 · roadmap · B")


def diag_05_c():
    """C: Kanban columns."""
    body = []
    W, H = 1400, 800
    cols = [
        ("shipped", ["v1.7.0", "v1.8.0", "v1.9.0", "v2.0.0"], True),
        ("next",    ["v2.5.0"], False),
        ("future",  ["v3.0.0"], False),
    ]
    col_w = 400
    col_gap = 40
    start_x = (W - 3 * col_w - 2 * col_gap) / 2
    for ci, (cname, versions, focal) in enumerate(cols):
        cx = start_x + ci * (col_w + col_gap)
        body.append(box(cx, 100, col_w, H - 180, "box-soft", rx=8))
        body.append(text(cx + 20, 130, cname.upper(), "label-accent", anchor="start"))
        body.append(text(cx + col_w - 20, 130, f"{len(versions):02d}", "label-tiny", anchor="end"))
        for vi, v in enumerate(versions):
            wave = next((w for w in WAVES if w[0] == v), None)
            if not wave:
                continue
            _, dt, title, items, fc = wave
            wy = 170 + vi * 140
            body.append(label_box(cx + col_w/2, wy + 50, col_w - 40, 100, [v + " · " + dt, title], focal=fc))
            for k, ln in enumerate(items.split("\n")):
                body.append(text(cx + col_w/2, wy + 90 + k * 14, ln, "label-tiny"))
    return svg(W, H, "\n".join(body), corner="05 · roadmap · C")


# ============================================================================
# MAIN
# ============================================================================
DIAGRAMS = {
    "01-architecture-A.svg":   diag_01_a,
    "01-architecture-B.svg":   diag_01_b,
    "01-architecture-C.svg":   diag_01_c,
    "02-pipeline-A.svg":       diag_02_a,
    "02-pipeline-B.svg":       diag_02_b,
    "02-pipeline-C.svg":       diag_02_c,
    "03-sub-skill-map-A.svg":  diag_03_a,
    "03-sub-skill-map-B.svg":  diag_03_b,
    "03-sub-skill-map-C.svg":  diag_03_c,
    "04-framework-A.svg":      diag_04_a,
    "04-framework-B.svg":      diag_04_b,
    "04-framework-C.svg":      diag_04_c,
    "05-roadmap-A.svg":        diag_05_a,
    "05-roadmap-B.svg":        diag_05_b,
    "05-roadmap-C.svg":        diag_05_c,
}


def main():
    for fname, fn in DIAGRAMS.items():
        out = DIAG_DIR / fname
        out.write_text(fn())
        print(f"  ✓ {fname}")
    print(f"\n{len(DIAGRAMS)} diagrams emitted to {DIAG_DIR}")


if __name__ == "__main__":
    main()
