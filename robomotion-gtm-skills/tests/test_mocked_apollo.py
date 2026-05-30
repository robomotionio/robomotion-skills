"""Mocked paid-API tests for apollo-lead-finder/apollo_search.py.

No network, no key: the ``post`` call is monkeypatched with canned Apollo people-search
pages so we test the discovery loop — in-page + cross-page dedup by LinkedIn URL,
client-side exclude-title filtering, the num-results cap, and pagination termination.
Also verifies the keyless-degrade contract when no API key is set."""
import contextlib
import io
import json
import os
import sys
import unittest

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _util import load_script, run_script  # noqa: E402

mod = load_script("apollo-lead-finder", "apollo_search.py")


def person(name, title, linkedin):
    first, _, last = name.partition(" ")
    return {"id": name, "first_name": first, "last_name": last, "title": title,
            "organization": {"name": "Acme", "primary_domain": "acme.com"},
            "linkedin_url": linkedin, "city": "Austin", "state": "TX", "country": "USA"}


class TestNoKeyContract(unittest.TestCase):
    def test_missing_key_points_to_keyless_degrade(self):
        r = run_script("apollo-lead-finder", "apollo_search.py", "--titles", "VP Sales",
                       env={"APOLLO_API_KEY": ""})
        self.assertNotEqual(r.returncode, 0)
        self.assertIn("serp_search.py", r.stderr)  # names the keyless fallback


class TestDiscoveryLoop(unittest.TestCase):
    def setUp(self):
        self._argv = sys.argv
        os.environ["APOLLO_API_KEY"] = "test-key"

    def tearDown(self):
        sys.argv = self._argv
        os.environ.pop("APOLLO_API_KEY", None)

    def _run_main(self, pages, argv_extra):
        calls = {"n": 0}

        def fake_post(url, body, key):
            i = calls["n"]
            calls["n"] += 1
            return pages[i] if i < len(pages) else {"people": [], "pagination": {"total_pages": 1}}

        mod.post = fake_post
        sys.argv = ["apollo_search.py", "--titles", "VP Sales", "--output", "-"] + argv_extra
        buf = io.StringIO()
        with contextlib.redirect_stdout(buf):
            mod.main()
        return json.loads(buf.getvalue())

    def test_dedups_within_and_across_pages(self):
        page1 = {"people": [person("Jane Doe", "VP Sales", "https://linkedin.com/in/jane"),
                            person("Jane Dup", "VP Sales", "https://linkedin.com/in/jane/")],
                 "pagination": {"total_pages": 2}}
        page2 = {"people": [person("Bob Lee", "VP Sales", "https://linkedin.com/in/bob"),
                            person("Jane Again", "VP Sales", "https://linkedin.com/in/jane")],
                 "pagination": {"total_pages": 2}}
        out = self._run_main([page1, page2], ["--num-results", "100"])
        urls = [p["linkedin_url"] for p in out]
        self.assertEqual(len(out), 2)  # Jane (once) + Bob; duplicates dropped
        self.assertEqual(sorted(u.rstrip("/").lower() for u in urls),
                         ["https://linkedin.com/in/bob", "https://linkedin.com/in/jane"])

    def test_exclude_titles_filtered_client_side(self):
        page = {"people": [person("Jane Doe", "VP Sales", "https://linkedin.com/in/jane"),
                           person("Sam Intern", "Sales Intern", "https://linkedin.com/in/sam")],
                "pagination": {"total_pages": 1}}
        out = self._run_main([page], ["--exclude-titles", "intern"])
        self.assertEqual([p["title"] for p in out], ["VP Sales"])

    def test_num_results_cap(self):
        page = {"people": [person(f"P{i}", "VP Sales", f"https://linkedin.com/in/p{i}")
                           for i in range(10)],
                "pagination": {"total_pages": 5}}
        out = self._run_main([page], ["--num-results", "3"])
        self.assertEqual(len(out), 3)


if __name__ == "__main__":
    unittest.main()
