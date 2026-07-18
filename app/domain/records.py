"""Normalized vehicle record shared by every provider.

A field that a provider did not report is simply absent from the record.
Absent means "not available" and is rendered honestly as such; empty strings
never appear as values.
"""

from dataclasses import dataclass, field
from typing import Any

CANONICAL_FIELDS = [
    "make",
    "model",
    "year",
    "trim",
    "series",
    "body_class",
    "vehicle_type",
    "engine_model",
    "engine_cylinders",
    "displacement_l",
    "fuel_type",
    "drive_type",
    "transmission",
    "doors",
    "manufacturer",
    "plant_city",
    "plant_country",
    "region",
]

FIELD_LABELS = {
    "make": "Make",
    "model": "Model",
    "year": "Model year",
    "trim": "Trim",
    "series": "Series",
    "body_class": "Body class",
    "vehicle_type": "Vehicle type",
    "engine_model": "Engine model",
    "engine_cylinders": "Engine cylinders",
    "displacement_l": "Displacement (L)",
    "fuel_type": "Fuel type",
    "drive_type": "Drive type",
    "transmission": "Transmission",
    "doors": "Doors",
    "manufacturer": "Manufacturer",
    "plant_city": "Plant city",
    "plant_country": "Plant country",
    "region": "Region",
}


@dataclass
class FieldValue:
    value: Any
    raw_value: str
    provider: str


@dataclass
class VehicleRecord:
    fields: dict[str, FieldValue] = field(default_factory=dict)

    def set(self, name: str, value: Any, raw_value: str, provider: str) -> None:
        """Store a field, silently dropping empty or placeholder values."""
        if name not in CANONICAL_FIELDS:
            return
        if value is None:
            return
        if isinstance(value, str):
            value = value.strip()
            if not value or value.lower() in {"not applicable", "n/a", "none", "null"}:
                return
        self.fields[name] = FieldValue(value=value, raw_value=raw_value, provider=provider)

    def get(self, name: str) -> FieldValue | None:
        return self.fields.get(name)
