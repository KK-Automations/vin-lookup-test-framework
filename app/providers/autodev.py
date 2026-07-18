"""Auto.dev VIN decode provider (https://api.auto.dev/vin/{vin}).

Bearer key auth. The mapper is defensive about payload shape: fields appear
both flat and nested under "vehicle" depending on API version.
"""

import requests

from app.domain.records import VehicleRecord
from app.providers.base import ProviderError, VinProvider

DECODE_URL = "https://api.auto.dev/vin/{vin}"


class AutoDevProvider(VinProvider):
    name = "autodev"
    display_name = "Auto.dev"
    needs_key = True
    timeout_s = 8.0
    # Auto.dev decodes largely from vPIC-derived data; treated as dependent.
    counts_as_independent = False

    def available(self) -> bool:
        return bool(self.settings.autodev_api_key)

    def fetch(self, vin: str) -> dict:
        try:
            response = requests.get(
                DECODE_URL.format(vin=vin),
                headers={"Authorization": f"Bearer {self.settings.autodev_api_key}"},
                timeout=self.timeout_s,
            )
            response.raise_for_status()
            payload = response.json()
        except requests.RequestException as exc:
            raise ProviderError(f"Auto.dev request failed: {exc}") from exc
        except ValueError as exc:
            raise ProviderError("Auto.dev returned invalid JSON") from exc
        if not isinstance(payload, dict):
            raise ProviderError("Auto.dev returned an unexpected payload")
        return payload

    def to_record(self, raw: dict) -> VehicleRecord:
        vehicle = raw.get("vehicle") if isinstance(raw.get("vehicle"), dict) else {}

        def pick(*keys):
            for key in keys:
                for source in (raw, vehicle):
                    value = source.get(key)
                    if value not in (None, ""):
                        return value
            return None

        record = VehicleRecord()
        record.set("make", pick("make"), str(pick("make")), self.name)
        record.set("model", pick("model"), str(pick("model")), self.name)

        year = pick("year")
        if isinstance(year, str) and year.isdigit():
            year = int(year)
        record.set("year", year if isinstance(year, int) else None,
                   str(pick("year")), self.name)

        record.set("trim", pick("trim"), str(pick("trim")), self.name)
        record.set("body_class", pick("body", "bodyType"), str(pick("body")), self.name)
        record.set("engine_model", pick("engine"), str(pick("engine")), self.name)
        record.set("fuel_type", pick("fuel", "fuelType"), str(pick("fuel")), self.name)
        record.set("drive_type", pick("drive", "driveType"), str(pick("drive")), self.name)
        record.set("transmission", pick("transmission"), str(pick("transmission")), self.name)
        record.set("manufacturer", pick("manufacturer"), str(pick("manufacturer")), self.name)
        return record
