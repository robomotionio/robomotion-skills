"""Unit tests for programmatic-seo-planner/cluster_url_patterns.py — the pSEO URL bucketer:
pattern matching, editorial-noise exclusion, and the varying-axis extraction."""
import json
import os
import sys
import unittest

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _util import load_script, run_script  # noqa: E402

mod = load_script("programmatic-seo-planner", "cluster_url_patterns.py")


class TestVaryingSegment(unittest.TestCase):
    def test_returns_segment_after_pattern_root(self):
        root = dict((n, rx.pattern) for n, rx in mod.PATTERNS)["vs"]
        self.assertEqual(mod.varying_segment("/vs/competitor-x", root), "competitor-x")


class TestClusteringEndToEnd(unittest.TestCase):
    def _run(self, urls):
        r = run_script("programmatic-seo-planner", "cluster_url_patterns.py",
                       "--urls", ",".join(urls))
        self.assertEqual(r.returncode, 0, r.stderr)
        return json.loads(r.stdout)

    def test_buckets_known_patterns(self):
        out = self._run([
            "https://x.com/vs/asana", "https://x.com/vs/trello",
            "https://x.com/integrations/slack",
            "https://x.com/glossary/what-is-rpa",
        ])
        names = {p["pattern"]: p["page_count"] for p in out["patterns"]}
        self.assertEqual(names.get("vs"), 2)
        self.assertIn("integrations", names)
        self.assertIn("glossary", names)

    def test_editorial_urls_excluded_by_default(self):
        out = self._run(["https://x.com/blog/post-1", "https://x.com/vs/asana"])
        self.assertEqual(out["editorial_excluded"], 1)
        self.assertEqual(out["total_urls"], 2)

    def test_uniform_depth_scores_full_consistency(self):
        out = self._run(["https://x.com/vs/a", "https://x.com/vs/b", "https://x.com/vs/c"])
        vs = next(p for p in out["patterns"] if p["pattern"] == "vs")
        self.assertEqual(vs["url_consistency"], 1.0)


if __name__ == "__main__":
    unittest.main()
