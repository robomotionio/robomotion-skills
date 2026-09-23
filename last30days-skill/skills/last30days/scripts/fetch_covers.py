#!/usr/bin/env python3
"""Download the cover image of YouTube videos and Reddit posts (added by Robomotion).

    fetch_covers.py --out DIR URL [URL ...]

YouTube: the video's thumbnail (maxres, else hq) from i.ytimg.com, which
needs no key. Reddit: the post's own image(s): a gallery's images, an
i.redd.it upload, or the preview Reddit made of a linked page. The post is
read through Scrape.do when SCRAPEDO_TOKEN is set; image hosts are fetched
directly. Text posts have no cover and are skipped.

Prints one JSON line per saved file: {"source": URL, "file": PATH, "kind": ...}.
"""

from __future__ import annotations

import argparse
import html
import json
import re
import sys
import urllib.request
from pathlib import Path
from urllib.parse import urlsplit

sys.path.insert(0, str(Path(__file__).resolve().parent))

from lib import http  # noqa: E402

_YT_ID = re.compile(r"(?:v=|youtu\.be/|/shorts/|/embed/)([A-Za-z0-9_-]{11})")
_IMAGE_HOSTS = ("i.ytimg.com", "i.redd.it", "preview.redd.it", "external-preview.redd.it")
_YOUTUBE_HOSTS = frozenset({"youtube.com", "www.youtube.com", "m.youtube.com", "youtu.be"})
_REDDIT_HOSTS = frozenset({"reddit.com", "www.reddit.com", "old.reddit.com", "new.reddit.com", "redd.it"})
_MAX_BYTES = 15 * 1024 * 1024


def _download(url: str, dest: Path) -> bool:
    host = (urlsplit(url).hostname or "").lower()
    if host not in _IMAGE_HOSTS:
        return False
    req = urllib.request.Request(url, headers={"User-Agent": http.BROWSER_USER_AGENT})
    try:
        with urllib.request.urlopen(req, timeout=30) as resp:
            if resp.status != 200 or not resp.headers.get("Content-Type", "").startswith("image/"):
                return False
            data = resp.read(_MAX_BYTES + 1)
    except Exception:
        return False
    if len(data) > _MAX_BYTES or len(data) < 2048:
        return False
    dest.write_bytes(data)
    return True


def youtube(url: str, out: Path) -> list[dict]:
    m = _YT_ID.search(url)
    if not m:
        return []
    vid = m.group(1)
    for size in ("maxresdefault", "hqdefault"):
        dest = out / f"youtube-{vid}.jpg"
        if _download(f"https://i.ytimg.com/vi/{vid}/{size}.jpg", dest):
            return [{"source": url, "file": str(dest), "kind": f"youtube thumbnail ({size})"}]
    return []


def _reddit_images(post: dict) -> list[str]:
    urls = []
    for item in (post.get("gallery_data") or {}).get("items", []):
        meta = (post.get("media_metadata") or {}).get(item.get("media_id"), {})
        src = (meta.get("s") or {}).get("u")
        if src:
            urls.append(html.unescape(src))
    direct = post.get("url_overridden_by_dest") or post.get("url") or ""
    if not urls and (urlsplit(direct).hostname or "") == "i.redd.it":
        urls.append(direct)
    if not urls:
        for image in (post.get("preview") or {}).get("images", [])[:1]:
            src = (image.get("source") or {}).get("url")
            if src:
                urls.append(html.unescape(src))
    return urls


def reddit(url: str, out: Path, limit: int) -> list[dict]:
    m = re.search(r"/comments/([a-z0-9]+)", url)
    if not m:
        return []
    post_id = m.group(1)
    try:
        data = http.request("GET", f"https://www.reddit.com/comments/{post_id}.json?raw_json=1&limit=1",
                            headers={"User-Agent": http.BROWSER_USER_AGENT}, timeout=60, retries=2)
        post = data[0]["data"]["children"][0]["data"]
    except Exception as exc:  # noqa: BLE001 - report and move on
        print(json.dumps({"source": url, "error": f"could not read post: {exc}"}), file=sys.stderr)
        return []
    saved = []
    for i, src in enumerate(_reddit_images(post)[:limit], 1):
        ext = ".png" if ".png" in src.split("?")[0] else ".jpg"
        dest = out / f"reddit-{post_id}-{i}{ext}"
        if _download(src, dest):
            saved.append({"source": url, "file": str(dest), "kind": "reddit image",
                          "title": post.get("title", "")})
    return saved


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--out", required=True, help="folder to save images in")
    parser.add_argument("--per-post", type=int, default=2, help="images per Reddit gallery (default 2)")
    parser.add_argument("urls", nargs="+")
    args = parser.parse_args(argv)
    out = Path(args.out)
    out.mkdir(parents=True, exist_ok=True)
    found = 0
    for url in args.urls:
        host = (urlsplit(url).hostname or "").lower()
        if host in _YOUTUBE_HOSTS:
            rows = youtube(url, out)
        elif host in _REDDIT_HOSTS:
            rows = reddit(url, out, args.per_post)
        else:
            rows = []
        for row in rows:
            print(json.dumps(row, ensure_ascii=False))
        found += len(rows)
        if not rows:
            print(json.dumps({"source": url, "file": None, "kind": "no cover image"}))
    return 0 if found else 1


if __name__ == "__main__":
    sys.exit(main())
