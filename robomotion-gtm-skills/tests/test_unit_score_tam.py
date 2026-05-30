"""End-to-end unit test for tam-builder/score_tam.py — weighted 0-100 fit scoring and tier
assignment. Drives the CLI with temp input + config files and checks the scored output."""
import json
import os
import sys
import tempfile
import unittest

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _util import load_script, run_script  # noqa: E402

mod = load_script("tam-builder", "score_tam.py")


class TestHelpers(unittest.TestCase):
    def test_in_any_range(self):
        self.assertTrue(mod.in_any_range(100, [[51, 200]]))
        self.assertFalse(mod.in_any_range(500, [[51, 200]]))
        self.assertFalse(mod.in_any_range(None, [[51, 200]]))

    def test_contains_any_case_insensitive(self):
        self.assertTrue(mod.contains_any("B2B Software", ["software"]))
        self.assertFalse(mod.contains_any("hardware", ["software"]))


class TestScoreTamCli(unittest.TestCase):
    def _run(self, companies, config):
        d = tempfile.mkdtemp()
        ip = os.path.join(d, "in.json")
        cp = os.path.join(d, "cfg.json")
        with open(ip, "w") as f:
            json.dump(companies, f)
        with open(cp, "w") as f:
            json.dump(config, f)
        r = run_script("tam-builder", "score_tam.py", "--input", ip, "--config", cp)
        self.assertEqual(r.returncode, 0, r.stderr)
        return json.loads(r.stdout)

    def test_perfect_fit_is_tier1_and_sorted_first(self):
        cfg = {
            "weights": {"industry": 0.35, "size": 0.25, "stage": 0.2, "geo": 0.2},
            "tiers": {"1": 75, "2": 50},
            "target_industries": ["software"], "target_sizes": [[51, 200]],
            "target_stages": ["series a"], "target_geos": ["united states"],
        }
        companies = [
            {"name": "Bad", "industry": "retail", "employees": 5000,
             "funding_stage": "ipo", "location": "France"},
            {"name": "Good", "industry": "software", "employees": 120,
             "funding_stage": "Series A", "location": "United States"},
        ]
        out = self._run(companies, cfg)
        self.assertEqual(out[0]["name"], "Good")  # sorted desc by score
        self.assertEqual(out[0]["fit_score"], 100.0)
        self.assertEqual(out[0]["tier"], 1)
        self.assertEqual(out[-1]["name"], "Bad")
        self.assertEqual(out[-1]["tier"], 3)


if __name__ == "__main__":
    unittest.main()
