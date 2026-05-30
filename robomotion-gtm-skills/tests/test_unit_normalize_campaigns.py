"""Unit tests for ad-campaign-analyzer/normalize_campaigns.py — currency/percent parsing,
column-alias canonicalization with derived metrics, and the channel rollup incl.
funnel-adjusted CAC."""
import os
import sys
import unittest

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _util import load_script  # noqa: E402

mod = load_script("ad-campaign-analyzer", "normalize_campaigns.py")


class TestNum(unittest.TestCase):
    def test_strips_currency_and_thousands(self):
        self.assertEqual(mod.num("$1,234.50"), 1234.5)

    def test_percent_and_symbols(self):
        self.assertEqual(mod.num("12.5%"), 12.5)
        self.assertEqual(mod.num("€99"), 99.0)

    def test_blank_and_na_are_zero(self):
        for v in ("", "-", "n/a", "NA", "--", None, "garbage"):
            self.assertEqual(mod.num(v), 0.0)


class TestCanon(unittest.TestCase):
    def test_alias_mapping_and_derived_metrics(self):
        row = mod.canon({"Channel": "Google", "Campaign": "Brand",
                         "Impressions": "10000", "Clicks": "200",
                         "Cost": "$400", "Conversions": "20", "Conv. value": "2000"})
        self.assertEqual(row["platform"], "Google")
        self.assertEqual(row["ctr"], 2.0)        # 200/10000*100
        self.assertEqual(row["cpc"], 2.0)        # 400/200
        self.assertEqual(row["conv_rate"], 10.0)  # 20/200*100
        self.assertEqual(row["cpa"], 20.0)       # 400/20
        self.assertEqual(row["roas"], 5.0)       # 2000/400

    def test_unknown_columns_ignored(self):
        row = mod.canon({"Weird Column": "x", "clicks": "5"})
        self.assertEqual(row["clicks"], 5.0)
        self.assertEqual(row["platform"], "")


class TestRollup(unittest.TestCase):
    def test_aggregates_per_channel(self):
        rows = [mod.canon({"channel": "Meta", "clicks": "100", "cost": "200", "impressions": "5000"}),
                mod.canon({"channel": "Meta", "clicks": "100", "cost": "200", "impressions": "5000"})]
        chans = mod.rollup(rows, {})
        self.assertEqual(len(chans), 1)
        self.assertEqual(chans[0]["clicks"], 200)
        self.assertEqual(chans[0]["cpc"], 2.0)
        self.assertEqual(chans[0]["rows"], 2)

    def test_funnel_adjusted_cac(self):
        rows = [mod.canon({"channel": "Google", "conversions": "100", "cost": "1000"})]
        funnel = {"lead_to_mql": 0.5, "mql_to_sql": 0.5, "sql_to_close": 0.4}
        chans = mod.rollup(rows, funnel)
        c = chans[0]
        self.assertEqual(c["estimated_closes"], 10.0)   # 100 * 0.5*0.5*0.4
        self.assertEqual(c["funnel_adj_cac"], 100.0)    # 1000 / 10


if __name__ == "__main__":
    unittest.main()
