"""Contract tests: recorded real provider payloads must map cleanly.

Every canonical field is either mapped to a usable value or explicitly
absent; placeholder junk (empty strings, "Not Applicable", paywall notices)
must never survive mapping.
"""

import json
from pathlib import Path

import pytest

from app.domain.records import CANONICAL_FIELDS
from app.providers.carapi import CarApiProvider
from app.providers.nhtsa_vpic import NhtsaVpicProvider
from config.settings import Settings

FIXTURES = Path(__file__).parent.parent / "fixtures"

PROVIDERS = {
    "nhtsa_vpic": lambda: NhtsaVpicProvider(Settings()),
    "carapi": lambda: CarApiProvider(Settings(carapi_token="t", carapi_secret="s")),
}


def fixture_cases():
    return [
        pytest.param(factory, path, id=f"{provider_name}-{path.stem}")
        for provider_name, factory in PROVIDERS.items()
        for path in sorted((FIXTURES / provider_name).glob("*.json"))
    ]


@pytest.mark.parametrize("factory,path", fixture_cases())
class TestRecordedPayloads:
    def test_maps_without_error(self, factory, path):
        record = factory().to_record(json.loads(path.read_text()))
        assert record.fields, "mapper produced an empty record"

    def test_fields_are_canonical_and_clean(self, factory, path):
        record = factory().to_record(json.loads(path.read_text()))
        for name, fv in record.fields.items():
            assert name in CANONICAL_FIELDS
            assert fv.value not in ("", None)
            if isinstance(fv.value, str):
                lowered = fv.value.lower()
                assert lowered not in {"not applicable", "n/a", "none", "null"}
                assert "***" not in fv.value
                assert "note:" not in lowered


class TestKnownVehicles:
    def test_vpic_honda_accord(self):
        payload = json.loads(
            (FIXTURES / "nhtsa_vpic" / "1HGCM82633A004352.json").read_text()
        )
        record = NhtsaVpicProvider(Settings()).to_record(payload)
        assert record.get("make").value == "Honda"
        assert record.get("model").value == "Accord"
        assert record.get("year").value == 2003

    def test_vpic_tesla_model3(self):
        payload = json.loads(
            (FIXTURES / "nhtsa_vpic" / "5YJ3E1EAXKF000316.json").read_text()
        )
        record = NhtsaVpicProvider(Settings()).to_record(payload)
        assert record.get("make").value == "Tesla"
        assert record.get("year").value == 2019
        assert record.get("fuel_type").value == "Electric"


@pytest.mark.live
class TestLiveVpic:
    def test_live_decode(self):
        provider = NhtsaVpicProvider(Settings())
        raw = provider.fetch("1HGCM82633A004352")
        record = provider.to_record(raw)
        assert record.get("make").value == "Honda"
