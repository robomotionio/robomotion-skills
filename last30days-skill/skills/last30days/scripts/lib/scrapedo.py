"""Optional Scrape.do routing (added by Robomotion).

Reddit answers most server and cloud addresses with 403, and YouTube search
from them is throttled. When ``SCRAPEDO_TOKEN`` is set, requests to those
hosts go through Scrape.do's API (https://api.scrape.do/?token=...&url=...),
which fetches them from residential addresses in a chosen country. With no
token nothing changes: the keyless paths run exactly as upstream wrote them.

Environment:
    SCRAPEDO_TOKEN  Scrape.do API token. Unset = off.
    SCRAPEDO_GEO    Two-letter country code (us, tr, de, ...) for Scrape.do's
                    geoCode, YouTube's gl and Google Trends' geo. Unset = no
                    country for Scrape.do and US for Google Trends.
    SCRAPEDO_SUPER  "0" turns off residential routing (super=true), which
                    Reddit needs. On by default.

Scrape.do takes its token only as a query parameter. Inside a Robomotion
sandbox the variable holds a vault placeholder that the robot's credential
proxy swaps for the real token on the way out, so the token itself never
appears in this process, its logs or its saved reports.
"""

from __future__ import annotations

import datetime as _dt
import json
import os
import re
from typing import Any, Dict, List, Optional
from urllib.parse import quote, urlencode, urlsplit

API = "https://api.scrape.do/"
PLUGIN = "https://api.scrape.do/plugin/google/"

# Hosts whose requests are routed when a token is set.
ROUTED_HOSTS = frozenset({
    "reddit.com", "www.reddit.com", "old.reddit.com", "new.reddit.com",
    "youtube.com", "www.youtube.com", "m.youtube.com",
})


# Variable names, read through os.environ like env.py reads its keys.
TOKEN_ENV = "SCRAPEDO_TOKEN"
GEO_ENV = "SCRAPEDO_GEO"
SUPER_ENV = "SCRAPEDO_SUPER"


def token() -> str:
    return (os.environ.get(TOKEN_ENV) or "").strip()


def enabled() -> bool:
    return bool(token())


def geo() -> str:
    """Lower-case two-letter country code, or '' when unset or malformed."""
    value = (os.environ.get(GEO_ENV) or "").strip().lower()
    return value if re.fullmatch(r"[a-z]{2}", value) else ""


def super_on() -> bool:
    value = (os.environ.get(SUPER_ENV) or "1").strip().lower()
    return value not in {"0", "false", "no", "off"}


def routes(url: str) -> bool:
    """True when ``url`` should be fetched through Scrape.do."""
    if not enabled():
        return False
    try:
        host = (urlsplit(url).hostname or "").lower()
    except ValueError:
        return False
    return host in ROUTED_HOSTS


def wrap(url: str) -> str:
    """The Scrape.do API URL that fetches ``url``."""
    params = [("token", token())]
    if super_on():
        params.append(("super", "true"))
    if geo():
        params.append(("geoCode", geo()))
    # The token is a vault placeholder or a plain key: letters, digits and _.
    query = urlencode(params) + "&url=" + quote(url, safe="")
    return API + "?" + query


def plugin_url(name: str, params: Dict[str, Any]) -> str:
    """A Scrape.do Google plugin URL (trends, trending) with the token."""
    clean = {k: str(v) for k, v in params.items() if v not in (None, "")}
    return PLUGIN + name + "?" + urlencode([("token", token())] + sorted(clean.items()))


# ---------------------------------------------------------------------------
# YouTube search through Scrape.do
# ---------------------------------------------------------------------------

# YouTube search filters: type video, uploaded this month / this week.
_SP_THIS_MONTH = "EgQIBBAB"
_SP_THIS_WEEK = "EgQIAxAB"

_REL_UNITS = {
    "second": 0, "minute": 0, "hour": 0,
    "day": 1, "week": 7, "month": 30, "year": 365,
}


def _relative_to_date(text: str, today: Optional[_dt.date] = None) -> Optional[str]:
    """'3 days ago' / '3d ago' / 'Streamed 2 weeks ago' -> YYYY-MM-DD."""
    today = today or _dt.date.today()
    m = re.search(r"(\d+)\s*(second|minute|hour|day|week|month|year|s|m|h|d|w|mo|y)\w*\s+ago", text or "", re.I)
    if not m:
        return None
    n = int(m.group(1))
    unit = m.group(2).lower()
    short = {"s": "second", "m": "minute", "h": "hour", "d": "day", "w": "week", "mo": "month", "y": "year"}
    unit = short.get(unit, unit)
    days = _REL_UNITS.get(unit, 0) * n
    return (today - _dt.timedelta(days=days)).isoformat()


def _count(text: str) -> int:
    """'95,137 views' / '1.2M views' / 'No views' -> int."""
    t = (text or "").replace(",", "").strip()
    m = re.search(r"([\d.]+)\s*([KMB]?)", t, re.I)
    if not m:
        return 0
    value = float(m.group(1))
    value *= {"": 1, "K": 1e3, "M": 1e6, "B": 1e9}[m.group(2).upper()]
    return int(value)


def _text(node: Any) -> str:
    if not isinstance(node, dict):
        return ""
    if "simpleText" in node:
        return str(node["simpleText"])
    return "".join(str(r.get("text", "")) for r in node.get("runs", []) if isinstance(r, dict))


def parse_youtube_results(html: str, today: Optional[_dt.date] = None) -> List[Dict[str, Any]]:
    """Video rows from a YouTube results page (its ytInitialData)."""
    m = re.search(r"var ytInitialData\s*=\s*(\{.*?\});\s*</script>", html or "", re.S)
    if not m:
        return []
    try:
        data = json.loads(m.group(1))
    except ValueError:
        return []
    rows: List[Dict[str, Any]] = []
    seen = set()
    stack = [data]
    while stack:
        node = stack.pop()
        if isinstance(node, dict):
            video = node.get("videoRenderer")
            if isinstance(video, dict) and video.get("videoId") and video["videoId"] not in seen:
                seen.add(video["videoId"])
                rows.append({
                    "video_id": video["videoId"],
                    "title": _text(video.get("title")),
                    "channel_name": _text(video.get("ownerText")),
                    "views": _count(_text(video.get("viewCountText"))),
                    "date": _relative_to_date(_text(video.get("publishedTimeText")), today),
                    "duration": _text(video.get("lengthText")) or None,
                    "description": "".join(
                        _text(s.get("snippetText")) for s in video.get("detailedMetadataSnippets", []) if isinstance(s, dict)
                    ) or _text(video.get("descriptionSnippet")),
                })
            stack.extend(node.values())
        elif isinstance(node, list):
            stack.extend(node)
    # ytInitialData lists results in page order; the stack walk reverses it.
    rows.reverse()
    return rows


def youtube_search_url(query: str, window_days: int = 30) -> str:
    sp = _SP_THIS_WEEK if window_days <= 7 else _SP_THIS_MONTH
    params = {"search_query": query, "sp": sp, "hl": "en"}
    if geo():
        params["gl"] = geo().upper()
    return "https://www.youtube.com/results?" + urlencode(params)
