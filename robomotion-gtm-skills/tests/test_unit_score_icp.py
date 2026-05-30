"""Unit tests for kol-engager-icp/score_icp.py — the deterministic ICP-fit + intent + topic
scoring, the hard gates (competitor employer / excluded title), and tier assignment."""
import os
import sys
import unittest
from types import SimpleNamespace

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _util import load_script  # noqa: E402

mod = load_script("kol-engager-icp", "score_icp.py")


def icp(**over):
    base = {
        "target_titles": ["head of revops", "revenue operations"],
        "exclude_titles": ["intern", "student"],
        "target_seniorities": ["director", "vp"],
        "industries": ["software"],
        "competitors": ["acme automation"],
        "geos": ["united states"],
        "company_sizes": ["51-200"],
        "topic_keywords": ["rpa", "automation"],
    }
    base.update(over)
    return base


class TestIcpFit(unittest.TestCase):
    def test_competitor_employer_is_hard_gate(self):
        _, _, gates = mod.score_icp_fit({"company": "Acme Automation Inc"}, icp())
        self.assertIn("competitor_employer", gates)

    def test_excluded_title_is_hard_gate(self):
        _, _, gates = mod.score_icp_fit({"title": "Marketing Intern"}, icp())
        self.assertIn("excluded_title", gates)

    def test_full_title_match_scores_max(self):
        pts, bd, gates = mod.score_icp_fit(
            {"title": "Head of RevOps", "seniority": "director",
             "industry": "Software", "company_size": "51-200",
             "location": "United States"}, icp())
        self.assertEqual(gates, [])
        self.assertEqual(bd["title_match"], 25)
        self.assertEqual(pts, 60.0)  # 25+12+10+8+5, capped at 60

    def test_neutral_scoring_when_icp_unspecified(self):
        empty = icp(target_titles=[], target_seniorities=[], industries=[],
                    company_sizes=[], geos=[])
        pts, bd, _ = mod.score_icp_fit({}, empty)
        self.assertEqual(bd["title_match"], 12)  # neutral, not zero
        self.assertEqual(pts, 30.0)              # 12+6+5+4+3


class TestIntentAndTopic(unittest.TestCase):
    def test_recent_commenter_scores_highest(self):
        val, bd = mod.score_intent({"engagement_type": "comment", "posted_days_ago": 3})
        self.assertEqual(bd["engagement_base"], 18)
        self.assertEqual(bd["recency_bonus"], 7)
        self.assertEqual(val, 25.0)

    def test_old_reaction_scores_low(self):
        val, bd = mod.score_intent({"engagement_type": "reaction", "posted_days_ago": 90})
        self.assertEqual(bd["engagement_base"], 10)
        self.assertEqual(bd["recency_bonus"], 1)
        self.assertEqual(val, 11.0)

    def test_topic_mention_in_comment_adds_points(self):
        val, bd = mod.score_topic({"comment_text": "we use RPA for this"}, icp())
        self.assertEqual(bd["comment_topic_mention"], 7)
        self.assertEqual(val, 15.0)

    def test_topic_base_only_when_no_mention(self):
        val, _ = mod.score_topic({"comment_text": "nice post"}, icp())
        self.assertEqual(val, 8.0)


class TestTiering(unittest.TestCase):
    def _args(self, **o):
        d = {"tier_a": 70.0, "tier_b": 50.0, "min_icp_fit": 25.0}
        d.update(o)
        return SimpleNamespace(**d)

    def test_gate_forces_tier_c(self):
        self.assertEqual(mod.tier_of(95, ["competitor_employer"], 60, self._args()), "C")

    def test_low_icp_fit_forces_tier_c(self):
        self.assertEqual(mod.tier_of(80, [], 20, self._args()), "C")

    def test_high_score_is_tier_a(self):
        self.assertEqual(mod.tier_of(75, [], 50, self._args()), "A")

    def test_mid_score_is_tier_b(self):
        self.assertEqual(mod.tier_of(55, [], 40, self._args()), "B")


if __name__ == "__main__":
    unittest.main()
