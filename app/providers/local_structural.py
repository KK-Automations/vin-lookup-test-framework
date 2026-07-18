"""Zero cost provider that decodes only what the VIN itself encodes.

It never fabricates make or model; it reports the model year, region,
country, and manufacturer only when the VIN structure and the curated WMI
table genuinely support them. It also guarantees a non-empty result when
every network provider is down.
"""

from app.domain.model_year import decode_model_year
from app.domain.records import VehicleRecord
from app.domain.wmi import manufacturer_for, region_for
from app.providers.base import VinProvider


class LocalStructuralProvider(VinProvider):
    name = "local"
    display_name = "Local structural decoder"
    needs_key = False
    timeout_s = 1.0
    counts_as_independent = True

    def fetch(self, vin: str) -> dict:
        region, country = region_for(vin)
        year = decode_model_year(vin)
        return {
            "vin": vin,
            "wmi": vin[0:3],
            "region": region,
            "country": country,
            "manufacturer": manufacturer_for(vin[0:3]),
            "year": year.year,
            "year_candidates": year.candidates,
            "year_rule": year.rule_applied,
        }

    def to_record(self, raw: dict) -> VehicleRecord:
        record = VehicleRecord()
        record.set("year", raw.get("year"), str(raw.get("year")), self.name)
        record.set("region", raw.get("region"), str(raw.get("region")), self.name)
        record.set("plant_country", raw.get("country"), str(raw.get("country")), self.name)
        record.set("manufacturer", raw.get("manufacturer"), str(raw.get("manufacturer")), self.name)
        return record
