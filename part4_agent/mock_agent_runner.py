"""Part 4: Mock agent runner. Ties Parts 1-3 together. No network, no API key, no sending.

Usage (from repo root):
    py part4_agent/mock_agent_runner.py may
    py part4_agent/mock_agent_runner.py june
    py part4_agent/mock_agent_runner.py corrupted
"""
import csv
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "part2_engine"))
sys.path.insert(0, os.path.join(HERE, "..", "part3_narrative"))

from growth_engine import mom_growth, is_flagged, validate_feed  # Part 2, unmodified
from narrative_template import fill_template                      # Part 3

MAX_DRAFTS = 3  # cap to prevent notification flooding


def _load(csv_path):
    """{category: revenue} from a month,category,revenue,n_orders CSV."""
    with open(csv_path, newline="", encoding="utf-8") as f:
        return {r["category"]: float(r["revenue"]) for r in csv.DictReader(f)}


def _prev_month_name(csv_path):
    with open(csv_path, newline="", encoding="utf-8") as f:
        return next(csv.DictReader(f))["month"]


def run(month: str, previous_month_csv: str, current_month_csv: str) -> dict:
    result = {
        "run_month": month,
        "validation_status": "valid",
        "validation_errors": [],
        "flagged_categories": [],
        "suppressed_categories": [],
        "escalated_categories": [],
        "action_taken": "drafted_and_held_for_approval",
    }

    # Subtasks 1-2: validate both feeds; invalid means Hard Stop (no MoM attempted)
    errors = []
    for path in (previous_month_csv, current_month_csv):
        ok, errs = validate_feed(path)
        errors.extend(errs)
    if errors:
        result["validation_status"] = "invalid"
        result["validation_errors"] = errors
        result["action_taken"] = "hard_stop"
        return result

    previous = _load(previous_month_csv)
    current = _load(current_month_csv)
    prev_month = _prev_month_name(previous_month_csv)

    # Subtasks 3-4: MoM and flag status for every category
    flagged, escalated = [], []
    for category, cur_rev in current.items():
        prev_rev = previous[category]
        pct = mom_growth(prev_rev, cur_rev)
        status = is_flagged(pct)
        if status == "flagged":
            flagged.append({"category": category, "mom_pct": pct,
                            "previous_revenue": prev_rev, "current_revenue": cur_rev})
        elif status == "escalate_exact_boundary":
            escalated.append(category)  # subtask 7b: never drafted, never dropped
        # "not_flagged" appears nowhere in the output

    # Subtask 5: sort flagged by size of change, largest first
    flagged.sort(key=lambda d: abs(d["mom_pct"]), reverse=True)

    # Subtasks 6-7: draft the top 3 only; the rest are suppressed for manual review
    for i, item in enumerate(flagged):
        if i < MAX_DRAFTS:
            item["drafted"] = True
            item["message"] = fill_template(item["category"], item["previous_revenue"],
                                            item["current_revenue"], item["mom_pct"],
                                            month, prev_month)
            result["flagged_categories"].append(item)
        else:
            result["suppressed_categories"].append(item["category"])

    result["escalated_categories"] = escalated
    return result  # subtask 8: one structured JSON object per run


if __name__ == "__main__":
    fx = os.path.join(HERE, "fixtures")
    scenarios = {
        "may": ("May", os.path.join(fx, "april.csv"), os.path.join(fx, "may.csv")),
        "june": ("June", os.path.join(fx, "may.csv"), os.path.join(fx, "june.csv")),
        "corrupted": ("July", os.path.join(fx, "june.csv"),
                      os.path.join(HERE, "..", "part2_engine", "fixtures", "corrupted_feed.csv")),
    }
    key = sys.argv[1] if len(sys.argv) > 1 else "may"
    print(json.dumps(run(*scenarios[key]), indent=2))