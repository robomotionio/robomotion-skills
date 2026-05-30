#!/usr/bin/env python3
"""graphics.py — driver CLI for graphics-studio.

Orchestrates the deterministic plumbing around an agent-authored graphic:

  1. resolve a STYLE -> design tokens, from one of:
       --style <id>     a catalog style in styles.json
       --ref <image>    extract an ad-hoc style (calls extract_style.py)
       --brand ...      synthesize a custom style from brand hex colors + font
  2. resolve the FORMAT -> canvas size + density rules + content schema (formats.json)
  3. (optional) source imagery (calls source_images.py)
  4. EMIT a render-plan + per-slide content scaffold for the AGENT to fill
  5. COMPOSE final HTML: the format template + injected :root style tokens + the agent's
     content + Google-fonts links, then invoke render.mjs.
  6. run a WCAG contrast check on text/bg + accent/bg and WARN on AA failure.

Subcommands:
  plan      print a render-plan (style tokens, canvas, density, content scaffold, font links)
  compose   fill a template with style tokens + an agent content fragment -> a render-ready HTML
  preview   compose+render ONE style-preview slide so the user can approve direction
  render    compose (if needed) and invoke render.mjs for a file or a directory of slides
  contrast  WCAG AA/AAA contrast report for a resolved style

No LLM calls. The agent authors the content fragment; this script does the deterministic
token-binding, templating, accessibility check, and render invocation.
"""
import argparse
import json
import os
import re
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
TEMPLATES = os.path.normpath(os.path.join(HERE, "..", "templates"))


# ---------------------------------------------------------------------------
# Loading catalog data
# ---------------------------------------------------------------------------
def load_json(path):
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def load_styles():
    return load_json(os.path.join(HERE, "styles.json")).get("styles", {})


def load_formats():
    return load_json(os.path.join(HERE, "formats.json")).get("formats", {})


# ---------------------------------------------------------------------------
# Style resolution
# ---------------------------------------------------------------------------
def synth_brand_style(hexes, heading_font, body_font, theme):
    """Synthesize a style object from brand hex colors + fonts (brand mode)."""
    hexes = [h if h.startswith("#") else "#" + h for h in hexes]
    bg = hexes[0]
    accent = hexes[1] if len(hexes) > 1 else hexes[0]
    is_dark = theme == "dark" or (theme == "auto" and _luminance(_hex(bg)) < 0.4)
    text = "#f5f5f0" if is_dark else "#141416"
    surface = _mix_hex(bg, "#ffffff", 0.08 if is_dark else 0.5 if _luminance(_hex(bg)) > 0.9 else 0.0)
    muted = _mix_hex(text, bg, 0.45)
    stack_h = f"'{heading_font}', system-ui, sans-serif"
    stack_b = f"'{body_font}', system-ui, sans-serif"
    return {
        "id": "brand-custom",
        "name": "Brand Custom",
        "aesthetic": "synthesized from brand colors",
        "mood_tags": ["brand", "custom", "dark" if is_dark else "light"],
        "palette": {"bg": bg, "surface": surface, "primary": text,
                    "accent": accent, "text": text, "muted": muted},
        "typography": {"heading_font": heading_font, "body_font": body_font,
                       "font_stack": stack_b, "_heading_stack": stack_h, "scale_ratio": 1.3},
        "radius": "14px",
        "shadow": "0 8px 30px rgba(0,0,0,0.25)" if is_dark else "0 2px 10px rgba(16,24,40,0.10)",
        "spacing_unit": "8px",
        "motifs": "Brand-driven style synthesized from the supplied colors + fonts.",
    }


def resolve_style(args):
    if args.brand:
        hexes = [h.strip() for h in args.brand.split(",") if h.strip()]
        return synth_brand_style(hexes, args.brand_heading or "Inter",
                                 args.brand_body or "Inter", args.theme)
    if args.ref:
        out = subprocess.run(
            [sys.executable, os.path.join(HERE, "extract_style.py"),
             "--image", args.ref, "--id", "ref-style", "--name", "Reference Style"],
            capture_output=True, text=True)
        if out.returncode != 0:
            sys.exit("ERROR extracting style from --ref:\n" + out.stderr)
        return json.loads(out.stdout)
    styles = load_styles()
    if not args.style:
        sys.exit("ERROR: provide --style <id>, --ref <image>, or --brand <hexes>. "
                 "Styles: " + ", ".join(styles.keys()))
    if args.style not in styles:
        sys.exit(f"ERROR: unknown style '{args.style}'. Available: " + ", ".join(styles.keys()))
    return styles[args.style]


# ---------------------------------------------------------------------------
# Color / WCAG
# ---------------------------------------------------------------------------
def _hex(h):
    h = h.lstrip("#")
    if len(h) == 3:
        h = "".join(c * 2 for c in h)
    return tuple(int(h[i:i + 2], 16) for i in (0, 2, 4))


def _hexs(rgb):
    return "#{:02x}{:02x}{:02x}".format(*(min(255, max(0, int(round(c)))) for c in rgb))


def _mix_hex(a, b, t):
    ca, cb = _hex(a), _hex(b)
    return _hexs(tuple(ca[i] + (cb[i] - ca[i]) * t for i in range(3)))


def _luminance(rgb):
    def chan(c):
        c = c / 255
        return c / 12.92 if c <= 0.03928 else ((c + 0.055) / 1.055) ** 2.4
    r, g, b = (chan(x) for x in rgb)
    return 0.2126 * r + 0.7152 * g + 0.0722 * b


def _is_gradient(v):
    return isinstance(v, str) and ("gradient(" in v or " " in v.strip() and v.strip().startswith("linear"))


def _solid_bg(palette):
    """For contrast, approximate a gradient bg by its first color stop."""
    bg = palette.get("bg", "#ffffff")
    if "gradient(" in bg:
        m = re.search(r"#[0-9a-fA-F]{3,6}", bg)
        return m.group(0) if m else "#888888"
    return bg


def contrast_ratio(a, b):
    la, lb = _luminance(_hex(a)), _luminance(_hex(b))
    hi, lo = max(la, lb), min(la, lb)
    return (hi + 0.05) / (lo + 0.05)


def contrast_report(style):
    p = style["palette"]
    bg = _solid_bg(p)
    pairs = {
        "text_on_bg": (p.get("text", "#000"), bg, 4.5),
        "accent_on_bg": (p.get("accent", "#000"), bg, 3.0),
        "muted_on_bg": (p.get("muted", "#666"), bg, 4.5),
        "bg_on_accent": (bg, p.get("accent", "#000"), 4.5),
    }
    rows = []
    for name, (fg, b, req) in pairs.items():
        try:
            ratio = round(contrast_ratio(fg, b), 2)
        except Exception:
            ratio = None
            rows.append({"pair": name, "ratio": None, "note": "non-solid color, skipped"})
            continue
        rows.append({
            "pair": name, "fg": fg, "bg": b, "ratio": ratio,
            "aa_normal": ratio >= 4.5, "aa_large": ratio >= 3.0, "aaa_normal": ratio >= 7.0,
            "required": req, "pass": ratio >= req,
        })
    return rows


def print_contrast_warnings(style):
    rows = contrast_report(style)
    warned = False
    for r in rows:
        if r.get("ratio") is None:
            continue
        if not r.get("pass", True):
            warned = True
            print(f"WARN: contrast {r['pair']} = {r['ratio']}:1 (need {r['required']}:1) "
                  f"[{r.get('fg')} on {r.get('bg')}] — fails WCAG AA.", file=sys.stderr)
    if not warned:
        print("contrast: all key text/accent pairs pass WCAG AA.", file=sys.stderr)
    return rows


# ---------------------------------------------------------------------------
# Token binding / template composition
# ---------------------------------------------------------------------------
def google_font_links(style):
    fams = set()
    typ = style.get("typography", {})
    for k in ("heading_font", "body_font"):
        f = typ.get(k)
        if f:
            fams.add(f)
    if not fams:
        return ""
    parts = "&".join("family=" + f.replace(" ", "+") + ":wght@400;500;700;800" for f in sorted(fams))
    return ('<link rel="preconnect" href="https://fonts.googleapis.com">\n'
            '<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>\n'
            f'<link href="https://fonts.googleapis.com/css2?{parts}&display=swap" rel="stylesheet">')


def style_vars_block(style, canvas):
    p = style["palette"]
    typ = style.get("typography", {})
    heading_stack = typ.get("_heading_stack") or typ.get("font_stack", "sans-serif")
    body_stack = typ.get("font_stack", "sans-serif")
    grad = p.get("gradient") or ("none" if "gradient(" not in p.get("bg", "") else p["bg"])
    lines = [
        ":root {",
        f"  --canvas-w: {canvas['w']}px;",
        f"  --canvas-h: {canvas['h']}px;",
        f"  --bg: {p.get('bg', '#ffffff')};",
        f"  --surface: {p.get('surface', '#f6f7f9')};",
        f"  --primary: {p.get('primary', p.get('text', '#111'))};",
        f"  --accent: {p.get('accent', '#2563eb')};",
        f"  --text: {p.get('text', '#111')};",
        f"  --muted: {p.get('muted', '#6b7280')};",
        f"  --gradient: {grad};",
        f"  --font-heading: {heading_stack};",
        f"  --font-body: {body_stack};",
        f"  --scale: {typ.get('scale_ratio', 1.25)};",
        f"  --radius: {style.get('radius', '16px')};",
        f"  --shadow: {style.get('shadow', 'none')};",
        f"  --space: {style.get('spacing_unit', '8px')};",
        "}",
    ]
    return "\n".join(lines)


def compose_html(style, fmt_name, canvas, content_fragment):
    tpl_path = os.path.join(TEMPLATES, f"{fmt_name}.html")
    if not os.path.exists(tpl_path):
        sys.exit(f"ERROR: no template for format '{fmt_name}' at {tpl_path}")
    with open(tpl_path, encoding="utf-8") as f:
        tpl = f.read()
    with open(os.path.join(TEMPLATES, "_base.css"), encoding="utf-8") as f:
        base_css = f.read()
    html = (tpl
            .replace("__FONT_LINKS__", google_font_links(style))
            .replace("__BASE_CSS__", base_css)
            .replace("__STYLE_VARS__", style_vars_block(style, canvas))
            .replace("__CONTENT__", content_fragment))
    return html


def preview_fragment(style, fmt_name, canvas):
    """A deterministic style-preview slide (no agent content needed)."""
    p = style["palette"]
    name = style.get("name", style.get("id", "Style"))
    swatches = "".join(
        f'<div style="width:120px;height:120px;border-radius:var(--radius);'
        f'background:{p[k]};box-shadow:var(--shadow)"></div>'
        for k in ("bg", "surface", "accent", "text", "muted") if k in p)
    return f"""<div class="slide" style="justify-content:center">
  <div class="pad">
    <div class="kicker">STYLE PREVIEW</div>
    <h1 style="margin:16px 0">{name}</h1>
    <p class="muted" style="max-width:640px">{style.get('aesthetic','')} · {', '.join(style.get('mood_tags', []))}</p>
    <div style="display:flex;gap:16px;margin:32px 0">{swatches}</div>
    <span class="pill">Accent / CTA</span>
    <p style="margin-top:24px">The quick brown fox jumps over the lazy dog — 0123456789.</p>
    <h3 style="margin-top:16px">Heading typeface sample</h3>
    <div class="page-no">preview</div>
  </div>
</div>"""


# ---------------------------------------------------------------------------
# Subcommands
# ---------------------------------------------------------------------------
def cmd_plan(args):
    style = resolve_style(args)
    formats = load_formats()
    if args.format not in formats:
        sys.exit(f"ERROR: unknown format '{args.format}'. Available: " + ", ".join(formats))
    fmt = formats[args.format]
    canvas = fmt["canvas"]
    plan = {
        "format": args.format,
        "canvas": canvas,
        "multi_slide": fmt.get("multi_slide", False),
        "density_rules": fmt.get("density_rules"),
        "content_schema": fmt.get("content_schema"),
        "slides": fmt.get("slides"),
        "style": {"id": style.get("id"), "name": style.get("name"),
                  "palette": style["palette"], "typography": style.get("typography"),
                  "motifs": style.get("motifs")},
        "font_links": google_font_links(style),
        "style_vars_css": style_vars_block(style, canvas),
        "contrast": contrast_report(style),
        "instructions": (
            "Author an HTML content fragment for each slide using the template's .slide root. "
            "graphics.py compose injects --STYLE_VARS--/--BASE_CSS--/--FONT_LINKS-- around it. "
            "Honor density_rules and content_schema; reference any sourced images by relative path."
        ),
    }
    print(json.dumps(plan, ensure_ascii=False, indent=2))
    print_contrast_warnings(style)


def cmd_compose(args):
    style = resolve_style(args)
    formats = load_formats()
    if args.format not in formats:
        sys.exit(f"ERROR: unknown format '{args.format}'.")
    canvas = formats[args.format]["canvas"]
    with open(args.content, encoding="utf-8") as f:
        fragment = f.read()
    html = compose_html(style, args.format, canvas, fragment)
    if args.out == "-":
        sys.stdout.write(html)
    else:
        os.makedirs(os.path.dirname(os.path.abspath(args.out)) or ".", exist_ok=True)
        with open(args.out, "w", encoding="utf-8") as f:
            f.write(html)
        print(f"composed {args.format} ({canvas['w']}x{canvas['h']}) -> {args.out}", file=sys.stderr)
    print_contrast_warnings(style)


def cmd_preview(args):
    style = resolve_style(args)
    formats = load_formats()
    fmt = formats.get(args.format)
    if not fmt:
        sys.exit(f"ERROR: unknown format '{args.format}'.")
    canvas = fmt["canvas"]
    html = compose_html(style, args.format, canvas, preview_fragment(style, args.format, canvas))
    html_path = args.html_out or os.path.join(args.out_dir or ".", "preview.html")
    os.makedirs(os.path.dirname(os.path.abspath(html_path)) or ".", exist_ok=True)
    with open(html_path, "w", encoding="utf-8") as f:
        f.write(html)
    print(f"preview HTML -> {html_path}", file=sys.stderr)
    print_contrast_warnings(style)
    if not args.no_render:
        png = (args.png_out or os.path.splitext(html_path)[0] + ".png")
        rc = run_render(["--html", html_path, "--out", png, "--format", args.format])
        if rc == 0:
            print(f"preview PNG -> {png}", file=sys.stderr)
        else:
            print("preview render skipped/failed (is Playwright installed?).", file=sys.stderr)


def cmd_render(args):
    # If --content/--dir-content given, compose first; else render existing HTML.
    extra = []
    if args.dir:
        extra = ["--dir", args.dir, "--out-dir", args.out_dir or "out"]
    elif args.html:
        extra = ["--html", args.html, "--out", args.out or "out.png"]
    else:
        sys.exit("ERROR: render needs --html <file> or --dir <slides-dir>.")
    extra += ["--format", args.format]
    if args.pdf:
        extra += ["--pdf", args.pdf]
    if args.wait:
        extra += ["--wait", str(args.wait)]
    sys.exit(run_render(extra))


def cmd_contrast(args):
    style = resolve_style(args)
    rows = contrast_report(style)
    print(json.dumps({"style": style.get("id"), "contrast": rows}, indent=2))
    print_contrast_warnings(style)


def run_render(extra_args):
    cmd = ["node", os.path.join(HERE, "render.mjs")] + extra_args
    try:
        return subprocess.call(cmd)
    except FileNotFoundError:
        print("ERROR: node not found; cannot render.", file=sys.stderr)
        return 1


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------
def add_style_args(sp):
    sp.add_argument("--style", help="catalog style id (see styles.json)")
    sp.add_argument("--ref", help="reference image -> ad-hoc extracted style")
    sp.add_argument("--brand", help="brand mode: comma hex colors, first=bg, second=accent")
    sp.add_argument("--brand-heading", help="brand mode heading font family")
    sp.add_argument("--brand-body", help="brand mode body font family")
    sp.add_argument("--theme", choices=["auto", "light", "dark"], default="auto",
                    help="brand-mode theme hint (default auto from bg luminance)")


def main():
    ap = argparse.ArgumentParser(description="graphics-studio driver (style/format/imagery/render orchestration).")
    sub = ap.add_subparsers(dest="cmd", required=True)

    p = sub.add_parser("plan", help="emit a render-plan + content scaffold for the agent")
    p.add_argument("--format", required=True)
    add_style_args(p)
    p.set_defaults(func=cmd_plan)

    p = sub.add_parser("compose", help="fill a template with style tokens + agent content -> HTML")
    p.add_argument("--format", required=True)
    p.add_argument("--content", required=True, help="agent-authored HTML content fragment file")
    p.add_argument("--out", default="-", help="output HTML path (default stdout)")
    add_style_args(p)
    p.set_defaults(func=cmd_compose)

    p = sub.add_parser("preview", help="compose+render ONE style-preview slide")
    p.add_argument("--format", default="carousel")
    p.add_argument("--out-dir", help="dir for preview.html/.png")
    p.add_argument("--html-out", help="explicit preview HTML path")
    p.add_argument("--png-out", help="explicit preview PNG path")
    p.add_argument("--no-render", action="store_true", help="write HTML only, skip Playwright")
    add_style_args(p)
    p.set_defaults(func=cmd_preview)

    p = sub.add_parser("render", help="invoke render.mjs for a file or a directory of slides")
    p.add_argument("--format", required=True)
    p.add_argument("--html", help="single composed HTML file")
    p.add_argument("--out", help="single output PNG path")
    p.add_argument("--dir", help="directory of per-slide composed HTML files")
    p.add_argument("--out-dir", help="output dir for multi-slide PNGs")
    p.add_argument("--pdf", help="also emit a combined PDF")
    p.add_argument("--wait", type=int, help="extra settle ms")
    p.set_defaults(func=cmd_render)

    p = sub.add_parser("contrast", help="WCAG contrast report for a resolved style")
    add_style_args(p)
    p.set_defaults(func=cmd_contrast)

    args = ap.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()
