"""Model year decoding from VIN position 10.

Year codes repeat on a 30 year cycle. For VINs conforming to the North
American standard, position 7 disambiguates: alphabetic means the 2010-2039
window, numeric means 1980-2009.
"""

from dataclasses import dataclass, field
from datetime import date

# Order matters: index in this string is the offset from the cycle base year.
# I, O, Q, U, Z and 0 are never used as year codes.
YEAR_CODES = "ABCDEFGHJKLMNPRSTVWXY123456789"

CYCLE_BASES = (1980, 2010, 2040)


@dataclass
class YearDecode:
    year: int | None
    candidates: list[int] = field(default_factory=list)
    rule_applied: str = ""


def decode_model_year(vin: str, today: date | None = None) -> YearDecode:
    """Decode position 10 into a model year, or candidates when ambiguous."""
    today = today or date.today()
    max_year = today.year + 1
    code = vin[9].upper() if len(vin) >= 10 else ""
    idx = YEAR_CODES.find(code)
    if idx == -1:
        return YearDecode(year=None, rule_applied="invalid_year_code")

    candidates = [base + idx for base in CYCLE_BASES if base + idx <= max_year]
    if not candidates:
        return YearDecode(year=None, rule_applied="invalid_year_code")

    pos7 = vin[6].upper() if len(vin) >= 7 else ""
    if pos7.isalpha():
        window = [y for y in candidates if y >= 2010]
        if window:
            return YearDecode(year=window[-1], candidates=candidates,
                              rule_applied="position7_alpha_2010_2039")
    elif pos7.isdigit():
        window = [y for y in candidates if y < 2010]
        if window:
            return YearDecode(year=window[-1], candidates=candidates,
                              rule_applied="position7_numeric_1980_2009")

    if len(candidates) == 1:
        return YearDecode(year=candidates[0], candidates=candidates,
                          rule_applied="single_candidate")
    return YearDecode(year=None, candidates=candidates, rule_applied="ambiguous")
