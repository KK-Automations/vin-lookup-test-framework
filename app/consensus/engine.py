"""Cross-provider consensus: per-field agreement, badges, and confidence.

Badge states:
    CONFIRMED  two or more providers agree on the value
    SINGLE     exactly one provider reported the field
    CONFLICT   providers disagree; every value is shown with its source
    UNKNOWN    no provider reported the field ("not available")

The overall confidence is a weighted average over reported fields. The
formula is deliberately simple and fully explained in the UI tooltip.
"""

from collections import Counter
from dataclasses import dataclass, field
from typing import Any

from app.domain.records import CANONICAL_FIELDS, FieldValue
from app.providers.base import ProviderResult

CONFIRMED = "confirmed"
SINGLE = "single"
CONFLICT = "conflict"
UNKNOWN = "unknown"

STATUS_SCORES = {CONFIRMED: 1.0, SINGLE: 0.5, CONFLICT: 0.2}

FIELD_WEIGHTS = {
    "make": 3, "model": 3, "year": 3,
    "trim": 2, "body_class": 2, "engine_model": 2, "engine_cylinders": 2,
    "displacement_l": 2, "fuel_type": 2,
}
DEFAULT_WEIGHT = 1

HIGH_THRESHOLD = 0.8
MEDIUM_THRESHOLD = 0.5


# Fields where providers report the same fact at different specificity,
# e.g. "Honda" vs "AMERICAN HONDA MOTOR CO., INC.". Containment counts as
# agreement and the shortest value is displayed.
CONTAINMENT_FIELDS = {"make", "manufacturer", "plant_country", "plant_city"}


def _comparable(field_name: str, value: Any) -> Any:
    """Normalize a value for cross-provider comparison."""
    if isinstance(value, str):
        return value.casefold().strip()
    if field_name == "displacement_l" and isinstance(value, (int, float)):
        return round(float(value), 1)
    return value


def _containment_groups(values: list[str]) -> list[list[str]]:
    """Group strings where one contains the other (case-insensitive)."""
    groups: list[list[str]] = []
    for value in values:
        folded = value.casefold()
        for group in groups:
            if any(folded in g.casefold() or g.casefold() in folded for g in group):
                group.append(value)
                break
        else:
            groups.append([value])
    return groups


@dataclass
class FieldConsensus:
    field: str
    status: str
    value: Any | None
    votes: list[FieldValue] = field(default_factory=list)
    independent_sources: int = 0


@dataclass
class ConsensusReport:
    fields: dict[str, FieldConsensus]
    confidence: float
    confidence_bucket: str
    providers_ok: int
    providers_total: int

    @property
    def confidence_pct(self) -> int:
        return round(self.confidence * 100)


class ConsensusEngine:
    def __init__(self, independence: dict[str, bool] | None = None) -> None:
        # provider name -> counts_as_independent
        self.independence = independence or {}

    def evaluate(self, results: list[ProviderResult]) -> ConsensusReport:
        ok_results = [r for r in results if r.ok and r.record is not None]

        fields: dict[str, FieldConsensus] = {}
        for name in CANONICAL_FIELDS:
            votes = [
                r.record.fields[name]
                for r in ok_results
                if name in r.record.fields
            ]
            fields[name] = self._evaluate_field(name, votes)

        reported = [fc for fc in fields.values() if fc.status != UNKNOWN]
        if reported:
            weighted_sum = sum(
                STATUS_SCORES[fc.status] * FIELD_WEIGHTS.get(fc.field, DEFAULT_WEIGHT)
                for fc in reported
            )
            total_weight = sum(
                FIELD_WEIGHTS.get(fc.field, DEFAULT_WEIGHT) for fc in reported
            )
            confidence = weighted_sum / total_weight
        else:
            confidence = 0.0

        if confidence >= HIGH_THRESHOLD:
            bucket = "High"
        elif confidence >= MEDIUM_THRESHOLD:
            bucket = "Medium"
        else:
            bucket = "Low"

        return ConsensusReport(
            fields=fields,
            confidence=confidence,
            confidence_bucket=bucket,
            providers_ok=len(ok_results),
            providers_total=len(results),
        )

    def _evaluate_field(self, name: str, votes: list[FieldValue]) -> FieldConsensus:
        if not votes:
            return FieldConsensus(field=name, status=UNKNOWN, value=None)

        independent = sum(
            1 for v in votes if self.independence.get(v.provider, True)
        )

        if len(votes) == 1:
            return FieldConsensus(
                field=name, status=SINGLE, value=votes[0].value,
                votes=votes, independent_sources=independent,
            )

        if name in CONTAINMENT_FIELDS and all(isinstance(v.value, str) for v in votes):
            groups = _containment_groups([v.value for v in votes])
            if len(groups) == 1:
                return FieldConsensus(
                    field=name, status=CONFIRMED,
                    value=min(groups[0], key=len),
                    votes=votes, independent_sources=independent,
                )
            return FieldConsensus(
                field=name, status=CONFLICT,
                value=min(max(groups, key=len), key=len),
                votes=votes, independent_sources=independent,
            )

        counts = Counter(_comparable(name, v.value) for v in votes)
        modal_key, _ = counts.most_common(1)[0]
        modal_value = next(
            v.value for v in votes if _comparable(name, v.value) == modal_key
        )

        status = CONFIRMED if len(counts) == 1 else CONFLICT
        return FieldConsensus(
            field=name, status=status, value=modal_value,
            votes=votes, independent_sources=independent,
        )
