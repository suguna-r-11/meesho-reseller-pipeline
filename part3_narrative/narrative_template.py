"""Part 3: offline template-fill for the prompt pack (no LLM, no API key).

Every number in the drafted message is one of the supplied inputs, so every figure
traces back to a Part 1 / Part 2 value.
"""


def fill_template(category: str, previous_revenue: float, current_revenue: float,
                  mom_pct: float, month: str, prev_month: str) -> str:
    rose = mom_pct > 0
    direction = "increase" if rose else "decline"
    if rose:
        action = (f"check whether the rise in {category} came from a few resellers or many, "
                  f"and confirm stock availability and return rates for {category} "
                  f"before {month} demand carries forward")
    else:
        action = (f"check whether resellers reduced their {category} listings or whether "
                  f"{category} demand fell, and compare order counts and return rates for "
                  f"{category} between {prev_month} and {month}")
    return (
        f"Context: This update covers {category} revenue, {month} versus {prev_month}. "
        f"Revenue was INR {previous_revenue:.2f} in {prev_month} and INR {current_revenue:.2f} in {month}.\n"
        f"Insight (fact): {category} revenue changed by {mom_pct}% month on month, an overall {direction}.\n"
        f"Implication (hypothesis, not proven by this data alone): the movement may reflect a "
        f"change in reseller activity or product mix. Recommended next step: {action}."
    )


if __name__ == "__main__":
    print(fill_template("Ethnic Wear", 104520.77, 185107.61, 77.1, "May", "April"))
    print()
    print(fill_template("Ethnic Wear", 185107.61, 76371.53, -58.74, "June", "May"))