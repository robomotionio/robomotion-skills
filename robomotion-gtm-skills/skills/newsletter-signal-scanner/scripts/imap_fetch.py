#!/usr/bin/env python3
"""imap_fetch.py — Fetch recent messages from a monitoring inbox over IMAP.

Reads IMAP_HOST / IMAP_USER / IMAP_PASSWORD (required — no inbox, nothing to scan) and
emits a JSON array of decoded messages (HTML stripped to plain text) for the campaign
matcher to scan. Optional IMAP_PORT (default 993), IMAP_FOLDER (default INBOX). Stdlib only
(imaplib, email).

Implements step 1-2 of the robomotion-gtm-skills `newsletter-monitor` contract.

Examples:
  imap_fetch.py --days 7 --limit 100 --output ${WORKSPACE}/messages.json
  imap_fetch.py --from-domains "substack.com,beehiiv.com" --days 14
"""
import argparse
import email
import email.utils
import html.parser
import imaplib
import json
import os
import re
import sys
from datetime import datetime, timezone, timedelta
from email.header import decode_header, make_header


class _TextExtractor(html.parser.HTMLParser):
    SKIP = {"script", "style", "head", "noscript"}

    def __init__(self):
        super().__init__()
        self.parts = []
        self._skip = 0

    def handle_starttag(self, tag, attrs):
        if tag in self.SKIP:
            self._skip += 1

    def handle_endtag(self, tag):
        if tag in self.SKIP and self._skip:
            self._skip -= 1

    def handle_data(self, data):
        if not self._skip and data.strip():
            self.parts.append(data.strip())


def strip_html(s):
    p = _TextExtractor()
    try:
        p.feed(s)
        return re.sub(r"[ \t]+", " ", " ".join(p.parts)).strip()
    except Exception:  # noqa: BLE001
        return re.sub(r"<[^>]+>", " ", s)


def decode_hdr(v):
    if not v:
        return ""
    try:
        return str(make_header(decode_header(v)))
    except Exception:  # noqa: BLE001
        return v


def body_text(msg):
    if msg.is_multipart():
        plain, htmltext = "", ""
        for part in msg.walk():
            ctype = part.get_content_type()
            if part.get("Content-Disposition", "").startswith("attachment"):
                continue
            try:
                payload = part.get_payload(decode=True)
            except Exception:  # noqa: BLE001
                continue
            if not payload:
                continue
            charset = part.get_content_charset() or "utf-8"
            try:
                text = payload.decode(charset, "ignore")
            except (LookupError, UnicodeDecodeError):
                text = payload.decode("utf-8", "ignore")
            if ctype == "text/plain" and not plain:
                plain = text
            elif ctype == "text/html" and not htmltext:
                htmltext = text
        return plain.strip() or strip_html(htmltext)
    payload = msg.get_payload(decode=True) or b""
    charset = msg.get_content_charset() or "utf-8"
    try:
        text = payload.decode(charset, "ignore")
    except (LookupError, UnicodeDecodeError):
        text = payload.decode("utf-8", "ignore")
    return strip_html(text) if msg.get_content_type() == "text/html" else text.strip()


def creds():
    host = os.environ.get("IMAP_HOST", "").strip()
    user = os.environ.get("IMAP_USER", "").strip()
    pwd = os.environ.get("IMAP_PASSWORD", "").strip()
    if not (host and user and pwd):
        sys.exit("ERROR: IMAP_HOST / IMAP_USER / IMAP_PASSWORD are required "
                 "(the skill has no inbox to scan without them).")
    port = int(os.environ.get("IMAP_PORT", "993"))
    folder = os.environ.get("IMAP_FOLDER", "INBOX")
    return host, port, user, pwd, folder


def main():
    ap = argparse.ArgumentParser(description="Fetch recent messages from a monitoring inbox over IMAP.")
    ap.add_argument("--days", type=int, default=0, help="only messages from last N days (0 = no limit)")
    ap.add_argument("--limit", type=int, default=100, help="max messages to fetch (newest first)")
    ap.add_argument("--from-domains", default="", help="comma-separated sender domains to scope the scan")
    ap.add_argument("--output", default="-", help="output JSON path (default stdout)")
    args = ap.parse_args()

    host, port, user, pwd, folder = creds()
    domains = [d.strip().lower() for d in args.from_domains.split(",") if d.strip()]

    M = imaplib.IMAP4_SSL(host, port)
    try:
        M.login(user, pwd)
        M.select(folder, readonly=True)
        criteria = ["ALL"]
        if args.days:
            since = (datetime.now(timezone.utc) - timedelta(days=args.days)).strftime("%d-%b-%Y")
            criteria = ["SINCE", since]
        typ, data = M.search(None, *criteria)
        ids = data[0].split() if data and data[0] else []
        ids = ids[::-1][: args.limit * 3 if domains else args.limit]  # over-fetch when filtering by domain

        out = []
        for num in ids:
            if len(out) >= args.limit:
                break
            typ, msg_data = M.fetch(num, "(RFC822)")
            if typ != "OK" or not msg_data or not msg_data[0]:
                continue
            msg = email.message_from_bytes(msg_data[0][1])
            sender = decode_hdr(msg.get("From", ""))
            addr = email.utils.parseaddr(sender)[1].lower()
            if domains and not any(addr.endswith("@" + d) or ("." + d) in addr or addr.endswith(d) for d in domains):
                continue
            date_hdr = msg.get("Date", "")
            try:
                dt = email.utils.parsedate_to_datetime(date_hdr)
                date_iso = dt.isoformat() if dt else date_hdr
            except (TypeError, ValueError):
                date_iso = date_hdr
            out.append({
                "message_id": msg.get("Message-ID", "").strip() or decode_hdr(msg.get("Subject", "")) + addr,
                "from": sender,
                "from_address": addr,
                "subject": decode_hdr(msg.get("Subject", "")),
                "date": date_iso,
                "body": body_text(msg),
            })
    finally:
        try:
            M.logout()
        except Exception:  # noqa: BLE001
            pass

    payload = json.dumps(out, ensure_ascii=False, indent=2)
    if args.output == "-":
        print(payload)
    else:
        with open(args.output, "w", encoding="utf-8") as f:
            f.write(payload + "\n")
        print(f"{len(out)} messages -> {args.output}", file=sys.stderr)


if __name__ == "__main__":
    main()
