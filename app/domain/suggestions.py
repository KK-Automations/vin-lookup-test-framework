"""Typo detection and correction suggestions for invalid VINs.

Strategy:
1. If the VIN contains I, O, or Q, substitute the digits they are usually
   confused with and keep combinations that pass the check digit.
2. If the VIN is well formed but fails the check digit, try single position
   swaps from a table of visually confusable pairs and keep candidates that
   pass the check digit.

Suggestions are capped and ranked so the UI can offer one click retries.
"""

from dataclasses import dataclass
from itertools import product

from app.domain.check_digit import check_digit_valid
from app.domain.vin import VIN_PATTERN, normalize_vin

MAX_SUGGESTIONS = 3

# Substitutions for characters that are illegal in VINs.
ILLEGAL_SUBS = {"I": ["1"], "O": ["0"], "Q": ["0", "9"]}

# Visually confusable pairs, applied in both directions.
CONFUSION_PAIRS = [("S", "5"), ("B", "8"), ("Z", "2"), ("G", "6"),
                   ("D", "0"), ("T", "7"), ("A", "4")]

CONFUSION_MAP: dict[str, list[str]] = {}
for a, b in CONFUSION_PAIRS:
    CONFUSION_MAP.setdefault(a, []).append(b)
    CONFUSION_MAP.setdefault(b, []).append(a)


@dataclass
class Suggestion:
    vin: str
    description: str
    confidence: str  # "high" | "medium"


def _describe_change(original: str, fixed: str) -> str:
    changes = [
        f"{o} to {f} at position {i + 1}"
        for i, (o, f) in enumerate(zip(original, fixed))
        if o != f
    ]
    return ", ".join(changes)


def suggest_corrections(raw: str) -> list[Suggestion]:
    vin = normalize_vin(raw)
    if len(vin) != 17:
        return []

    suggestions: list[Suggestion] = []
    seen: set[str] = set()

    illegal_positions = [i for i, ch in enumerate(vin) if ch in ILLEGAL_SUBS]
    if illegal_positions:
        options = [ILLEGAL_SUBS[vin[i]] for i in illegal_positions]
        for combo in product(*options):
            candidate = list(vin)
            for pos, repl in zip(illegal_positions, combo):
                candidate[pos] = repl
            fixed = "".join(candidate)
            if fixed in seen or not VIN_PATTERN.match(fixed):
                continue
            seen.add(fixed)
            if check_digit_valid(fixed):
                suggestions.append(Suggestion(
                    vin=fixed,
                    description=f"{_describe_change(vin, fixed)}, check digit valid",
                    confidence="high",
                ))
            else:
                suggestions.append(Suggestion(
                    vin=fixed,
                    description=_describe_change(vin, fixed),
                    confidence="medium",
                ))
        suggestions.sort(key=lambda s: s.confidence != "high")
        return suggestions[:MAX_SUGGESTIONS]

    if VIN_PATTERN.match(vin) and not check_digit_valid(vin):
        for i, ch in enumerate(vin):
            for repl in CONFUSION_MAP.get(ch, []):
                candidate = vin[:i] + repl + vin[i + 1:]
                if candidate in seen or not VIN_PATTERN.match(candidate):
                    continue
                seen.add(candidate)
                if check_digit_valid(candidate):
                    suggestions.append(Suggestion(
                        vin=candidate,
                        description=f"{ch} to {repl} at position {i + 1}, check digit valid",
                        confidence="high",
                    ))
        return suggestions[:MAX_SUGGESTIONS]

    return []
