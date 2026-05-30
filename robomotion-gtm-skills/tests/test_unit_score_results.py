"""Unit tests for messaging-ab-tester/score_results.py — fixed-weight normalization and the
significance gate (>20% relative-lift email winner, LinkedIn scorability)."""
import os
import sys
import unittest

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _util import load_script  # noqa: E402

mod = load_script("messaging-ab-tester", "score_results.py")


class TestDerive(unittest.TestCase):
    def test_email_rates_and_thresholds(self):
        d = mod.derive_email({"variant": "A", "sends": 200, "opens": 100,
                              "replies": 20, "positive_replies": 8})
        self.assertEqual(d["open_rate"], 0.5)
        self.assertEqual(d["reply_rate"], 0.1)
        self.assertTrue(d["directional"])
        self.assertTrue(d["confident"])  # >= 200 sends

    def test_email_below_directional(self):
        d = mod.derive_email({"variant": "A", "sends": 40})
        self.assertFalse(d["directional"])

    def test_linkedin_scorable_threshold(self):
        self.assertTrue(mod.derive_linkedin({"variant": "A", "impressions": 500})["scorable"])
        self.assertFalse(mod.derive_linkedin({"variant": "B", "impressions": 499})["scorable"])


class TestEmailWinner(unittest.TestCase):
    def _score(self, rows):
        rows = mod.normalize_and_score(rows, mod.EMAIL_WEIGHTS,
                                       ["open_rate", "reply_rate", "positive_reply_rate"])
        return mod.rank(rows)

    def test_clear_winner_over_20pct_lift(self):
        a = mod.derive_email({"variant": "A", "sends": 300, "opens": 180,
                              "replies": 60, "positive_replies": 40})
        b = mod.derive_email({"variant": "B", "sends": 300, "opens": 90,
                              "replies": 15, "positive_replies": 5})
        verdict = mod.call_winner_email(self._score([a, b]))
        self.assertEqual(verdict["winner"], "A")
        self.assertGreater(verdict["relative_lift"], 0.20)
        self.assertEqual(verdict["confidence"], "confident")  # both >=200 sends

    def test_too_close_to_call_is_a_tie(self):
        a = mod.derive_email({"variant": "A", "sends": 300, "opens": 152,
                              "replies": 31, "positive_replies": 16})
        b = mod.derive_email({"variant": "B", "sends": 300, "opens": 150,
                              "replies": 30, "positive_replies": 15})
        verdict = mod.call_winner_email(self._score([a, b]))
        self.assertIsNone(verdict["winner"])
        self.assertEqual(verdict["confidence"], "tie")

    def test_insufficient_volume_refuses(self):
        a = mod.derive_email({"variant": "A", "sends": 30, "opens": 20, "replies": 5})
        verdict = mod.call_winner_email(self._score([a]))
        self.assertEqual(verdict["confidence"], "insufficient")


class TestLinkedinWinner(unittest.TestCase):
    def test_unscorable_is_directional_only(self):
        rows = [mod.derive_linkedin({"variant": "A", "impressions": 100, "engagements": 5})]
        rows = mod.normalize_and_score(
            rows, mod.LINKEDIN_WEIGHTS,
            ["engagement", "comment_quality", "impressions", "profile_visits"])
        verdict = mod.call_winner_linkedin(mod.rank(rows))
        self.assertEqual(verdict["confidence"], "insufficient")


if __name__ == "__main__":
    unittest.main()
