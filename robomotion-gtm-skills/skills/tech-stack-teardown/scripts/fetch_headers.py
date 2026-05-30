#!/usr/bin/env python3
"""fetch_headers.py — HTTP header / cookie recon (keyless detection signal #2).

Deterministic, stdlib-only. Does a GET (with a HEAD fallback) on a URL and captures:
  - the response headers (server / x-powered-by / CDN / security headers)
  - Set-Cookie names
  - the final URL after redirects
Then maps header + cookie patterns to vendors via signatures.json (sigdb).

Headers are a high-signal layer that source-grepping misses: CDN/hosting (Cloudflare,
Vercel, Netlify, Fastly, CloudFront, Akamai), platform (Shopify powered-by), and
session cookies (HubSpot __hstc, Marketo _mkto_trk, Intercom intercom-id) all surface
here even when the HTML is minified or JS-rendered.

Examples:
  fetch_headers.py --url example.com
  fetch_headers.py --url https://example.com --output ${WORKSPACE}/headers.json
"""
import argparse
import json
import ssl
import sys
import urllib.error
import urllib.request

import sigdb

UA = ("Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
      "(KHTML, like Gecko) Chrome/124.0 Safari/537.36")

# notable headers to always surface in the report (lowercased)
NOTABLE = [
    "server", "x-powered-by", "via", "x-served-by", "cf-ray", "cf-cache-status",
    "x-vercel-id", "x-vercel-cache", "x-nf-request-id", "x-amz-cf-id", "x-amz-cf-pop",
    "x-amz-request-id", "x-github-request-id", "x-fastly-request-id", "x-shopify-stage",
    "powered-by", "x-drupal-cache", "x-generator", "x-aspnet-version",
    "strict-transport-security", "content-security-policy", "x-frame-options",
    "x-content-type-options", "referrer-policy", "permissions-policy",
]
SECURITY_HEADERS = [
    "strict-transport-security", "content-security-policy", "x-frame-options",
    "x-content-type-options", "referrer-policy", "permissions-policy",
]


def normalize_url(raw):
    raw = raw.strip()
    if raw.startswith("http://") or raw.startswith("https://"):
        return [raw]
    raw = raw.strip("/")
    return [f"https://{raw}", f"http://{raw}"]


def fetch(url, method="GET"):
    ctx = ssl.create_default_context()
    req = urllib.request.Request(url, method=method,
                                 headers={"User-Agent": UA, "Accept": "*/*"})
    with urllib.request.urlopen(req, timeout=30, context=ctx) as r:
        # read a little to ensure body-bearing headers are populated; discard
        if method == "GET":
            try:
                r.read(2048)
            except Exception:
                pass
        return r


def collect(raw_url):
    last_err = ""
    for url in normalize_url(raw_url):
        for method in ("GET", "HEAD"):
            try:
                r = fetch(url, method)
            except (urllib.error.HTTPError,) as e:
                # an HTTPError still carries useful headers
                r = e
            except (urllib.error.URLError, TimeoutError, ConnectionError, ssl.SSLError, OSError) as e:
                last_err = str(e)
                continue
            headers = {}
            for k, v in r.headers.items():
                headers[k.lower()] = v
            set_cookie_names = []
            for k, v in r.headers.items():
                if k.lower() == "set-cookie":
                    name = v.split("=", 1)[0].strip()
                    if name and name not in set_cookie_names:
                        set_cookie_names.append(name)
            final_url = getattr(r, "url", None) or getattr(r, "geturl", lambda: url)()
            status = getattr(r, "status", None) or getattr(r, "code", None)
            return {
                "ok": True,
                "request_url": url,
                "final_url": final_url,
                "status": status,
                "method": method,
                "headers": headers,
                "set_cookie_names": set_cookie_names,
            }
    return {"ok": False, "request_url": raw_url, "error": last_err or "fetch failed",
            "headers": {}, "set_cookie_names": []}


def main():
    ap = argparse.ArgumentParser(
        description="HTTP header/cookie recon -> vendor signals via signatures.json (keyless).")
    ap.add_argument("--url", required=True, help="domain or full URL (e.g. example.com)")
    ap.add_argument("--signatures", default=None, help="path to signatures.json (default: bundled)")
    ap.add_argument("--output", default="-", help="output JSON path (default stdout)")
    args = ap.parse_args()

    info = collect(args.url)
    techs = sigdb.load_signatures(args.signatures)

    detected = []
    if info.get("ok"):
        h = sigdb.match_headers(info["headers"], techs)
        c = sigdb.match_cookies(info["set_cookie_names"], techs)
        detected = sigdb.merge(h, c)

    notable = {k: info["headers"][k] for k in NOTABLE if k in info.get("headers", {})}
    sec_present = [k for k in SECURITY_HEADERS if k in info.get("headers", {})]

    result = {
        "input": args.url,
        "fetch": {k: info.get(k) for k in ("ok", "request_url", "final_url", "status", "method", "error")},
        "notable_headers": notable,
        "set_cookie_names": info.get("set_cookie_names", []),
        "security_headers_present": sec_present,
        "detected": detected,
    }
    out = json.dumps(result, ensure_ascii=False, indent=2)
    if args.output == "-":
        print(out)
    else:
        with open(args.output, "w", encoding="utf-8") as f:
            f.write(out + "\n")
        print(f"headers {args.url} -> {args.output} ({len(detected)} signals)", file=sys.stderr)


if __name__ == "__main__":
    main()
