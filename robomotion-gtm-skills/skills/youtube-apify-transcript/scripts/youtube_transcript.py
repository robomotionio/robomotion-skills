#!/usr/bin/env python3
"""youtube_transcript.py — fetch a YouTube transcript (keyless default; Apify optional).

DEFAULT (keyless): hit YouTube's own public transcript endpoints with stdlib urllib —
read the watch page for the caption-track list, then fetch the `timedtext` track and parse
its segments. No key, no cost. This works from most IPs; cloud/datacenter IPs may get
throttled/blocked by YouTube, which is exactly when Apify helps.

OPTIONAL UPGRADE (`APIFY_API_TOKEN` set): the Apify residential-proxy transcript actor is
more reliable from blocked cloud IPs. If `APIFY_API_TOKEN` is set the script uses the Apify
path (cost-gated); if not, it uses the keyless path. Force either with --prefer.

Routing:
  - if APIFY_API_TOKEN set  -> Apify path (cost-gated; --yes / --estimate-only apply)
  - if not set              -> keyless timedtext path (free; --yes/--estimate-only no-op)
  - --prefer keyless        -> always keyless (ignore the token)
  - --prefer apify          -> require the token (error if absent)

Stdlib only (urllib). Deterministic I/O: parse URL -> check cache -> fetch (keyless or
Apify) -> format -> cache. CACHE HITS never spend and never need --yes.

Single:
  youtube_transcript.py --url "https://youtu.be/dQw4w9WgXcQ" --format text          # keyless
  youtube_transcript.py --url "https://youtu.be/dQw4w9WgXcQ" --format text --yes     # Apify if token set
Batch:
  youtube_transcript.py --urls-file urls.txt --format json --cache-dir .cache
"""
import argparse
import json
import os
import re
import sys
import urllib.error
import urllib.parse
import urllib.request

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import apify_common  # noqa: E402  (vendored async run/poll + cost gate)

ACTOR = os.environ.get("APIFY_YT_TRANSCRIPT_ACTOR", "pintostudio~youtube-transcript-scraper")
# Public-actor list price for this transcript actor (~$0.007/video) — used only for the
# --estimate-only projection; the hard gate is the live usage read in apify_common.
PER_VIDEO_USD = 0.007

VID_RE = re.compile(r"(?:v=|/shorts/|/embed/|youtu\.be/|/v/)([A-Za-z0-9_-]{11})")
UA = ("Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
      "(KHTML, like Gecko) Chrome/124.0 Safari/537.36")


def has_token():
    return bool(os.environ.get("APIFY_API_TOKEN", "").strip())


def token():
    t = os.environ.get("APIFY_API_TOKEN", "").strip()
    if not t:
        sys.exit("ERROR: APIFY_API_TOKEN is not set but --prefer apify was requested. "
                 "Unset --prefer (or use --prefer keyless) to use the free timedtext path.")
    return t


# ---------------------------------------------------------------------------
# Keyless path: YouTube's own public timedtext endpoint (no key, no cost).
# ---------------------------------------------------------------------------
def _http_get(url, timeout=30):
    req = urllib.request.Request(url, headers={"User-Agent": UA,
                                               "Accept-Language": "en-US,en;q=0.9"})
    with urllib.request.urlopen(req, timeout=timeout) as r:
        return r.read().decode("utf-8", "ignore")


def _unescape(s):
    import html
    return html.unescape(s or "").strip()


def _attr(tag, name):
    m = re.search(r'\b%s="([\d.]+)"' % name, tag)
    return m.group(1) if m else ""


def _parse_timedtext_xml(xml):
    """Parse a YouTube timedtext XML track into {start,dur,text}.

    Handles the legacy `<text start dur>` format (seconds) and the srv3 `<p t d>`
    format (milliseconds, with `<s>` word children). Attribute order is not assumed.
    """
    segs = []
    # legacy: <text start="s" dur="s">...</text>
    for m in re.finditer(r'<text\b([^>]*)>(.*?)</text>', xml, re.S):
        attrs, body = m.group(1), m.group(2)
        text = _unescape(re.sub(r"<[^>]+>", "", body))
        if text:
            segs.append({"start": _attr(attrs, "start"),
                         "dur": _attr(attrs, "dur"), "text": text})
    if segs:
        return segs
    # srv3: <p t="ms" d="ms"><s>word</s>...</p>
    for m in re.finditer(r'<p\b([^>]*)>(.*?)</p>', xml, re.S):
        attrs, body = m.group(1), m.group(2)
        text = _unescape(re.sub(r"<[^>]+>", "", body))
        if not text:
            continue
        t = _attr(attrs, "t")
        d = _attr(attrs, "d")
        segs.append({
            "start": f"{int(t) / 1000:.3f}" if t.isdigit() else "",
            "dur": f"{int(d) / 1000:.3f}" if d.isdigit() else "",
            "text": text,
        })
    return segs


def _parse_timedtext_json3(raw):
    """Parse the json3 timedtext format into {start,dur,text}."""
    try:
        doc = json.loads(raw)
    except ValueError:
        return []
    segs = []
    for ev in doc.get("events", []) or []:
        segs_text = "".join(s.get("utf8", "") for s in (ev.get("segs") or []))
        text = _unescape(segs_text)
        if not text:
            continue
        start = ev.get("tStartMs")
        dur = ev.get("dDurationMs")
        segs.append({
            "start": f"{start / 1000:.3f}" if isinstance(start, (int, float)) else "",
            "dur": f"{dur / 1000:.3f}" if isinstance(dur, (int, float)) else "",
            "text": text,
        })
    return segs


def _parse_timedtext(raw):
    """Parse whatever timedtext format we got (json3 or XML)."""
    s = (raw or "").lstrip()
    if s.startswith("{"):
        segs = _parse_timedtext_json3(raw)
        if segs:
            return segs
    return _parse_timedtext_xml(raw)


def _caption_tracks(watch_html):
    """Extract the list of caption tracks from the watch page's player response."""
    m = re.search(r'"captionTracks":(\[.*?\])', watch_html)
    if not m:
        return []
    blob = m.group(1)
    # The JSON inside the page is valid JSON for this array; load it directly.
    try:
        # The blob may contain escaped unicode like & — json.loads handles it.
        return json.loads(blob)
    except ValueError:
        return []


def _pick_track(tracks, lang):
    if not tracks:
        return None
    if lang:
        for t in tracks:
            if (t.get("languageCode") or "").lower().startswith(lang.lower()):
                return t
    # prefer a non-ASR (human) English track, else first
    for t in tracks:
        if (t.get("languageCode") or "").lower().startswith("en") and t.get("kind") != "asr":
            return t
    for t in tracks:
        if (t.get("languageCode") or "").lower().startswith("en"):
            return t
    return tracks[0]


def fetch_keyless(vid, lang):
    """Fetch a transcript via YouTube's public timedtext track. Returns segments or []."""
    try:
        html = _http_get(f"https://www.youtube.com/watch?v={vid}&hl=en")
    except (urllib.error.URLError, urllib.error.HTTPError, OSError) as e:
        return [], f"watch-page fetch failed ({e})"
    tracks = _caption_tracks(html)
    if not tracks:
        return [], "no caption tracks found (captions disabled or page blocked from this IP)"
    track = _pick_track(tracks, lang)
    base = (track or {}).get("baseUrl")
    if not base:
        return [], "caption track has no baseUrl"
    base = base.replace("\\u0026", "&")
    base_noemt = re.sub(r"&fmt=[^&]*", "", base)
    last_err = ""
    # Try json3 first (richest), then the default XML track. Some IPs/tracks only
    # answer one format; fall through until one yields parseable segments.
    for suffix in ("&fmt=json3", "", "&fmt=srv3"):
        try:
            raw = _http_get(base_noemt + suffix)
        except (urllib.error.URLError, urllib.error.HTTPError, OSError) as e:
            last_err = f"timedtext fetch failed ({e})"
            continue
        segs = _parse_timedtext(raw)
        if segs:
            return segs, ""
    return [], (last_err or "timedtext returned no parseable segments "
                "(YouTube may be blocking this IP from the caption endpoint)")


def video_id(url):
    m = VID_RE.search(url or "")
    if m:
        return m.group(1)
    # bare 11-char id
    s = (url or "").strip()
    if re.fullmatch(r"[A-Za-z0-9_-]{11}", s):
        return s
    return None


def run_actor(video_url, lang, tok, max_cost_usd, timeout_s):
    body = {"videoUrl": video_url}
    if lang:
        body["language"] = lang
    try:
        return apify_common.run_actor(
            ACTOR, body, max_cost_usd=max_cost_usd, timeout_s=timeout_s, tok=tok)
    except apify_common.CostGateError as e:
        sys.exit(f"ERROR: cost gate: {e}")
    except apify_common.ApifyError as e:
        sys.exit(f"ERROR: Apify: {e}")


def parse_segments(items):
    """The actor returns a list; segments live under a 'data' array of {start,dur,text}.

    Be liberal: accept either a top-level data array or a flat list of segments.
    """
    if not items:
        return []
    first = items[0]
    if isinstance(first, dict) and isinstance(first.get("data"), list):
        raw = first["data"]
    elif isinstance(first, dict) and ("text" in first or "snippet" in first):
        raw = items
    else:
        raw = items[0].get("transcript", []) if isinstance(first, dict) else []
    segs = []
    for s in raw:
        if not isinstance(s, dict):
            continue
        segs.append({
            "start": s.get("start") or s.get("offset") or s.get("startTime") or "",
            "dur": s.get("dur") or s.get("duration") or "",
            "text": (s.get("text") or s.get("snippet") or "").strip(),
        })
    return [s for s in segs if s["text"]]


def cache_path(cache_dir, vid):
    return os.path.join(cache_dir, f"{vid}.json")


def load_cache(cache_dir, vid):
    p = cache_path(cache_dir, vid)
    if os.path.exists(p):
        try:
            with open(p, encoding="utf-8") as f:
                return json.load(f)
        except (OSError, ValueError):
            return None
    return None


def save_cache(cache_dir, vid, payload):
    os.makedirs(cache_dir, exist_ok=True)
    with open(cache_path(cache_dir, vid), "w", encoding="utf-8") as f:
        json.dump(payload, f, ensure_ascii=False, indent=2)


def fetch_one(url, lang, use_cache, cache_dir, use_apify, tok, max_cost_usd, timeout_s):
    vid = video_id(url)
    if not vid:
        return {"video_url": url, "error": "could not parse a YouTube video id from URL"}
    if use_cache and cache_dir:
        cached = load_cache(cache_dir, vid)
        if cached:
            cached["from_cache"] = True
            return cached

    title = ""
    if use_apify:
        items = run_actor(f"https://www.youtube.com/watch?v={vid}", lang, tok,
                          max_cost_usd, timeout_s)
        segments = parse_segments(items)
        if items and isinstance(items[0], dict):
            title = items[0].get("title") or items[0].get("videoTitle") or ""
        if not segments:
            return {"video_id": vid, "video_url": url, "source": "apify",
                    "error": "no transcript returned (video may have captions disabled)"}
        source = "apify"
    else:
        segments, err = fetch_keyless(vid, lang)
        if not segments:
            hint = ("" if has_token() else
                    " (set APIFY_API_TOKEN for the residential-proxy fallback if your IP "
                    "is blocked)")
            return {"video_id": vid, "video_url": url, "source": "keyless",
                    "error": f"keyless transcript fetch failed: {err}{hint}"}
        source = "keyless"

    full_text = " ".join(s["text"] for s in segments)
    payload = {
        "video_id": vid,
        "video_url": url,
        "title": title,
        "source": source,
        "transcript": segments,
        "full_text": full_text,
        "from_cache": False,
    }
    if cache_dir:
        save_cache(cache_dir, vid, payload)
    return payload


def render(payload, fmt):
    if "error" in payload:
        return f"# {payload.get('video_url')}\nERROR: {payload['error']}"
    if fmt == "json":
        return json.dumps(payload, ensure_ascii=False, indent=2)
    return payload["full_text"]


def main():
    ap = argparse.ArgumentParser(
        description="Fetch YouTube transcript(s): keyless timedtext by default; Apify if "
                    "APIFY_API_TOKEN is set (more reliable from blocked cloud IPs).")
    g = ap.add_mutually_exclusive_group(required=True)
    g.add_argument("--url", help="single YouTube URL (watch?v= or youtu.be)")
    g.add_argument("--urls-file", help="file with one YouTube URL per line (batch mode)")
    ap.add_argument("--lang", default="", help="preferred transcript language (best effort)")
    ap.add_argument("--format", default="text", choices=["text", "json"],
                    help="text (full_text) or json (segments + timestamps)")
    ap.add_argument("--cache-dir", default="", help="dir to cache transcripts by video_id ($0 re-fetch)")
    ap.add_argument("--no-cache", action="store_true", help="ignore cache for this run")
    ap.add_argument("--prefer", choices=["auto", "keyless", "apify"], default="auto",
                    help="auto: Apify if APIFY_API_TOKEN set else keyless (default); "
                         "keyless: always the free timedtext path; apify: require the token")
    ap.add_argument("--estimate-only", action="store_true",
                    help="Apify cost gate: print projected cost (uncached videos) and exit 0 (no spend)")
    ap.add_argument("--yes", action="store_true",
                    help="Apify cost gate: confirm actual spend (required when any video must be fetched)")
    ap.add_argument("--max-cost-usd", type=float, default=0.50,
                    help="Apify cost gate: abort a video's run if reported usage exceeds this (default 0.50)")
    ap.add_argument("--apify-timeout", type=int, default=300,
                    help="Apify run/poll wall-clock timeout in seconds per video (default 300)")
    ap.add_argument("--output", default="-", help="output path (default stdout)")
    args = ap.parse_args()

    # Route: keyless by default, Apify only when a token is present (or forced).
    if args.prefer == "keyless":
        use_apify = False
    elif args.prefer == "apify":
        use_apify = True
    else:  # auto
        use_apify = has_token()
    tok = token() if use_apify else ""
    use_cache = not args.no_cache

    if args.url:
        urls = [args.url]
    else:
        with open(args.urls_file, encoding="utf-8") as f:
            urls = [ln.strip() for ln in f if ln.strip() and not ln.startswith("#")]
        # dedup by video id, preserve order
        seen, deduped = set(), []
        for u in urls:
            v = video_id(u) or u
            if v in seen:
                continue
            seen.add(v)
            deduped.append(u)
        urls = deduped

    # Which URLs would actually hit Apify (uncached)? Cache hits never spend.
    def is_cached(u):
        if not (use_cache and args.cache_dir):
            return False
        vid = video_id(u)
        return bool(vid and load_cache(args.cache_dir, vid))

    uncached = [u for u in urls if not is_cached(u)]

    # COST GATE applies ONLY to the Apify path. The keyless timedtext path is free, so
    # --estimate-only just reports $0 and --yes is a no-op there.
    if args.estimate_only:
        if use_apify:
            est = apify_common.estimate(
                ACTOR, {"videoUrl": "<per-video>", "count": len(uncached)},
                max_cost_usd=args.max_cost_usd, timeout_s=args.apify_timeout,
                items_hint=len(uncached), per_item_usd=PER_VIDEO_USD,
                label="youtube-apify-transcript")
        else:
            est = {"estimate_only": True, "path": "keyless", "projected_cost_usd": 0.0,
                   "would_spend": False,
                   "note": "keyless timedtext path — no key, no cost."}
        est["cached_skipped"] = len(urls) - len(uncached)
        est["videos_to_fetch"] = len(uncached)
        json.dump(est, sys.stdout, ensure_ascii=False, indent=2)
        sys.stdout.write("\n")
        return
    if use_apify and uncached and not args.yes:
        sys.exit(f"ERROR: cost gate — {len(uncached)} uncached video(s) would spend Apify "
                 "credits (~$0.007/video). Re-run with --yes to confirm (and --max-cost-usd "
                 "to cap per video), or --estimate-only to preview. Cache hits never spend. "
                 "(Use --prefer keyless for the free path.)")

    results = [fetch_one(u, args.lang, use_cache, args.cache_dir, use_apify, tok,
                         args.max_cost_usd, args.apify_timeout) for u in urls]

    if args.url:
        out = render(results[0], args.format)
    elif args.format == "json":
        out = json.dumps(results, ensure_ascii=False, indent=2)
    else:
        out = "\n\n".join(
            f"### {r.get('title') or r.get('video_url')}\n{render(r, 'text')}"
            for r in results
        )

    if args.output == "-":
        print(out)
    else:
        with open(args.output, "w", encoding="utf-8") as f:
            f.write(out + "\n")
        print(f"{len(results)} transcript(s) -> {args.output}", file=sys.stderr)


if __name__ == "__main__":
    main()
