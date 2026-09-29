"""Part 2: Guardrail and growth-detection engine."""
import csv


def mom_growth(previous: float, current: float) -> float:
    """Month-on-Month growth percentage, rounded to 2 decimals."""
    return round((current - previous) / previous * 100, 2)


def is_flagged(mom_pct: float, threshold: float = 8.0) -> str:
    """Return 'flagged', 'not_flagged' or 'escalate_exact_boundary' (never a bare bool)."""
    if abs(mom_pct) > threshold:
        return "flagged"
    if abs(mom_pct) < threshold:
        return "not_flagged"
    return "escalate_exact_boundary"


def validate_feed(csv_path: str):
    """Input guardrail for a month,category,revenue,n_orders CSV.

    Returns (True, []) if there are no errors, else (False, errors).
    Line numbers are 1-indexed with the header as line 1.
    """
    errors = []
    with open(csv_path, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for line_no, row in enumerate(reader, start=2):
            month = (row.get("month") or "").strip()
            category = (row.get("category") or "").strip()
            revenue = (row.get("revenue") or "").strip()

            if category == "":
                errors.append(f"line {line_no}: missing category (month={month})")

            if revenue == "":
                errors.append(f"line {line_no}: missing revenue (category={category})")
            else:
                try:
                    value = float(revenue)
                except ValueError:
                    errors.append(f"line {line_no}: revenue not numeric: {revenue!r}")
                else:
                    if value < 0:
                        errors.append(
                            f"line {line_no}: negative revenue ({value}) for category={category}"
                        )
    return (len(errors) == 0, errors)