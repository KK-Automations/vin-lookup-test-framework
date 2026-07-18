class TestPages:
    def test_index_renders(self, client):
        response = client.get("/")
        assert response.status_code == 200
        assert b"Decode any VIN" in response.data

    def test_healthz(self, client):
        response = client.get("/healthz")
        assert response.status_code == 200
        assert response.get_json()["status"] == "ok"


class TestLookupPartial:
    def test_valid_vin_returns_result_fragment(self, client):
        response = client.post("/partials/lookup", data={"vin": "1HGCM82633A004352"})
        assert response.status_code == 200
        assert b"1HGCM82633A004352" in response.data
        assert b"Honda" in response.data

    def test_invalid_vin_returns_error_card(self, client):
        response = client.post("/partials/lookup", data={"vin": "TOOSHORT"})
        assert response.status_code == 200
        assert b"second look" in response.data

    def test_illegal_letter_offers_suggestion(self, client):
        response = client.post("/partials/lookup", data={"vin": "1HGCM8263OA004352"})
        assert response.status_code == 200
        assert b"Did you mean" in response.data
        assert b"1HGCM82630A004352" in response.data
