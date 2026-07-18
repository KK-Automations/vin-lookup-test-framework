import pytest

from app import create_app
from app.domain.records import VehicleRecord
from app.providers.base import VinProvider
from app.services.lookup import LookupService
from config.settings import Settings


class FakeProvider(VinProvider):
    name = "fake"
    display_name = "Fake provider"
    needs_key = False
    timeout_s = 1.0

    def __init__(self, settings, fields: dict | None = None):
        super().__init__(settings)
        self._fields = fields or {"make": "Honda", "model": "Accord", "year": 2003}

    def fetch(self, vin: str) -> dict:
        return dict(self._fields)

    def to_record(self, raw: dict) -> VehicleRecord:
        record = VehicleRecord()
        for name, value in raw.items():
            record.set(name, value, str(value), self.name)
        return record


@pytest.fixture
def settings(tmp_path):
    return Settings(vin_db_path=str(tmp_path / "test.sqlite3"), testing=True)


@pytest.fixture
def app(settings):
    app = create_app(settings)
    app.config["TESTING"] = True
    app.config["LOOKUP_SERVICE"] = LookupService(
        settings, providers=[FakeProvider(settings)]
    )
    return app


@pytest.fixture
def client(app):
    return app.test_client()
