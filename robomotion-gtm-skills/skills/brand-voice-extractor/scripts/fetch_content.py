#!/usr/bin/env python3
"""fetch_content.py — Fetch a list of pages, strip chrome, and emit a clean text corpus
plus deterministic style metrics for brand-voice analysis.

Pattern B: this is a deterministic tool only. It does NO voice synthesis — the host
agent reads the emitted corpus + metrics and writes the Brand Voice Profile.

Keyless. Stdlib only (urllib + html.parser) so it runs on the base image with no pip
install. For JS-rendered/auth-walled blogs, use fetch_content_js.mjs instead (Playwright).

Outputs JSON: {company, pages:[{url,title,word_count,text,metrics{...}}], corpus_metrics{...}}

Example:
  fetch_content.py --company "Acme" --urls https://acme.com/blog/a https://acme.com/blog/b \
      --num-pages 15 --output corpus.json
"""
import argparse
import json
import re
import sys
import time
import urllib.error
import urllib.request
from html.parser import HTMLParser

UA = "robomotion-gtm-skills/brand-voice-extractor (+https://agentskills.io)"
# Tags whose text content is chrome, not body copy.
SKIP_TAGS = {"script", "style", "nav", "footer", "header", "aside", "form",
             "noscript", "svg", "button", "select", "option", "iframe"}
BLOCK_TAGS = {"p", "div", "section", "article", "li", "br", "h1", "h2", "h3",
              "h4", "h5", "h6", "tr", "blockquote"}


class Extractor(HTMLParser):
    """Pulls visible body text + counts structural elements (headers/lists/emphasis)."""

    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.parts = []
        self.skip_depth = 0
        self.title = ""
        self._in_title = False
        self.counts = {"h": 0, "li": 0, "ul_ol": 0, "strong_em": 0,
                       "blockquote": 0, "a": 0, "img": 0}

    def handle_starttag(self, tag, attrs):
        if tag in SKIP_TAGS:
            self.skip_depth += 1
        if tag == "title":
            self._in_title = True
        if self.skip_depth:
            return
        if tag in ("h1", "h2", "h3", "h4", "h5", "h6"):
            self.counts["h"] += 1
        elif tag == "li":
            self.counts["li"] += 1
        elif tag in ("ul", "ol"):
            self.counts["ul_ol"] += 1
        elif tag in ("strong", "b", "em", "i"):
            self.counts["strong_em"] += 1
        elif tag == "blockquote":
            self.counts["blockquote"] += 1
        elif tag == "a":
            self.counts["a"] += 1
        elif tag == "img":
            self.counts["img"] += 1
        if tag in BLOCK_TAGS:
            self.parts.append("\n")

    def handle_endtag(self, tag):
        if tag in SKIP_TAGS and self.skip_depth:
            self.skip_depth -= 1
        if tag == "title":
            self._in_title = False
        if tag in BLOCK_TAGS:
            self.parts.append("\n")

    def handle_data(self, data):
        if self._in_title:
            self.title += data
        if self.skip_depth:
            return
        if data.strip():
            self.parts.append(data)

    def text(self):
        raw = "".join(self.parts)
        # collapse whitespace within lines, keep paragraph breaks
        lines = [re.sub(r"[ \t]+", " ", ln).strip() for ln in raw.split("\n")]
        lines = [ln for ln in lines if ln]
        return "\n".join(lines)


SENT_SPLIT = re.compile(r"[.!?]+(?:\s+|$)")
WORD_RE = re.compile(r"[A-Za-z][A-Za-z'\-]*")
VOWEL_GROUPS = re.compile(r"[aeiouy]+", re.I)


def count_syllables(word):
    w = word.lower().strip("'-")
    if not w:
        return 0
    groups = VOWEL_GROUPS.findall(w)
    syl = len(groups)
    if w.endswith("e") and syl > 1 and not w.endswith("le"):
        syl -= 1
    return max(1, syl)


def text_metrics(text):
    """Deterministic readability + structure metrics (no judgement, just numbers)."""
    words = WORD_RE.findall(text)
    sentences = [s for s in SENT_SPLIT.split(text) if s.strip()]
    paragraphs = [p for p in text.split("\n") if p.strip()]
    n_words = len(words)
    n_sent = max(1, len(sentences))
    n_syl = sum(count_syllables(w) for w in words)
    # Flesch Reading Ease + Flesch-Kincaid Grade
    if n_words:
        fre = 206.835 - 1.015 * (n_words / n_sent) - 84.6 * (n_syl / n_words)
        fkg = 0.39 * (n_words / n_sent) + 11.8 * (n_syl / n_words) - 15.59
    else:
        fre = fkg = 0.0
    # POV pronoun usage
    low = text.lower()
    pov = {
        "first_person_plural": len(re.findall(r"\b(we|our|us|ours)\b", low)),
        "first_person_singular": len(re.findall(r"\b(i|my|me|mine)\b", low)),
        "second_person": len(re.findall(r"\b(you|your|yours)\b", low)),
    }
    sent_lengths = [len(WORD_RE.findall(s)) for s in sentences] or [0]
    para_lengths = [len(WORD_RE.findall(p)) for p in paragraphs] or [0]
    questions = text.count("?")
    exclamations = text.count("!")
    return {
        "word_count": n_words,
        "sentence_count": len(sentences),
        "paragraph_count": len(paragraphs),
        "avg_sentence_len_words": round(n_words / n_sent, 1),
        "max_sentence_len_words": max(sent_lengths),
        "min_sentence_len_words": min(sent_lengths),
        "avg_paragraph_len_words": round(sum(para_lengths) / max(1, len(para_lengths)), 1),
        "flesch_reading_ease": round(fre, 1),
        "flesch_kincaid_grade": round(fkg, 1),
        "pov": pov,
        "question_marks": questions,
        "exclamation_marks": exclamations,
    }


def fetch(url, timeout):
    req = urllib.request.Request(url, headers={"User-Agent": UA})
    for attempt in range(4):
        try:
            with urllib.request.urlopen(req, timeout=timeout) as r:
                charset = r.headers.get_content_charset() or "utf-8"
                return r.read().decode(charset, "replace")
        except urllib.error.HTTPError as e:
            if e.code in (429, 503) and attempt < 3:
                time.sleep(2 ** attempt)
                continue
            raise
        except urllib.error.URLError:
            if attempt < 3:
                time.sleep(2 ** attempt)
                continue
            raise
    raise RuntimeError("exhausted retries")


def merge_metrics(page_metrics):
    """Roll per-page metrics up to a corpus-level summary the agent scores from."""
    if not page_metrics:
        return {}
    keys = ["avg_sentence_len_words", "avg_paragraph_len_words",
            "flesch_reading_ease", "flesch_kincaid_grade"]
    out = {}
    for k in keys:
        vals = [m[k] for m in page_metrics]
        out[k + "_mean"] = round(sum(vals) / len(vals), 1)
        out[k + "_min"] = min(vals)
        out[k + "_max"] = max(vals)
    pov_tot = {"first_person_plural": 0, "first_person_singular": 0, "second_person": 0}
    for m in page_metrics:
        for k in pov_tot:
            pov_tot[k] += m["pov"][k]
    out["pov_totals"] = pov_tot
    out["total_words"] = sum(m["word_count"] for m in page_metrics)
    return out


def main():
    ap = argparse.ArgumentParser(
        description="Fetch pages, strip chrome, emit clean corpus + style metrics "
                    "for brand-voice analysis (deterministic; agent does synthesis).")
    ap.add_argument("--company", required=True, help="company name (for labeling)")
    ap.add_argument("--urls", nargs="+", required=True, help="page URLs to analyze")
    ap.add_argument("--num-pages", type=int, default=15,
                    help="cap on pages to fetch (default 15; sweet spot 10-20)")
    ap.add_argument("--min-words", type=int, default=80,
                    help="drop pages with fewer body words than this (default 80)")
    ap.add_argument("--timeout", type=int, default=30, help="per-request timeout seconds")
    ap.add_argument("--output", default="-", help="output JSON path (default stdout)")
    args = ap.parse_args()

    # dedup while preserving order, cap at num-pages
    seen, urls = set(), []
    for u in args.urls:
        u = u.strip()
        if u and u not in seen:
            seen.add(u)
            urls.append(u)
    urls = urls[: args.num_pages]

    pages, errors = [], []
    for u in urls:
        try:
            html = fetch(u, args.timeout)
        except Exception as e:  # noqa: BLE001 - report, keep going
            errors.append({"url": u, "error": str(e)})
            continue
        ex = Extractor()
        try:
            ex.feed(html)
        except Exception as e:  # noqa: BLE001
            errors.append({"url": u, "error": f"parse: {e}"})
            continue
        text = ex.text()
        m = text_metrics(text)
        if m["word_count"] < args.min_words:
            errors.append({"url": u, "error": f"thin content ({m['word_count']} words) "
                                              f"- likely JS-rendered; try fetch_content_js.mjs"})
            continue
        m.update(ex.counts)
        pages.append({
            "url": u,
            "title": ex.title.strip(),
            "word_count": m["word_count"],
            "text": text,
            "metrics": m,
        })
        time.sleep(0.3)  # be polite to one domain

    out = {
        "company": args.company,
        "pages_requested": len(urls),
        "pages_fetched": len(pages),
        "corpus_metrics": merge_metrics([p["metrics"] for p in pages]),
        "pages": pages,
        "errors": errors,
    }
    payload = json.dumps(out, ensure_ascii=False, indent=2)
    if args.output == "-":
        print(payload)
    else:
        with open(args.output, "w", encoding="utf-8") as f:
            f.write(payload + "\n")
        print(f"{len(pages)}/{len(urls)} pages -> {args.output} "
              f"({len(errors)} errors)", file=sys.stderr)


if __name__ == "__main__":
    main()
