#!/usr/bin/env python3
"""Search Google and fetch web pages through Scrape.do.

    web-search "<query>" [--gl us] [--hl en] [--page N] [--period last_month] [--json]
    web-fetch <url> [--geo us] [--render] [--super] [--max-chars 40000]

Standard library only. The token comes from SCRAPEDO_TOKEN. Inside a
Robomotion sandbox that variable holds a vault placeholder which the robot's
credential proxy swaps for the real token on the way out, so the token never
appears in this process's output, its logs or its saved files. Scrape.do takes
its token only as a query parameter, so this script never prints a URL it
requested.

Costs (Scrape.do credits): a search is 10, a plain fetch 1, a fetch with
--super or --render more (a residential fetch with rendering is 25).
"""
from __future__ import annotations

import argparse
import gzip
import json
import os
import sys
import urllib.error
import urllib.request
from urllib.parse import urlencode, urlsplit

API = "https://api.scrape.do/"
SEARCH = "https://api.scrape.do/plugin/google/search"
PERIODS = ("last_hour", "last_day", "last_week", "last_month", "last_year")


def token() -> str:
    t = (os.environ.get("SCRAPEDO_TOKEN") or "").strip()
    if not t:
        sys.exit("web-search/web-fetch: no Scrape.do token. Ask the person to add their "
                 "Scrape.do token in the agent's settings (Integrations), then try again.")
    return t


def get(url: str, timeout: int = 90) -> tuple[int, bytes]:
    req = urllib.request.Request(url, headers={"Accept-Encoding": "gzip"})
    try:
        with urllib.request.urlopen(req, timeout=timeout) as r:
            body = r.read()
            if r.headers.get("Content-Encoding") == "gzip":
                body = gzip.decompress(body)
            return r.status, body
    except urllib.error.HTTPError as e:
        body = e.read() or b""
        try:
            body = gzip.decompress(body)
        except OSError:
            pass
        return e.code, body
    except (urllib.error.URLError, TimeoutError) as e:
        # str(e) can hold the URL, and the URL holds the token: name the reason only.
        sys.exit(f"Scrape.do could not be reached ({type(e).__name__}). Try again in a minute.")


def fail(status: int, body: bytes) -> None:
    try:
        msg = json.loads(body).get("message") or ""
    except ValueError:
        msg = body[:200].decode("utf-8", "replace")
    hint = {401: "the Scrape.do token was refused", 402: "the Scrape.do account is out of credits",
            429: "Scrape.do is rate limiting; wait a minute"}.get(status, "")
    sys.exit(f"Scrape.do answered {status}{': ' + hint if hint else ''}. {msg}".strip())


def search(args: argparse.Namespace) -> None:
    params = [("token", token()), ("q", args.query), ("start", str(max(0, args.page - 1) * 10))]
    for key in ("gl", "hl", "google_domain"):
        if getattr(args, key):
            params.append((key, getattr(args, key)))
    if args.period:
        params.append(("time_period", args.period))
    status, body = get(SEARCH + "?" + urlencode(params))
    if status != 200:
        fail(status, body)
    data = json.loads(body)
    if args.json:
        data.pop("search_parameters", None)  # echoes the request, token included
        print(json.dumps(data, ensure_ascii=False, indent=1))
        return
    out = [f"# Google: {args.query}" + (f" (page {args.page})" if args.page > 1 else "")]
    kg = data.get("knowledge_graph") or {}
    if kg.get("title"):
        out.append(f"\n## Knowledge panel: {kg.get('title')}" + (f" ({kg['type']})" if kg.get("type") else ""))
        if kg.get("description"):
            out.append(kg["description"])
        if kg.get("website"):
            out.append(f"Website: {kg['website']}")
    organic = data.get("organic_results") or []
    out.append(f"\n## Results ({len(organic)})")
    for r in organic:
        line = f"\n{r.get('position', '?')}. {r.get('title', '').strip()}\n   {r.get('link', '')}"
        if r.get("date"):
            line += f"\n   date: {r['date']}"
        if r.get("snippet"):
            line += f"\n   {r['snippet'].strip()}"
        out.append(line)
    qs = [q.get("question") for q in data.get("related_questions") or [] if q.get("question")]
    if qs:
        out.append("\n## People also ask\n" + "\n".join(f"- {q}" for q in qs))
    rel = [r.get("query") for r in data.get("related_searches") or [] if r.get("query")]
    if rel:
        out.append("\n## Related searches\n" + "\n".join(f"- {r}" for r in rel))
    if not organic:
        out.append("\nNo results. Try fewer or different words.")
    print("\n".join(out))


def fetch(args: argparse.Namespace) -> None:
    parts = urlsplit(args.url)
    if parts.scheme not in ("http", "https") or not parts.hostname:
        sys.exit("web-fetch: give a full http(s) address")
    params = [("token", token()), ("url", args.url), ("output", "markdown")]
    if args.render:
        params.append(("render", "true"))
    if args.super:
        params.append(("super", "true"))
    if args.geo:
        params.append(("geoCode", args.geo))
    status, body = get(API + "?" + urlencode(params), timeout=120)
    if status != 200:
        fail(status, body)
    text = body.decode("utf-8", "replace")
    if len(text) > args.max_chars:
        text = text[: args.max_chars] + f"\n\n[cut at {args.max_chars} characters of {len(text)}]"
    print(f"# {args.url}\n\n{text}")


def main(argv: list[str]) -> None:
    prog = os.path.basename(argv[0])
    if prog == "web-fetch" or (len(argv) > 1 and argv[1] == "fetch"):
        argv = argv[2:] if prog != "web-fetch" else argv[1:]
        p = argparse.ArgumentParser(prog="web-fetch", description="Read a web page as Markdown through Scrape.do.")
        p.add_argument("url")
        p.add_argument("--geo", help="two-letter country to fetch from (needs --super)")
        p.add_argument("--render", action="store_true", help="run the page's JavaScript first (costs more)")
        p.add_argument("--super", action="store_true", help="residential address, for sites that block servers (costs more)")
        p.add_argument("--max-chars", type=int, default=40000)
        fetch(p.parse_args(argv))
        return
    argv = argv[2:] if prog != "web-search" and len(argv) > 1 and argv[1] == "search" else argv[1:]
    p = argparse.ArgumentParser(prog="web-search", description="Google results through Scrape.do.")
    p.add_argument("query")
    p.add_argument("--gl", help="country of the searcher, two letters (us, gb, de, tr)")
    p.add_argument("--hl", help="interface language (en, de, tr)")
    p.add_argument("--google-domain", dest="google_domain", help="e.g. google.de")
    p.add_argument("--page", type=int, default=1, help="results page, 10 per page, at most 10")
    p.add_argument("--period", choices=PERIODS, help="only results from this period")
    p.add_argument("--json", action="store_true", help="the whole response as JSON (ads, local results, AI overview)")
    a = p.parse_args(argv)
    a.page = min(max(a.page, 1), 10)
    search(a)


if __name__ == "__main__":
    main(sys.argv)
