#!/usr/bin/env python3
"""fetch_competitors.py — Fetch each competitor's key marketing pages (homepage, pricing,
about + common variants) and extract positioning signals: page <title>, meta description,
the hero headline/subhead, prominent CTAs, and candidate "category / positioning" phrases
("we help", "the only", "the #1", "platform for ...").

Pattern B / composite glue: deterministic extraction only. The host agent reads the
emitted corpus and builds the positioning framework (April Dunford) — category decision,
competitive alternatives, value-prop mapping, messaging hierarchy.

Keyless, stdlib only. For JS-rendered marketing sites that come back thin, escalate to
fetch_competitors_js.mjs (Playwright).

Example:
  fetch_competitors.py \
    --competitors "Acme=https://acme.com" "Globex=https://globex.io" \
    --output competitors.json
"""
import argparse
import json
import re
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
from html.parser import HTMLParser

UA = "robomotion-gtm-skills/launch-positioning-builder (+https://agentskills.io)"
PAGE_PATHS = ["", "/pricing", "/about", "/about-us", "/product", "/platform", "/features"]

# Positioning / category language patterns worth surfacing verbatim to the agent.
POS_PATTERNS = [
    re.compile(r"\bthe only\b[^.!?\n]{0,120}", re.I),
    re.compile(r"\bthe #?1\b[^.!?\n]{0,120}", re.I),
    re.compile(r"\bwe help\b[^.!?\n]{0,120}", re.I),
    re.compile(r"\b(?:the )?(?:leading|best|fastest|easiest|most [a-z]+)\b[^.!?\n]{0,120}", re.I),
    re.compile(r"\bplatform (?:for|to)\b[^.!?\n]{0,120}", re.I),
    re.compile(r"\b(?:all-in-one|end-to-end|purpose-built|built for)\b[^.!?\n]{0,120}", re.I),
]
SKIP_TAGS = {"script", "style", "nav", "footer", "noscript", "svg", "iframe"}


class HeroParser(HTMLParser):
    """Capture title, meta description, first H1/H2 (hero headline/subhead), and CTA-ish
    button/link text near the top of the page."""

    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.title = ""
        self.meta_description = ""
        self.h1 = ""
        self.h2 = ""
        self.ctas = []
        self.text_parts = []
        self._cur = None
        self._skip = 0
        self._a_text = ""
        self._in_a = False

    def handle_starttag(self, tag, attrs):
        ad = dict(attrs)
        if tag == "meta" and ad.get("name", "").lower() == "description":
            self.meta_description = ad.get("content", "") or self.meta_description
        if tag == "meta" and ad.get("property", "").lower() == "og:description" and not self.meta_description:
            self.meta_description = ad.get("content", "")
        if tag in SKIP_TAGS:
            self._skip += 1
        if self._skip:
            return
        if tag == "title":
            self._cur = "title"
        elif tag == "h1" and not self.h1:
            self._cur = "h1"
        elif tag == "h2" and not self.h2:
            self._cur = "h2"
        elif tag == "a" or tag == "button":
            cls = (ad.get("class", "") or "").lower()
            if tag == "button" or "btn" in cls or "button" in cls or "cta" in cls:
                self._in_a = True
                self._a_text = ""

    def handle_endtag(self, tag):
        if tag in SKIP_TAGS and self._skip:
            self._skip -= 1
        if tag in ("title", "h1", "h2"):
            self._cur = None
        if tag in ("a", "button") and self._in_a:
            t = self._a_text.strip()
            if 2 <= len(t) <= 40 and t not in self.ctas:
                self.ctas.append(t)
            self._in_a = False

    def handle_data(self, data):
        if self._skip:
            return
        if self._cur == "title":
            self.title += data
        elif self._cur == "h1":
            self.h1 += data
        elif self._cur == "h2":
            self.h2 += data
        if self._in_a:
            self._a_text += data
        if data.strip():
            self.text_parts.append(data.strip())

    def body_text(self):
        return re.sub(r"\s+", " ", " ".join(self.text_parts))


def fetch(url, timeout=30):
    req = urllib.request.Request(url, headers={"User-Agent": UA})
    for attempt in range(3):
        try:
            with urllib.request.urlopen(req, timeout=timeout) as r:
                charset = r.headers.get_content_charset() or "utf-8"
                return r.read().decode(charset, "replace")
        except urllib.error.HTTPError as e:
            if e.code in (429, 503) and attempt < 2:
                time.sleep(2 ** attempt)
                continue
            raise
        except urllib.error.URLError:
            if attempt < 2:
                time.sleep(2 ** attempt)
                continue
            raise
    raise RuntimeError("exhausted retries")


def positioning_phrases(text):
    raw = []
    for rx in POS_PATTERNS:
        for m in rx.findall(text):
            phrase = re.sub(r"\s+", " ", m).strip()
            # trim a dangling partial word from the 120-char cap so phrases read cleanly
            if len(phrase) >= 118 and " " in phrase:
                phrase = phrase.rsplit(" ", 1)[0].rstrip(",;:- ")
            if phrase:
                raw.append(phrase)
    # dedup, and drop any phrase that is a substring of a longer captured phrase
    raw = sorted(set(raw), key=len, reverse=True)
    found = []
    for p in raw:
        pl = p.lower()
        if not any(pl != q.lower() and pl in q.lower() for q in found):
            found.append(p)
    return found[:15]


def extract_page(url, timeout):
    html = fetch(url, timeout)
    p = HeroParser()
    p.feed(html)
    body = p.body_text()
    return {
        "url": url,
        "title": p.title.strip(),
        "meta_description": p.meta_description.strip(),
        "hero_headline": p.h1.strip(),
        "hero_subhead": p.h2.strip(),
        "ctas": p.ctas[:8],
        "positioning_phrases": positioning_phrases(body),
        "body_word_count": len(re.findall(r"[A-Za-z][A-Za-z'\-]*", body)),
    }


def parse_competitor(spec):
    if "=" in spec:
        name, url = spec.split("=", 1)
        return name.strip(), url.strip()
    return urllib.parse.urlsplit(spec).netloc or spec, spec.strip()


def main():
    ap = argparse.ArgumentParser(
        description="Fetch competitor marketing pages + extract positioning signals "
                    "(deterministic; agent builds the framework).")
    ap.add_argument("--competitors", nargs="+", required=True,
                    help='one or more "Name=https://url" (or bare URLs)')
    ap.add_argument("--paths", nargs="*", default=PAGE_PATHS,
                    help="page paths to try per competitor (default: home/pricing/about/...)")
    ap.add_argument("--timeout", type=int, default=30, help="per-request timeout seconds")
    ap.add_argument("--output", default="-", help="output JSON path (default stdout)")
    args = ap.parse_args()

    competitors = []
    for spec in args.competitors:
        name, base = parse_competitor(spec)
        sp = urllib.parse.urlsplit(base)
        if not sp.scheme:
            base = "https://" + base
            sp = urllib.parse.urlsplit(base)
        origin = f"{sp.scheme}://{sp.netloc}"
        pages, errors = [], []
        tried = set()
        for path in args.paths:
            url = origin + path if path.startswith("/") else (base if path == "" else origin + "/" + path)
            url = url.rstrip("/") if path == "" else url
            if not url:
                url = base
            if url in tried:
                continue
            tried.add(url)
            try:
                pages.append(extract_page(url, args.timeout))
            except Exception as e:  # noqa: BLE001
                errors.append({"url": url, "error": str(e)})
            time.sleep(0.3)
        thin = all(p["body_word_count"] < 50 for p in pages) if pages else True
        competitors.append({
            "name": name,
            "base_url": base,
            "pages": pages,
            "errors": errors,
            "likely_js_rendered": thin,
        })

    out = {"competitors": competitors}
    payload = json.dumps(out, ensure_ascii=False, indent=2)
    if args.output == "-":
        print(payload)
    else:
        with open(args.output, "w", encoding="utf-8") as f:
            f.write(payload + "\n")
        n = sum(len(c["pages"]) for c in competitors)
        print(f"{n} pages across {len(competitors)} competitors -> {args.output}",
              file=sys.stderr)


if __name__ == "__main__":
    main()
