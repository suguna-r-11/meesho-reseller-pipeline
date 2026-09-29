"""Part 3.4: Masking policy. External-facing text must never contain a raw reseller name."""


def alias_for(reseller_id: str) -> str:
    """RS019 -> ALIAS-19, RS006 -> ALIAS-06."""
    return f"ALIAS-{reseller_id[3:]}"


def assert_no_raw_names_leak(text: str, reseller_names: list) -> bool:
    """Return False if any raw reseller name appears verbatim in text, else True."""
    for name in reseller_names:
        if name in text:
            return False
    return True


if __name__ == "__main__":
    print(alias_for("RS019"))  # ALIAS-19
    print(alias_for("RS006"))  # ALIAS-06
    names = ["Mumbai Reseller 1", "Mumbai Reseller 4"]
    print(assert_no_raw_names_leak("West region ALIAS-19 led spend.", names))          # True
    print(assert_no_raw_names_leak("West region Mumbai Reseller 1 led spend.", names))  # False