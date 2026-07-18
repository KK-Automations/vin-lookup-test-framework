from app.consensus.engine import (
    CONFIRMED,
    CONFLICT,
    SINGLE,
    UNKNOWN,
    ConsensusEngine,
)
from app.domain.records import VehicleRecord
from app.providers.base import ProviderResult


def make_result(provider: str, fields: dict) -> ProviderResult:
    record = VehicleRecord()
    for name, value in fields.items():
        record.set(name, value, str(value), provider)
    return ProviderResult(
        provider=provider, display_name=provider, ok=True,
        record=record, raw={}, error=None, latency_ms=1,
    )


class TestBadgeStates:
    def test_confirmed_when_two_agree(self):
        report = ConsensusEngine().evaluate([
            make_result("a", {"make": "Honda"}),
            make_result("b", {"make": "honda"}),
        ])
        assert report.fields["make"].status == CONFIRMED
        assert report.fields["make"].value == "Honda"

    def test_single_source(self):
        report = ConsensusEngine().evaluate([
            make_result("a", {"make": "Honda"}),
            make_result("b", {}),
        ])
        assert report.fields["make"].status == SINGLE

    def test_conflict_shows_all_votes(self):
        report = ConsensusEngine().evaluate([
            make_result("a", {"year": 2003}),
            make_result("b", {"year": 2004}),
        ])
        field = report.fields["year"]
        assert field.status == CONFLICT
        assert {v.value for v in field.votes} == {2003, 2004}

    def test_unknown_when_no_source(self):
        report = ConsensusEngine().evaluate([make_result("a", {})])
        assert report.fields["make"].status == UNKNOWN


class TestConfidence:
    def test_all_confirmed_is_high(self):
        report = ConsensusEngine().evaluate([
            make_result("a", {"make": "Honda", "model": "Accord", "year": 2003}),
            make_result("b", {"make": "Honda", "model": "Accord", "year": 2003}),
        ])
        assert report.confidence == 1.0
        assert report.confidence_bucket == "High"

    def test_all_single_is_medium(self):
        report = ConsensusEngine().evaluate([
            make_result("a", {"make": "Honda", "model": "Accord"}),
        ])
        assert report.confidence == 0.5
        assert report.confidence_bucket == "Medium"

    def test_empty_results_is_low(self):
        report = ConsensusEngine().evaluate([])
        assert report.confidence == 0.0
        assert report.confidence_bucket == "Low"


class TestContainmentAgreement:
    def test_brand_vs_corporate_entity_confirmed(self):
        report = ConsensusEngine().evaluate([
            make_result("a", {"manufacturer": "Honda"}),
            make_result("b", {"manufacturer": "AMERICAN HONDA MOTOR CO., INC."}),
        ])
        field = report.fields["manufacturer"]
        assert field.status == CONFIRMED
        assert field.value == "Honda"

    def test_country_variants_confirmed(self):
        report = ConsensusEngine().evaluate([
            make_result("a", {"plant_country": "United States"}),
            make_result("b", {"plant_country": "UNITED STATES (USA)"}),
        ])
        assert report.fields["plant_country"].status == CONFIRMED

    def test_real_disagreement_still_conflicts(self):
        report = ConsensusEngine().evaluate([
            make_result("a", {"manufacturer": "Honda"}),
            make_result("b", {"manufacturer": "Toyota"}),
        ])
        assert report.fields["manufacturer"].status == CONFLICT


class TestIndependence:
    def test_dependent_provider_not_counted(self):
        engine = ConsensusEngine(independence={"a": True, "b": False})
        report = engine.evaluate([
            make_result("a", {"make": "Honda"}),
            make_result("b", {"make": "Honda"}),
        ])
        field = report.fields["make"]
        assert field.status == CONFIRMED
        assert field.independent_sources == 1
