from app.cache.repository import CatalogCacheRepository, VinCacheRepository


class TestVinCacheRepository:
    def test_response_roundtrip(self, tmp_path):
        repo = VinCacheRepository(str(tmp_path / "cache.sqlite3"))
        repo.save_response("VIN1", "nhtsa_vpic", "ok", 120, {"Make": "HONDA"})
        fresh = repo.fresh_responses("VIN1")
        assert "nhtsa_vpic" in fresh
        assert fresh["nhtsa_vpic"].raw == {"Make": "HONDA"}

    def test_error_responses_not_served(self, tmp_path):
        repo = VinCacheRepository(str(tmp_path / "cache.sqlite3"))
        repo.save_response("VIN1", "carapi", "error", 50, None)
        assert repo.fresh_responses("VIN1") == {}

    def test_expired_responses_not_served(self, tmp_path):
        repo = VinCacheRepository(str(tmp_path / "cache.sqlite3"), response_ttl_days=0)
        repo.save_response("VIN1", "nhtsa_vpic", "ok", 120, {"Make": "HONDA"})
        assert repo.fresh_responses("VIN1") == {}

    def test_recent_lookups_ordering_and_hits(self, tmp_path):
        repo = VinCacheRepository(str(tmp_path / "cache.sqlite3"))
        repo.record_lookup("VINA", "Honda", "Accord", 2003, 0.8, "High")
        repo.record_lookup("VINB", "Ford", "F-150", 2019, 0.6, "Medium")
        repo.record_lookup("VINA", "Honda", "Accord", 2003, 0.8, "High")
        recent = repo.recent_lookups()
        assert recent[0]["vin"] == "VINA"
        assert recent[0]["hit_count"] == 2
        assert len(recent) == 2


class TestCatalogCacheRepository:
    def test_roundtrip(self, tmp_path):
        repo = CatalogCacheRepository(str(tmp_path / "cache.sqlite3"))
        repo.put("makes", ["HONDA", "FORD"])
        assert repo.get("makes") == ["HONDA", "FORD"]

    def test_expiry(self, tmp_path):
        repo = CatalogCacheRepository(str(tmp_path / "cache.sqlite3"), ttl_days=0)
        repo.put("makes", ["HONDA"])
        assert repo.get("makes") is None

    def test_missing_key(self, tmp_path):
        repo = CatalogCacheRepository(str(tmp_path / "cache.sqlite3"))
        assert repo.get("nope") is None
