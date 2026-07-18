"""VIN parsing and validation pipeline."""

import re
from dataclasses import dataclass, field

from app.domain.check_digit import check_digit_valid, compute_check_digit
from app.domain.model_year import YearDecode, decode_model_year
from app.domain.wmi import manufacturer_for, region_for

VIN_PATTERN = re.compile(r"^[A-HJ-NPR-Z0-9]{17}$")
ILLEGAL_CHARS = set("IOQ")


@dataclass
class VinIssue:
    code: str
    message: str
    severity: str  # "error" blocks lookup, "warning" does not


@dataclass
class ParsedVIN:
    raw: str
    normalized: str
    wmi: str = ""
    vds: str = ""
    vis: str = ""
    valid_format: bool = False
    check_digit_ok: bool = False
    year_decode: YearDecode = field(default_factory=lambda: YearDecode(year=None))
    issues: list[VinIssue] = field(default_factory=list)

    @property
    def errors(self) -> list[VinIssue]:
        return [i for i in self.issues if i.severity == "error"]

    @property
    def warnings(self) -> list[VinIssue]:
        return [i for i in self.issues if i.severity == "warning"]

    @property
    def ok(self) -> bool:
        return not self.errors


def normalize_vin(raw: str) -> str:
    """Uppercase and strip whitespace and hyphens."""
    return re.sub(r"[\s\-]", "", (raw or "")).upper()


def parse_vin(raw: str, strict: bool = False) -> ParsedVIN:
    """Validate and structurally parse a VIN.

    Check digit failure is a warning by default because VINs from outside
    North America do not always conform to ISO 3779; strict mode promotes
    it to an error.
    """
    normalized = normalize_vin(raw)
    parsed = ParsedVIN(raw=raw, normalized=normalized)

    if len(normalized) != 17:
        parsed.issues.append(VinIssue(
            code="length",
            message=f"VINs are exactly 17 characters; you entered {len(normalized)}.",
            severity="error",
        ))
        return parsed

    illegal = sorted(set(normalized) & ILLEGAL_CHARS)
    if illegal:
        parsed.issues.append(VinIssue(
            code="illegal_chars",
            message=(
                f"The letter{'s' if len(illegal) > 1 else ''} {', '.join(illegal)} never "
                f"appear{'' if len(illegal) > 1 else 's'} in a VIN. "
                "I is usually a mistyped 1; O and Q are usually 0."
            ),
            severity="error",
        ))
        return parsed

    if not VIN_PATTERN.match(normalized):
        parsed.issues.append(VinIssue(
            code="charset",
            message="VINs may only contain letters (except I, O, Q) and digits.",
            severity="error",
        ))
        return parsed

    parsed.valid_format = True
    parsed.wmi = normalized[0:3]
    parsed.vds = normalized[3:9]
    parsed.vis = normalized[9:17]
    parsed.year_decode = decode_model_year(normalized)

    parsed.check_digit_ok = check_digit_valid(normalized)
    if not parsed.check_digit_ok:
        expected = compute_check_digit(normalized)
        parsed.issues.append(VinIssue(
            code="check_digit",
            message=(
                f"Check digit mismatch: position 9 is {normalized[8]!r} but ISO 3779 "
                f"computes {expected!r}. North American VINs must pass this check; "
                "some imported vehicles legitimately fail it."
            ),
            severity="error" if strict else "warning",
        ))

    return parsed


def structural_summary(parsed: ParsedVIN) -> dict:
    """What the VIN itself tells us, independent of any provider."""
    region, country = region_for(parsed.normalized)
    return {
        "wmi": parsed.wmi,
        "vds": parsed.vds,
        "vis": parsed.vis,
        "region": region,
        "country": country,
        "manufacturer": manufacturer_for(parsed.wmi),
        "year": parsed.year_decode.year,
        "year_candidates": parsed.year_decode.candidates,
        "check_digit_ok": parsed.check_digit_ok,
    }
