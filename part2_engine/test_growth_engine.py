"""Given-When-Then tests for growth_engine. Run: py part2_engine/test_growth_engine.py"""
import csv
import os
import unittest

from growth_engine import mom_growth, is_flagged, validate_feed

HERE = os.path.dirname(os.path.abspath(__file__))
FIX = os.path.join(HERE, "fixtures")


def load_revenue(path):
    """{(month, category): revenue} from a month,category,revenue,n_orders CSV."""
    with open(path, newline="", encoding="utf-8") as f:
        return {(r["month"], r["category"]): float(r["revenue"]) for r in csv.DictReader(f)}


class TestGrowthEngine(unittest.TestCase):
    def test_1_ethnic_wear_april_to_may_flagged(self):
        # GIVEN April->May Ethnic Wear revenue moves 104520.77 -> 185107.61
        prev, cur = 104520.77, 185107.61
        # WHEN mom_growth then is_flagged run
        pct = mom_growth(prev, cur)
        # THEN 77.1 and "flagged"
        self.assertEqual(pct, 77.1)
        self.assertEqual(is_flagged(pct), "flagged")

    def test_2_beauty_may_to_june_not_flagged(self):
        # GIVEN May->June Beauty & Personal Care 35542.11 -> 37559.07
        pct = mom_growth(35542.11, 37559.07)
        # THEN 5.67 and "not_flagged"
        self.assertEqual(pct, 5.67)
        self.assertEqual(is_flagged(pct), "not_flagged")

    def test_3_exact_boundary_escalates(self):
        # GIVEN previous=100000, current=108000 (exactly on the threshold)
        pct = mom_growth(100000, 108000)
        # THEN exactly 8.0 and "escalate_exact_boundary"
        self.assertEqual(pct, 8.0)
        self.assertEqual(is_flagged(pct), "escalate_exact_boundary")

    def test_4_corrupted_feed_returns_three_errors(self):
        # GIVEN the corrupted feed fixture
        ok, errors = validate_feed(os.path.join(FIX, "corrupted_feed.csv"))
        # THEN (False, errors) with exactly 3 entries, in order
        self.assertFalse(ok)
        self.assertEqual(errors, [
            "line 3: negative revenue (-4200.0) for category=Western Wear",
            "line 4: missing category (month=July)",
            "line 6: missing revenue (category=Home & Kitchen)",
        ])

    def test_5_clean_feed_passes(self):
        # GIVEN the validated Part 1 output
        ok, errors = validate_feed(os.path.join(FIX, "monthly_category_revenue.csv"))
        # THEN (True, [])
        self.assertEqual((ok, errors), (True, []))

    def test_6_may_vs_april_table(self):
        rev = load_revenue(os.path.join(FIX, "monthly_category_revenue.csv"))
        expected = {"Ethnic Wear": 77.1, "Western Wear": -23.6, "Kids Wear": -23.48,
                    "Home & Kitchen": -9.25, "Beauty & Personal Care": -12.75}
        for cat, exp in expected.items():
            pct = mom_growth(rev[("April", cat)], rev[("May", cat)])
            self.assertEqual(pct, exp, cat)
            self.assertEqual(is_flagged(pct), "flagged", cat)

    def test_7_june_vs_may_table(self):
        rev = load_revenue(os.path.join(FIX, "monthly_category_revenue.csv"))
        expected = {"Ethnic Wear": (-58.74, "flagged"), "Western Wear": (11.97, "flagged"),
                    "Kids Wear": (23.9, "flagged"), "Home & Kitchen": (42.59, "flagged"),
                    "Beauty & Personal Care": (5.67, "not_flagged")}
        for cat, (exp, status) in expected.items():
            pct = mom_growth(rev[("May", cat)], rev[("June", cat)])
            self.assertEqual(pct, exp, cat)
            self.assertEqual(is_flagged(pct), status, cat)


if __name__ == "__main__":
    unittest.main(verbosity=2)