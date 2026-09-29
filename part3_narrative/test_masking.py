"""Tests for masking.py. Run from the repo root:  py part3_narrative/test_masking.py"""
import csv
import os
import unittest

from masking import alias_for, assert_no_raw_names_leak

HERE = os.path.dirname(os.path.abspath(__file__))


def reseller_names():
    path = os.path.join(HERE, "..", "data", "resellers.csv")
    with open(path, newline="", encoding="utf-8") as f:
        return [r["reseller_name"] for r in csv.DictReader(f)]


def top_reseller_section():
    with open(os.path.join(HERE, "narrative_report.md"), encoding="utf-8") as f:
        text = f.read()
    return text.split("## 5. Top-reseller narrative")[1]


class TestMasking(unittest.TestCase):
    def test_alias_for(self):
        self.assertEqual(alias_for("RS019"), "ALIAS-19")
        self.assertEqual(alias_for("RS006"), "ALIAS-06")

    def test_final_narrative_has_no_raw_names(self):
        self.assertTrue(assert_no_raw_names_leak(top_reseller_section(), reseller_names()))

    def test_negative_case_leaky_version_fails(self):
        leaky = top_reseller_section().replace("ALIAS-19", "Mumbai Reseller 1")
        self.assertFalse(assert_no_raw_names_leak(leaky, reseller_names()))


if __name__ == "__main__":
    unittest.main(verbosity=2)