from app.providers.carapi import CarApiProvider
from config.settings import Settings

PAYWALL = ("*** (NOTE: Data is limited to 2015-2020 for non-paying users. "
           "Subscribe to unlock this data.)")


def make_provider():
    return CarApiProvider(Settings(carapi_token="t", carapi_secret="s"))


class TestCarApiMapper:
    def test_normal_payload_maps(self):
        record = make_provider().to_record({
            "make": "HONDA", "model": "Accord", "year": "2003",
            "trim": "EX-V6",
            "specs": {"body_class": "Coupe", "doors": 2, "fuel_type": "Gasoline"},
        })
        assert record.get("make").value == "HONDA"
        assert record.get("year").value == 2003
        assert record.get("doors").value == 2

    def test_paywall_placeholders_become_absent(self):
        record = make_provider().to_record({
            "make": "HONDA",
            "model": PAYWALL,
            "trim": PAYWALL,
            "year": PAYWALL,
            "specs": {"body_class": PAYWALL},
        })
        assert record.get("make").value == "HONDA"
        assert record.get("model") is None
        assert record.get("trim") is None
        assert record.get("year") is None
        assert record.get("body_class") is None
