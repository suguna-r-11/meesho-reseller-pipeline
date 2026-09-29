"""Agent-level tests. Run from the repo root:  py part4_agent/test_mock_agent_runner.py"""
import os
import re
import tempfile
import unittest

from mock_agent_runner import run

HERE = os.path.dirname(os.path.abspath(__file__))
FX = os.path.join(HERE, "fixtures")
CORRUPTED = os.path.join(HERE, "..", "part2_engine", "fixtures", "corrupted_feed.csv")
KEYS = {"run_month", "validation_status", "validation_errors", "flagged_categories",
        "suppressed_categories", "escalated_categories", "action_taken"}


def may():
    return run("May", os.path.join(FX, "april.csv"), os.path.join(FX, "may.csv"))


def june():
    return run("June", os.path.join(FX, "may.csv"), os.path.join(FX, "june.csv"))


class TestAgent(unittest.TestCase):
    def test_may_scenario(self):
        r = may()
        self.assertEqual(set(r), KEYS)
        self.assertEqual(r["validation_status"], "valid")
        self.assertEqual([(d["category"], d["mom_pct"]) for d in r["flagged_categories"]],
                         [("Ethnic Wear", 77.1), ("Western Wear", -23.6), ("Kids Wear", -23.48)])
        self.assertTrue(all(d["drafted"] for d in r["flagged_categories"]))
        self.assertEqual(sorted(r["suppressed_categories"]),
                         ["Beauty & Personal Care", "Home & Kitchen"])
        self.assertEqual(r["escalated_categories"], [])
        self.assertEqual(r["action_taken"], "drafted_and_held_for_approval")

    def test_june_scenario(self):
        r = june()
        self.assertEqual([(d["category"], d["mom_pct"]) for d in r["flagged_categories"]],
                         [("Ethnic Wear", -58.74), ("Home & Kitchen", 42.59), ("Kids Wear", 23.9)])
        self.assertEqual(r["suppressed_categories"], ["Western Wear"])
        names = [d["category"] for d in r["flagged_categories"]] + r["suppressed_categories"]
        self.assertNotIn("Beauty & Personal Care", names)  # never flagged
        self.assertEqual(r["escalated_categories"], [])

    def test_corrupted_feed_hard_stop(self):
        r = run("July", os.path.join(FX, "june.csv"), CORRUPTED)
        self.assertEqual(set(r), KEYS)
        self.assertEqual(r["validation_status"], "invalid")
        self.assertEqual(r["action_taken"], "hard_stop")
        self.assertEqual(r["validation_errors"], [
            "line 3: negative revenue (-4200.0) for category=Western Wear",
            "line 4: missing category (month=July)",
            "line 6: missing revenue (category=Home & Kitchen)",
        ])
        self.assertEqual(r["flagged_categories"], [])
        self.assertEqual(r["suppressed_categories"], [])

    def test_every_number_in_messages_traces_to_inputs(self):
        for r in (may(), june()):
            for d in r["flagged_categories"]:
                allowed = {d["previous_revenue"], d["current_revenue"], d["mom_pct"]}
                found = {float(x) for x in re.findall(r"-?\d+(?:\.\d+)?", d["message"])}
                self.assertTrue(found <= allowed, (d["category"], found - allowed))
                self.assertIn(d["category"], d["message"])
                self.assertIn(str(d["mom_pct"]), d["message"])

    def test_exact_boundary_is_escalated_not_drafted(self):
        with tempfile.TemporaryDirectory() as tmp:
            prev, cur = os.path.join(tmp, "p.csv"), os.path.join(tmp, "c.csv")
            with open(prev, "w", newline="") as f:
                f.write("month,category,revenue,n_orders\nApril,Boundary Cat,100000,10\n")
            with open(cur, "w", newline="") as f:
                f.write("month,category,revenue,n_orders\nMay,Boundary Cat,108000,10\n")
            r = run("May", prev, cur)
        self.assertEqual(r["escalated_categories"], ["Boundary Cat"])
        self.assertEqual(r["flagged_categories"], [])
        self.assertEqual(r["suppressed_categories"], [])


if __name__ == "__main__":
    unittest.main(verbosity=2)