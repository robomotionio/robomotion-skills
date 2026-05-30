"""Keyless-path tests for the no-credential fallbacks.

Two kinds live here:
  * Offline (always runs): the deterministic SERP HTML parser, exercised with canned markup.
  * Network-gated (``@net_gate``): the live keyless endpoints — Hacker News (Algolia),
    Wayback CDX, Google Suggest, DuckDuckGo SERP. These hit the public internet, so they
    only run when ``GTM_NET_TESTS=1``. The scripts degrade gracefully (exit 0 with an empty
    result set on rate-limit), so these assert structure, not exact counts.
"""
import json
import os
import sys
import unittest

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _util import load_script, net_gate, run_script  # noqa: E402

serp = load_script("seo-traffic-analyzer", "serp_probe.py")

CANNED_SERP = """
<div class="results">
  <a class="result__a" href="https://www.example.com/a">First &amp; Best</a>
  <a class="result__snippet" href="x">A snippet about example.</a>
  <a class="result__a" href="/l/?uddg=https%3A%2F%2Ftest.org%2Fb">Second Result</a>
  <a class="result__snippet" href="y">Another snippet.</a>
</div>
"""


class TestSerpParserOffline(unittest.TestCase):
    def test_parses_ranked_results_and_unwraps_redirects(self):
        rows = serp.parse_results(CANNED_SERP, limit=10)
        self.assertEqual(len(rows), 2)
        self.assertEqual(rows[0]["position"], 1)
        self.assertEqual(rows[0]["url"], "https://www.example.com/a")
        self.assertEqual(rows[0]["domain"], "example.com")  # www stripped
        self.assertEqual(rows[0]["title"], "First & Best")   # entities unescaped, tags removed
        self.assertEqual(rows[1]["url"], "https://test.org/b")  # uddg redirect decoded

    def test_limit_is_respected(self):
        self.assertEqual(len(serp.parse_results(CANNED_SERP, limit=1)), 1)


class TestKeylessLive(unittest.TestCase):
    @net_gate
    def test_hacker_news_search(self):
        r = run_script("competitor-monitoring-system", "hn_fetch.py",
                       "--query", "automation", "--days", "120", "--max-results", "3")
        self.assertEqual(r.returncode, 0, r.stderr)
        data = json.loads(r.stdout)
        self.assertIsInstance(data, list)

    @net_gate
    def test_wayback_snapshots(self):
        r = run_script("competitor-monitoring-system", "wayback_fetch.py",
                       "--url", "https://example.com", "--snapshots", "1")
        self.assertEqual(r.returncode, 0, r.stderr)
        data = json.loads(r.stdout)
        self.assertEqual(data["url"], "https://example.com")
        self.assertIn("snapshots", data)

    @net_gate
    def test_google_autocomplete_expand(self):
        r = run_script("google-search-ads-builder", "autocomplete_expand.py",
                       "--seeds", "workflow automation", "--max-per-seed", "5")
        self.assertEqual(r.returncode, 0, r.stderr)
        data = json.loads(r.stdout)
        self.assertIn("expansions", data)
        self.assertEqual(data["seeds"], ["workflow automation"])

    @net_gate
    def test_duckduckgo_serp_probe(self):
        r = run_script("seo-traffic-analyzer", "serp_probe.py", "search",
                       "--query", "workflow automation", "--max-results", "3")
        self.assertEqual(r.returncode, 0, r.stderr)
        data = json.loads(r.stdout)
        self.assertIn("results", data)
        self.assertIsInstance(data["results"], list)


if __name__ == "__main__":
    unittest.main()
