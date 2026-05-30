"""Unit tests for ad-campaign-analyzer/ab_significance.py — the two-proportion z-test and
the minimum-sample significance gate. Pure math + a couple of end-to-end CLI checks."""
import json
import os
import sys
import unittest

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _util import load_script, run_script  # noqa: E402

mod = load_script("ad-campaign-analyzer", "ab_significance.py")


class TestZTest(unittest.TestCase):
    def test_equal_proportions_gives_zero_z_and_p_one(self):
        z, p, p1, p2 = mod.two_prop_ztest(50, 1000, 50, 1000)
        self.assertAlmostEqual(z, 0.0, places=6)
        self.assertAlmostEqual(p, 1.0, places=6)
        self.assertEqual((p1, p2), (0.05, 0.05))

    def test_known_z_value(self):
        # 10/100 vs 20/100: pooled p=0.15, se=sqrt(0.15*0.85*0.02)=0.050497, z=0.1/se=1.980
        z, p, p1, p2 = mod.two_prop_ztest(10, 100, 20, 100)
        self.assertAlmostEqual(z, 1.980, places=2)
        self.assertLess(p, 0.05)
        self.assertEqual((p1, p2), (0.1, 0.2))

    def test_zero_denominator_returns_none(self):
        self.assertIsNone(mod.two_prop_ztest(5, 0, 5, 100))

    def test_zero_variance_is_safe(self):
        # no successes in either arm -> se == 0 -> defined, not a crash
        z, p, p1, p2 = mod.two_prop_ztest(0, 100, 0, 100)
        self.assertEqual((z, p), (0.0, 1.0))

    def test_norm_cdf_midpoint(self):
        self.assertAlmostEqual(mod.norm_cdf(0.0), 0.5, places=9)


class TestCliGate(unittest.TestCase):
    def _run(self, *args):
        r = run_script("ad-campaign-analyzer", "ab_significance.py", *args)
        self.assertEqual(r.returncode, 0, r.stderr)
        return json.loads(r.stdout)

    def test_ctr_below_min_sample_refuses_verdict(self):
        out = self._run("--metric", "ctr", "--a-clicks", "40", "--a-impr", "1000",
                        "--b-clicks", "55", "--b-impr", "1000")
        self.assertFalse(out["enough_data"])
        self.assertFalse(out["significant"])
        self.assertIn("100 clicks", out["reason"])

    def test_ctr_significant_picks_winner(self):
        out = self._run("--metric", "ctr", "--a-clicks", "300", "--a-impr", "12000",
                        "--b-clicks", "600", "--b-impr", "12000")
        self.assertTrue(out["enough_data"])
        self.assertTrue(out["significant"])
        self.assertEqual(out["winner"], "B")

    def test_cpa_below_min_conversions_refuses(self):
        out = self._run("--metric", "cpa", "--a-conv", "10", "--a-clicks", "500",
                        "--b-conv", "12", "--b-clicks", "500")
        self.assertFalse(out["enough_data"])
        self.assertIn("30 conversions", out["reason"])


if __name__ == "__main__":
    unittest.main()
