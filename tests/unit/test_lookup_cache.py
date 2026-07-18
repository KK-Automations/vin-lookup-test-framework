from app.services.lookup import LookupService
from tests.conftest import FakeProvider

VIN = "1HGCM82633A004352"


class CountingProvider(FakeProvider):
    name = "counting"
    display_name = "Counting provider"

    def __init__(self, settings):
        super().__init__(settings)
        self.fetch_calls = 0

    def fetch(self, vin: str) -> dict:
        self.fetch_calls += 1
        return super().fetch(vin)


class TestLookupCaching:
    def test_second_lookup_served_from_cache(self, settings):
        provider = CountingProvider(settings)
        service = LookupService(settings, providers=[provider])

        first = service.lookup(VIN)
        second = service.lookup(VIN)

        assert provider.fetch_calls == 1
        assert not first.from_cache
        assert second.from_cache
        assert second.consensus.fields["make"].value == "Honda"

    def test_force_refresh_bypasses_cache(self, settings):
        provider = CountingProvider(settings)
        service = LookupService(settings, providers=[provider])

        service.lookup(VIN)
        service.lookup(VIN, force_refresh=True)

        assert provider.fetch_calls == 2

    def test_lookup_recorded_for_recent_list(self, settings):
        provider = CountingProvider(settings)
        service = LookupService(settings, providers=[provider])
        service.lookup(VIN)

        recent = service.repository.recent_lookups()
        assert recent[0]["vin"] == VIN
        assert recent[0]["make"] == "Honda"
