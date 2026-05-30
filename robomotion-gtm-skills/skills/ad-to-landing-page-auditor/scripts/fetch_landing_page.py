#!/usr/bin/env python3
"""fetch_landing_page.py — Fetch a landing-page URL and extract its structure.

Keyless, stdlib only (urllib + html.parser). Mirrors robomotion-serp Extract Content:
returns {headers, paragraphs, lists, links, images} plus content stats and a best-guess
hero / primary-CTA / form-field-count read that feeds message-match and friction scoring.

Deterministic: it parses HTML only — no LLM. The host agent does message-match and
friction scoring (see ../SKILL.md). For JS-rendered / gated LPs the agent should escalate
to a Playwright fetch; this handles static + server-rendered pages.

Examples:
  fetch_landing_page.py --url https://example.com/pricing
  fetch_landing_page.py --urls urls.txt --output lps.json
"""
import argparse
import json
import re
import sys
import urllib.error
import urllib.request
from html.parser import HTMLParser

UA = "Mozilla/5.0 (compatible; robomotion-gtm-skills/ad-lp-auditor; +https://agentskills.io)"

CTA_WORDS = re.compile(
    r"\b(get started|start (free|trial)|sign up|book (a )?demo|request (a )?demo|"
    r"try (it )?free|buy now|add to cart|subscribe|download|learn more|contact (sales|us)|"
    r"get (a )?quote|join|register|see pricing|talk to)\b",
    re.I,
)


class Extractor(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.headers = []          # [{level, text}]
        self.paragraphs = []
        self.lists = []            # list of item-lists
        self.links = []            # [{text, href}]
        self.images = []           # [src]
        self._cur = None           # current capturing tag context
        self._buf = []
        self._cur_list = None
        self._href = ""
        self._link_text = []
        self.title = ""
        self._in_title = False
        # form fields
        self.input_count = 0
        self.form_count = 0
        self.button_texts = []
        self._in_button = False
        self._btn_buf = []
        self.video = False
        self._capturing_link = False

    def handle_starttag(self, tag, attrs):
        ad = dict(attrs)
        if tag in ("h1", "h2", "h3", "h4"):
            self._cur = tag
            self._buf = []
        elif tag == "p":
            self._cur = "p"
            self._buf = []
        elif tag in ("ul", "ol"):
            self._cur_list = []
        elif tag == "li" and self._cur_list is not None:
            self._cur = "li"
            self._buf = []
        elif tag == "a":
            self._href = ad.get("href", "")
            self._link_text = []
            self._capturing_link = True
        elif tag == "img":
            src = ad.get("src") or ad.get("data-src") or ""
            if src:
                self.images.append(src)
        elif tag == "title":
            self._in_title = True
        elif tag in ("input", "select", "textarea"):
            t = (ad.get("type") or "").lower()
            if t not in ("hidden", "submit", "button"):
                self.input_count += 1
        elif tag == "form":
            self.form_count += 1
        elif tag in ("button",):
            self._in_button = True
            self._btn_buf = []
        elif tag in ("video",):
            self.video = True

    def handle_endtag(self, tag):
        text = "".join(self._buf).strip()
        if tag in ("h1", "h2", "h3", "h4") and self._cur == tag:
            if text:
                self.headers.append({"level": int(tag[1]), "text": text})
            self._cur = None
        elif tag == "p" and self._cur == "p":
            if text:
                self.paragraphs.append(text)
            self._cur = None
        elif tag == "li" and self._cur == "li":
            if text and self._cur_list is not None:
                self._cur_list.append(text)
            self._cur = None
        elif tag in ("ul", "ol"):
            if self._cur_list:
                self.lists.append(self._cur_list)
            self._cur_list = None
        elif tag == "a":
            lt = "".join(self._link_text).strip()
            if self._href and lt:
                self.links.append({"text": lt, "href": self._href})
            self._href = ""
            self._link_text = []
            self._capturing_link = False
        elif tag == "title":
            self._in_title = False
        elif tag == "button":
            bt = "".join(self._btn_buf).strip()
            if bt:
                self.button_texts.append(bt)
            self._in_button = False

    def handle_data(self, data):
        if self._cur:
            self._buf.append(data)
        if getattr(self, "_capturing_link", False):
            self._link_text.append(data)
        if self._in_title:
            self.title += data
        if self._in_button:
            self._btn_buf.append(data)


def fetch(url, timeout=30):
    req = urllib.request.Request(url, headers={"User-Agent": UA, "Accept": "text/html"})
    with urllib.request.urlopen(req, timeout=timeout) as r:
        ctype = r.headers.get("Content-Type", "")
        charset = "utf-8"
        m = re.search(r"charset=([\w-]+)", ctype)
        if m:
            charset = m.group(1)
        return r.read().decode(charset, "replace"), r.status


def analyze(url, timeout):
    try:
        html, status = fetch(url, timeout)
    except urllib.error.HTTPError as e:
        return {"url": url, "ok": False, "status": e.code, "error": f"HTTP {e.code}"}
    except Exception as e:
        return {"url": url, "ok": False, "status": 0, "error": str(e)}

    p = Extractor()
    try:
        p.feed(html)
    except Exception:
        pass

    hero = p.headers[0]["text"] if p.headers else ""
    subhead = ""
    for h in p.headers[1:]:
        if h["level"] in (2, 3):
            subhead = h["text"]
            break
    # primary CTA: first link/button text matching CTA vocabulary
    cta_candidates = [l["text"] for l in p.links] + p.button_texts
    primary_cta = next((c for c in cta_candidates if CTA_WORDS.search(c)), "")
    above_fold_cta = bool(primary_cta)

    # crude trust/proof signals
    blob = " ".join(p.paragraphs + [h["text"] for h in p.headers]).lower()
    proof_signals = {
        "testimonial": bool(re.search(r"testimonial|customers love|trusted by|rated|reviews?", blob)),
        "logos": sum(1 for s in p.images if re.search(r"logo|customer|brand", s, re.I)),
        "numbers_claim": bool(re.search(r"\b\d[\d,]*\+?\s*(customers|users|companies|teams)\b", blob)),
    }

    return {
        "url": url,
        "ok": True,
        "status": status,
        "title": p.title.strip(),
        "hero_headline": hero,
        "subhead": subhead,
        "primary_cta": primary_cta,
        "above_fold_cta": above_fold_cta,
        "headers": p.headers,
        "paragraphs": p.paragraphs[:60],
        "benefit_lists": p.lists[:10],
        "link_count": len(p.links),
        "nav_link_count": sum(1 for l in p.links if l["href"].startswith(("/", "#")) or "nav" in l["text"].lower()),
        "image_count": len(p.images),
        "form_count": p.form_count,
        "form_field_count": p.input_count,
        "button_texts": p.button_texts[:20],
        "has_video": p.video,
        "proof_signals": proof_signals,
        "word_count": len(blob.split()),
    }


def main():
    ap = argparse.ArgumentParser(description="Fetch landing pages and extract structure (keyless).")
    g = ap.add_mutually_exclusive_group(required=True)
    g.add_argument("--url", help="single landing-page URL")
    g.add_argument("--urls", help="file with one URL per line")
    ap.add_argument("--timeout", type=int, default=30, help="per-request timeout seconds")
    ap.add_argument("--output", default="-", help="output JSON path (default stdout)")
    args = ap.parse_args()

    urls = []
    if args.url:
        urls = [args.url]
    else:
        with open(args.urls, encoding="utf-8") as f:
            urls = [ln.strip() for ln in f if ln.strip() and not ln.startswith("#")]

    results = [analyze(u, args.timeout) for u in urls]
    payload = json.dumps(results if len(results) > 1 else results[0], ensure_ascii=False, indent=2)
    if args.output == "-":
        print(payload)
    else:
        with open(args.output, "w", encoding="utf-8") as f:
            f.write(payload + "\n")
        print(f"{len(results)} page(s) -> {args.output}", file=sys.stderr)


if __name__ == "__main__":
    main()
