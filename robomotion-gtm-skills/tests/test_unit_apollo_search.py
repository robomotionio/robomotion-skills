"""Unit tests for apollo-lead-finder/apollo_search.py — the pure helpers: LinkedIn URL
normalization, Apollo person normalization, and existing-contact dedup loading."""
import os
import sys
import tempfile
import unittest

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _util import load_script  # noqa: E402

mod = load_script("apollo-lead-finder", "apollo_search.py")


class TestNormLinkedin(unittest.TestCase):
    def test_strips_query_trailing_slash_and_lowercases(self):
        self.assertEqual(
            mod.norm_linkedin("http://LinkedIn.com/in/Jane-Doe/?utm=x"),
            "https://linkedin.com/in/jane-doe")

    def test_empty_is_empty(self):
        self.assertEqual(mod.norm_linkedin(""), "")


class TestNormalize(unittest.TestCase):
    def test_builds_name_from_parts_and_joins_location(self):
        p = mod.normalize({
            "first_name": "Jane", "last_name": "Doe", "title": "VP Sales",
            "organization": {"name": "Acme", "primary_domain": "acme.com"},
            "city": "Austin", "state": "TX", "country": "USA",
        })
        self.assertEqual(p["name"], "Jane Doe")
        self.assertEqual(p["company"], "Acme")
        self.assertEqual(p["company_domain"], "acme.com")
        self.assertEqual(p["location"], "Austin, TX, USA")

    def test_missing_org_is_safe(self):
        p = mod.normalize({"name": "Bob", "title": "CEO"})
        self.assertEqual(p["company"], "")
        self.assertEqual(p["location"], "")


class TestLoadExisting(unittest.TestCase):
    def test_reads_linkedin_column_normalized(self):
        with tempfile.NamedTemporaryFile("w", suffix=".csv", delete=False, newline="") as f:
            f.write("name,linkedin_url\nJane,https://linkedin.com/in/Jane/\n")
            path = f.name
        try:
            seen = mod.load_existing(path)
            self.assertIn("https://linkedin.com/in/jane", seen)
        finally:
            os.unlink(path)

    def test_no_path_returns_empty(self):
        self.assertEqual(mod.load_existing(""), set())


if __name__ == "__main__":
    unittest.main()
