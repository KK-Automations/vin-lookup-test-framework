"""NHTSA vPIC provider. Free, no key, authoritative for North America."""

import requests

from app.domain.records import VehicleRecord
from app.providers.base import ProviderError, VinProvider

DECODE_URL = "https://vpic.nhtsa.dot.gov/api/vehicles/DecodeVinValues/{vin}?format=json"

# vPIC values that mean "no data", mapped to absent fields.
EMPTY_VALUES = {"", "not applicable", "n/a", "0"}


def _clean(value: str | None) -> str | None:
    if value is None:
        return None
    value = value.strip()
    return value if value.lower() not in EMPTY_VALUES else None


def _to_int(value: str | None) -> int | None:
    value = _clean(value)
    try:
        return int(value) if value is not None else None
    except ValueError:
        return None


def _to_float(value: str | None) -> float | None:
    value = _clean(value)
    try:
        return round(float(value), 1) if value is not None else None
    except ValueError:
        return None


class NhtsaVpicProvider(VinProvider):
    name = "nhtsa_vpic"
    display_name = "NHTSA vPIC"
    needs_key = False
    timeout_s = 8.0
    counts_as_independent = True

    def fetch(self, vin: str) -> dict:
        try:
            response = requests.get(DECODE_URL.format(vin=vin), timeout=self.timeout_s)
            response.raise_for_status()
            payload = response.json()
        except requests.RequestException as exc:
            raise ProviderError(f"NHTSA vPIC request failed: {exc}") from exc
        except ValueError as exc:
            raise ProviderError("NHTSA vPIC returned invalid JSON") from exc

        results = payload.get("Results") or []
        if not results:
            raise ProviderError("NHTSA vPIC returned no results")
        return results[0]

    def to_record(self, raw: dict) -> VehicleRecord:
        record = VehicleRecord()

        def put(field: str, key: str, converter=None):
            raw_value = raw.get(key)
            value = converter(raw_value) if converter else _clean(raw_value)
            record.set(field, value, str(raw_value), self.name)

        put("make", "Make")
        put("model", "Model")
        put("year", "ModelYear", _to_int)
        put("trim", "Trim")
        put("series", "Series")
        put("body_class", "BodyClass")
        put("vehicle_type", "VehicleType")
        put("engine_model", "EngineModel")
        put("engine_cylinders", "EngineCylinders", _to_int)
        put("displacement_l", "DisplacementL", _to_float)
        put("fuel_type", "FuelTypePrimary")
        put("drive_type", "DriveType")
        put("transmission", "TransmissionStyle")
        put("doors", "Doors", _to_int)
        put("manufacturer", "Manufacturer")
        put("plant_city", "PlantCity")
        put("plant_country", "PlantCountry")

        make = record.get("make")
        if make and isinstance(make.value, str):
            record.set("make", make.value.title(), make.raw_value, self.name)
        return record
