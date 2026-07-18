import re

VIN_PATTERN = re.compile(r"^[A-HJ-NPR-Z0-9]{17}$")


def is_valid_vin(vin):
    """Check that a VIN is 17 characters from the allowed alphabet (no I, O, Q)."""
    if not vin:
        return False
    return bool(VIN_PATTERN.match(vin.upper()))
